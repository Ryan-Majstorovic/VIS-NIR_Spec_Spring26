# Documentation build layout

`source/` contains the version-controlled Sphinx source files and `conf.py`
contains the Sphinx configuration. `build/html/` is the ignored local preview
output. `pages/` is an ignored, CI-only GitHub Pages artifact directory.

To build the site locally on Windows, run:

```bat
docs\build-pages.bat
```

The same build is performed by `.github/workflows/docs-pages.yml` on pushes to
`main`, but its isolated runner writes to `docs/pages/`. The workflow uploads
that directory as the GitHub Pages artifact, so no compiled HTML needs to be
committed.
