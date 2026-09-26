"""Read retained EDR-0001 artefacts; publish separately labelled exploratory diagnostics.

Run from the locked project environment with --study pointing to the external
EDR-0001 directory and --output to a new external directory. No model or database
is called. Detailed pair texts stay in that directory; only summary.json is
intended for the repository, subject to review of its aggregate contents.
"""

import argparse
import hashlib
import json
import math
import re
import subprocess
from collections import Counter
from fractions import Fraction
from itertools import combinations
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[3]
COSINE_GRID = (0.60, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95)
LEXICAL_GRID = tuple(Fraction(x, 100) for x in (10, 15, 20, 25, 30, 40, 50))


def verified(path, identity):
    """Require exact recorded bytes before inspecting a retained input."""
    content = path.read_bytes()
    if hashlib.sha256(content).hexdigest() != identity:
        raise ValueError(f"Digest mismatch: {path.name}")
    return content


def quantiles(values):
    """Use nearest-rank quantiles, retaining observed rather than interpolated values."""
    values = sorted(values)
    return {
        str(p): float(values[max(0, math.ceil(p * len(values)) - 1)])
        for p in (0, 0.25, 0.5, 0.75, 0.9, 0.95, 1)
    }


def partition(scores, threshold):
    """Independently traverse an inclusive undirected similarity graph."""
    neighbours = [set() for _ in scores]
    for i, j in combinations(range(len(scores)), 2):
        if scores[i][j] >= threshold:
            neighbours[i].add(j)
            neighbours[j].add(i)
    unseen, groups, outliers = set(range(len(scores))), [], []
    while unseen:
        pending, component = [min(unseen)], set()
        while pending:
            item = pending.pop()
            if item in component:
                continue
            component.add(item)
            pending.extend(neighbours[item] - component)
        unseen -= component
        if len(component) >= 2:
            groups.append(sorted(component))
        else:
            outliers.extend(component)
    return groups, sorted(outliers), sum(map(len, neighbours)) // 2


def description(scores, threshold):
    """Summarise graph structure without treating it as human-rated coherence."""
    groups, outliers, edges = partition(scores, threshold)
    return {
        "threshold": float(threshold),
        "groups": len(groups),
        "group_sizes": sorted(map(len, groups), reverse=True),
        "covered": len(scores) - len(outliers),
        "edges": edges,
        "chained_groups": sum(
            any(scores[i][j] < threshold for i, j in combinations(group, 2)) for group in groups
        ),
        "minimum_within_group_similarity": [
            float(min(scores[i][j] for i, j in combinations(group, 2))) for group in groups
        ],
    }


def diagnose(scores, grid):
    """Check every graph-changing breakpoint; never choose an adoption threshold."""
    pairs = [scores[i][j] for i, j in combinations(range(len(scores)), 2)]
    # Include a no-edge state. Equal scores enter together at their inclusive threshold.
    thresholds = [max(pairs) + 1, *sorted(set(pairs), reverse=True)]
    sweep = [description(scores, threshold) for threshold in thresholds]
    summary = {
        "pairs": len(pairs),
        "pair_quantiles": quantiles(pairs),
        "nearest_neighbour_quantiles": quantiles(
            max(row[j] for j in range(len(row)) if j != i) for i, row in enumerate(scores)
        ),
        "fixed_grid": [description(scores, t) for t in grid],
        "breakpoint_states": len(sweep),
        "maximum_groups": max(s["groups"] for s in sweep),
        "any_state_with_eight_groups_and_24_covered": any(
            s["groups"] >= 8 and s["covered"] >= 24 for s in sweep
        ),
    }
    return summary, sweep


def lexical(texts):
    """Compute independent exact token-set Jaccard scores for the stated texts."""
    tokens = [set(re.findall(r"[a-z0-9]+", text.casefold())) for text in texts]
    return [
        [Fraction(len(a & b), len(a | b)) if a | b else Fraction(0) for b in tokens] for a in tokens
    ]


def verify_method():
    """Challenge transitive chaining, tied edges, empty tokens and inclusive boundaries."""
    chain = [[1, 0.8, 0.1, 0], [0.8, 1, 0.8, 0], [0.1, 0.8, 1, 0], [0, 0, 0, 1]]
    assert partition(chain, 0.8) == ([[0, 1, 2]], [3], 2)
    assert description(chain, 0.8)["chained_groups"] == 1
    assert partition(chain, 0.81) == ([], [0, 1, 2, 3], 0)
    assert lexical(("", "")) == [[0, 0], [0, 0]]
    assert lexical(("A b", "a c"))[0][1] == Fraction(1, 3)
    assert quantiles([1, 2, 3, 4])["0.5"] == 2


def main():
    """Verify identities, calculate bounded diagnostics and retain all output in a new folder."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--study", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    verify_method()
    args.output.mkdir(parents=True, exist_ok=False)
    inventory = json.loads((ROOT / "docs/edr/evidence/0001-comparison-outcome.json").read_bytes())
    keys = inventory["artefacts"]
    runtime = args.study / "runtime"
    comparison = json.loads(
        verified(
            args.study / "comparison" / f"{keys['comparison_sha256']}.json",
            keys["comparison_sha256"],
        )
    )
    selection = json.loads(
        verified(
            runtime / "selections" / f"{keys['selection_sha256']}.json", keys["selection_sha256"]
        )
    )
    vector_path = runtime / "discovery" / f"{keys['vectors_sha256']}.parquet"
    verified(vector_path, keys["vectors_sha256"])
    with duckdb.connect() as db:
        rows = db.execute(
            "SELECT position, annotation_id, text, vector FROM read_parquet(?) ORDER BY position",
            [str(vector_path)],
        ).fetchall()
    ids = [row[1] for row in rows]
    assert [row[0] for row in rows] == list(range(40))
    assert ids == selection["request"]["annotation_ids"]
    assert ids == [item["id"] for item in comparison["value"]["items"]]
    records = {r["annotation"]["id"]: r for r in selection["records"]}
    interpretations = [records[identity]["interpretation"] for identity in ids]
    issues = [item["issue_statement"] for item in interpretations]
    invariants = [item["proposed_invariant"] or "" for item in interpretations]
    texts = [
        "\n".join((issue, invariant, ", ".join(item["coarse_categories"])))
        for issue, invariant, item in zip(issues, invariants, interpretations, strict=True)
    ]
    assert texts == [row[2] for row in rows]
    assert texts == [item["text"] for item in comparison["value"]["items"]]
    vectors = [row[3] for row in rows]
    assert all(len(v) == 768 and all(math.isfinite(x) for x in v) for v in vectors)
    norms = [math.sqrt(sum(x * x for x in v)) for v in vectors]
    assert all(abs(n - 1) < 1e-10 for n in norms)
    vectors = [[x / norm for x in v] for v, norm in zip(vectors, norms, strict=True)]
    cosine = [[sum(a * b for a, b in zip(x, y, strict=True)) for y in vectors] for x in vectors]
    full = lexical(texts)
    for method, scores, threshold in (
        ("baseline", full, Fraction(1, 4)),
        ("candidate", cosine, 0.85),
    ):
        groups, outliers, _ = partition(scores, threshold)
        expected = comparison["value"][method]
        assert {tuple(sorted(ids[i] for i in g)) for g in groups} == {
            tuple(sorted(g["members"])) for g in expected["groups"]
        }
        assert {ids[i] for i in outliers} == set(expected["outliers"])
    flags = [item["actionable_engineering_concern"] for item in interpretations]
    assert set(flags) <= {"yes", "no", "uncertain"}
    concern = [flag == "yes" for flag in flags]
    summary = {
        "purpose": "post-result exploration; no adoption threshold or human coherence ratings",
        "scope_commit": "d1a1e39",
        "input_identities": keys,
        "method_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "verification": {
            "synthetic_challenges_passed": True,
            "independent_registered_partition_replay_passed": True,
            "aligned_records": len(rows),
            "dimensions": 768,
            "duplicate_vector_rows": len(vectors) - len({tuple(v) for v in vectors}),
            "norm_min": min(norms),
            "norm_max": max(norms),
        },
        "corpus": {
            "concern_flags": dict(Counter(flags)),
            "categories": dict(Counter(c for i in interpretations for c in i["coarse_categories"])),
            "repository_counts": dict(
                Counter(i["repository"] for i in comparison["value"]["items"])
            ),
            "text_character_quantiles": quantiles(map(len, texts)),
        },
        "diagnostics": {},
        "registered_groups": {},
    }
    details = {"sweeps": {}, "top_concern_pairs": {}, "registered_group_texts": {}}
    variants = {
        "cosine_full": (cosine, COSINE_GRID),
        "lexical_full": (full, LEXICAL_GRID),
        "lexical_issue_only": (lexical(issues), LEXICAL_GRID),
        "lexical_issue_invariant": (
            lexical([a + "\n" + b for a, b in zip(issues, invariants, strict=True)]),
            LEXICAL_GRID,
        ),
    }
    for name, (scores, grid) in variants.items():
        summary["diagnostics"][name], details["sweeps"][name] = diagnose(scores, grid)
    for name, scores, threshold in (
        ("cosine_full", cosine, 0.85),
        ("lexical_full", full, Fraction(1, 4)),
    ):
        groups, _, _ = partition(scores, threshold)
        summary["registered_groups"][name] = [
            {"members": len(g), "concerns": sum(concern[i] for i in g)} for g in groups
        ]
        details["registered_group_texts"][name] = [[texts[i] for i in g] for g in groups]
        pairs = sorted(
            ((i, j) for i, j in combinations(range(40), 2) if concern[i] and concern[j]),
            key=lambda p: (-scores[p[0]][p[1]], ids[p[0]], ids[p[1]]),
        )[:10]
        details["top_concern_pairs"][name] = [
            {"ids": [ids[i], ids[j]], "score": float(scores[i][j]), "texts": [texts[i], texts[j]]}
            for i, j in pairs
        ]
    summary["code_commit"] = subprocess.check_output(
        ["git", "-c", f"safe.directory={ROOT.as_posix()}", "-C", str(ROOT), "rev-parse", "HEAD"],
        text=True,
    ).strip()
    for name, value in (("details", details), ("summary", summary)):
        (args.output / f"{name}.json").write_text(
            json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8"
        )
    print(json.dumps({"output": str(args.output), "verification": summary["verification"]}))


if __name__ == "__main__":
    main()
