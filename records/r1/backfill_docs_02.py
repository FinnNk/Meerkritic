from pathlib import Path
R=Path('WORKSPACE/extras/der-checkouts/vs2-draft-repair')
def edit(name,old,new):
 p=R/name;s=p.read_text(encoding='utf-8');assert old in s,name;p.write_text(s.replace(old,new),encoding='utf-8')
p=R/'docs/edr/0001-discovery-grouping-method.md';s=p.read_text(encoding='utf-8');start=s.index('The agreed target of 40 usable');end=s.index('\nSource checks retained',start);s=s[:start]+'''Under the rules in force at the initial pass, the target was unreachable: only
33 valid drafts were available before human rejection. The prospective amendment
above now permits human correction/rejection of retained failed drafts. The
harness implements that path while preserving the one model pass and unchanged
schema/evidence checks. Forty usable inputs remain possible, not guaranteed;
registration still waits for the actual reviewed selection.
'''+s[end:];p.write_text(s,encoding='utf-8')
edit('docs/plans/VS2-plan.md','The completed input-preparation pass cannot meet the agreed 40-input target:','Before the agreed correction amendment, the input pass could not meet 40 inputs:')
edit('docs/plans/VS2-plan.md','grouping runs have occurred. EDR-0001 records the evidence and the required owner\nchoice before a prospective amendment.','grouping runs have occurred. EDR-0001 records the evidence and the subsequent\nowner-agreed prospective amendment.')
edit('docs/plans/VS2-plan.md','backend/UI contracts with tests, then backfill current guides and confirmation.','backend/UI contracts with tests, then backfill current guides and confirmation.\n\nThe correction path is implemented with separate original/human evidence, versioned\nselection reading and focused backend/browser checks. A migration rehearsal on a\ncopy of the study database preserves every application table and verifies all\n33 successful and 22 failed outputs are reviewable with their appropriate actions.\nNo human research decisions or further model calls were made. The ordered local\nhandoff precedes input judgements; grouping judgements wait for selection freeze\nand registration. Final DER checkpoint qualification and owner acceptance remain\nseparate from this implementation record.')
edit('docs/adr/ADR-0013-preserve-failed-drafts-during-human-correction.md','status: accepted','status: implemented')
p=R/'docs/adr/ADR-0013-preserve-failed-drafts-during-human-correction.md';s=p.read_text(encoding='utf-8');start=s.index('Before marking this implemented');end=s.index('\n## Pros and Cons',start);s=s[:start]+'''Implemented on 20 September 2026. Ten backend and four web tests cover unchanged
failed job/result bytes, valid/invalid correction, rejection, duplicate/conflicting
submissions, atomic events, restart, selection freezing and legacy reading.
A browser exercise retained an invalid synthetic edit, then saved a valid correction
while keeping the original failure visible. A SQLite-backup migration rehearsal
preserved every application table and verified all 55 original study outputs.
The study still contains zero annotations. Evidence is retained in DER
`vs2-draft-repair/r1` (`backend-tests-04.log`, `web-tests.log`, `browser-check.json`,
`upgrade-rehearsal.json`); software acceptance is a separate gate.
'''+s[end:];p.write_text(s,encoding='utf-8')
p=R/'docs/adr/README.md';s=p.read_text(encoding='utf-8');lines=s.splitlines();lines=[line.replace('| accepted |','| implemented |') if 'ADR-0013' in line else line for line in lines];p.write_text('\n'.join(lines)+'\n',encoding='utf-8')
p=R/'docs/images/README.md';s=p.read_text(encoding='utf-8');s=s.replace('records pixel crop rectangles','and [the correction captures](captures-draft-repair.json) record pixel crop rectangles');s=s.replace('Overview, 1232 × 712 | Proposed issue through all three assessment buttons','Overview, 1232 × 535 | Proposed issue and quoted evidence');s=s.replace('Panel, 960 × 212','Panel, 960 × 221');s=s.replace('| [Saved selection]', '| [Failed draft](failed-draft-assessment.png) | `failed_annotation` | Overview, 1232 × 635 | Failure explanation, original draft editor and Edit/Reject controls |\n| [Saved selection]',1);s+='\nThe correction capture record supersedes the earlier result and assessment entries\nin `captures.json`; the other original captures remain current. The failed-draft\nimage shows an unreviewed synthetic job. Browser verification used a separate\nsynthetic job and saved one correction; neither is research data.\n';p.write_text(s,encoding='utf-8')
p=R/'docs/slice-reviews/VS2-integration.md';s=p.read_text(encoding='utf-8');s+='''
## Comparison tooling integration

The owner approved and merged [PR #16](https://github.com/FinnNk/Meerkritic/pull/16)
on 20 September 2026. Reviewed head `2adeb88d3bbcf1af2ee8b5c498c7a32cbe1c100c`
maps to integrated head `e7726500930e79f0ba69becae5d12b77edbb5dea`; all five
ordered reviewed trees match. Isolated locked Windows/Python 3.12 checks pass
with 215 tests. Mapping and baseline records live in DER `vs2-draft-repair/r1`.

This integrates the comparison software, not a research result. The owner also
agreed a prospective human-correction amendment, recorded in EDR-0001. Its
implementation retains the single normalisation pass; human input judgements,
selection freeze, registration, group ratings and empirical decision remain open.
''';p.write_text(s,encoding='utf-8')
p=R/'tests/README.md';s=p.read_text(encoding='utf-8');s+='''
## Failed-draft correction

`test_failed_drafts.py` challenges provenance, schema/quote rejection, terminal
eligibility, atomic events, concurrency, restart, progress denominators and both
selection versions. `test_failed_draft_web.py` checks escaped source/output,
Edit/Reject-only failures, retained invalid drafts and inspection-only provider
failures. All decisions are synthetic; these tests supply no research labels.
''';p.write_text(s,encoding='utf-8')
p=R/'IMPLEMENTATION_BACKLOG.yaml';s=p.read_text(encoding='utf-8');needle='- id: VS2\n';assert needle in s;s=s.replace(needle,needle+'  current_follow_up: Human correction of retained failed drafts implemented; human input reviews and registered comparison remain outstanding (DER vs2-draft-repair r1).\n',1);p.write_text(s,encoding='utf-8')
print('Backfilled maintained documentation and ADR confirmation')
