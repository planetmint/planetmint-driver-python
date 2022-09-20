# Copyright Planetmint GmbH and Planetmint contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

import sys
import os
import datetime

import sphinx_rtd_theme

# Get the project root dir, which is the parent dir of this
cwd = os.getcwd()
project_root = os.path.dirname(cwd)

# Insert the project root dir as the first element in the PYTHONPATH.
# This lets us ensure that the source package is imported, and that its
# version is used.
sys.path.insert(0, project_root)
# autodoc_mock_imports = ['_tkinter']

import planetmint_driver


extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx.ext.coverage",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinxcontrib.httpdomain",
    "IPython.sphinxext.ipython_console_highlighting",
    "IPython.sphinxext.ipython_directive",
]

autodoc_default_options = {
    "show-inheritance": None,
}
templates_path = ["_templates"]
source_suffix = ".rst"
master_doc = "index"
project = "Planetmint Python Driver"
now = datetime.datetime.now()
copyright = str(now.year) + ", Planetmint Contributors"
version = planetmint_driver.__version__
release = planetmint_driver.__version__
exclude_patterns = ["_build"]
pygments_style = "sphinx"
todo_include_todos = True
suppress_warnings = ["image.nonlocal_uri"]

html_theme = "press"
# html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_static_path = ["_static"]
htmlhelp_basename = "planetmint_python_driverdoc"

latex_elements = {}

latex_documents = [
    (
        "index",
        "planetmint_python_driver.tex",
        "Planetmint Python Driver Documentation",
        "Planetmint",
        "manual",
    ),
]

man_pages = [
    (
        "index",
        "planetmint_python_driver",
        "Planetmint Python Driver Documentation",
        ["Planetmint"],
        1,
    )
]

texinfo_documents = [
    (
        "index",
        "planetmint_python_driver",
        "Planetmint Python Driver Documentation",
        "Planetmint",
        "planetmint_python_driver",
        "",
        "Miscellaneous",
    ),
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    #    'planetmint-server': (
    #        'https://docs.planetmint.com/projects/server/en/latest/', None),
}
