# Local Dataset Storage and Working-Copy Strategy

**Companion to:**  
- `01_SYSTEM_DESIGN.md`  
- `02_EXPERIMENTAL_PLAN.md`

**Purpose:** Define a practical local-storage strategy for the public code-review, SATD, repair and repository datasets used by the evidence-grounded semantic code-review research programme.

---

## 1. Executive summary

Keeping local working copies of the proposed datasets is practical and, for reproducibility, preferable to repeatedly reading mutable remote sources.

The core structured datasets discussed in this programme are **laptop-scale** [1]–[4]. The storage challenge is not primarily the review/SATD datasets themselves. The larger costs arise later from:

- cloned source repositories;
- historical Git worktrees;
- repository build environments;
- container images;
- local model weights;
- embeddings;
- mutation-testing artefacts;
- logs and repeated experiment outputs.

The recommended strategy is therefore a **two-tier local store**:

```text
Tier 1 — persistent and always local
    raw datasets
    normalised observations
    labels
    embeddings
    structural features
    split manifests
    rule registry
    experiment manifests

Tier 2 — cached/reconstructable
    full repository clones
    historical worktrees
    virtual environments
    containers
    test artefacts
    mutation outputs
```

Raw datasets should be treated as immutable. All transformations should create derived datasets rather than modifying source material in place.

Parquet should be the preferred working format for tabular research data, queried directly with tools such as DuckDB or Polars [7], [8].

Repository storage should use shared Git object stores and disposable worktrees rather than repeated full clones [9].

A practical local capacity target is:

- **minimum PoC:** ~100 GB free;
- **comfortable research workstation:** 250–500 GB free;
- **large-scale repository replay:** potentially 1 TB or more depending on cache-retention policy.

---

## 2. Why local copies are desirable

Local copies provide several advantages over repeatedly consuming upstream datasets.

### 2.1 Reproducibility

Experiments should remain reproducible even if an upstream dataset changes.

The experiment should be able to state:

```text
dataset revision
+ exact input files
+ hashes
+ split manifest
+ transformation version
+ model/prompt version
```

rather than simply:

```text
dataset = latest
```

This is particularly important for actively maintained datasets.

### 2.2 Stable train/test boundaries

Repository-level train/development/test splits should be fixed once established.

If upstream rows are added or removed, a query against the latest version could silently alter:

- repository counts;
- class balance;
- cluster composition;
- test-set membership.

Keeping a pinned local snapshot avoids this.

### 2.3 Faster iteration

Local Parquet enables repeated scans, filtering and joins without network latency.

For example:

```sql
SELECT *
FROM read_parquet('derived/observations/*.parquet')
WHERE language = 'Python'
  AND generalisable = true;
```

This can be executed directly with DuckDB without loading the whole dataset into memory.

### 2.4 Auditability

A local immutable source layer makes it possible to establish exactly which upstream material produced a derived result.

### 2.5 Reduced dependency risk

Development is not blocked by:

- upstream outages;
- API rate limits;
- deleted repositories;
- changed file structures;
- changed access methods.

---

## 3. Expected storage scale

The principal structured datasets are relatively small compared with repository and execution artefacts.

A reasonable planning budget is:

| Component | Approximate working budget |
|---|---:|
| Core review/SATD datasets | < 5 GB |
| Converted/normalised Parquet | 5–20 GB |
| Human labels and metadata | < 1 GB |
| Embeddings | 1–20 GB |
| BCA/static-analysis features | 1–10 GB |
| Selected repository mirrors | 20–200+ GB |
| Historical Git worktrees | potentially 100s of GB |
| Python environments | 10–100+ GB |
| Container images/layers | 20–100+ GB |
| Local model weights | 20–100+ GB |
| Mutation/test outputs | 10s–100s of GB over time |
| Logs and reports | typically modest, but unbounded if unmanaged |

These figures are planning ranges rather than hard limits.

The main conclusion is:

> **The datasets are cheap; repository reconstruction and execution are expensive.**

---

## 4. Recommended directory layout

A local research tree should clearly separate immutable source material from generated artefacts.

```text
research-data/
├── datasets/
│   ├── raw/
│   │   ├── github-codereview/
│   │   │   └── <revision>/
│   │   ├── crc-py/
│   │   │   └── <git-sha>/
│   │   ├── satd/
│   │   │   └── <git-sha>/
│   │   ├── review4repair/
│   │   │   └── <revision>/
│   │   ├── codereviewer/
│   │   │   └── <revision>/
│   │   ├── bugsinpy/
│   │   └── swe-bench/
│   │
│   ├── derived/
│   │   ├── normalised-observations/
│   │   ├── verified-negatives/
│   │   ├── embeddings/
│   │   ├── bca-features/
│   │   ├── taxonomy-labels/
│   │   └── repair-cases/
│   │
│   ├── splits/
│   │   ├── repo-split-v1.parquet
│   │   ├── temporal-split-v1.parquet
│   │   └── repair-split-v1.parquet
│   │
│   └── manifests/
│       ├── dataset-lock.yaml
│       └── licence-manifest.yaml
│
├── repositories/
│   ├── mirrors/
│   └── worktrees/
│
├── models/
│   ├── llm/
│   └── embeddings/
│
├── experiments/
│   ├── manifests/
│   ├── outputs/
│   ├── logs/
│   └── patches/
│
├── caches/
│   ├── containers/
│   ├── python/
│   └── mutation/
│
└── reports/
```

---

## 5. Raw datasets should be immutable

The `datasets/raw` layer should be treated as write-once.

Do not:

- edit source CSV/JSON/Parquet in place;
- overwrite downloaded files;
- append locally produced labels to the original dataset;
- rely on mutable upstream `main` branches without recording revisions.

Instead:

```text
raw dataset
    ↓
transform
    ↓
derived dataset
```

This preserves a clean lineage.

---

## 6. Dataset locking

Each upstream dataset should be pinned using:

- source URL;
- source revision;
- retrieval date;
- file names;
- file sizes;
- cryptographic hashes;
- licence information.

Example:

```yaml
github_codereview:
  source: https://huggingface.co/datasets/ronantakizawa/github-codereview
  revision: <dataset-revision>
  retrieved: 2026-09-19
  files:
    train.parquet:
      size_bytes: ...
      sha256: ...
  licence:
    declared: other
    notes: >
      Review redistribution/training implications separately
      from underlying repository licences.
```

For Git repositories:

```yaml
crc_py:
  source: https://github.com/busraicoz/crc-py-dataset
  commit: <sha>
  retrieved: 2026-09-19
```

Experiment manifests should refer to these locked versions.

---

## 7. Preferred working format: Parquet

Where practical, derived research tables should be stored as Parquet.

Advantages:

- columnar compression;
- efficient scanning;
- predicate pushdown;
- compatibility with DuckDB, Polars, Pandas, Spark and many other tools;
- easy partitioning;
- good schema preservation;
- straightforward versioning.

Suggested partitions:

```text
derived/normalised-observations/
├── language=Python/
├── language=Java/
└── ...
```

or:

```text
dataset=<source>/
language=<language>/
year=<year>/
```

Avoid excessive partitioning for small datasets.

---

## 8. DuckDB as a local query layer

A dedicated database server is not required initially.

DuckDB can query Parquet directly [7]:

```sql
SELECT
    repository_id,
    coarse_category,
    COUNT(*) AS observations
FROM read_parquet(
    'datasets/derived/normalised-observations/**/*.parquet'
)
WHERE language = 'Python'
GROUP BY repository_id, coarse_category;
```

This is useful for:

- experiment cohort selection;
- repo-level split creation;
- cluster analysis;
- joining observations with BCA features;
- producing evaluation tables.

The underlying files remain ordinary Parquet.

---

## 9. Embedding storage

Embeddings should be treated as derived artefacts.

Store:

```text
observation_id
embedding_model
embedding_model_revision
embedding_dimension
embedding
normalisation_config
```

Possible storage approaches:

- Parquet fixed-size arrays;
- NumPy/Arrow arrays;
- FAISS index plus metadata table.

A dedicated vector database is unnecessary for the first research phase.

It becomes relevant only if:

- interactive retrieval latency matters;
- the corpus grows substantially;
- multiple users/services query the index concurrently.

---

## 10. Repository storage

Repository reconstruction is likely to become the dominant storage consumer.

### 10.1 Avoid repeated clones

Do not create:

```text
experiment-001/repo/
experiment-002/repo/
experiment-003/repo/
```

as independent full clones.

Instead maintain one bare or mirror repository:

```text
repositories/mirrors/
└── psf__requests.git
```

and materialise worktrees:

```text
repositories/worktrees/
├── exp-001-requests/
├── exp-002-requests/
└── exp-003-requests/
```

The worktrees share the Git object database [9].

### 10.2 Delete worktrees after experiments

Preserve:

- commit SHA;
- patch;
- experiment manifest;
- test results;
- required logs.

Delete the worktree unless there is a concrete reason to retain it.

### 10.3 Fetch repositories on demand

For E1–E5, many experiments can operate solely on code snippets already included in review datasets.

Do not clone hundreds of repositories before they are needed.

Preferred flow:

```text
dataset row
   ↓
snippet-level experiment
   ↓
repository required?
      ├── no → continue
      └── yes
            ↓
      fetch/cache mirror
            ↓
      create temporary worktree
```

---

## 11. Repository cache policy

Use an explicit cache-retention policy.

Example:

### Hot

Repositories used within the last 30 days.

Keep locally.

### Warm

Frequently reused repositories but inactive.

Keep the bare mirror; delete worktrees.

### Cold

Rarely reused repositories.

Delete local mirror if space is constrained.

The manifest still records:

- upstream URL;
- commit SHA;
- required submodules/LFS data;
- environment reconstruction information.

---

## 12. SWE-bench and BugsInPy environments

Execution-oriented datasets such as SWE-bench and BugsInPy introduce another storage class [5], [6]:

```text
source repository
+ dependencies
+ build cache
+ container/environment
+ generated test artefacts
```

Do not persist every fully instantiated execution environment indefinitely.

Prefer preserving:

```text
base commit
patch
environment specification
tool versions
test command
test outputs
experiment result
```

Then reconstruct when needed.

Container layers can be shared, but should be garbage-collected periodically.

---

## 13. Local model storage

Model weights may exceed the core datasets in size.

Recommended separation:

```text
models/
├── llm/
│   ├── model-a/
│   └── model-b/
└── embeddings/
```

Record:

- model name;
- upstream revision;
- quantisation;
- file checksum;
- inference engine compatibility.

Do not copy model weights into individual experiment directories.

Experiment manifests should reference shared model IDs.

---

## 14. Derived data lifecycle

Derived artefacts fall into three classes.

### 14.1 Permanent

Retain indefinitely:

- validated labels;
- rule registry;
- verified negatives;
- experiment manifests;
- split manifests;
- final metrics;
- accepted patches/results.

### 14.2 Recomputable but expensive

Usually retain:

- embeddings;
- BCA features;
- static-analysis outputs;
- normalised observations.

### 14.3 Cheap/reconstructable

Safe to delete:

- temporary worktrees;
- build directories;
- compiler caches;
- intermediate logs;
- transient agent scratch files.

This classification should drive cleanup tooling.

---

## 15. Experiment directory discipline

Each experiment should have a small, reproducible manifest rather than a huge copied workspace.

Example:

```text
experiments/
└── replay-2026-09-001/
    ├── experiment.yaml
    ├── results.parquet
    ├── summary.json
    ├── patches/
    └── logs/
```

`experiment.yaml`:

```yaml
dataset:
  name: crc-py
  revision: <sha>

split:
  manifest: repo-split-v1.parquet

normaliser:
  version: 5

rules:
  registry_version: 3

model:
  id: local-model-x
  quantisation: q4

repository_cache:
  policy: mirror-plus-worktree
```

The source repository itself should not live here.

---

## 16. Backup strategy

Back up what cannot be recreated cheaply.

### Back up

- manually adjudicated labels;
- rule registry;
- verified negatives;
- split manifests;
- experiment manifests;
- final results;
- licence metadata;
- accepted patch sets;
- custom prompts/configuration.

### Usually do not back up

- repository mirrors;
- model weights;
- downloaded public raw datasets;
- transient containers;
- temporary worktrees.

These can be redownloaded if their exact revisions are recorded.

For especially fragile or mutable public sources, retaining the raw copy may still be worthwhile.

---

## 17. Compression and deduplication

### 17.1 Parquet compression

Use a modern default such as Zstandard or Snappy depending on throughput requirements.

### 17.2 Git object deduplication

Mirror/worktree architecture already avoids much duplication.

### 17.3 Avoid duplicated text blobs

If many observations reference the same source file, consider storing:

```text
blob_sha
```

and a shared code-blob table instead of copying full files repeatedly.

Do not introduce this complexity until duplication is measurable.

---

## 18. Storage monitoring

Track storage by category:

```text
raw datasets
derived datasets
repositories
worktrees
models
containers
mutation artefacts
logs
```

A simple periodic report is sufficient initially.

Example:

```text
Category              Size
--------------------------------
raw datasets          3.8 GB
derived               12.6 GB
repo mirrors          47.2 GB
worktrees             83.5 GB
models                51.0 GB
containers            36.4 GB
mutation cache        14.8 GB
```

The report makes it obvious which tier requires cleanup.

---

## 19. Suggested capacity planning

### Small PoC

Suitable for:

- CRC-Py;
- SATD;
- Python review subset;
- embeddings;
- a few repositories;
- one or two local models.

Recommended free space:

**~100 GB**

### Comfortable research workstation

Suitable for:

- all core structured datasets;
- multiple model weights;
- dozens/hundreds of repository mirrors;
- repeated repair experiments;
- moderate SWE-bench/BugsInPy use.

Recommended free space:

**250–500 GB**

### Large replay programme

Suitable for:

- hundreds of repositories;
- many concurrent historical worktrees;
- persistent containers;
- mutation-testing outputs;
- multiple model variants.

Recommended:

**1 TB+**, or a separate high-capacity SSD/cache volume.

---

## 20. Hardware implications

The structured datasets themselves do not require exceptional RAM.

For example:

- DuckDB can scan Parquet lazily;
- Polars can operate out-of-core;
- embeddings can be processed in batches;
- repository mirrors live primarily on disk.

For a workstation with high system RAM, storage bandwidth and disk capacity are likely to become limiting before tabular-memory capacity.

NVMe storage is preferable for:

- large Git worktrees;
- test execution;
- container extraction;
- mutation testing;
- repeated Parquet scans.

---

## 21. Recommended local architecture

A practical implementation:

```text
NVMe SSD
│
├── persistent/
│   ├── datasets/raw
│   ├── datasets/derived
│   ├── splits
│   ├── manifests
│   ├── rules
│   └── experiment results
│
└── cache/
    ├── repositories
    ├── worktrees
    ├── containers
    ├── build caches
    └── mutation artefacts
```

If a second drive is available:

```text
fast SSD:
    active datasets
    active worktrees
    model weights

large secondary SSD:
    repository mirrors
    cold caches
    archived experiment outputs
```

---

## 22. Recommended implementation sequence

### Step 1

Create the immutable/derived directory structure.

### Step 2

Download and lock:

- CRC-Py [2];
- SATD [3];
- GitHub Code Review dataset [1];
- Review4Repair metadata/data [4].

### Step 3

Generate `dataset-lock.yaml`.

### Step 4

Convert non-Parquet sources to derived Parquet.

### Step 5

Create repository-level split manifests.

### Step 6

Add a DuckDB research database or views over Parquet.

### Step 7

Add embedding and BCA feature tables.

### Step 8

Introduce repository mirrors only when replay experiments require them.

### Step 9

Add automatic worktree cleanup.

### Step 10

Add storage reporting and cache eviction.

---

## 23. Practical recommendation

The programme should assume that all **structured research datasets and derived tables remain local permanently**.

Full repositories and execution environments should be treated as a **cache**.

That leads to the following guiding rule:

> Preserve information needed to reproduce an experiment; reconstruct bulky execution state when required.

This gives the project strong reproducibility without allowing repository worktrees, containers and mutation artefacts to consume storage indefinitely.

---


## Routing configuration and telemetry storage

Routing state is small operational metadata and should follow the existing storage split.

SQLite:

- project default policy;
- task policy override;
- `RoutingDecision`;
- `RoutingPolicyTransition`;
- current `ProviderHealth`;
- live `ModelUsage`.

Versioned files/config:

- `ModelInventory`;
- `RoutingPolicy`;
- price catalogue;
- context-strategy definitions.

Parquet/DuckDB:

- completed model-usage history;
- policy/route analysis across runs;
- spend/turnaround aggregates.

Historical inventory, policy and price-catalog versions referenced by completed runs must remain available even after models or policies are retired.



## Double-Entry Review evidence storage

DER requires a dedicated evidence store outside all application worktrees and Git metadata.
The harness may retain references/hashes and display state, but must not duplicate the DER store
as a competing source of truth.

Suggested local layout:

```text
research-data/
└── der-evidence/
    └── <pair-id>/
        ├── events/
        ├── rounds/
        ├── reviews/
        ├── verification/
        └── archives/
```

Materiality records, pair/round references and current readiness may be indexed in SQLite.
Large/immutable DER evidence stays in the external evidence store.


# References

[1] R. Takizawa, “GitHub Code Review Dataset,” Hugging Face Datasets, 2026. [Online]. Available: https://huggingface.co/datasets/ronantakizawa/github-codereview. [Accessed: Sep. 19, 2026].

[2] B. Icoz, “CRC-Py Dataset: Public Dataset of Python Code Review Comments Labeled with an ESEM'23 Taxonomy,” GitHub repository. [Online]. Available: https://github.com/busraicoz/crc-py-dataset. [Accessed: Sep. 19, 2026].

[3] Y. Li, M. Soliman, and P. Avgeriou, “Replication Package for Automatic Identification of Self-Admitted Technical Debt from Four Different Sources,” GitHub repository. [Online]. Available: https://github.com/yikun-li/satd-different-sources-data. [Accessed: Sep. 19, 2026].

[4] Review4Repair, “Review4Repair dataset and source code,” GitHub repository. [Online]. Available: https://github.com/Review4Repair/Review4Repair. [Accessed: Sep. 19, 2026].


[5] C. E. Jimenez, J. Yang, A. Wettig, S. Yao, K. Pei, O. Press, and K. Narasimhan, “SWE-bench: Can Language Models Resolve Real-World GitHub Issues?” arXiv:2310.06770, 2023. [Online]. Available: https://arxiv.org/abs/2310.06770.

[6] R. Widyasari *et al*., “BugsInPy: A Database of Existing Bugs in Python Programs to Enable Controlled Testing and Debugging Studies,” in *Proc. 28th ACM Joint Meeting on European Software Engineering Conf. and Symp. on the Foundations of Software Engineering (ESEC/FSE)*, 2020, doi: 10.1145/3368089.3417943.

[7] DuckDB Foundation, “DuckDB Documentation: Reading and Writing Parquet Files,” 2026. [Online]. Available: https://duckdb.org/docs/stable/data/parquet/overview. [Accessed: Sep. 19, 2026].

[8] Apache Arrow, “Apache Parquet,” 2026. [Online]. Available: https://parquet.apache.org/. [Accessed: Sep. 19, 2026].

[9] Git Project, “git-worktree Documentation,” 2026. [Online]. Available: https://git-scm.com/docs/git-worktree. [Accessed: Sep. 19, 2026].