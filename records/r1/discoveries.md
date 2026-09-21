# Implementation observations

1. Baseline canonical checks passed at 796db0e: 233 tests, zero skips.
2. Implemented ordinary HTML form fields and server-rendered list operations.
   No JavaScript runtime or new dependency is necessary. The web adapter translates
   representation; AnnotationService still validates and saves the decision.
3. First targeted run (form-tests-first.log) failed: CRLF quote normalisation
   considered both CRLF and its trailing LF overlapping matches. Corrected the
   matcher so LF inside CRLF is never a second candidate; genuine overlapping
   source occurrences still fail closed. Two existing HTML absence assertions
   matched a CSS value selector rather than a button; changed the styling to a
   named class, retaining the tests unweakened. Recorded first implementation at
   68e262b and correction at c676a60. Follow-up: all 18 targeted tests passed.
4. Actual synthetic browser submission preserved invalid evidence and notes, but
   its error was above the form anchor and initially outside the viewport.
   Moved the error inside the editor at f2993a8; repeat inspection placed it at
   y=86.47px. A subsequent synthetic save showed the exact changed issue, unknown
   scope, added category and notes, without changing original output.
5. Clarified 'each decision' instead of 'each action' at 8f8b0c7 because list
   actions only return an unsaved form. Updated the affected screenshot.
6. Backfilled current guides and screenshots at bd62a77. Required new-form
   operational instructions were already present with the implementation.

Host execution note: initial log redirection under the restricted identity could
not write the host-owned evidence directory; tests did not run in that attempt.
Used the authorised host execution context, without changing ACLs. No failed
test run was discarded. No model was invoked or research judgement submitted.

An unrelated-to-code research save discrepancy was discovered through read-only
inspection after the owner reported saving another tab. Its identities and
intended judgement remain only in the external study feedback record. They are
excluded from public software evidence and require explicit research reconciliation.
