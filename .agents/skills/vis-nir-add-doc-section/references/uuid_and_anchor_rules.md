# UUID And Anchor Rules

All tracked items must be linkable by UUID.
Use standard UUIDs only.

## Required Pattern

Place a Sphinx label before the page title or subsection title:

```rst

ADC Count Extraction
====================

UUID: :ref:`A3B7D520-4E6F-4C81-B091-2F3A6C94D70E <uuid-a3b7d520-4e6f-4c81-b091-2f3a6c94d70e>`
```

Apply the same pattern to tracked technical content:

- specification sections
- device-characteristic sections
- states
- transitions
- calculations
- diagnostics items
- validation items
- testing items

Do not generate UUID anchors for purely organizational grouping headers unless
the user explicitly wants them treated as independently traceable blocks.
Do not generate a page-title UUID when UUID-tagged subsections already provide
the traceable anchors for that page.

## Normalization

Normalize the UUID to a safe label name:

1. lowercase the value
2. replace any non-alphanumeric run with `-`
3. trim leading and trailing `-`
4. prefix with `uuid-`

Examples:

- `A3B7D520-4E6F-4C81-B091-2F3A6C94D70E` -> `uuid-a3b7d520-4e6f-4c81-b091-2f3a6c94d70e`

## Display IDs

Human-oriented IDs such as `S0`, `T0`, `D0`, `C0`, `TEST0`, or `VAL0` can
appear in the headed block title, but the UUID remains the canonical link
target for cross-reference communication.

Do not repeat that same display ID on a separate `ID:` line when it is already
present in the heading.
