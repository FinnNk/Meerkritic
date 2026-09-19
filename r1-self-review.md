# R1 self-review finding

Reviewed semantic dead2c75f7792799a5acefbe6c560ca76c62f55c, whole P1 and aggregate.
No approval implied. Author-session self-review, not independent.

R1-F1 (low, bug, verified): observations.py tells users to re-register when Parquet
has changed. Exclusive publication correctly refuses to replace corrupt content,
so that instruction alone cannot recover a changed file. The dataset guide already
explains preserving the damaged file before restoration. Correct the error to point
to recovery guidance on the diary, then re-freeze and verify a new candidate.

Other inspected obligations: retained source indices/repeated IDs/null optional context;
hash-before-publication; metadata/event transaction; read-only web with bounded
queries and escaped text; isolated composition; source/runtime separation; unchanged
architecture contracts. No other blocking findings from this self-review.
