# Copyright Planetmint GmbH and Planetmint contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

from pytest import mark
from requests.utils import default_headers
from responses import RequestsMock


class TestConnection:
    url = "http://dummy"

    def test_init_with_custom_headers(self):
        from planetmint_driver.connection import Connection

        custom_headers = {"app_id": "id_value", "app_key": "key_value"}
        connection = Connection(node_url=self.url, headers=custom_headers)
        expected_headers = default_headers()
        expected_headers.update(custom_headers)
        assert connection.session.headers == expected_headers

    @mark.parametrize(
        "content_type,json,data",
        (
            ("application/json", {"a": 1}, {"a": 1}),
            ("text/plain", {}, {}),
        ),
    )
    def test_response_content_type_handling(self, content_type, json, data):
        from planetmint_driver.connection import Connection

        connection = Connection(node_url=self.url)
        with RequestsMock() as requests_mock:
            requests_mock.add("GET", self.url, json=json)
            response = connection.request("GET")
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        assert response.data == data

    @mark.parametrize("headers", ({}, {"app_name": "name"}, {"app_id": "id", "app_key": "key"}))
    def test_request_with_headers(self, headers):
        from planetmint_driver.connection import Connection

        connection = Connection(node_url=self.url, headers=headers)
        with RequestsMock() as requests_mock:
            requests_mock.add("GET", self.url, adding_headers=headers)
            response = connection.request("GET")
        assert response.status_code == 200
        del response.headers["Content-type"]
        assert response.headers == headers
