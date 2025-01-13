"""rm -rf doc/_generated/; sphinx-build doc build/sphinx/html -E -a
"""

import importlib.metadata

release = importlib.metadata.version("ewoksjob")

project = "ewoksjob"
version = ".".join(release.split(".")[:2])
copyright = "2019-2025, ESRF"
author = "ESRF"
docstitle = f"{project} {version}"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "sphinx_autodoc_typehints",
]
templates_path = ["_templates"]
exclude_patterns = []

always_document_param_types = True

html_theme = "classic"
html_static_path = []

autosummary_generate = True
autodoc_default_flags = ["members", "undoc-members", "show-inheritance"]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "pydata_sphinx_theme"
# To renable when adding static resources
# html_static_path = ["_static"]
html_theme_options = {
    "icon_links": [
        {
            "name": "gitlab",
            "url": "https://gitlab.esrf.fr/workflow/ewoks/ewoksjob",
            "icon": "fa-brands fa-gitlab",
        },
        {
            "name": "pypi",
            "url": "https://pypi.org/project/ewoksjob",
            "icon": "fa-brands fa-python",
        },
    ],
    "navbar_start": ["navbar_start"],
    "footer_start": ["copyright"],
    "footer_end": ["footer_end"],
}
