from __future__ import annotations

from datetime import date

project = "VIS-NIR Spectrometer Technical Documentation"
author = "SDDEC26-06 Team Spectro"
copyright = f"{date.today().year}, {author}"
release = "0.1"

extensions = [
    "sphinx_rtd_theme",
    "sphinx.ext.autosectionlabel",
]

templates_path = ["source/_templates"]
exclude_patterns = ["build", "Thumbs.db", ".DS_Store"]

root_doc = "index"
html_theme = "sphinx_rtd_theme"
html_static_path = ["source/_static"]
html_title = project
html_short_title = "VIS-NIR Docs"

html_theme_options = {
    "collapse_navigation": True,
    "sticky_navigation": True,
    "navigation_depth": 4,
    "includehidden": True,
    "titles_only": True,
}
suppress_warnings = ["autosectionlabel.*"]


def setup(app):
    app.add_css_file("css/my_theme.css")

