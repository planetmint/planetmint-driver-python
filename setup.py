#!/usr/bin/env python
# Copyright Planetmint GmbH and Planetmint contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

from setuptools import setup, find_packages

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("CHANGELOG.rst") as changelog_file:
    changelog = changelog_file.read()

install_requires = [
    "requests>=2.20.0",
    "pysha3~=1.0.2",
    "python-rapidjson>=1.0.0",
    "python-rapidjson-schema==0.1.1",
    "planetmint-transactions>=0.6.0",
    "planetmint-ipld>=0.0.3",
]

tests_require = [
    "tox>=2.3.1",
    "coverage>=4.1",
    "black",
    "pytest>=3.0.1",
    "pytest-cov",
    "pytest-env",
    "pytest-sugar",
    "pytest-xdist",
    "responses>=0.22.0",
]

dev_require = ["ipdb", "ipython", "pre-commit", "jinja2==3.0.0"]

docs_require = [
    "Sphinx",
    "sphinx-autobuild",
    "sphinxcontrib-autorun",
    "sphinxcontrib-napoleon>=0.4.4",
    "sphinx_rtd_theme",
    "sphinxcontrib-httpdomain",
    "matplotlib",
    "base58",
]

setup(
    name="planetmint_driver",
    version="0.16.0",
    description="Python driver for Planetmint",
    long_description=readme + "\n\n" + changelog,
    long_description_content_type="text/x-rst",
    author="Planetmint",
    author_email="contact@ipdb.global",
    url="https://github.com/planetmint/planetmint-driver",
    packages=find_packages(exclude=["tests*"]),
    package_dir={"planetmint_driver": "planetmint_driver"},
    include_package_data=True,
    install_requires=install_requires,
    python_requires=">=3.9",
    license="Apache Software License 2.0",
    zip_safe=False,
    keywords="planetmint_driver",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.9",
    ],
    test_suite="tests",
    extras_require={
        "test": tests_require,
        "dev": dev_require + tests_require + docs_require,
        "docs": docs_require,
    },
)
