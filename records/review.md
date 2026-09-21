# Documentation skill extraction review

Classification: routine. This extracts existing editorial advice, without changing application behaviour, evidence semantics, quality commands, architecture rules or delivery permissions. No DER pair or ADR is needed.

| Existing guidance | Reusable owner | Meerkritic-specific remainder |
| --- | --- | --- |
| Reader/purpose, plain English, steps/tables, current behaviour and UTF-8 | SKILL.md | British English, project terminology/glossary, locked commands, preserved source policy |
| Screenshots | references/screenshots.md | docs/images location, PNG/capture conventions, synthetic harness, no research decisions/model calls for illustration |
| PR descriptions and validation | references/pr-descriptions.md | Semantic review/stack map, tools/check.py and exact standard tools, DER/evidence links, owner acceptance |
| Author/reviewer checklist | SKILL.md | Local checklist and review stages retained |
| Docstrings | Explicitly outside reusable scope | Existing Python/code-comment conventions retain authority |

Self-review considered: a non-Python project with its own check command/language; a requested review without edit permission; a guide referring to old milestones versus an historical ADR; a partial test run; and an illustration needing private live data. The instructions preserve each boundary and defer local conventions. This is an instruction review, not an independent behavioural evaluation.

No Meerkritic paths, tools, dataset/schema names, credentials or platform-specific requirements occur in the portable skill. Its two references are relative and it declares no tool dependency. Automatic discovery remains enabled by default. Project links use the repository copy, so other contributors do not need the personal installation.

The first quick_validate invocation used the Windows default cp1252 decoder and failed on valid UTF-8 punctuation. Running the unchanged validator with Python -X utf8 passes; no valid text was replaced. No new scripts ship in the skill.
