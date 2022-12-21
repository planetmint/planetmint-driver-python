import os
import json
import base58
from hashlib import sha3_256
from planetmint_cryptoconditions.types.ed25519 import Ed25519Sha256
from planetmint_cryptoconditions.types.zenroom import ZenroomSha256
from transactions.common.transaction import Transaction
from zenroom import zencode_exec
from ipld import multihash, marshal
import ast


def prepare_tx(script, data, zenroom_signer, plnmint_signer, zenroom_sha256):
    condition_uri_zen = zenroom_sha256.condition.serialize_uri()
    unsigned_fulfillment_dict_zen = {
        "type": zenroom_sha256.TYPE_NAME,
        "public_key": base58.b58encode(plnmint_signer.public_key).decode(),
    }
    output = {
        "amount": "1",
        "condition": {
            "details": unsigned_fulfillment_dict_zen,
            "uri": condition_uri_zen,
        },
        "public_keys": [
            plnmint_signer.public_key,
        ],
    }
    input_ = {
        "fulfillment": None,
        "fulfills": None,
        "owners_before": [
            plnmint_signer.public_key,
        ],
    }
    metadata = {}
    script_ = {
        "code": {"type": "zenroom", "raw": "test_string", "parameters": [{"obj": "1"}, {"obj": "2"}]},  # obsolete
        "state": "dd8bbd234f9869cab4cc0b84aa660e9b5ef0664559b8375804ee8dce75b10576",  #
        "input": data,
        "output": ["ok"],
        "policies": {},
    }
    token_creation_tx = {
        "operation": "CREATE",
        "assets": [{"data": multihash(marshal({"test": "my asset"}))}],
        "metadata": multihash(marshal(metadata)),
        "script": script_,
        "outputs": [
            output,
        ],
        "inputs": [
            input_,
        ],
        "version": Transaction.VERSION,
        "id": None,
    }
    return token_creation_tx, script_


def create_contract_execution(script, data, zenroom_signer, plnmint_signer):
    # prepare transaction
    zenroomscpt = ZenroomSha256(script=script, data=None, keys=zenroom_signer)
    token_transaction, script_input_ = prepare_tx(script, data, zenroom_signer, plnmint_signer, zenroomscpt)

    # prepare contract
    script_input = json.dumps(script_input_)
    execution_output = zenroomscpt.sign(script_input, script, zenroom_signer)
    out_dict = json.loads(execution_output)
    del out_dict["output"]["logs"]
    print(f"output: {execution_output}")
    assert zenroomscpt.validate(message=json.dumps(out_dict))

    fulfillment_uri_zen = zenroomscpt.serialize_uri()
    token_transaction["inputs"][0]["fulfillment"] = fulfillment_uri_zen
    token_transaction["script"] = out_dict  # execution_output
    token_transaction["id"] = None
    json_str_tx = json.dumps(token_transaction, sort_keys=True, skipkeys=False, separators=(",", ":"))
    shared_creation_txid = sha3_256(json_str_tx.encode()).hexdigest()
    token_transaction["id"] = shared_creation_txid
    return token_transaction
