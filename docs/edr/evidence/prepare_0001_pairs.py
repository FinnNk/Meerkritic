"""Prepare twelve developmental pairs and read-only cards from frozen EDR-0001 inputs."""

import argparse
import hashlib
import html
import json
import math
from collections import Counter
from itertools import combinations
from pathlib import Path

import duckdb
from diagnose_0001 import ROOT, lexical, verified

SCOPE = "9213bbd10c2320ff8f6fb42143d8f20a961e6aba"


def encoded(value):
    """Canonicalise finite JSON for stable identities and seeded ordering."""
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()


def digest(value):
    """Hash bytes, or canonical JSON for a structured value."""
    return hashlib.sha256(value if isinstance(value, bytes) else encoded(value)).hexdigest()


def rank(stage, pair):
    """Use the frozen stage-separated pair ordering."""
    return digest({"seed": 20260927, "stage": stage, "members": list(pair)})


def choose(ids, flags, cosine, jaccard):
    """Fill the fixed disjoint portions without treating selection flags as new labels."""
    pairs = list(combinations(sorted(ids), 2))
    positive = [p for p in pairs if all(flags[i] == "yes" for i in p)]
    selected = {}

    def take(name, count, candidates):
        available = [p for p in candidates if p not in selected][:count]
        if len(available) != count:
            raise ValueError(f"Insufficient pairs for {name}; no substitution allowed.")
        selected.update((p, name) for p in available)

    take("semantic", 4, sorted(positive, key=lambda p: (-cosine[p], p)))
    take("lexical", 3, sorted(positive, key=lambda p: (-jaccard[p], p)))
    take("general", 2, sorted(positive, key=lambda p: rank("select", p)))
    for name, expected in (
        ("no-no", ["no", "no"]),
        ("no-yes", ["no", "yes"]),
        ("uncertain-yes", ["uncertain", "yes"]),
    ):
        pool = [p for p in pairs if sorted(flags[i] for i in p) == expected]
        take(name, 1, sorted(pool, key=lambda p: rank("select", p)))
    return [(p, selected[p]) for p in sorted(selected, key=lambda p: rank("present", p))]


def card_page(pair, pack_id):
    """Escape every retained text field; cards expose no scores, strata or old flags."""
    escape = html.escape
    cards = []
    for side, item in zip(("A", "B"), pair["items"], strict=True):
        limits = "".join(f"<li>{escape(x)}</li>" for x in item["exclusions"])
        cards.append(
            f"<article><h2>Item {side}</h2><h3>Concern as assessed</h3>"
            f"<p>{escape(item['issue_statement'])}</p><h3>Candidate rule · not validated</h3>"
            f"<p>{escape(item['proposed_invariant'] or 'No candidate rule recorded.')}</p>"
            f"<h3>Applicability limits</h3><ul>{limits}</ul>"
            + (
                ""
                if limits
                else "<p>No limits recorded; this does not establish universal validity.</p>"
            )
            + f'<a href="{escape(item["source_url"], quote=True)}" target="_blank" '
            'rel="noopener">Open source assessment</a></article>'
        )
    nav = " ".join(
        f'<a href="P{i:02}.html"'
        + (' aria-current="page"' if pair["pair_id"] == f"P{i:02}" else "")
        + f">{i}</a>"
        for i in range(1, 13)
    )
    return f"""<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>Pair {pair["pair_id"]} · Meerkritic</title>
<style>
*{{box-sizing:border-box}}body{{margin:0;background:#f2f5f7;color:#202e3a;font:17px/1.55 system-ui}}
main{{max-width:1160px;margin:auto;padding:24px}}
header p{{margin:4px 0}}h1{{font-size:28px;margin:8px 0}}
.eyebrow{{color:#466372;font-weight:650}}nav{{display:flex;gap:7px;flex-wrap:wrap;margin:16px 0}}
nav a{{padding:5px 13px;background:white;border:1px solid #c4d2da;
border-radius:6px;text-decoration:none}}
nav a[aria-current]{{background:#164c63;color:white}}a{{color:#125c7a}}
a:focus-visible{{outline:3px solid #ad5700}}
.instructions{{background:#e4eff3;border-left:4px solid #286d83;
padding:12px 18px;border-radius:6px}}
.cards{{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin:22px 0}}
article{{padding:22px;background:white;border:1px solid #c4d2da;border-radius:10px}}
h2{{margin:0 0 14px;font-size:22px}}h3{{font-size:15px;color:#4c606d;margin:20px 0 7px}}
article p{{white-space:pre-wrap;margin:6px 0}}article ul:empty{{display:none}}
table{{border-collapse:collapse;width:100%;background:white}}
th,td{{padding:10px;border:1px solid #c4d2da;text-align:left}}
details{{margin:18px 0}}summary{{cursor:pointer;font-weight:650}}
footer{{color:#516572;font-size:13px;overflow-wrap:anywhere}}
@media(max-width:700px){{.cards{{grid-template-columns:1fr}}main{{padding:16px}}}}
</style><main><header><p class="eyebrow">
Meerkritic · Developmental pair review · {pair["pair_id"]} of 12</p>
<h1>Do these express the same engineering concern?</h1>
<p>Compare their meaning, intended action and applicability, not just shared words.</p></header>
<nav aria-label="Choose pair">{nav}</nav>
<section class="instructions"><strong>This page is read-only. Reply in chat.</strong>
<p>First: is each item a usable engineering concern or investigation? Answer A and B with
<b>yes</b>, <b>no</b> or <b>uncertain</b>. Then choose the relationship and give a short reason.
We will confirm unclear answers before recording them.
Opening a card records no judgement.</p></section>
<section class="cards">{"".join(cards)}</section>
<table><thead><tr><th>Relationship</th><th>Use when both items are eligible</th></tr></thead><tbody>
<tr><td>Same specific concern</td><td>One specific engineering requirement
with compatible conditions explains both.</td></tr>
<tr><td>Merely related</td><td>A shared topic, but materially different
requirements, actions or conditions.</td></tr>
<tr><td>Unrelated</td><td>No meaningful engineering-concern relationship is supported.</td></tr>
<tr><td>Uncertain</td><td>There is not enough information to decide.</td></tr></tbody></table>
<details><summary>Eligibility and review notes</summary><ul>
<li>A concrete investigation can qualify even when no defect is proven.
A missing candidate rule does not automatically disqualify it.</li>
<li>Praise without a concern does not qualify. Eligibility does not establish
reviewer correctness or a valid general rule.</li>
<li>If either item is no, the relationship is not applicable. Otherwise,
an uncertain eligibility answer leaves the relationship uncertain.</li>
<li>Tell us if you open the source or recognise an example. Existing assessments
stay unchanged; confirmed pair answers are recorded separately.</li>
</ul></details><footer>Pack: {pack_id}<br>
Read-only cards have no save action or browser-local response storage.
</footer></main></html>"""


def main():
    """Verify immutable evidence, create the deterministic pack, and retain blank response forms."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--study", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    keys = json.loads((ROOT / "docs/edr/evidence/0001-comparison-outcome.json").read_bytes())[
        "artefacts"
    ]
    selection = json.loads(
        verified(
            args.study / "runtime/selections" / f"{keys['selection_sha256']}.json",
            keys["selection_sha256"],
        )
    )
    vector_path = args.study / "runtime/discovery" / f"{keys['vectors_sha256']}.parquet"
    verified(vector_path, keys["vectors_sha256"])
    with duckdb.connect() as db:
        rows = db.execute(
            "SELECT annotation_id,text,vector FROM read_parquet(?) ORDER BY position",
            [str(vector_path)],
        ).fetchall()
    ids = [r[0] for r in rows]
    assert ids == selection["request"]["annotation_ids"] and len(set(ids)) == 40
    records = {r["annotation"]["id"]: r for r in selection["records"]}
    for identity, text, vector in rows:
        item = records[identity]["interpretation"]
        assert text == "\n".join(
            (
                item["issue_statement"],
                item["proposed_invariant"] or "",
                ", ".join(item["coarse_categories"]),
            )
        )
        assert len(vector) == 768 and all(math.isfinite(x) for x in vector)
        assert abs(sum(x * x for x in vector) - 1) < 1e-10
    norms = [math.sqrt(sum(x * x for x in r[2])) for r in rows]
    vectors = {r[0]: [x / n for x in r[2]] for r, n in zip(rows, norms, strict=True)}
    pairs = list(combinations(sorted(ids), 2))
    cosine = {
        p: sum(a * b for a, b in zip(vectors[p[0]], vectors[p[1]], strict=True)) for p in pairs
    }
    scores = lexical([r[1] for r in rows])
    positions = {identity: i for i, identity in enumerate(ids)}
    jaccard = {p: scores[positions[p[0]]][positions[p[1]]] for p in pairs}
    flags = {i: records[i]["interpretation"]["actionable_engineering_concern"] for i in ids}
    selected = choose(ids, flags, cosine, jaccard)
    public, private = [], []
    for number, (pair, stratum) in enumerate(selected, 1):
        order = pair if int(rank("sides", pair)[0], 16) % 2 == 0 else pair[::-1]
        items = []
        for identity in order:
            record = records[identity]
            item = record["interpretation"]
            items.append(
                {
                    "annotation_id": identity,
                    **{k: item[k] for k in ("issue_statement", "proposed_invariant", "exclusions")},
                    "source_url": f"http://127.0.0.1:8010/jobs/{record['annotation']['job_id']}",
                }
            )
        public.append({"pair_id": f"P{number:02}", "items": items})
        private.append(
            {
                "pair_id": f"P{number:02}",
                "members": pair,
                "stratum": stratum,
                "cosine": cosine[pair],
                "jaccard": float(jaccard[pair]),
            }
        )
    pack = {
        "protocol": "edr-0001-development-pairs-v1",
        "scope_commit": SCOPE,
        "selection_sha256": keys["selection_sha256"],
        "pairs": public,
    }
    pack_id = digest(pack)
    manifest = {
        "pack_sha256": pack_id,
        "scope_commit": SCOPE,
        "selection_sha256": keys["selection_sha256"],
        "vectors_sha256": keys["vectors_sha256"],
        "method_sha256": digest(Path(__file__).read_bytes()),
        "diagnostic_helper_sha256": digest(
            Path(__file__).with_name("diagnose_0001.py").read_bytes()
        ),
        "private_map_sha256": digest(private),
        "pairs": len(public),
        "distinct_inputs": len({i["annotation_id"] for p in public for i in p["items"]}),
        "portions": dict(Counter(p["stratum"] for p in private)),
        "human_judgements": 0,
    }
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output / "cards").mkdir()
    (args.output / "responses").mkdir()
    for filename, value in (
        ("pack.json", pack),
        ("private-map.json", private),
        ("manifest.json", manifest),
    ):
        (args.output / filename).write_bytes(encoded(value))
    for pair in public:
        (args.output / "cards" / f"{pair['pair_id']}.html").write_text(
            card_page(pair, pack_id), encoding="utf-8"
        )
    template = {
        "pack_sha256": pack_id,
        "pair_id": None,
        "reviewer": None,
        "recorded_at": None,
        "eligibility_a": None,
        "eligibility_b": None,
        "relationship": None,
        "reason": None,
        "context_consulted": [],
        "assistance": None,
        "recognition": None,
        "human_confirmed": False,
        "supersedes": None,
    }
    (args.output / "response-template.json").write_bytes(encoded(template))
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
