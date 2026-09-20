# Reconstruction attempts

Attempt 1 retained at refactor/vs1-milestone-architecture-review and series-attempt-1.json.
P2 failed Ruff I001 because the diary's import-order correction arrived in P3.
The frozen diary already contains the correct ordering. Reconstruction attempt 2
moves only that existing correction into P2; it does not change final content.
P1 is unchanged and retains its own exact-SHA verification. All new descendant
identities require new checkpoint checks, even if an old corresponding tree passed.
The original failed log r1-p2-checks.log and all other attempt-1 results are retained.
No source/test/quality policy is changed or weakened. No candidate was published.
