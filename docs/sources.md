# Source provenance

The owner supplied the original research pack and skills under the parent
`extras/` directory. Their exact locations are workstation state and are not
required to read this repository. Only selected research text, companion YAML
and unpacked independent skills are versioned here; no ZIP archives or datasets
are tracked.

## Imported sources

- `evidence_grounded_code_review_research_pack_der_alpha2.zip` — SHA-256 `1edfbec21664166c36d22c0fcde9e7ca49feb5be8120f0675418951d38fded9d`.
- `double-entry-review-core-0.3.0-alpha.2.zip` — SHA-256 `0165bfef40145ba494fe3591785edf4d4debdd094c55ca06b278d828d8c2a41c`.
- `software-design-clarity.zip` — SHA-256 `e96aa0fc8663b62fd5e5b11ea4d2edcef0f730cc66ca7499a5483abaae242ea2`.

The [machine-readable manifest](source-manifest.json) records a hash for every
imported research/skill file and its source-relative identifier. Copies are
byte-identical to the supplied source. These are content-identity checks, not
validation of the source's factual claims. The separate DER archive matches the
copy inside the research pack.

The research-pack copies of CONTEXT, backlog and slice template are frozen source
snapshots. Their maintained successors live at repository root and under
`docs/slice-reviews/`, as explained in [the research index](research/README.md).
The additional coding-agent handover Markdown is also an unmodified source copy.

## Independent skills

- Double-Entry Review 0.3.0-alpha.2, method revision 7: installed at
  `.agents/skills/double-entry-review/`, retaining its supplied licence.
- Software Design Clarity: installed at `.agents/skills/software-design-clarity/`,
  retaining its supplied MIT licence; the source archive hash identifies this
  distribution because no release version is asserted by its metadata.

These are static upstream tooling. DER working evidence belongs outside application
worktrees and is not included in this source manifest.

## ADR and commit conventions

The ADR template adapts [MADR at revision
ba75bb1b20d42af5746b246ad348c202419ae681](https://github.com/adr/madr/blob/ba75bb1b20d42af5746b246ad348c202419ae681/template/adr-template.md),
retrieved on 2026-09-19. Upstream offers MIT OR CC0-1.0; the adaptation uses CC0-1.0.
Meerkritic's first-party code and documentation use the root [MIT licence](../LICENSE.md).
Imported material and third-party skills retain their existing licence notices and
attribution; the project licence does not replace those terms.
The root `LICENSE.md` contains the standard MIT text and is recognised by GitHub.

Commit guidance follows [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/)
as requested by the owner. The EDR process is project-authored documentation.
