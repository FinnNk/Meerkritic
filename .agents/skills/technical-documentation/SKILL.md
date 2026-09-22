---
name: technical-documentation
description: Write or review technical guides, READMEs, references and PR descriptions for clear language, usable instructions, accurate screenshots and evidence-based validation summaries. Use for documentation passes and changes affecting existing guides, not for general copywriting or choosing code docstring conventions.
metadata:
  version: "0.1.1"
---

# Technical documentation people can use

Help the intended reader complete a task or understand behaviour without first learning the implementation or delivery history. Follow the host project's language, terminology and contribution rules. When the audience is unspecified, write for a technically aware reader unfamiliar with the project; adapt when the request identifies another audience.

Keep the requested scope: a review produces findings before edits when requested. Writing or checking a document does not authorise publication, deployment, model calls or actions on live user data. Preserve imported originals, essential attribution and historical decision/evidence records.

## Choose the purpose

| Document | Lead with | Keep elsewhere unless needed |
| --- | --- | --- |
| README | What the project does, who it helps and how to try or use it | Detailed planning, source-history narrative and implementation internals |
| Task guide | Outcome, prerequisites and actions | Delivery history and detailed contracts |
| Operations guide | Setup, expected results, diagnosis and recovery | Chronological test logs |
| Technical reference | Purpose, terms, behaviour, constraints and examples | Procedures already owned by a guide |
| Contribution policy | Required actions, who performs them and when | Past PR narratives |
| PR description | The concrete problem and resulting behaviour | Work diary and raw logs |
| Plan or decision record | Relevant decision, scope, alternatives and evidence | Unrelated history; retain necessary milestone references |

A document can serve several purposes when sections make them clear. Link to detail that would interrupt the task; do not split files merely to reduce their length.

## Write for action and understanding

- Explain a necessary specialist term in plain language where it first matters. A glossary link supplements the explanation. Keep precise terminology in contracts where precision matters.
- Prefer concrete verbs and named objects. For example, replace an unexplained “version fence” with “If the settings changed after you opened the form, reload them before retrying.” Avoid implementation names in introductions unless they help the reader act.
- Use exact UI labels for controls; format commands, paths and identifiers as code. Preserve literal commands, upstream quotations and standard licence wording when applying language conventions.
- Put procedures in numbered steps when order matters, bullets for independent actions, or tables for choices and repeated action/result mappings. Do not bury a procedure in a paragraph. Keep rationale in short paragraphs.
- Give commands enough context to run: prerequisites, working directory, shell/environment, complete commands, where placeholder values come from, expected result and next action. Use the environment the project actually supports.
- Put consequential cautions beside the relevant step. For likely failures, explain recovery rather than merely naming an error. Do not invent generic warnings or hypothetical checklists.
- Use tables for real comparisons, not long paragraphs compressed into cells. A small diagram is useful when relationships are clearer than a list; neither diagrams nor screenshots are mandatory decoration.
- Read and write maintained text with explicit UTF-8 in scripts. If punctuation looks corrupted, inspect saved bytes and a rendered view before changing it; terminal display alone does not establish corruption.

## Describe the current system

Task guides describe behaviour at the stated version or checkout. Remove unnecessary past milestone, PR and commit chronology from them; preserve it where it belongs in plans and historical records. Mention current or future milestones only when needed to explain a limitation or next step.

Check affected existing guides as well as changed files: counts, defaults, states, UI labels, example configuration and claims that an implemented feature is still proposed. Distinguish active configuration from illustrative or reserved configuration. Never imply that a file is loaded when the application does not read it.

Give shared policy one clear owner and link to it. A short local reminder or project-specific qualification can be worth duplicating. Keep material limits near the claim they qualify without repeating them throughout a guide. A successful software test does not establish user benefit, model quality or empirical validity.

## Keep documentation changes reviewable

Where a project uses semantic commits (commits organised around a complete reviewable change), separate changes to writing policy from backfills that apply the policy to existing documents. Keep documentation and comments needed to understand new behaviour with the code they explain. An unrelated documentation or comment backfill can have its own commit when that makes review clearer.

This does not require a separate PR for every commit or impose a particular history-reconstruction process. Follow the project's delivery rules and existing authorisation for commits, publication and any rewriting of published history.

## Apply conditional guidance

- When screenshots could help readers recognise a control or result, read [screenshots](references/screenshots.md). Do not load it for unrelated prose edits.
- When writing or reviewing a PR description or its validation section, read [PR descriptions and evidence summaries](references/pr-descriptions.md).
- For code comments/docstrings, use the project's code-documentation conventions. This skill does not choose a docstring format, API documentation framework, ADR format or review-history process.

## Review before delivery

Apply the relevant checks to authorship and review, including the final combined change. Judge meaning rather than word counts or checklist scores.

- [ ] Can the reader identify the purpose and first useful action from the opening?
- [ ] Are necessary terms introduced, and are procedures scannable steps or tables?
- [ ] Do commands, paths, control labels and behaviour match the intended version? Are prerequisites, expected outcomes and likely recovery actions sufficient?
- [ ] Is current guidance free of unnecessary delivery history, while historical records and attribution remain intact?
- [ ] Do links and anchors resolve, tables render cleanly, and Unicode characters survive saving and rendering?
- [ ] Where present, do images clarify a task, remain readable and faithfully show the described state? Follow the screenshot reference's checks.
- [ ] Are evidence claims and limits accurate? Follow the PR reference when summarising validation.
- [ ] Have affected unchanged guides and screenshots been considered, and have existing human amendments been retained?
- [ ] Where semantic commits are used, are policy changes and existing-document backfills distinguishable, with documentation needed for new behaviour kept with its code?

Inspect relevant CLI help, code or observed behaviour to validate examples. Run safe examples in a disposable environment when useful and authorised; do not exercise mutating instructions on live user data merely to check prose. Report unavailable checks and their practical limits rather than inventing a pass. Do not add brittle prose-matching tests or weaken software checks for editorial work.
