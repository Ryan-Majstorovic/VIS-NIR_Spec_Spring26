# File Layout Rules

## Section Root

Create the section under the explicit parent path:

```text
<parent>/<slug>/
```

The root contains:

- `index.rst`
- `inputs_and_outputs.rst`
- `procedure.rst`
- `diagnostics.rst`
- `testing.rst`
- `calculations.rst`
- `validation.rst`

## Diagrams

Create blank Visio placeholder files only:

```text
docs/source/_static/diagrams/<slug>/<slug>-io.vsdx
docs/source/_static/diagrams/<slug>/<slug>-state-machine.vsdx
```

Do not create image exports.
Do not populate the Visio documents.

## Calibration Mirror

When the user requests calibration support, create:

```text
<parent>/<slug>/calibration/
```

Mirror the same seven-page structure inside that folder.

## Parent Navigation

Update the parent `index.rst` once by adding:

```text
<slug>/index
```

Do not add duplicate toctree entries.
