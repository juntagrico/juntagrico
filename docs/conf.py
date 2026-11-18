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
    "rtd": ("https://docs.readthedocs.com/platform/stable/", None),
    'django': ('https://docs.djangoproject.com/en/5.2/', 'https://docs.djangoproject.com/en/5.2/objects.inv'),
    "python": ("https://docs.python.org/3/", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master/", None),
}
intersphinx_disabled_domains = ["std"]

templates_path = ["_templates"]

html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "canonical_url": "https://juntagrico.readthedocs.io",
    "logo_only": False,
    "style_external_links": False,
}

gettext_uuid = True
gettext_compact = False
