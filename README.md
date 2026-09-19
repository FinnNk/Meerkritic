# Local normalisation — DER round r2

Evidence-only branch: never merge it into main. Application: feat/normalisation-workflow-r2.
Start with r2/plan.md, r2/review.md, r2/discoveries.md and r2/verification-summary.json.

Frozen diary 3da9af4a2c04fecb1bd18fee309af0411c8a9894 and semantic tip
fc30a333e950270356d99b29ab06cf84ca91154c have exactly equal tracked trees.
The five semantic checkpoints pass 43/53/58/68/72 tests and all canonical gates in
separate Windows/Python3.12 locked own-source environments. The frozen diary passes 72.
See exact identity, environment, lock hash, command and exit records, not only counts.

Real browser submission and a separate worker executed the real MAF 1.19.0 graph against
the pinned local llama.cpp/Qwen fixture. r2/live.json records source identity, usage,
framework observation, events and immutable result digest. Model output is not judged
correct merely because quotes match. Human annotation and VS1 completion remain pending.

Full review is self-review. A fresh-context scoped challenge found defects and test gaps;
dispositions are retained. R1 and its earlier reconstructed candidate are preserved;
neither was published as an accepted revision. R2 corrects completion after deadline.
Synchronous blocked I/O may return after elapsed deadline; late success is rejected.
No hosted CI, owner approval, integration or other-platform execution is claimed.

Reproduce checkpoints: clone rounds/r2/history.bundle, check out each SHA in r2/commits.json,
use Python3.12 and uv sync --locked, then uv run --locked python tools/check.py. Each
checkpoint needs its own source and environment. Typed architecture snapshots use
python tools/architecture.py snapshot --root CHECKOUT and its delta command. Live
reproduction uses docs/development/local-inference.md and normalisation.md at the tip,
the pinned public dataset and verified-downloads.json. GPU output/timing can vary.

Bundles, manifests and ledger events are byte-preserved copies of canonical external
evidence. Text paths and line endings are normalised; export-provenance.json records
both hashes. SHA256SUMS.json covers every payload file. Private data, credentials, model
weights and raw public dataset/prompt/result bodies are omitted. Their identities and
reproduction methods are recorded where applicable. No hidden reasoning or transcripts
are exported. Later publication/review events remain in the canonical external ledger;
this immutable archive does not claim actions that had not happened when it was built.
