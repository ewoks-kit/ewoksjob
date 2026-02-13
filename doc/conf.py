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
    "sphinx_copybutton",
]
templates_path = ["_templates"]
exclude_patterns = []

always_document_param_types = True

autosummary_generate = True
autodoc_default_flags = ["members", "undoc-members", "show-inheritance"]

copybutton_prompt_text = r">>> |\.\.\. |\$ |In \[\d*\]: | {2,5}\.\.\.: | {5,8}: "
copybutton_prompt_is_regexp = True

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "pydata_sphinx_theme"
html_title = docstitle
html_logo = "_static/logo.png"
html_static_path = ["_static"]
html_template_path = ["_templates"]
html_css_files = ["custom.css"]

html_theme_options = {
    "icon_links": [
        {
            "name": "github",
            "url": "https://github.com/ewoks-kit/ewoksjob",
            "icon": "fa-brands fa-github",
        },
        {
            "name": "pypi",
            "url": "https://pypi.org/project/ewoksjob",
            "icon": "fa-brands fa-python",
        },
    ],
    "logo": {
        "text": docstitle,
    },
    "footer_start": ["copyright"],
    "footer_end": ["footer_end"],
}
