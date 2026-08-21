## Agent skills

### Issue tracker

Issues are tracked as local markdown files under `.scratch/`. See `docs/agents/issue-tracker.md`.

### Triage labels

Triage uses the default label vocabulary: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, and `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

This repo uses a single-context domain-doc layout centered on a root `CONTEXT.md` and `docs/adr/`. See `docs/agents/domain.md`.

## Requirements documentation authoring

Treat `docs/source/` as the authoritative intended-behavior specification.
When authoring or revising requirements documentation, follow these rules:

- Write every normative behavior as a requirement using this structure:
  `The <named system or subsystem> shall <perform X> <under condition Y> <to produce Z>.`
- Prefer an explicit `**Requirement:**` field for each independently traceable
  technical item.
- Do not substitute descriptive factual prose for a normative requirement. A
  fact may appear as labeled context or source evidence, but it does not define
  intended behavior until it is expressed as a `shall` requirement.
- Place `**Rationale:**` immediately with the requirement it explains. The
  rationale shall explain why that specific behavior, constraint, boundary, or
  response is necessary, such as the downstream function it protects, the
  failure it prevents, or the verification need it supports.
- Do not use a rationale to explain why a page exists, why a section is
  organized a certain way, why documentation should remain authoritative, or
  why the requirement was written down.
- Do not merely restate the requirement in the rationale.
- Use page-level summaries only to establish scope and relationships. They do
  not replace requirement-level rationales.
- If the required behavior, condition, output, or rationale is not supported by
  the authoritative documentation, write `Not In Docs` instead of inventing it.
- Keep planned requirements distinct from implementation evidence. Code may be
  used during a later conformance review, but it shall not create intended
  behavior.

Avoid this pattern:

```rst
**Summary:** The detector contains 3648 effective pixels.

**Rationale:** This page keeps the Embedded documentation authoritative.
```

Use this pattern:

```rst
**Requirement:** The Embedded system shall preserve all 3648 effective
detector samples in acquisition order for every accepted measurement frame.

**Rationale:** Preserving acquisition order maintains the detector-position
relationship required for wavelength mapping and prevents downstream
corrections from being applied to the wrong sample.
```
