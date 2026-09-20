# Final own-source live/browser verification

Source: c1d6487fe41f3165e87a2217c2733e96d5657778 in its isolated r1-p3 checkout,
with its own locked environment. Public runtime is separate from user data.
The retained live.py completed all required assertions (see live.json): three
successes, Accept/Edit/Reject, one closed-port provider failure, one process-exit
interruption, usage export/analysis, artefact/log references and DER index.

Browser on port 8004 showed 3/3 reviewed results, 1/1030 distinct source coverage,
one of each action, two failed jobs, no queued/running jobs and no pending results.
The DER page displayed vs1-annotation/r1, exact diary/semantic heads, event 2,
owner_review_ready and unchanged file hashes, with the assertion/approval caveat.

Stopped web process 68892 and restarted the exact same source/environment as
process 44468. Browser again showed the same counts and action totals. The two
temporary development servers were stopped; the final preview remains available.
No user annotations were created or altered: every verification decision has an
explicit automated-functional-test note. No engineering-quality conclusion.
