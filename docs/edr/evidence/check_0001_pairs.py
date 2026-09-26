"""Check pair-selection edge cases and byte-for-byte reproduction of two local packs."""

import argparse
import json
from itertools import combinations
from pathlib import Path

from prepare_0001_pairs import card_page, choose, digest


def main():
    """Fail on unstable selection, leaked metadata, unsafe text or changed replay bytes."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original", type=Path)
    parser.add_argument("replay", type=Path)
    args = parser.parse_args()
    ids = list("abcdefgh")
    flags = dict(zip(ids, ["yes"] * 5 + ["no", "no", "uncertain"], strict=True))
    ties = dict.fromkeys(combinations(ids, 2), 1)
    selected = choose(ids, flags, ties, ties)
    assert len(selected) == len(dict(selected)) == 12
    assert {p for p, portion in selected if portion == "semantic"} == {
        ("a", "b"),
        ("a", "c"),
        ("a", "d"),
        ("a", "e"),
    }
    assert {p for p, portion in selected if portion == "lexical"} == {
        ("b", "c"),
        ("b", "d"),
        ("b", "e"),
    }
    assert choose(ids[::-1], flags, ties, ties) == selected
    try:
        choose(ids, dict.fromkeys(ids, "yes"), ties, ties)
    except ValueError as error:
        assert "no-no" in str(error)
    else:
        raise AssertionError("Missing control pool was silently replaced.")

    hostile = '<script>alert("x")</script>'
    item = {
        "issue_statement": hostile,
        "proposed_invariant": None,
        "exclusions": [hostile],
        "source_url": "http://127.0.0.1:8010/jobs/example",
        "coarse_categories": ["SECRET_CATEGORY"],
        "actionable_engineering_concern": "SECRET_FLAG",
    }
    card = card_page({"pair_id": "P01", "items": [item, item]}, "synthetic")
    assert hostile not in card and "&lt;script&gt;" in card
    assert "SECRET_CATEGORY" not in card and "SECRET_FLAG" not in card
    assert "<form" not in card and "<script" not in card

    files = sorted(p.relative_to(args.original) for p in args.original.rglob("*") if p.is_file())
    replay_files = sorted(p.relative_to(args.replay) for p in args.replay.rglob("*") if p.is_file())
    assert files == replay_files
    for path in files:
        assert (args.original / path).read_bytes() == (args.replay / path).read_bytes(), path
    manifest = json.loads((args.original / "manifest.json").read_bytes())
    assert digest((args.original / "pack.json").read_bytes()) == manifest["pack_sha256"]
    assert (
        digest((args.original / "private-map.json").read_bytes()) == manifest["private_map_sha256"]
    )
    assert not list((args.original / "responses").iterdir())
    print(
        json.dumps(
            {
                "synthetic_checks": "passed",
                "identical_files": len(files),
                "human_judgements": 0,
                "pack_sha256": manifest["pack_sha256"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
