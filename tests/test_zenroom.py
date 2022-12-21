import os
import json
import base58
from hashlib import sha3_256
from planetmint_cryptoconditions.types.ed25519 import Ed25519Sha256
from planetmint_cryptoconditions.types.zenroom import ZenroomSha256
from zenroom import zencode_exec
from planetmint_driver import Planetmint
from planetmint_driver.crypto import generate_keypair
from planetmint_driver.driver import Planetmint

from ipld import multihash, marshal
import ast
from planetmint_driver import helper

version = "3.0"


def test_zenroom_signing_simple(
    gen_key_zencode,
    secret_key_to_private_key_zencode,
    fulfill_script_zencode,
    zenroom_data,
    zenroom_house_assets,
    zenroom_script_input,
    condition_script_zencode,
    zenroom_public_keys,
):
    zenroomscpt = ZenroomSha256(script=fulfill_script_zencode, data=zenroom_data, keys=zenroom_public_keys)
    print(f"zenroom is: {zenroomscpt.script}")


def test_zenroom_signing(
    gen_key_zencode,
    secret_key_to_private_key_zencode,
    fulfill_script_zencode,
    zenroom_data,
    zenroom_house_assets,
    condition_script_zencode,
    zenroom_script_input,
    bdb_node,
    zenroom_public_keys,
    alice,
    bob,
):

    plnmnt_keypair = generate_keypair()

    zenroomscpt = ZenroomSha256(script=fulfill_script_zencode, data=zenroom_data, keys=zenroom_public_keys)
    print(f"zenroom is: {zenroomscpt.script}")

    # CRYPTO-CONDITIONS: generate the condition uri
    condition_uri_zen = zenroomscpt.condition.serialize_uri()
    print(f"\nzenroom condition URI: {condition_uri_zen}")

    # CRYPTO-CONDITIONS: construct an unsigned fulfillment dictionary
    unsigned_fulfillment_dict_zen = {
        "type": zenroomscpt.TYPE_NAME,
        "public_key": base58.b58encode(plnmnt_keypair.public_key).decode(),
    }
    output = {
        "amount": "10",
        "condition": {
            "details": unsigned_fulfillment_dict_zen,
            "uri": condition_uri_zen,
        },
        "public_keys": [
            plnmnt_keypair.public_key,
        ],
    }
    input_ = {
        "fulfillment": None,
        "fulfills": None,
        "owners_before": [
            plnmnt_keypair.public_key,
        ],
    }
    metadata = {"result": {"output": ["ok"]}}

    script_ = {
        "code": {
            "type": "zenroom",
            "raw": "test_string",
            "parameters": [{"obj": "1"}, {"obj": "2"}],
        },  # obsolete
        "state": "dd8bbd234f9869cab4cc0b84aa660e9b5ef0664559b8375804ee8dce75b10576",  #
        "input": zenroom_script_input,
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
        "version": version,
        "id": None,
    }

    # JSON: serialize the transaction-without-id to a json formatted string
    tx = json.dumps(
        token_creation_tx,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    script_ = json.dumps(script_)
    # major workflow:
    # we store the fulfill script in the transaction/message (zenroom-sha)
    # the condition script is used to fulfill the transaction and create the signature
    #
    # the server should ick the fulfill script and recreate the zenroom-sha and verify the signature

    signed_input = zenroomscpt.sign(script_, condition_script_zencode, {"keyring": alice})

    input_signed = json.loads(signed_input)
    input_signed["input"]["signature"] = input_signed["output"]["signature"]
    del input_signed["output"]["signature"]
    del input_signed["output"]["logs"]
    input_signed["output"] = ["ok"]  # define expected output that is to be compared
    input_msg = json.dumps(input_signed)

    assert zenroomscpt.validate(message=input_msg)

    tx = json.loads(tx)
    fulfillment_uri_zen = zenroomscpt.serialize_uri()

    tx["inputs"][0]["fulfillment"] = fulfillment_uri_zen
    tx["script"] = input_signed
    tx["id"] = None
    json_str_tx = json.dumps(tx, sort_keys=True, skipkeys=False, separators=(",", ":"))

    # SHA3: hash the serialized id-less transaction to generate the id
    shared_creation_txid = sha3_256(json_str_tx.encode()).hexdigest()
    tx["id"] = shared_creation_txid

    plntmnt = Planetmint(bdb_node)
    sent_transfer_tx = plntmnt.transactions.send_commit(tx)

    print(f"\n\nstatus and result : + {sent_transfer_tx}")


alice_reflow_signing_credentials = {
    "Alice": {
        "credentials": {
            "h": "AxLWb+Cd+Fhy+8aFDafVUzCUvJsaZfmvo+kdkhXWBkXQLvWgJOeSaupLSb3yL7GcPw==",
            "s": "AgQbbYfS8964sDlIaKr2XVYE5YkaEvtJcsOTd5+D+YEfpuyd+ObyTheezj4+YzYMpQ==",
        },
        "keyring": {
            "credential": "X3rx6qfFk35gn6F3n6if1Fzq+rMWbvKWFyd0ypwIQAM=",
            "reflow": "FJzMtffio9DV2+0cgXbI6K0TPkZZgJRV9APUPI8FueI=",
        },
    }
}
reflow_seal_ = {
    "The_Authority": {
        "issuer_public_key": {
            "alpha": "B3pNAhcGoR9rW1mIROuVVd5C1xMz3wEur87pEQPvUuR7lU19mrDHHC7qZrmOL3OdAqJkiIw6ko59Kx6GXPSlNyqa/M2QU3F12OSm534LuOxb0lKls2blPEWk11T+GlJ9GFHyqzVY5NBgActqUEs/D51twHewhT+uXIZoEdOcR//I2i+7gJUBipMOzUzrWK/WDs8pXS4M5fGDsaHtalITqM/pexCuIa+iRFvz7G3Pm1j0QTpDeXlqkPIxcAkqKtwz",
            "beta": "ECbmDkI33ibcuVDf9olouqoiOpEyse3qw9+DuBE2Doz3dc4ohFBH1M/zWigs2XBBFI+Doycq2E402g+wy4haCGU6Nt2jGjw4N5HQA360gad492XvrHS918bLl4kQUbsyC2EHde3ClZgZIM4eDDkoPtXaT2qJpkuuv5Y/Q+CzmemVlTJiaiB3ppcYnZn4UtmAAZujtdUvSimh2jShRGLeOyLo93p1r/sdkznFrnWTZ4TU8wgv4Hr3Z26d8eMcxC4O",
        }
    },
    "reflow_seal": {
        "SM": "AgszTl/cnllWhVbD9gtJal2fVDhdeW4seLbtvwUHEu2qOG7EkXx/0pwhfuABLIorog==",
        "identity": "Agy3w73Mu1b155J5FD5CsUIdx3YQ5C5m8qvHABelVjdvIDF+j79mJ+4iosp1waOMAA==",
        "verifier": "Ba76hy9H7Gkrpr0Pa+HQBWL6wefi7XLKNeV42YF/NOFwaOPHIvzwlUwrZT9big73EF60VEoPQqLBw9SnXsGRFAfpoW+4zDXZu1xHkNGxg7oRphsKNY4n7i7LhVcshPyPCjW2PrEyh3+2fBaGK4v05GfxWUoJSv7kXvUgC/VWT3/kYuBcNE/JpkPWggbMnNYLDvq+fLfO/75+TGG1wNq4JdJ4lye4idTftUV0takDxxozzNPrzosAgkXnxJ1ek4yA",
    },
}


def test_attest_the_reflow_seal(zenroom_public_keys, get_reflow_seal, alice, sign_reflow_seal, bdb_node, driver):
    plnmnt_keypair = generate_keypair()
    plntmnt_alice = generate_keypair()

    get_reflow_object = {
        "Sale": {
            "Buyer": "Alice",
            "Seller": "Bob",
            "Witness": "Carl",
            "Good": "Cow",
            "Price": 100,
            "Currency": "EUR",
            "Timestamp": "1422779638",
            "Text": "Bob sells the cow to Alice, cause the cow grew too big and Carl, Bob's roomie, was complaining",
        }
    }

    get_reflow_keys = {
        "public_keys": {
            "Alice": {
                "reflow_public_key": "DgIQvRyyfS/5Sty6XTSeA59NWam3bkK/lClOLRiS+nTpA6pfmDwjB5DLB6O6N7FYGMEKgI5YcdLDPkN9yM6jB9EUJ23DZ9fN7rsHdhW8yvM7Z/tgQQBpsA1IiylW5FSEDxG1oy4+AyUFlg0MGl/iF/4DCd8CzUAPGr9EztN4LG65xTfL0yq3uJlf2F3+eSUSDG3n809j4tnZcgsG6RjPqoJtjq2XNw+gDScsuxOZ8Hkq6RRWdRXbJMLoeHDy3zjl"
            },
            "Bob": {
                "reflow_public_key": "AfZYZt8R6cNlpQwmSSWGEtAG4kX0DWXLwfYflySZyiwpyhf6bl7tVi9fTfs3xu0bB/YpFeidVCRJLrxbIh7cMchHWJTTlVgkq1+fIelwczPQ/3xe6wAQl7PKvhxJgXhvFSU+ez7DJg+g5qQQK4tw1uxoSkXBiT94vYKJNABGJG7D5z18Lk6Rsp6Ijc6r7uB3A1zD1Lxpz1oSHkSjw7ur9S02qqo6QvgzMMIvI1IKk/y8y+OaghsZwsMaipJ3Dc7D"
            },
            "Carl": {
                "reflow_public_key": "DmFtGO7bpyIgIJXgF+7wrKlQQEtXUxuagWNryz3H/8xbdM3zgCgp3L/T/rHt0ZeyBQtVPeSCurKN/WZ5TEgKXTQjM/HTZTUCTcacXP+fZYnBpMvuzGRF/cJfMsfjsDf2ERDHoBPSLZWpL04jnjpv0pjivPeWjk8Nua2VFFKNE2ccU6pIgIv5f9awx28DWFaFBfeWlw8LB73yAdHs83+bEBOr1GPd4j1n+Zy/5G3nbY0DRlGoIazG9LujAL+ZPGlp"
            },
        }
    }

    # one actor creates the seal and attests the seal to planetmint
    create_seal_result = zencode_exec(
        get_reflow_seal,
        keys=json.dumps(get_reflow_keys),
        data=json.dumps(get_reflow_object),
    )
    seal = create_seal_result.output
    print(f" Reflow Seal: {seal}")

    seal = json.loads(seal)
    print(f" Reflow Seal: {seal}")

    seal = reflow_seal_  # take the original one
    cid = multihash(marshal(seal))
    transaction = driver.transactions.prepare(signers=[plnmnt_keypair.public_key], assets=[{"data": cid}])
    tx = driver.transactions.fulfill(transaction, private_keys=plnmnt_keypair.private_key)
    reflow_seal_transaction = driver.transactions.send_commit(tx)

    print(f"\n\nstatus and result : + {reflow_seal_transaction}")


def test_sign_reflow_seal(zenroom_public_keys, get_reflow_seal, alice, sign_reflow_seal, bdb_node, driver):
    plntmnt_alice = generate_keypair()
    # alice actor signs the reflow signature
    alice_keys = {
        "Alice": {
            "credentials": {
                "h": "AxLWb+Cd+Fhy+8aFDafVUzCUvJsaZfmvo+kdkhXWBkXQLvWgJOeSaupLSb3yL7GcPw==",
                "s": "AgQbbYfS8964sDlIaKr2XVYE5YkaEvtJcsOTd5+D+YEfpuyd+ObyTheezj4+YzYMpQ==",
            },
            "keyring": {
                "credential": "X3rx6qfFk35gn6F3n6if1Fzq+rMWbvKWFyd0ypwIQAM=",
                "reflow": "FJzMtffio9DV2+0cgXbI6K0TPkZZgJRV9APUPI8FueI=",
            },
        }
    }
    sign_relfow = """Scenario 'reflow': sign the reflow seal 
        Given I am 'Alice'
        Given I have my 'credentials'
        Given I have my 'keyring'
        Given I have a 'reflow seal'
        Given I have a 'issuer public key' from 'The Authority'

        # Here the participant is producing a signature, which will later 
        # be added to the reflow seal, along with the other signatures  
        When I create the reflow signature
        Then print the 'reflow signature'"""

    create_seal_result = zencode_exec(sign_relfow, keys=json.dumps(alice_keys), data=json.dumps(reflow_seal_))
    seal_sig = create_seal_result.output
    print(f" Reflow Seal: {seal_sig}")
    seal_sig = ast.literal_eval(seal_sig)
    # seal_sig = json.loads(seal_sig)

    print(f" Reflow Seal signature: {seal_sig}")

    cid = multihash(marshal(seal_sig))
    transaction = driver.transactions.prepare(signers=[plntmnt_alice.public_key], assets=[{"data": cid}])
    tx = driver.transactions.fulfill(transaction, private_keys=plntmnt_alice.private_key)
    reflow_seal_sig_transaction = driver.transactions.send_commit(tx)

    print(f"\n\nstatus and result : + {reflow_seal_sig_transaction}")

    # a random party puts together the seal with the signature
    add_sign_script = """Scenario 'reflow': add the signature to the seal
        Given I have a 'reflow seal'
        Given I have a 'issuer public key' in 'The Authority'
        Given I have a 'reflow signature'

        When I aggregate all the issuer public keys
        When I verify the reflow signature credential
        When I check the reflow signature fingerprint is new
        When I add the reflow fingerprint to the reflow seal
        When I add the reflow signature to the reflow seal
        Then print the 'reflow seal'"""

    transaction = helper.create_contract_execution(add_sign_script, reflow_seal_, seal_sig, plntmnt_alice)
    send_add_sig_2_seal_tx = driver.transactions.send_commit(transaction)

    print(f"\n\nstatus and result : + {send_add_sig_2_seal_tx}")


def test_add_signature_to_reflow_seal(zenroom_public_keys, get_reflow_seal, alice, sign_reflow_seal, bdb_node, driver):
    plnmnt_keypair = generate_keypair()
    plntmnt_alice = generate_keypair()
    seal = reflow_seal_
    get_reflow_object = {
        "Sale": {
            "Buyer": "Alice",
            "Seller": "Bob",
            "Witness": "Carl",
            "Good": "Cow",
            "Price": 100,
            "Currency": "EUR",
            "Timestamp": "1422779638",
            "Text": "Bob sells the cow to Alice, cause the cow grew too big and Carl, Bob's roomie, was complaining",
        }
    }

    get_reflow_keys = {
        "public_keys": {
            "Alice": {
                "reflow_public_key": "DgIQvRyyfS/5Sty6XTSeA59NWam3bkK/lClOLRiS+nTpA6pfmDwjB5DLB6O6N7FYGMEKgI5YcdLDPkN9yM6jB9EUJ23DZ9fN7rsHdhW8yvM7Z/tgQQBpsA1IiylW5FSEDxG1oy4+AyUFlg0MGl/iF/4DCd8CzUAPGr9EztN4LG65xTfL0yq3uJlf2F3+eSUSDG3n809j4tnZcgsG6RjPqoJtjq2XNw+gDScsuxOZ8Hkq6RRWdRXbJMLoeHDy3zjl"
            },
            "Bob": {
                "reflow_public_key": "AfZYZt8R6cNlpQwmSSWGEtAG4kX0DWXLwfYflySZyiwpyhf6bl7tVi9fTfs3xu0bB/YpFeidVCRJLrxbIh7cMchHWJTTlVgkq1+fIelwczPQ/3xe6wAQl7PKvhxJgXhvFSU+ez7DJg+g5qQQK4tw1uxoSkXBiT94vYKJNABGJG7D5z18Lk6Rsp6Ijc6r7uB3A1zD1Lxpz1oSHkSjw7ur9S02qqo6QvgzMMIvI1IKk/y8y+OaghsZwsMaipJ3Dc7D"
            },
            "Carl": {
                "reflow_public_key": "DmFtGO7bpyIgIJXgF+7wrKlQQEtXUxuagWNryz3H/8xbdM3zgCgp3L/T/rHt0ZeyBQtVPeSCurKN/WZ5TEgKXTQjM/HTZTUCTcacXP+fZYnBpMvuzGRF/cJfMsfjsDf2ERDHoBPSLZWpL04jnjpv0pjivPeWjk8Nua2VFFKNE2ccU6pIgIv5f9awx28DWFaFBfeWlw8LB73yAdHs83+bEBOr1GPd4j1n+Zy/5G3nbY0DRlGoIazG9LujAL+ZPGlp"
            },
        }
    }

    # one actor creates the seal and attests the seal to planetmint

    alice_keys = {
        "Alice": {
            "credentials": {
                "h": "AxLWb+Cd+Fhy+8aFDafVUzCUvJsaZfmvo+kdkhXWBkXQLvWgJOeSaupLSb3yL7GcPw==",
                "s": "AgQbbYfS8964sDlIaKr2XVYE5YkaEvtJcsOTd5+D+YEfpuyd+ObyTheezj4+YzYMpQ==",
            },
            "keyring": {
                "credential": "X3rx6qfFk35gn6F3n6if1Fzq+rMWbvKWFyd0ypwIQAM=",
                "reflow": "FJzMtffio9DV2+0cgXbI6K0TPkZZgJRV9APUPI8FueI=",
            },
        }
    }
    sign_relfow = """Scenario 'reflow': sign the reflow seal 
        Given I am 'Alice'
        Given I have my 'credentials'
        Given I have my 'keyring'
        Given I have a 'reflow seal'
        Given I have a 'issuer public key' from 'The Authority'

        # Here the participant is producing a signature, which will later 
        # be added to the reflow seal, along with the other signatures  
        When I create the reflow signature
        Then print the 'reflow signature'"""

    # a random party puts together the seal with the signature
    add_sign_script = """Scenario 'reflow': add the signature to the seal
        Given I have a 'reflow seal'
        Given I have a 'issuer public key' in 'The Authority'
        Given I have a 'reflow signature'

        When I aggregate all the issuer public keys
        When I verify the reflow signature credential
        When I check the reflow signature fingerprint is new
        When I add the reflow fingerprint to the reflow seal
        When I add the reflow signature to the reflow seal
        Then print the 'reflow seal'"""

    create_seal_result = zencode_exec(sign_relfow, keys=json.dumps(alice_keys), data=json.dumps(seal))
    seal_sig = create_seal_result.output
    print(f" Reflow Seal: {seal_sig}")
    seal_sig = ast.literal_eval(seal_sig)

    transaction = helper.create_contract_execution(add_sign_script, reflow_seal_, seal_sig, plntmnt_alice)
    from transactions.common.transaction import Transaction

    try:
        t = Transaction.from_dict(transaction)

    except Exception as e:
        print(f"Exception : {e}")
    send_add_sig_2_seal_tx = driver.transactions.send_commit(transaction)

    print(f"\n\nstatus and result : + {send_add_sig_2_seal_tx}")
