# Copyright Planetmint GmbH and Planetmint contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

from .transport import Transport
from .offchain import prepare_transaction, fulfill_transaction
from .utils import normalize_nodes


class Planetmint:
    """A :class:`~planetmint_driver.Planetmint` driver is able to create, sign,
    and submit transactions to one or more nodes in a Federation.

    If initialized with ``>1`` nodes, the driver will send successive
    requests to different nodes in a round-robin fashion (this will be
    customizable in the future).

    """

    def __init__(self, *nodes, transport_class=Transport, headers=None, timeout=20):
        """Initialize a :class:`~planetmint_driver.Planetmint` driver instance.

        Args:
            *nodes (list of (str or dict)): Planetmint nodes to connect to.
                Currently, the full URL must be given. In the absence of any
                node, the default(``'http://localhost:9984'``) will be used.
                If node is passed as a dict, `endpoint` is a required key;
                `headers` is an optional `dict` of headers.
            transport_class: Optional transport class to use.
                Defaults to :class:`~planetmint_driver.transport.Transport`.
            headers (dict): Optional headers that will be passed with
                each request. To pass headers only on a per-request
                basis, you can pass the headers to the method of choice
                (e.g. :meth:`Planetmint().transactions.send_commit()
                <.TransactionsEndpoint.send_commit>`).
            timeout (int): Optional timeout in seconds that will be passed
                to each request.
        """
        self._nodes = normalize_nodes(*nodes, headers=headers)
        self._transport = transport_class(*self._nodes, timeout=timeout)
        self._transactions = TransactionsEndpoint(self)
        self._outputs = OutputsEndpoint(self)
        self._blocks = BlocksEndpoint(self)
        self._assets = AssetsEndpoint(self)
        self._metadata = MetadataEndpoint(self)
        self.api_prefix = "/api/v1"

    @property
    def nodes(self):
        """:obj:`tuple` of :obj:`str`: URLs of connected nodes."""
        return self._nodes

    @property
    def transport(self):
        """:class:`~planetmint_driver.transport.Transport`: Object
        responsible for forwarding requests to a
        :class:`~planetmint_driver.connection.Connection` instance (node).
        """
        return self._transport

    @property
    def transactions(self):
        """:class:`~planetmint_driver.driver.TransactionsEndpoint`:
        Exposes functionalities of the ``'/transactions'`` endpoint.
        """
        return self._transactions

    @property
    def outputs(self):
        """:class:`~planetmint_driver.driver.OutputsEndpoint`:
        Exposes functionalities of the ``'/outputs'`` endpoint.
        """
        return self._outputs

    @property
    def assets(self):
        """:class:`~planetmint_driver.driver.AssetsEndpoint`:
        Exposes functionalities of the ``'/assets'`` endpoint.
        """
        return self._assets

    @property
    def metadata(self):
        """:class:`~planetmint_driver.driver.MetadataEndpoint`:
        Exposes functionalities of the ``'/metadata'`` endpoint.
        """
        return self._metadata

    @property
    def blocks(self):
        """:class:`~planetmint_driver.driver.BlocksEndpoint`:
        Exposes functionalities of the ``'/blocks'`` endpoint.
        """
        return self._blocks

    def info(self, headers=None):
        """Retrieves information of the node being connected to via the
        root endpoint ``'/'``.

        Args:
            headers (dict): Optional headers to pass to the request.

        Returns:
            dict: Details of the node that this instance is connected
            to. Some information that may be interesting:

                * the server version and
                * an overview of all the endpoints

        Note:
            Currently limited to one node, and will be expanded to
            return information for each node that this instance is
            connected to.

        """
        return self.transport.forward_request(method="GET", path="/", headers=headers)

    def api_info(self, headers=None):
        """Retrieves information provided by the API root endpoint
        ``'/api/v1'``.

        Args:
            headers (dict): Optional headers to pass to the request.

        Returns:
            dict: Details of the HTTP API provided by the Planetmint
            server.

        """
        return self.transport.forward_request(
            method="GET",
            path=self.api_prefix,
            headers=headers,
        )


class NamespacedDriver:
    """Base class for creating endpoints (namespaced objects) that can be added
    under the :class:`~planetmint_driver.driver.Planetmint` driver.
    """

    PATH = "/"

    def __init__(self, driver):
        """Initializes an instance of
        :class:`~planetmint_driver.driver.NamespacedDriver` with the given
        driver instance.

        Args:
            driver (Planetmint): Instance of
                :class:`~planetmint_driver.driver.Planetmint`.
        """
        self.driver = driver

    @property
    def transport(self):
        return self.driver.transport

    @property
    def api_prefix(self):
        return self.driver.api_prefix

    @property
    def path(self):
        return self.api_prefix + self.PATH


class TransactionsEndpoint(NamespacedDriver):
    """Exposes functionality of the ``'/transactions/'`` endpoint.

    Attributes:
        path (str): The path of the endpoint.

    """

    PATH = "/transactions/"

    @staticmethod
    def prepare(*, operation="CREATE", signers=None, recipients=None, assets=None, metadata=None, inputs=None):
        """Prepares a transaction payload, ready to be fulfilled.

        Args:
            operation (str): The operation to perform. Must be ``'CREATE'``
                or ``'TRANSFER'``. Case insensitive. Defaults to ``'CREATE'``.
            signers (:obj:`list` | :obj:`tuple` | :obj:`str`, optional):
                One or more public keys representing the issuer(s) of
                the assets being created. Only applies for ``'CREATE'``
                operations. Defaults to ``None``.
            recipients (:obj:`list` | :obj:`tuple` | :obj:`str`, optional):
                One or more public keys representing the new recipients(s)
                of the assets being created or transferred.
                Defaults to ``None``.
            assets (:obj:`dict`, optional): The assets to be created or
                transferred. MUST be supplied for ``'TRANSFER'`` operations.
                Defaults to ``None``.
            metadata (:obj:`dict`, optional): Metadata associated with the
                transaction. Defaults to ``None``.
            inputs (:obj:`dict` | :obj:`list` | :obj:`tuple`, optional):
                One or more inputs holding the condition(s) that this
                transaction intends to fulfill. Each input is expected to
                be a :obj:`dict`. Only applies to, and MUST be supplied for,
                ``'TRANSFER'`` operations.

        Returns:
            dict: The prepared transaction.

        Raises:
            :class:`~.exceptions.PlanetmintException`: If ``operation`` is
                not ``'CREATE'`` or ``'TRANSFER'``.

        .. important::

            **CREATE operations**

            * ``signers`` MUST be set.
            * ``recipients``, ``assets``, and ``metadata`` MAY be set.
            * If ``assets`` is set, it MUST be in the form of::

                {
                    'data': {
                        ...
                    }
                }

            * The argument ``inputs`` is ignored.
            * If ``recipients`` is not given, or evaluates to
              ``False``, it will be set equal to ``signers``::

                if not recipients:
                    recipients = signers

            **TRANSFER operations**

            * ``recipients``, ``assets``, and ``inputs`` MUST be set.
            * ``assets`` MUST be in the form of::

                {
                    'id': '<Asset ID (i.e. TX ID of its CREATE transaction)>'
                }

            * ``metadata`` MAY be set.
            * The argument ``signers`` is ignored.

        """
        return prepare_transaction(
            operation=operation,
            signers=signers,
            recipients=recipients,
            assets=assets,
            metadata=metadata,
            inputs=inputs,
        )

    @staticmethod
    def fulfill(transaction, private_keys):
        """Fulfills the given transaction.

        Args:
            transaction (dict): The transaction to be fulfilled.
            private_keys (:obj:`str` | :obj:`list` | :obj:`tuple`): One or
                more private keys to be used for fulfilling the
                transaction.

        Returns:
            dict: The fulfilled transaction payload, ready to be sent to a
            Planetmint federation.

        Raises:
            :exc:`~.exceptions.MissingPrivateKeyError`: If a private
                key is missing.

        """
        return fulfill_transaction(transaction, private_keys=private_keys)

    def get(self, *, asset_ids, operation=None, headers=None):
        """Given an assets id, get its list of transactions (and
        optionally filter for only ``'CREATE'`` or ``'TRANSFER'``
        transactions).

        Args:
            asset_id (str): Id of the assets.
            operation (str): The type of operation the transaction
                should be. Either ``'CREATE'`` or ``'TRANSFER'``.
                Defaults to ``None``.
            headers (dict): Optional headers to pass to the request.

        Note:
            Please note that the id of an assets in Planetmint is
            actually the id of the transaction which created the assets.
            In other words, when querying for an assets id with the
            operation set to ``'CREATE'``, only one transaction should
            be expected. This transaction will be the transaction in
            which the assets was created, and the transaction id will be
            equal to the given assets id. Hence, the following calls to
            :meth:`.retrieve` and :meth:`.get` should return the same
            transaction.

                >>> bdb = Planetmint()
                >>> bdb.transactions.retrieve('foo')
                >>> bdb.transactions.get(asset_id='foo', operation='CREATE')

            Since :meth:`.get` returns a list of transactions, it may
            be more efficient to use :meth:`.retrieve` instead, if one
            is only interested in the ``'CREATE'`` operation.

        Returns:
            list: List of transactions.

        """
        return self.transport.forward_request(
            method="GET",
            path=self.path,
            params={"asset_ids": asset_ids, "operation": operation},
            headers=headers,
        )

    def send_async(self, transaction, headers=None):
        """Submit a transaction to the Federation with the mode `async`.

        Args:
            transaction (dict): the transaction to be sent
                to the Federation node(s).
            headers (dict): Optional headers to pass to the request.

        Returns:
            dict: The transaction sent to the Federation node(s).

        """
        return self.transport.forward_request(
            method="POST",
            path=self.path,
            json=transaction,
            params={"mode": "async"},
            headers=headers,
        )

    def send_sync(self, transaction, headers=None):
        """Submit a transaction to the Federation with the mode `sync`.

        Args:
            transaction (dict): the transaction to be sent
                to the Federation node(s).
            headers (dict): Optional headers to pass to the request.

        Returns:
            dict: The transaction sent to the Federation node(s).

        """
        return self.transport.forward_request(
            method="POST",
            path=self.path,
            json=transaction,
            params={"mode": "sync"},
            headers=headers,
        )

    def send_commit(self, transaction, headers=None):
        """Submit a transaction to the Federation with the mode `commit`.

        Args:
            transaction (dict): the transaction to be sent
                to the Federation node(s).
            headers (dict): Optional headers to pass to the request.

        Returns:
            dict: The transaction sent to the Federation node(s).

        """
        return self.transport.forward_request(
            method="POST",
            path=self.path,
            json=transaction,
            params={"mode": "commit"},
            headers=headers,
        )

    def retrieve(self, txid, headers=None):
        """Retrieves the transaction with the given id.

        Args:
            txid (str): Id of the transaction to retrieve.
            headers (dict): Optional headers to pass to the request.

        Returns:
            dict: The transaction with the given id.

        """
        path = self.path + txid
        return self.transport.forward_request(method="GET", path=path, headers=None)


class OutputsEndpoint(NamespacedDriver):
    """Exposes functionality of the ``'/outputs'`` endpoint.

    Attributes:
        path (str): The path of the endpoint.

    """

    PATH = "/outputs/"

    def get(self, public_key, spent=None, headers=None):
        """Get transaction outputs by public key. The public_key parameter
        must be a base58 encoded ed25519 public key associated with
        transaction output ownership.

        Args:
            public_key (str): Public key for which unfulfilled
                conditions are sought.
            spent (bool): Indicate if the result set should include only spent
                or only unspent outputs. If not specified (``None``) the
                result includes all the outputs (both spent and unspent)
                associated with the public key.
            headers (dict): Optional headers to pass to the request.

        Returns:
            :obj:`list` of :obj:`str`: List of unfulfilled conditions.

        Example:
            Given a transaction with `id` ``da1b64a907ba54`` having an
            `ed25519` condition (at index ``0``) with alice's public
            key::

                >>> bdb = Planetmint()
                >>> bdb.outputs.get(alice_pubkey)
                ... ['../transactions/da1b64a907ba54/conditions/0']

        """
        return self.transport.forward_request(
            method="GET",
            path=self.path,
            params={"public_key": public_key, "spent": spent},
            headers=headers,
        )


class BlocksEndpoint(NamespacedDriver):
    """Exposes functionality of the ``'/blocks'`` endpoint.

    Attributes:
        path (str): The path of the endpoint.

    """

    PATH = "/blocks/"

    def get(self, *, txid, headers=None):
        """Get the block that contains the given transaction id (``txid``)
           else return ``None``

        Args:
            txid (str): Transaction id.
            headers (dict): Optional headers to pass to the request.

        Returns:
            :obj:`list` of :obj:`int`: List of block heights.

        """
        block_list = self.transport.forward_request(
            method="GET",
            path=self.path,
            params={"transaction_id": txid},
            headers=headers,
        )
        return block_list if block_list else None

    def retrieve(self, block_height, headers=None):
        """Retrieves the block with the given ``block_height``.

        Args:
            block_height (str): height of the block to retrieve.
            headers (dict): Optional headers to pass to the request.

        Returns:
            dict: The block with the given ``block_height``.

        """
        path = self.path + block_height
        return self.transport.forward_request(method="GET", path=path, headers=None)


class AssetsEndpoint(NamespacedDriver):
    """Exposes functionality of the ``'/assets'`` endpoint.

    Attributes:
        path (str): The path of the endpoint.

    """

    PATH = "/assets/"

    def get(self, *, cid, limit=0, headers=None):
        """Retrieves the assets that match a given text search string.

        Args:
            search (str): Text search string.
            limit (int): Limit the number of returned documents. Defaults to
                zero meaning that it returns all the matching assets.
            headers (dict): Optional headers to pass to the request.

        Returns:
            :obj:`list` of :obj:`dict`: List of assets that match the query.

        """
        return self.transport.forward_request(
            method="GET",
            path=self.path + "/" + cid,
            params={"limit": limit},
            headers=headers,
        )


class MetadataEndpoint(NamespacedDriver):
    """Exposes functionality of the ``'/metadata'`` endpoint.

    Attributes:
        path (str): The path of the endpoint.

    """

    PATH = "/metadata/"

    def get(self, *, search, limit=0, headers=None):
        """Retrieves the metadata that match a given text search string.

        Args:
            search (str): Text search string.
            limit (int): Limit the number of returned documents. Defaults to
                zero meaning that it returns all the matching metadata.
            headers (dict): Optional headers to pass to the request.

        Returns:
            :obj:`list` of :obj:`dict`: List of metadata that match the query.

        """
        return self.transport.forward_request(
            method="GET",
            path=self.path,
            params={"search": search, "limit": limit},
            headers=headers,
        )
