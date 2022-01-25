
.. Copyright Planetmint GmbH and Planetmint contributors
   SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
   Code is Apache-2.0 and docs are CC-BY-4.0

Library Reference
=================

.. automodule:: planetmint_driver

``driver``
----------

.. autoclass:: Planetmint
    :members:

    .. automethod:: __init__

.. automodule:: planetmint_driver.driver

.. autoclass:: TransactionsEndpoint
    :members:

.. autoclass:: OutputsEndpoint
    :members:

.. autoclass:: AssetsEndpoint
    :members:

.. autoclass:: NamespacedDriver
    :members:

    .. automethod:: __init__


``offchain``
------------
.. automodule:: planetmint_driver.offchain
.. autofunction::  prepare_transaction
.. autofunction::  prepare_create_transaction
.. autofunction::  prepare_transfer_transaction
.. autofunction::  fulfill_transaction


``transport``
-------------
.. automodule:: planetmint_driver.transport

.. autoclass:: Transport
    :members:

    .. automethod:: __init__

``pool``
--------
.. automodule:: planetmint_driver.pool

.. autoclass:: Pool
    :members:

    .. automethod:: __init__

.. autoclass:: RoundRobinPicker
    :members:

    .. automethod:: __init__

.. autoclass:: AbstractPicker
    :members:


``connection``
--------------
.. automodule:: planetmint_driver.connection

.. autoclass:: Connection
    :members:

    .. automethod:: __init__


``crypto``
----------
.. automodule:: planetmint_driver.crypto
    :members:


``exceptions``
--------------

.. automodule:: planetmint_driver.exceptions

.. autoexception:: PlanetmintException

.. autoexception:: TransportError

.. autoexception:: ConnectionError

.. autoexception:: NotFoundError

.. autoexception:: KeypairNotFoundException

.. autoexception:: InvalidPrivateKey

.. autoexception:: InvalidPublicKey

.. autoexception:: MissingPrivateKeyError


``utils``
---------

.. automodule:: planetmint_driver.utils
    :members:
    :private-members:
