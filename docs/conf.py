# -- Project information -----------------------------------------------------

project = "juntagrico"
copyright = "GNU Lesser General Public License v3 (LGPLv3)"


# -- General configuration ---------------------------------------------------
# -- General configuration

extensions = [
    "sphinx.ext.duration",
    "sphinx.ext.doctest",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
]

intersphinx_mapping = {
    "rtd": ("https://docs.readthedocs.io/en/stable/", None),
    'django': ('https://docs.djangoproject.com/en/4.2/', 'https://docs.djangoproject.com/en/4.2/_objects/'),
    "python": ("https://docs.python.org/3/", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master/", None),
}
intersphinx_disabled_domains = ["std"]

templates_path = ["_templates"]
