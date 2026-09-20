import json, subprocess
from pathlib import Path

ROOT=Path('WORKSPACE')
E=ROOT/'extras/der-evidence/assessment-clarity/r1'
PUB=ROOT/'extras/der-publication/assessment-clarity-r1'
W=ROOT/'working'
R=ROOT/'extras/der-checkouts/assessment-clarity-semantic'
PY='HOST_USER/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
HELPER=ROOT/'extras/tooling/meerkritic-agent/agent.py'
i=json.loads((E/'semantic-commits.json').read_text())
archive=json.loads((E/'export-result.json').read_text())
summary=json.loads((E/'verification-summary.json').read_text())
assert summary['status']=='passed'

def run(args,label=None):
    p=subprocess.run([str(x) for x in args],cwd=R,capture_output=True,text=True,encoding='utf-8')
    if label:(E/(label+'.log')).write_text(p.stdout+p.stderr,encoding='utf-8')
    assert p.returncode==0,p.stdout+p.stderr
    return p.stdout.strip()

git=['git','-c','safe.directory='+W.as_posix(),'-C',W]
pr17=json.loads(run([PY,HELPER,'gh','pr','view','17','--json','state,headRefName,headRefOid']))
assert pr17['state']=='OPEN' and pr17['headRefOid']==i['base'],'Predecessor changed; reassess stack base before publishing.'
base=pr17['headRefName']
assert run(git+['ls-remote','origin','refs/heads/'+base]).split()[0]==i['base']
for branch in ('evidence/assessment-clarity-r1','feat/assessment-clarity'):
    assert not run(git+['ls-remote','origin','refs/heads/'+branch]),'Unexpected existing branch; preserve it.'
run(git+['fetch',PUB,'refs/heads/evidence/assessment-clarity-r1:refs/heads/evidence/assessment-clarity-r1'],'archive-import')
run(git+['push','origin','refs/heads/evidence/assessment-clarity-r1'],'publish-archive')
assert run(git+['ls-remote','origin','refs/heads/evidence/assessment-clarity-r1']).split()[0]==archive['archive_commit']
run(git+['push','-u','origin','refs/heads/feat/assessment-clarity'],'publish-branch')
assert run(git+['ls-remote','origin','refs/heads/feat/assessment-clarity']).split()[0]==i['commits'][-1]
c=i['commits'];u='https://github.com/FinnNk/Meerkritic/tree/'+archive['archive_commit']
body=f'''The first human walkthrough exposed ambiguous field meanings: investigation needs were being treated as impact scope, and missing evidence as applicability exceptions. The harness now explains those distinctions and accepts **unknown impact scope** when the supplied evidence does not establish the affected extent.

The source opens in a distinct panel, a task introduction explains what acceptance means, and field help separates **Applicability limits** from **Assessment notes and evidence limitations**. Existing notes retain investigation needs and human advice beyond the source. Original model outputs remain unchanged; future prompts are versioned as `normalisation-v3`.

**Stacked on #17. Review and merge #17 first, then this PR.**

![Synthetic assessment controls with field help and separate evidence notes.](https://raw.githubusercontent.com/FinnNk/Meerkritic/{c[-1]}/docs/images/annotation-assessment.png)

[Synthetic capture notes](https://github.com/FinnNk/Meerkritic/blob/{c[-1]}/docs/images/README.md). No research judgement is shown or submitted.

## Review sequence

| Commit | What it establishes |
| --- | --- |
| `{c[0][:7]}` | Define field meanings, author/reviewer guidance and the prospective study clarification in ADR-0014. |
| `{c[1][:7]}` | Apply the compatible schema, prompt and UI contract, with grounded-edit and provenance tests. |
| `{c[2][:7]}` | Backfill guides, glossary, navigation and screenshots; record candidate implementation. |

## Validation

**Standard checks: passed** at `{c[-1][:7]}` — [retained evidence]({u}/records/r1/verification-summary.json). Each semantic checkpoint and the frozen diary passed with locked dependencies on Windows/Python 3.12. Final total: **233 tests, 0 skipped**.

| Coverage change from #17 | Added | Altered | Removed |
| --- | ---: | ---: | ---: |
| Unknown/invalid impact scope through the MAF workflow | 2 | 0 | 0 |
| Field help, separate notes, immutable originals and saved edits after restart | 2 | 0 | 0 |
| Failure provenance expects the new prompt version | 0 | 1 | 0 |

The initial complete run caught the old prompt-version expectation. It was corrected on the diary before reconstruction; all other assertions remain. [Failure and disposition]({u}/records/r1/discoveries.md).

- [Schema compatibility]({u}/records/r1/schema-compatibility.json): only the unknown scope option changes validation; all 33 original successful drafts round-trip unchanged.
- [Live harness]({u}/records/r1/live-after.json): 55 unchanged outputs; 55 jobs, 331 events, zero annotations and zero discovery runs after restart.
- [Documentation]({u}/records/r1/docs-check.json): 359 local links and 59 preserved source files checked; affected synthetic screenshots refreshed.
- [Architecture delta]({u}/records/r1/architecture-delta.json): no new modules, dependencies, boundary exceptions or database migration.
- [Double-Entry Review evidence]({u}): exact diary/semantic tree equivalence and full author self-review. This is not independent approval or a hosted CI claim.

## Research handoff

The first judgement remains unsaved and its preliminary observations are retained locally. The EDR records the clarified method and assistance; it remains draft. No model rerun or grouping comparison was performed. Notes are retained with annotations but are not interpretation text for grouping, so meaning-changing uncertainty must also qualify the issue or candidate rule.
'''
(E/'pr-body.md').write_text(body,encoding='utf-8')
url=run([PY,HELPER,'gh','pr','create','--base',base,'--head','feat/assessment-clarity','--title','feat: clarify assessment fields before collecting judgements','--body-file',E/'pr-body.md'],'publish-pr')
(E/'pr-url.txt').write_text(url+'\n',encoding='utf-8')
print(json.dumps(dict(pr=url,head=c[-1],base=i['base'],archive=archive['archive_commit'])))
