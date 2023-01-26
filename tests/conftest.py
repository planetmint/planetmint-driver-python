# Copyright Planetmint GmbH and Planetmint contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

import json
from base64 import b64encode
from collections import namedtuple
from os import environ, urandom

import requests
import base58
from planetmint_cryptoconditions import Ed25519Sha256
from pytest import fixture
from sha3 import sha3_256
from ipld import multihash, marshal
from zenroom import zencode_exec


from transactions.types.assets.create import Create
from transactions.types.assets.compose import Compose
from transactions.common.utils import _fulfillment_to_details
from transactions.common.utils import _fulfillment_from_details
from transactions.common.transaction import (
    Input,
    TransactionLink,
)


def make_ed25519_condition(public_key, *, amount=1):
    ed25519 = Ed25519Sha256(public_key=base58.b58decode(public_key))
    return {
        "amount": str(amount),
        "condition": {
            "details": _fulfillment_to_details(ed25519),
            "uri": ed25519.condition_uri,
        },
        "public_keys": (public_key,),
    }


def make_fulfillment(*public_keys, input_=None):
    return {
        "fulfillment": None,
        "fulfills": input_,
        "owners_before": public_keys,
    }


def serialize_transaction(transaction):
    return json.dumps(
        transaction,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def hash_transaction(transaction):
    return sha3_256(serialize_transaction(transaction).encode()).hexdigest()


def set_transaction_id(transaction):
    tx_id = hash_transaction(transaction)
    transaction["id"] = tx_id


def sign_transaction(transaction, *, public_key, private_key):
    ed25519 = Ed25519Sha256(public_key=base58.b58decode(public_key))
    message = json.dumps(
        transaction,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    message = sha3_256(message.encode())
    ed25519.sign(message.digest(), base58.b58decode(private_key))
    return ed25519.serialize_uri()


@fixture
def alice_privkey():
    return "CT6nWhSyE7dF2znpx3vwXuceSrmeMy9ChBfi9U92HMSP"


@fixture
def alice_pubkey():
    return "G7J7bXF8cqSrjrxUKwcF8tCriEKC5CgyPHmtGwUi4BK3"


@fixture
def alice_keypair(alice_privkey, alice_pubkey):
    keypair = namedtuple("alice_keypair", ["pubkey", "privkey"])
    keypair.vk = alice_pubkey
    keypair.sk = alice_privkey
    return keypair


@fixture
def bob_privkey():
    return "4S1dzx3PSdMAfs59aBkQefPASizTs728HnhLNpYZWCad"


@fixture
def bob_pubkey():
    return "2dBVUoATxEzEqRdsi64AFsJnn2ywLCwnbNwW7K9BuVuS"


@fixture
def bob_keypair(bob_privkey, bob_pubkey):
    keypair = namedtuple("bob_keypair", ["pubkey", "privkey"])
    keypair.vk = bob_pubkey
    keypair.sk = bob_privkey
    return keypair


@fixture
def carol_keypair():
    from planetmint_driver.crypto import generate_keypair

    return generate_keypair()


@fixture
def carol_privkey(carol_keypair):
    return carol_keypair.private_key


@fixture
def carol_pubkey(carol_keypair):
    return carol_keypair.public_key


@fixture
def dimi_keypair():
    from planetmint_driver.crypto import generate_keypair

    return generate_keypair()


@fixture
def dimi_privkey(dimi_keypair):
    return dimi_keypair.private_key


@fixture
def dimi_pubkey(dimi_keypair):
    return dimi_keypair.public_key


@fixture
def ewy_keypair():
    from planetmint_driver.crypto import generate_keypair

    return generate_keypair()


@fixture
def ewy_privkey(ewy_keypair):
    return ewy_keypair.private_key


@fixture
def ewy_pubkey(ewy_keypair):
    return ewy_keypair.public_key


@fixture
def bdb_host():
    return environ.get("BDB_HOST", "localhost")


@fixture
def bdb_port():
    return environ.get("BDB_PORT", "9984")


@fixture
def custom_headers():
    return {"app_id": "id"}


@fixture
def bdb_node(bdb_host, bdb_port):
    return "http://{host}:{port}".format(host=bdb_host, port=bdb_port)


@fixture
def bdb_nodes(bdb_node, custom_headers):
    return [
        {"endpoint": "http://unavailable"},  # unavailable node
        {"endpoint": bdb_node, "headers": custom_headers},
    ]


@fixture
def driver_multiple_nodes(bdb_nodes):
    from planetmint_driver import Planetmint

    return Planetmint(*bdb_nodes)


@fixture
def driver(bdb_node):
    from planetmint_driver import Planetmint

    return Planetmint(bdb_node)


@fixture
def api_root(bdb_node):
    return bdb_node + "/api/v1"


@fixture
def transactions_api_full_url(api_root):
    return api_root + "/transactions?mode=commit"


@fixture
def blocks_api_full_url(api_root):
    return api_root + "/blocks"


@fixture
def mock_requests_post(monkeypatch):
    class MockResponse:
        def __init__(self, json):
            self._json = json

        def json(self):
            return self._json

    def mockreturn(*args, **kwargs):
        return MockResponse(kwargs.get("json"))

    monkeypatch.setattr("requests.post", mockreturn)


@fixture
def alice_transaction_obj(alice_pubkey):
    serial_number = b64encode(urandom(10), altchars=b"-_").decode()
    return Create.generate(
        tx_signers=[alice_pubkey],
        recipients=[([alice_pubkey], 1)],
        assets=[{"data": multihash(marshal({"serial_number": serial_number}))}],
    )


@fixture
def alice_transaction(alice_transaction_obj):
    return alice_transaction_obj.to_dict()


@fixture
def signed_alice_transaction_not_dict(alice_privkey, alice_transaction_obj):
    signed_transaction = alice_transaction_obj.sign([alice_privkey])
    return signed_transaction


@fixture
def signed_alice_transaction(signed_alice_transaction_not_dict):
    return signed_alice_transaction_not_dict.to_dict()


@fixture
def alice_transaction_signature(signed_alice_transaction):
    return Ed25519Sha256.from_uri(signed_alice_transaction["inputs"][0]["fulfillment"]).signature


@fixture
def persisted_alice_transaction(signed_alice_transaction, transactions_api_full_url):
    response = requests.post(transactions_api_full_url, json=signed_alice_transaction)
    return response.json()


@fixture
def persisted_random_transaction(alice_pubkey, alice_privkey):
    from uuid import uuid4

    assets = [{"data": multihash(marshal({"x": str(uuid4())}))}]
    tx = Create.generate(
        tx_signers=[alice_pubkey],
        recipients=[([alice_pubkey], 1)],
        assets=assets,
    )
    return tx.sign([alice_privkey]).to_dict()


@fixture
def compose_asset_cid():
    return "QmW5GVMW98D3mktSDfWHS8nX2UiCd8gP1uCiujnFX4yK8n"


@fixture
def persisted_compose_transaction(signed_alice_transaction, alice_pubkey, compose_asset_cid):
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
    compose_transaction = Compose.generate(inputs=inputs_, recipients=[([alice_pubkey], 1)], assets=assets_)
    return compose_transaction


@fixture
def persisted_decompose_transaction(signed_alice_transaction, alice_pubkey, compose_asset_cid):
    from planetmint_driver.offchain import prepare_decompose_transaction

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
    assets_ = [
        signed_alice_transaction["id"],
        "bafkreiawyk3ou5qzqec4ggbvrs56dv5ske2viwprf6he5wj5gr4yv5orsu",
        "bafkreibncbonglm6mi3znbrqbchk56wmgftk4gfevxqlgeif3g5jdotcka",
        "bafkreibkokzihpnnyqf3xslcievqkadf2ozkdi72wyibijih447vq42kjm",
    ]
    recipients = [([alice_pubkey], 1), ([alice_pubkey], 2), ([alice_pubkey], 3)]
    decompose_transaction = prepare_decompose_transaction(inputs=inputs_, recipients=recipients, assets=assets_)
    return decompose_transaction


@fixture
def sent_persisted_random_transaction(alice_pubkey, alice_privkey, transactions_api_full_url):
    from uuid import uuid4

    assets = [{"data": multihash(marshal({"x": str(uuid4())}))}]
    tx = Create.generate(
        tx_signers=[alice_pubkey],
        recipients=[([alice_pubkey], 1)],
        assets=assets,
    )
    tx_signed = tx.sign([alice_privkey])
    response = requests.post(transactions_api_full_url, json=tx_signed.to_dict())
    return response.json()


@fixture
def block_with_alice_transaction(sent_persisted_random_transaction, blocks_api_full_url):
    return requests.get(
        blocks_api_full_url,
        params={"transaction_id": sent_persisted_random_transaction["id"]},
    ).json()[0][2]


@fixture
def bicycle_data():
    return {
        "bicycle": {
            "manufacturer": "bkfab",
            "serial_number": "abcd1234",
        },
    }


@fixture
def car_data():
    return {
        "car": {
            "manufacturer": "bkfab",
            "vin": "5YJRE11B781000196",
        },
    }


@fixture
def prepared_carol_bicycle_transaction(carol_keypair, bicycle_data):
    condition = make_ed25519_condition(carol_keypair.public_key)
    fulfillment = make_fulfillment(carol_keypair.public_key)
    tx = {
        "assets": [
            {
                "data": multihash(marshal(bicycle_data)),
            }
        ],
        "metadata": None,
        "operation": "CREATE",
        "outputs": (condition,),
        "inputs": (fulfillment,),
        "version": "3.0",
        "id": None,
    }
    return tx


@fixture
def signed_carol_bicycle_transaction(request, carol_keypair, prepared_carol_bicycle_transaction):
    fulfillment_uri = sign_transaction(
        prepared_carol_bicycle_transaction,
        public_key=carol_keypair.public_key,
        private_key=carol_keypair.private_key,
    )
    prepared_carol_bicycle_transaction["inputs"][0].update(
        {"fulfillment": fulfillment_uri},
    )
    set_transaction_id(prepared_carol_bicycle_transaction)
    return prepared_carol_bicycle_transaction


@fixture
def persisted_carol_bicycle_transaction(transactions_api_full_url, signed_carol_bicycle_transaction):
    response = requests.post(transactions_api_full_url, json=signed_carol_bicycle_transaction)
    return response.json()


@fixture
def prepared_carol_car_transaction(carol_keypair, car_data):
    condition = make_ed25519_condition(carol_keypair.public_key)
    fulfillment = make_fulfillment(carol_keypair.public_key)
    tx = {
        "assets": [
            {
                "data": multihash(marshal(car_data)),
            }
        ],
        "metadata": None,
        "operation": "CREATE",
        "outputs": (condition,),
        "inputs": (fulfillment,),
        "version": "3.0",
        "id": None,
    }
    return tx


@fixture
def signed_carol_car_transaction(request, carol_keypair, prepared_carol_car_transaction):
    fulfillment_uri = sign_transaction(
        prepared_carol_car_transaction,
        public_key=carol_keypair.public_key,
        private_key=carol_keypair.private_key,
    )
    prepared_carol_car_transaction["inputs"][0].update(
        {"fulfillment": fulfillment_uri},
    )
    set_transaction_id(prepared_carol_car_transaction)
    return prepared_carol_car_transaction


@fixture
def persisted_carol_car_transaction(transactions_api_full_url, signed_carol_car_transaction):
    response = requests.post(transactions_api_full_url, json=signed_carol_car_transaction)
    return response.json()


@fixture
def persisted_transfer_carol_car_to_dimi(
    carol_keypair,
    dimi_pubkey,
    transactions_api_full_url,
    persisted_carol_car_transaction,
):
    output_txid = persisted_carol_car_transaction["id"]
    ed25519_dimi = Ed25519Sha256(public_key=base58.b58decode(dimi_pubkey))
    transaction = {
        "assets": [{"id": output_txid}],
        "metadata": None,
        "operation": "TRANSFER",
        "outputs": (
            {
                "amount": "1",
                "condition": {
                    "details": _fulfillment_to_details(ed25519_dimi),
                    "uri": ed25519_dimi.condition_uri,
                },
                "public_keys": (dimi_pubkey,),
            },
        ),
        "inputs": (
            {
                "fulfillment": None,
                "fulfills": {
                    "output_index": 0,
                    "transaction_id": output_txid,
                },
                "owners_before": (carol_keypair.public_key,),
            },
        ),
        "version": "3.0",
        "id": None,
    }
    serialized_transaction = json.dumps(
        transaction,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    serialized_transaction = sha3_256(serialized_transaction.encode())

    if transaction["inputs"][0]["fulfills"]:
        serialized_transaction.update(
            "{}{}".format(
                transaction["inputs"][0]["fulfills"]["transaction_id"],
                transaction["inputs"][0]["fulfills"]["output_index"],
            ).encode()
        )

    ed25519_carol = Ed25519Sha256(public_key=base58.b58decode(carol_keypair.public_key))
    ed25519_carol.sign(serialized_transaction.digest(), base58.b58decode(carol_keypair.private_key))
    transaction["inputs"][0]["fulfillment"] = ed25519_carol.serialize_uri()
    set_transaction_id(transaction)
    response = requests.post(transactions_api_full_url, json=transaction)
    return response.json()


@fixture
def persisted_transfer_dimi_car_to_ewy(
    dimi_keypair,
    ewy_pubkey,
    transactions_api_full_url,
    persisted_transfer_carol_car_to_dimi,
):
    output_txid = persisted_transfer_carol_car_to_dimi["id"]
    ed25519_ewy = Ed25519Sha256(public_key=base58.b58decode(ewy_pubkey))
    transaction = {
        "assets": [{"id": persisted_transfer_carol_car_to_dimi["assets"][0]["id"]}],
        "metadata": None,
        "operation": "TRANSFER",
        "outputs": (
            {
                "amount": "1",
                "condition": {
                    "details": _fulfillment_to_details(ed25519_ewy),
                    "uri": ed25519_ewy.condition_uri,
                },
                "public_keys": (ewy_pubkey,),
            },
        ),
        "inputs": (
            {
                "fulfillment": None,
                "fulfills": {
                    "output_index": 0,
                    "transaction_id": output_txid,
                },
                "owners_before": (dimi_keypair.public_key,),
            },
        ),
        "version": "3.0",
        "id": None,
    }
    serialized_transaction = json.dumps(
        transaction,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    serialized_transaction = sha3_256(serialized_transaction.encode())
    if transaction["inputs"][0]["fulfills"]:
        serialized_transaction.update(
            "{}{}".format(
                transaction["inputs"][0]["fulfills"]["transaction_id"],
                transaction["inputs"][0]["fulfills"]["output_index"],
            ).encode()
        )

    ed25519_dimi = Ed25519Sha256(public_key=base58.b58decode(dimi_keypair.public_key))
    ed25519_dimi.sign(serialized_transaction.digest(), base58.b58decode(dimi_keypair.private_key))
    transaction["inputs"][0]["fulfillment"] = ed25519_dimi.serialize_uri()
    set_transaction_id(transaction)
    response = requests.post(transactions_api_full_url, json=transaction)
    return response.json()


@fixture
def unsigned_transaction():
    return {
        "operation": "CREATE",
        "assets": [{"data": multihash(marshal({"serial_number": "NNP43x-DaYoSWg=="}))}],
        "version": "3.0",
        "outputs": [
            {
                "condition": {
                    "details": {
                        "public_key": "G7J7bXF8cqSrjrxUKwcF8tCriEKC5CgyPHmtGwUi4BK3",  # noqa E501
                        "type": "ed25519-sha-256",
                    },
                    "uri": "ni:///sha-256;7U_VA9u_5e4hsgGkaxO_n0W3ZtSlzhCNYWV6iEYU7mo?fpt=ed25519-sha-256&cost=131072",  # noqa E501
                },
                "public_keys": ["G7J7bXF8cqSrjrxUKwcF8tCriEKC5CgyPHmtGwUi4BK3"],
                "amount": "1",
            }
        ],
        "inputs": [
            {
                "fulfills": None,
                "owners_before": ["G7J7bXF8cqSrjrxUKwcF8tCriEKC5CgyPHmtGwUi4BK3"],
                "fulfillment": {
                    "public_key": "G7J7bXF8cqSrjrxUKwcF8tCriEKC5CgyPHmtGwUi4BK3",  # noqa E501
                    "type": "ed25519-sha-256",
                },
            }
        ],
        "id": None,
        "metadata": None,
    }


@fixture
def search_assets():
    assets = [
        {"data": multihash(marshal({"msg": "Hello Planetmint 1!"}))},
        {"data": multihash(marshal({"msg": "Hello Planetmint 2!"}))},
        {"data": multihash(marshal({"msg": "Hello Planetmint 3!"}))},
    ]
    return assets


@fixture
def text_search_assets(api_root, transactions_api_full_url, alice_pubkey, alice_privkey, search_assets):
    # check if the fixture was already executed
    response = requests.get(api_root + "/assets/planetmint")
    response = response.json()
    if len(response) == 3:
        assets = []
        for asset in response:
            assets[asset["id"]] = asset["data"]
        return assets

    # define the assets that will be used by text_search tests

    # write the assets to Planetmint
    assets_to_return = []
    for asset in search_assets:
        tx = Create.generate(
            tx_signers=[alice_pubkey],
            recipients=[([alice_pubkey], 1)],
            assets=[asset],
            metadata=multihash(marshal({"msg": "So call me maybe"})),
        )
        tx_signed = tx.sign([alice_privkey])
        requests.post(transactions_api_full_url, json=tx_signed.to_dict())
        assets_to_return.append({"id": tx_signed.id, "data": asset["data"]})

    # return the assets indexed with the txid that created the assets
    return assets_to_return


CONDITION_SCRIPT = """Scenario 'ecdh': create the signature of an object
    Given I have the 'keyring'
    Given that I have a 'string dictionary' named 'houses'
    When I create the signature of 'houses'
    Then print the 'signature'"""

FULFILL_SCRIPT = """Scenario 'ecdh': Bob verifies the signature from Alice
    Given I have a 'ecdh public key' from 'Alice'
    Given that I have a 'string dictionary' named 'houses'
    Given I have a 'signature' named 'signature'
    When I verify the 'houses' has a signature in 'signature' by 'Alice'
    Then print the string 'ok'"""

SK_TO_PK = """Scenario 'ecdh': Create the keypair
    Scenario 'reflow': Create the key
    Given that I am known as '{}'
    Given I have the 'keyring'
    When I create the ecdh public key
    When I create the bitcoin address
    When I create the reflow public key
    Then print my 'ecdh public key'
    Then print my 'bitcoin address'
    Then print my 'reflow public key'"""

GENERATE_KEYPAIR = """Scenario 'ecdh': Create the keypair
    Scenario 'reflow': Create the key
    Given that I am known as 'Pippo'
    When I create the ecdh key
    When I create the bitcoin key
    When I create the reflow key
    Then print keyring"""

INITIAL_STATE = {"also": "more data"}
SCRIPT_INPUT = {
    "houses": [
        {
            "name": "Harry",
            "team": "Gryffindor",
        },
        {
            "name": "Draco",
            "team": "Slytherin",
        },
    ],
}

metadata = {"units": 300, "type": "KG"}

ZENROOM_DATA = {"that": "is my data"}


@fixture
def gen_key_zencode():
    return GENERATE_KEYPAIR


@fixture
def secret_key_to_private_key_zencode():
    return SK_TO_PK


@fixture
def fulfill_script_zencode():
    return FULFILL_SCRIPT


@fixture
def condition_script_zencode():
    return CONDITION_SCRIPT


@fixture
def zenroom_house_assets():
    return SCRIPT_INPUT


@fixture
def zenroom_script_input():
    return SCRIPT_INPUT


@fixture
def zenroom_data():
    return ZENROOM_DATA


@fixture
def alice(gen_key_zencode):
    alice = json.loads(zencode_exec(gen_key_zencode).output)["keyring"]
    return alice


@fixture
def bob(gen_key_zencode):
    bob = json.loads(zencode_exec(gen_key_zencode).output)["keyring"]
    return bob


@fixture
def zenroom_public_keys(gen_key_zencode, secret_key_to_private_key_zencode, alice, bob):
    zen_public_keys = json.loads(
        zencode_exec(secret_key_to_private_key_zencode.format("Alice"), keys=json.dumps({"keyring": alice})).output
    )
    zen_public_keys.update(
        json.loads(
            zencode_exec(secret_key_to_private_key_zencode.format("Bob"), keys=json.dumps({"keyring": bob})).output
        )
    )
    return zen_public_keys


@fixture
def get_reflow_seal():
    return """Scenario 'reflow': creation of reflow seal
        Given I have a 'reflow public key array' named 'public keys'
        Given I have a 'string dictionary' named 'Sale'
        When I aggregate the reflow public key from array 'public keys'
        When I create the reflow identity of 'Sale'
        When I rename the 'reflow identity' to 'SaleIdentity'
        When I create the reflow seal with identity 'SaleIdentity'
        Then print the 'reflow seal'"""


@fixture
def sign_reflow_seal():
    return """Scenario 'reflow': sign the reflow seal 
        Given I am 'Alice'
        Given I have my 'credentials'
        Given I have my 'keyring'
        Given I have a 'reflow seal'
        Given I have a 'issuer public key' from 'The Authority'

        # Here the participant is producing a signature, which will later 
        # be added to the reflow seal, along with the other signatures  
        When I create the reflow signature
        Then print the 'reflow signature'"""
