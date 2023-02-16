
.. Copyright Planetmint GmbH and Planetmint contributors
   SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
   Code is Apache-2.0 and docs are CC-BY-4.0

.. image:: https://badges.gitter.im/planetmint/planetmint-driver.svg
   :alt: Join the chat at https://gitter.im/planetmint/planetmint-driver
   :target: https://gitter.im/planetmint/planetmint-driver?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge


.. image:: https://badge.fury.io/py/planetmint-driver.svg
    :target: https://badge.fury.io/py/planetmint-driver

.. image:: https://app.travis-ci.com/planetmint/planetmint-driver.svg?branch=main
    :target: https://app.travis-ci.com/planetmint/planetmint-driver

.. image:: https://img.shields.io/codecov/c/github/planetmint/planetmint-driver/master.svg
    :target: https://codecov.io/github/planetmint/planetmint-driver?branch=master


Planetmint Python Driver
==========================

* Free software: AGPLv3
* Check our `Documentation`_

.. contents:: Table of Contents


Features
--------

* Support for preparing, fulfilling, and sending transactions to a Planetmint
  node.
* Retrieval of transactions by id.

Install
----------

The instructions below were tested on Ubuntu 16.04 LTS. They should also work on other Linux distributions and on macOS. The driver might work on Windows as well, but we do not guarantee it. We recommend to set up (e.g. via Docker on Windows) an Ubuntu VM there.

We recommend you use a virtual environment to install and update to the latest stable version using `pip` (or `pip3`):

.. code-block:: text

    pip install -U planetmint-driver

That will install the latest *stable* Planetmint Python Driver. If you want to install an Alpha, Beta or RC version of the Python Driver, use something like:

.. code-block:: text

    pip install -U planetmint_driver==0.11.1

The above command will install version 0.11.1. You can find a list of all versions in `the release history page on PyPI <https://pypi.org/project/planetmint-driver/#history>`_.

More information on how to install the driver can be found in the `Quickstart`_

Planetmint Documentation
------------------------------------
* `Planetmint Server Quickstart`_
* `The Hitchhiker's Guide to Planetmint`_
* `HTTP API Reference`_
* `All Planetmint Documentation`_

Usage
----------
Example: Create a divisible asset for Alice who issues 10 token to Bob so that he can use her Game Boy.
Afterwards Bob spends 3 of these tokens.

If you want to send a transaction you need to `Determine the Planetmint Root URL`_.

.. code-block:: python

    # import Planetmint and create an object
    from planetmint_driver import Planetmint
    bdb_root_url = 'https://example.com:9984'
    bdb = Planetmint(bdb_root_url)

    # generate a keypair
    from planetmint_driver.crypto import generate_keypair
    alice, bob = generate_keypair(), generate_keypair()

    # create a digital asset for Alice
    game_boy_token = {
        'data': {
            'token_for': {
                'game_boy': {
                    'serial_number': 'LR35902'
                }
            },
            'description': 'Time share token. Each token equals one hour of usage.',
        },
    }

    # prepare the transaction with the digital asset and issue 10 tokens for Bob
    prepared_token_tx = bdb.transactions.prepare(
        operation='CREATE',
        signers=alice.public_key,
        recipients=[([bob.public_key], 10)],
        asset=game_boy_token)

    # fulfill and send the transaction
    fulfilled_token_tx = bdb.transactions.fulfill(
        prepared_token_tx,
        private_keys=alice.private_key)
    bdb.transactions.send_commit(fulfilled_token_tx)

    # Use the tokens
    # create the output and inout for the transaction
    transfer_asset = {'id': fulfilled_token_tx['id']}
    output_index = 0
    output = fulfilled_token_tx['outputs'][output_index]
    transfer_input = {'fulfillment': output['condition']['details'],
                      'fulfills': {'output_index': output_index,
                                   'transaction_id': transfer_asset['id']},
                      'owners_before': output['public_keys']}

    # prepare the transaction and use 3 tokens
    prepared_transfer_tx = bdb.transactions.prepare(
        operation='TRANSFER',
        asset=transfer_asset,
        inputs=transfer_input,
        recipients=[([alice.public_key], 3), ([bob.public_key], 7)])

    # fulfill and send the transaction
    fulfilled_transfer_tx = bdb.transactions.fulfill(
        prepared_transfer_tx,
        private_keys=bob.private_key)
    sent_transfer_tx = bdb.transactions.send_commit(fulfilled_transfer_tx)

Compatibility Matrix
--------------------

+-----------------------+---------------------------+
| **Planetmint Server** | **Planetmint Driver**     |
+=======================+===========================+
| ``>= 2.0.0b7``        | ``0.6.2``                 |
+-----------------------+---------------------------+
| ``>= 2.0.0b7``        | ``0.6.1``                 |
+-----------------------+---------------------------+
| ``>= 2.0.0b7``        | ``0.6.0``                 |
+-----------------------+---------------------------+
| ``>= 2.0.0b5``        | ``0.5.3``                 |
+-----------------------+---------------------------+
| ``>= 2.0.0b5``        | ``0.5.2``                 |
+-----------------------+---------------------------+
| ``>= 2.0.0b5``        | ``0.5.1``                 |
+-----------------------+---------------------------+
| ``>= 2.0.0b1``        | ``0.5.0``                 |
+-----------------------+---------------------------+
| ``>= 2.0.0a3``        | ``0.5.0a4``               |
+-----------------------+---------------------------+
| ``>= 2.0.0a2``        | ``0.5.0a2``               |
+-----------------------+---------------------------+
| ``>= 2.0.0a1``        | ``0.5.0a1``               |
+-----------------------+---------------------------+
| ``>= 1.0.0``          | ``0.4.x``                 |
+-----------------------+---------------------------+
| ``== 1.0.0rc1``       | ``0.3.x``                 |
+-----------------------+---------------------------+
| ``>= 0.9.1``          | ``0.2.x``                 |
+-----------------------+---------------------------+
| ``>= 0.8.2``          | ``>= 0.1.3``              |
+-----------------------+---------------------------+

`Although we do our best to keep the master branches in sync, there may be
occasional delays.`

License
--------
* `licenses`_ - open source & open content

Credits
-------

This package was initially created using Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template. Many Planetmint developers have contributed since then.

.. _Documentation: https://docs.planetmint.com/projects/py-driver/
.. _pypi history: https://pypi.org/project/planetmint-driver/#history
.. _Quickstart: https://docs.planetmint.com/projects/py-driver/en/latest/quickstart.html
.. _Planetmint Server Quickstart: https://docs.planetmint.com/projects/server/en/latest/quickstart.html
.. _The Hitchhiker's Guide to Planetmint: https://www.planetmint.com/developers/guide/
.. _HTTP API Reference: https://docs.planetmint.com/projects/server/en/latest/http-client-server-api.html
.. _All Planetmint Documentation: https://docs.planetmint.com/
.. _Determine the Planetmint Root URL: https://docs.planetmint.com/projects/py-driver/en/latest/connect.html
.. _licenses: https://github.com/planetmint/planetmint-driver/blob/master/LICENSES.md
.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
