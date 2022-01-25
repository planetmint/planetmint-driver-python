#!/bin/bash
# Copyright Planetmint GmbH and Planetmint contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0


set -e -x

if [[ "${TOXENV}" == "py35" || "${TOXENV}" == "py36" ]]; then
  docker-compose run --rm planetmint-driver pytest -v --cov=planetmint_driver --cov-report xml:htmlcov/coverage.xml
else
  tox -e ${TOXENV}
fi
