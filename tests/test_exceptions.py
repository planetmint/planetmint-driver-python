# Copyright Planetmint GmbH and Planetmint contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0


class TestTransportError:
    not_found = "not found"

    def test_status_code_property(self):
        from planetmint_driver.exceptions import TransportError

        err = TransportError(404)
        assert err.status_code == 404

    def test_error_property(self):
        from planetmint_driver.exceptions import TransportError

        err = TransportError(404, self.not_found)
        assert err.error == self.not_found

    def test_info_property(self):
        from planetmint_driver.exceptions import TransportError

        err = TransportError(404, self.not_found, {"error": self.not_found})
        assert err.info == {"error": self.not_found}
