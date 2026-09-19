# R4 final semantic plan

Read `intent.md` for the initial plan. A subsequent owner instruction accepted
ADR-0002's Preserve source records option. Its candidate implementation already
passed the stated confirmation, so P6 records it as implemented with the actual
owner decision and evidence. ADR-0001 retains accepted pending first empirical use.

P1 registration, P2 browsing and P3 architecture reporting retain r3's bounded
capabilities and now carry their own exposed-operation and internal-intent comments.
P4 backfills only tools/check.py, which predates this PR. P5 introduces the guidance,
ADR-0003 and explicit ADR lifecycle review, after the backfill is present. P6 updates
ADR-0002 and its index. This keeps policy documentation separate from application,
and the two owner decisions independently reviewable. No test is removed or weakened.

The actual diary adds application, backfill, a Ruff wording correction, guidance
and finally the newly accepted ADR-0002 decision, in that order. Frozen diary:
797d8189ff7194bf025885ab0815b3f301fa21d2. `commits.json` maps the six semantic commits;
`range-diff.txt` maps r3 to r4. Final semantic: c66dcfe605e00a8b3ea41208647df11bb7be4da6.
Both share tree dc03ff60ee94dfbe4dbac25c9f1a7081b97fa3c7 and base 3db848bd0992d0686bb5c45ddadd87ec6fbde8d2.

Every checkpoint runs the full canonical quality command in its own worktree and
locked environment. P1 has no FastAPI dependency; each source probe resolves its
own src directory. P1/P2/P3-P6 run 11/14/15 tests respectively. Initial runner and
lint failures are retained and explained; no source/test workaround was used.

R3 is retained on public evidence commit 2d8cd8d3024eeb70ef35f1afcbff8279141c71b6.
R4's archive retains the r3 and r4 bundles plus accessible paginated discussion.
Rewriting PR3 is authorised by the owner's explicit semantic-placement request;
the expected previous head is 8e5e77f406639c88655c88c20341083f655e7013. Use an exact lease.
