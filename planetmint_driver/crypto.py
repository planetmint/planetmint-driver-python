# Copyright Planetmint GmbH and Planetmint contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

from collections import namedtuple

from planetmint_cryptoconditions import crypto


CryptoKeypair = namedtuple("CryptoKeypair", ("private_key", "public_key"))


def generate_keypair(seed=None):
    """Generates a cryptographic key pair.

    Args:
        seed (bytes): 32-byte seed for deterministic generation.
                      Defaults to `None`.
    Returns:
        :class:`~planetmint_driver.crypto.CryptoKeypair`: A
        :obj:`collections.namedtuple` with named fields
        :attr:`~planetmint_driver.crypto.CryptoKeypair.private_key` and
        :attr:`~planetmint_driver.crypto.CryptoKeypair.public_key`.

    """
    return CryptoKeypair(*(k.decode() for k in crypto.ed25519_generate_key_pair(seed)))
