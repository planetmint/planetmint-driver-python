#!/bin/bash
# Copyright Planetmint GmbH and Planetmint contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0


set -e -x

if [ "${TOXENV}" == "py39" ]; then
    codecov -v -f htmlcov/coverage.xml
fi
