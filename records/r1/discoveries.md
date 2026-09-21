# Implementation observations

- Baseline a39b989 passed canonical checks and 241 tests in its own Windows/Python 3.12 checkout.
- Initial targeted run: 23 tests, one existing test-wrapper TypeError because its spy accepted positional arguments only. The wrapper now forwards keyword arguments; the event-loop/thread assertion is unchanged. Raw failure retained in targeted-first.log.
- First lint pass found normal formatting/import ordering plus one long SQL string. Formatted with Ruff; split the remaining SQL literal without changing its statement.
- Inspected the unchanged selection consumer: its snapshot embeds Annotation, so the new optional digest is retained. Added verification of attached context before freezing and a missing-file failure test rather than leaving a dangling reference unchecked.
- The second targeted run passed 24 tests. No research judgement/model run occurred.

- Rehearsal importer first attached 51/54 receipts. Three GitHub redirects used numeric repository URLs; strict equality with the response canonical URL rejected them. Added general numeric-redirect support while retaining requested URL, comment/PR/path and response-hash checks, with a negative test for the wrong comment ID. Fresh rehearsal3 attached all 54, preserving 1 annotation, 58 files and 332 original events.
- The first rehearsal verification stopped on an external audit-script bug (event key is sequence, not id); rehearsal2 retained the three import failures, and rehearsal3 is the corrected complete evidence. Both earlier runtime copies remain outside source control.
- Running the standalone importer without PYTHONPATH revealed its checkout source was not importable. The tool now binds its own src path, and a subprocess test exercises an actual synthetic import with PYTHONPATH absent. The documentation screenshot fixture still uses its documented PYTHONPATH setup.
- 12 source-context tests pass. A synthetic browser Accept retains context identity and notes. Screenshot captured before that synthetic decision, no research labels submitted.
