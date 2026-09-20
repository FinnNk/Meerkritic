"""Run the fixed lexical method, prepare masked assessments and analyse frozen human ratings."""

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from semantic_reviewer.adapters.discovery import ParquetDiscovery
from semantic_reviewer.application.comparison import assemble, baseline
from semantic_reviewer.bootstrap import build_discovery, runtime_path
from semantic_reviewer.domain.study import Comparison, Ratings, analyse, assessment, digest

ROOT = Path(__file__).resolve().parents[1]
EDR = "docs/edr/0001-discovery-grouping-method.md"


def registration(
    purpose: str, selection: str, commit: str | None, profile: dict | None = None, root: Path = ROOT
) -> dict | None:
    """Verify a two-commit registration reference before research operations.

    Require the exact selection/profile in the completed plan, its ancestor SHA in
    the registration commit, and unchanged tracked implementation/configuration.
    This checks recorded provenance, not truthful human attestation or undisclosed
    earlier experiments. Fixture runs must not carry a registration claim.
    """
    if purpose == "fixture":
        if commit:
            raise ValueError("Fixtures cannot claim research registration.")
        return None
    if not commit or not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("Research requires the full registration commit SHA.")
    document = _git(root, "show", f"{commit}:{EDR}")
    if not re.search(r"^- Status: registered\s*$", document, re.M):
        raise ValueError("The referenced EDR is not registered.")
    match = re.search(r"^- Registered plan: `([0-9a-f]{40})`", document, re.M)
    if not match or match[1] == commit:
        raise ValueError("Registration must name a separate completed-plan commit.")
    plan = match[1]
    _git(root, "merge-base", "--is-ancestor", plan, commit)
    frozen = _git(root, "show", f"{plan}:{EDR}")
    if f"- Selection: `{selection}`" not in frozen:
        raise ValueError("The frozen plan does not name this exact selection.")
    if profile is not None and f"- Embedding profile: `{digest(profile)}`" not in frozen:
        raise ValueError("The frozen plan does not name this exact embedding profile.")
    paths = ("src", "tools", "config", "uv.lock", "pyproject.toml", "tach.toml")
    _git(root, "diff", "--exit-code", plan, "HEAD", "--", *paths)
    _git(root, "diff", "--exit-code", "HEAD", "--", *paths)
    if _git(root, "ls-files", "--others", "--exclude-standard", "--", *paths).strip():
        raise ValueError("Untracked implementation files differ from the registered code.")
    return {
        "commit": commit,
        "plan_commit": plan,
        "registered_at": _git(root, "show", "-s", "--format=%cI", commit).strip(),
    }


def main() -> int:
    """Publish immutable external artefacts; print identities, never method mappings or ratings."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--registration-commit")
    commands = parser.add_subparsers(dest="command", required=True)
    lexical = commands.add_parser("baseline")
    lexical.add_argument("selection_id")
    lexical.add_argument("--previous")
    lexical.add_argument("--retry-reason")
    pack = commands.add_parser("pack")
    pack.add_argument("baseline_sha256")
    pack.add_argument("--attempts", type=Path, required=True)
    pack.add_argument("--profile", type=Path)
    report = commands.add_parser("analyse")
    report.add_argument("comparison_sha256")
    report.add_argument("--ratings", type=Path, required=True)
    args = parser.parse_args()
    try:
        files = ParquetDiscovery(runtime_path(args.evidence))
        if args.command == "baseline":
            service = build_discovery(args.data_root)
            summary, _ = service.selections.read(args.selection_id)
            registered = registration(summary.purpose, summary.id, args.registration_commit)
            previous = files.read_json(args.previous) if args.previous else None
            if previous and (
                previous.get("kind") != "baseline" or previous.get("registration") != registered
            ):
                raise ValueError("Retry predecessor has a different kind or registration.")
            result = baseline(
                service, summary.id, previous["result"] if previous else None, args.retry_reason
            )
            output = {
                "baseline_sha256": files.write_json(
                    {
                        "kind": "baseline",
                        "previous_baseline_sha256": args.previous,
                        "registration": registered,
                        "code_sha": _git(ROOT, "rev-parse", "HEAD").strip(),
                        "result": result,
                    }
                )
            }
        elif args.command == "pack":
            saved = files.read_json(args.baseline_sha256)
            if saved.get("kind") != "baseline":
                raise ValueError("Expected a saved baseline record.")
            lexical = saved["result"]
            profile = _read(args.profile) if args.profile else None
            registered = registration(
                lexical["purpose"], lexical["selection_id"], args.registration_commit, profile
            )
            if registered != saved["registration"]:
                raise ValueError("Baseline and comparison registration differ.")
            value, provenance = assemble(
                build_discovery(args.data_root), lexical, _read(args.attempts), profile
            )
            if registered:
                _after_registration(registered, lexical["started_at"])
                for attempt in provenance["attempts"]:
                    _after_registration(registered, attempt["embedding"]["queued_at"])
            comparison = files.write_json(
                {
                    "kind": "comparison",
                    "registration": registered,
                    "baseline_sha256": args.baseline_sha256,
                    "value": value.model_dump(mode="json"),
                    "provenance": json.loads(
                        json.dumps(provenance, default=lambda v: v.model_dump(mode="json"))
                    ),
                    "code_sha": _git(ROOT, "rev-parse", "HEAD").strip(),
                }
            )
            masked, mapping = assessment(value)
            pack_digest = files.write_json(masked)
            template = {
                "pack_sha256": pack_digest,
                "purpose": value.purpose,
                "rater": "",
                "suspected_unmasking": "",
                "ratings": [
                    {"group_id": group["group_id"], "judgement": "", "reason": ""}
                    for group in masked["groups"]
                ],
            }
            output = {
                "comparison_sha256": comparison,
                "pack_sha256": pack_digest,
                "ratings_template_sha256": files.write_json(template),
                "private_mapping_sha256": files.write_json(mapping),
                "status": mapping["status"],
            }
        else:
            saved = files.read_json(args.comparison_sha256)
            if saved.get("kind") != "comparison":
                raise ValueError("Expected a saved comparison record.")
            value = Comparison.model_validate(saved["value"])
            provenance = saved["provenance"]
            registered = registration(
                value.purpose,
                provenance["selection_id"],
                args.registration_commit,
                provenance["expected_profile"],
            )
            if registered != saved["registration"]:
                raise ValueError("Analysis and comparison registration differ.")
            ratings = Ratings.model_validate(_read(args.ratings))
            masked, _ = assessment(value)
            expected = {group["group_id"] for group in masked["groups"]}
            if {r.group_id for r in ratings.ratings} != expected:
                raise ValueError("Complete all selected ratings before unmasking the report.")
            # Persist the exact submission before calculating or revealing method scores.
            rating_digest = files.write_json(ratings.model_dump(mode="json"))
            result = analyse(value, ratings)
            output = {
                "ratings_sha256": rating_digest,
                "report_sha256": files.write_json(
                    {
                        "comparison_sha256": args.comparison_sha256,
                        "ratings_sha256": rating_digest,
                        "report": result,
                    }
                ),
                "status": result["status"],
            }
        print(json.dumps(output, indent=2))
        return 0
    except (
        ValueError,
        LookupError,
        OSError,
        KeyError,
        TypeError,
        subprocess.CalledProcessError,
    ) as error:
        print(f"Study comparison failed ({type(error).__name__}): {error}", file=sys.stderr)
        return 1


def _after_registration(registered, timestamp):
    if datetime.fromisoformat(timestamp) < datetime.fromisoformat(registered["registered_at"]):
        raise ValueError("Research execution predates its recorded registration.")


def _read(path):
    with path.open("rb") as stream:
        content = stream.read(32_000_001)
    if len(content) > 32_000_000:
        raise ValueError("Study input exceeds 32 MB.")
    return json.loads(content)


def _git(root, *args):
    return subprocess.run(
        ["git", "-c", f"safe.directory={root.as_posix()}", "-C", str(root), *args],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    ).stdout


if __name__ == "__main__":
    raise SystemExit(main())
