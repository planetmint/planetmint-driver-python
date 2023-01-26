# Copyright Planetmint GmbH and Planetmint contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

import rapidjson


from planetmint_cryptoconditions import Fulfillment
from sha3 import sha3_256
from pytest import raises, mark
from ipld import multihash, marshal
from transactions.common.utils import _fulfillment_from_details
from transactions.common.transaction import (
    Input,
    TransactionLink,
)


@mark.parametrize(
    "operation,function,return_value",
    (
        ("CREATE", "prepare_create_transaction", "create"),
        ("TRANSFER", "prepare_transfer_transaction", "transfer"),
    ),
)
def test_prepare_transaction(operation, return_value, function, monkeypatch):
    from planetmint_driver import offchain
    from planetmint_driver.offchain import prepare_transaction

    def mock(signers=None, recipients=None, inputs=None, assets=None, metadata=None):
        return return_value

    monkeypatch.setattr(offchain, function, mock)
    assert prepare_transaction(operation=operation) == return_value


def test_prepare_transaction_raises():
    from planetmint_driver.offchain import prepare_transaction
    from planetmint_driver.exceptions import PlanetmintException

    with raises(PlanetmintException):
        prepare_transaction(operation=None)


def test_prepare_create_transaction_default(alice_pubkey):
    from planetmint_driver.offchain import prepare_create_transaction

    create_transaction = prepare_create_transaction(signers=alice_pubkey)
    assert "id" in create_transaction
    assert "version" in create_transaction
    assert "assets" in create_transaction
    assert create_transaction["assets"] == None
    assert "outputs" in create_transaction
    assert "inputs" in create_transaction
    assert "metadata" in create_transaction
    assert "operation" in create_transaction
    assert create_transaction["operation"] == "CREATE"


@mark.parametrize(
    "assets",
    (
        None,
        [{"data": multihash(marshal({"msg": "Hello Planetmint!"}))}],
    ),
)
@mark.parametrize(
    "signers",
    (
        "G7J7bXF8cqSrjrxUKwcF8tCriEKC5CgyPHmtGwUi4BK3",
        ("G7J7bXF8cqSrjrxUKwcF8tCriEKC5CgyPHmtGwUi4BK3",),
        ["G7J7bXF8cqSrjrxUKwcF8tCriEKC5CgyPHmtGwUi4BK3"],
    ),
)
@mark.parametrize(
    "recipients",
    (
        "2dBVUoATxEzEqRdsi64AFsJnn2ywLCwnbNwW7K9BuVuS",
        ("2dBVUoATxEzEqRdsi64AFsJnn2ywLCwnbNwW7K9BuVuS",),
        [(["2dBVUoATxEzEqRdsi64AFsJnn2ywLCwnbNwW7K9BuVuS"], 1)],
    ),
)
def test_prepare_create_transaction(assets, signers, recipients):
    from planetmint_driver.offchain import prepare_create_transaction

    create_transaction = prepare_create_transaction(signers=signers, recipients=recipients, assets=assets)
    assert "id" in create_transaction
    assert "version" in create_transaction
    assert "assets" in create_transaction
    assert create_transaction["assets"] == assets or [{"data": None}]
    assert "outputs" in create_transaction
    assert "inputs" in create_transaction
    assert "metadata" in create_transaction
    assert "operation" in create_transaction
    assert create_transaction["operation"] == "CREATE"


@mark.parametrize(
    "recipients",
    (
        "2dBVUoATxEzEqRdsi64AFsJnn2ywLCwnbNwW7K9BuVuS",
        ("2dBVUoATxEzEqRdsi64AFsJnn2ywLCwnbNwW7K9BuVuS",),
        [(["2dBVUoATxEzEqRdsi64AFsJnn2ywLCwnbNwW7K9BuVuS"], 1)],
    ),
)
def test_prepare_transfer_transaction(signed_alice_transaction, recipients):
    from planetmint_driver.offchain import prepare_transfer_transaction

    condition_index = 0
    condition = signed_alice_transaction["outputs"][condition_index]
    input_ = {
        "fulfillment": condition["condition"]["details"],
        "fulfills": {
            "output_index": condition_index,
            "transaction_id": signed_alice_transaction["id"],
        },
        "owners_before": condition["public_keys"],
    }
    assets = [{"id": signed_alice_transaction["id"]}]
    transfer_transaction = prepare_transfer_transaction(inputs=input_, recipients=recipients, assets=assets)
    assert "id" in transfer_transaction
    assert "version" in transfer_transaction
    assert "assets" in transfer_transaction
    assert "id" in transfer_transaction["assets"][0]
    assert "outputs" in transfer_transaction
    assert "inputs" in transfer_transaction
    assert "metadata" in transfer_transaction
    assert "operation" in transfer_transaction
    assert transfer_transaction["operation"] == "TRANSFER"


def test_prepare_compose_transaction(signed_alice_transaction, compose_asset_cid, alice_pubkey):
    from planetmint_driver.offchain import prepare_compose_transaction

    condition_index = 0
    condition = signed_alice_transaction["outputs"][condition_index]
    inputs_ = [
        Input(
            _fulfillment_from_details(condition["condition"]["details"]),
            condition["public_keys"],
            fulfills=TransactionLink(
                txid=signed_alice_transaction["id"],
                output=condition_index,
            ),
        )
    ]
    assets_ = [signed_alice_transaction["id"], compose_asset_cid]
    compose_transaction = prepare_compose_transaction(inputs=inputs_, recipients=[([alice_pubkey], 1)], assets=assets_)
    assert "id" in compose_transaction
    assert "version" in compose_transaction
    assert "assets" in compose_transaction
    assert "id" in compose_transaction["assets"][1]
    assert "data" in compose_transaction["assets"][0]
    assert len(compose_transaction["assets"]) == 2
    assert compose_asset_cid == compose_transaction["assets"][0]["data"]
    assert "outputs" in compose_transaction
    assert "inputs" in compose_transaction
    assert "metadata" in compose_transaction
    assert "operation" in compose_transaction
    assert compose_transaction["operation"] == "COMPOSE"


def test_prepare_decompose_transaction(
    signed_alice_transaction_not_dict, compose_asset_cid, alice_pubkey, alice_privkey
):
    from planetmint_driver.offchain import prepare_decompose_transaction

    tx_obj = signed_alice_transaction_not_dict
    tx = signed_alice_transaction_not_dict.to_dict()
    inputs_ = tx_obj.to_inputs()
    assets_ = [
        tx["id"],
        "bafkreiawyk3ou5qzqec4ggbvrs56dv5ske2viwprf6he5wj5gr4yv5orsu",
        "bafkreibncbonglm6mi3znbrqbchk56wmgftk4gfevxqlgeif3g5jdotcka",
        "bafkreibkokzihpnnyqf3xslcievqkadf2ozkdi72wyibijih447vq42kjm",
    ]
    recipients = [([alice_pubkey], 1), ([alice_pubkey], 2), ([alice_pubkey], 3)]
    decompose_transaction = prepare_decompose_transaction(inputs=inputs_, recipients=recipients, assets=assets_)

    decompose_transaction_signed = decompose_transaction.sign([alice_privkey])
    decompose_transaction_signed = decompose_transaction_signed.to_dict()

    assert "id" in decompose_transaction_signed
    assert "version" in decompose_transaction_signed
    assert "assets" in decompose_transaction_signed
    assert "id" in decompose_transaction_signed["assets"][3]
    assert "data" in decompose_transaction_signed["assets"][0]
    assert "data" in decompose_transaction_signed["assets"][1]
    assert "data" in decompose_transaction_signed["assets"][2]
    assert len(decompose_transaction_signed["assets"]) == 4
    assert tx["id"] == decompose_transaction_signed["assets"][3]["id"]
    assert "outputs" in decompose_transaction_signed
    assert len(decompose_transaction_signed["outputs"]) == 3
    assert "inputs" in decompose_transaction_signed
    assert len(decompose_transaction_signed["inputs"]) == 1
    assert "metadata" in decompose_transaction_signed
    assert "operation" in decompose_transaction_signed
    assert decompose_transaction_signed["operation"] == "DECOMPOSE"


@mark.parametrize(
    "alice_sk",
    (
        "CT6nWhSyE7dF2znpx3vwXuceSrmeMy9ChBfi9U92HMSP",
        ("CT6nWhSyE7dF2znpx3vwXuceSrmeMy9ChBfi9U92HMSP",),
        ["CT6nWhSyE7dF2znpx3vwXuceSrmeMy9ChBfi9U92HMSP"],
    ),
)
def test_fulfill_transaction(alice_transaction, alice_sk):
    from planetmint_driver.offchain import fulfill_transaction

    fulfilled_transaction = fulfill_transaction(alice_transaction, private_keys=alice_sk)
    inputs = fulfilled_transaction["inputs"]
    assert len(inputs) == 1
    alice_transaction["inputs"][0]["fulfillment"] = None
    message = rapidjson.dumps(
        alice_transaction,
        skipkeys=False,
        ensure_ascii=False,
        sort_keys=True,
    )
    message = sha3_256(message.encode())
    fulfillment_uri = inputs[0]["fulfillment"]
    assert Fulfillment.from_uri(fulfillment_uri).validate(message=message.digest())


def test_fulfill_transaction_raises(alice_transaction, bob_privkey):
    from planetmint_driver.offchain import fulfill_transaction
    from planetmint_driver.exceptions import MissingPrivateKeyError

    with raises(MissingPrivateKeyError):
        fulfill_transaction(alice_transaction, private_keys=bob_privkey)


def test_transaction_fulfill_with_signingning_delegation(
    alice_privkey, alice_transaction, alice_transaction_signature
):
    from planetmint_driver.offchain import (
        fulfill_transaction,
        fulfill_with_signing_delegation,
    )

    fulfilled_transaction = fulfill_transaction(alice_transaction, private_keys=alice_privkey)

    fulfilled_transaction_with_delegation = fulfill_with_signing_delegation(
        alice_transaction, lambda x, y: alice_transaction_signature
    )

    assert fulfilled_transaction == fulfilled_transaction_with_delegation
