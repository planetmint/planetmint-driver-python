#!/bin/bash
# Copyright Planetmint GmbH and Planetmint contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0


set -e -x

pip install --upgrade pip
pip install --upgrade tox

if [[ "${TOXENV}" == "py39" ]]; then
    docker-compose build --no-cache planetmint planetmint-driver
    pip install --upgrade codecov
fi
