#!/usr/bin/env python3
"""Mechanical Double-Entry Review helpers; never execute models or remote writes.

Python 3.10+, standard library only. All output is JSON. See helper-usage.md.
These checks are not a sandbox, an approval mechanism, or a correctness proof.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Iterator

VERSION = "0.3.0-alpha.2"
METHOD_REVISION = 7
METHOD_SHA256 = "f4f01865a4ec5d9b9b88d1c475b076c221820eb89041ce0b0053ed5ae0661b04"
SKILL = Path(__file__).resolve().parents[1]
ID = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{0,79}$")
SHA = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")


class DERError(Exception):
    def __init__(self, message: str, code: int = 2):
        super().__init__(message)
        self.code = code


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def canonical(data: Any) -> bytes:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def digest(data: Any) -> str:
    return hashlib.sha256(canonical(data)).hexdigest()


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_json(path: str | Path) -> Any:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise DERError(f"Cannot read JSON {path}: {e}") from e


def write_new(path: Path, data: Any) -> None:
    """Create one file without overwriting; callers control their own private paths."""
    with path.open("x", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2, ensure_ascii=True)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())


def valid_id(value: str) -> str:
    if not ID.fullmatch(value) or value in (".", ".."):
        raise DERError(f"Unsafe identifier: {value!r}")
    return value


def ref_input(value: str) -> str:
    if not value or value.startswith("-") or any(ord(x) < 33 or ord(x) == 127 for x in value):
        raise DERError("Invalid ref: use a nonempty ref/SHA without whitespace/control characters")
    return value


def env() -> dict[str, str]:
    # Discard caller Git overrides, credentials/config injection and object replacements.
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
             GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0", GIT_PAGER="cat",
             GIT_NO_REPLACE_OBJECTS="1", GIT_NO_LAZY_FETCH="1", LC_ALL="C")
    return e


def process(argv: list[str], cwd: Path | None = None, timeout: int = 120) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(argv, cwd=cwd, env=env(), stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired) as e:
        raise DERError(f"Process failed: {argv[0]}: {e}") from e


class Git:
    def __init__(self, repo: str | Path):
        self.path = Path(repo).expanduser().resolve()
        if not self.path.is_dir():
            raise DERError(f"Repository directory does not exist: {self.path}")
        self.text("rev-parse", "--git-dir")

    def run(self, *args: str, allowed: tuple[int, ...] = (0,), timeout: int = 120) -> subprocess.CompletedProcess:
        p = process(["git", "--no-pager", "-c", "core.fsmonitor=false", "-c",
                     "core.untrackedCache=false", "-c", "core.hooksPath=" + os.devnull,
                     "-C", str(self.path), *args], timeout=timeout)
        if p.returncode not in allowed:
            raise DERError(f"git {args[0] if args else ''} failed ({p.returncode}): " +
                           p.stderr.decode("utf-8", "replace")[-3000:])
        return p

    def text(self, *args: str) -> str:
        return self.run(*args).stdout.decode("utf-8", "replace").strip()

    def commit(self, ref: str) -> str:
        return self.text("rev-parse", "--verify", "--end-of-options", ref_input(ref) + "^{commit}")

    def tree(self, sha: str) -> str:
        return self.text("rev-parse", "--verify", "--end-of-options", ref_input(sha) + "^{tree}")

    def ancestor(self, base: str, tip: str) -> bool:
        return self.run("merge-base", "--is-ancestor", base, tip, allowed=(0, 1)).returncode == 0


def status(g: Git) -> dict[str, Any]:
    bare = g.text("rev-parse", "--is-bare-repository") == "true"
    h = g.run("rev-parse", "--verify", "HEAD", allowed=(0, 128))
    if h.returncode:
        head = None
    else:
        head = h.stdout.decode().strip()
    b = g.run("symbolic-ref", "--quiet", "--short", "HEAD", allowed=(0, 1))
    result: dict[str, Any] = {"repository": str(g.path), "bare": bare, "head": head,
                             "branch": b.stdout.decode("utf-8", "replace").strip() or None}
    if bare:
        result.update(clean=None, changes=[])
        return result
    rows = g.run("status", "--porcelain=v1", "-z", "--untracked-files=all").stdout.split(b"\0")
    changes = []
    i = 0
    while i < len(rows) and rows[i]:
        row = rows[i]
        item = {"xy": row[:2].decode("ascii"), "path": os.fsdecode(row[3:])}
        if b"R" in row[:2] or b"C" in row[:2]:
            i += 1
            if i >= len(rows) or not rows[i]:
                raise DERError("Incomplete Git status rename record")
            item["original_path"] = os.fsdecode(rows[i])
        changes.append(item)
        i += 1
    result.update(clean=not changes, changes=changes,
                  tree=g.tree(head) if head else None)
    return result


def equivalence(g: Git, diary: str, semantic: str,
                diary_base: str | None = None, semantic_base: str | None = None) -> dict[str, Any]:
    if bool(diary_base) != bool(semantic_base):
        raise DERError("Supply both diary and semantic bases, or neither")
    d, s = g.commit(diary), g.commit(semantic)
    dt, st = g.tree(d), g.tree(s)
    diff = g.run("diff", "--no-ext-diff", "--no-textconv", "--no-renames", "--exit-code",
                 d, s, "--", allowed=(0, 1))
    result: dict[str, Any] = {
        "diary": {"tip": d, "tree": dt}, "semantic": {"tip": s, "tree": st},
        "trees_equal": dt == st, "direct_diff_exit_code": diff.returncode,
        "equal": dt == st and diff.returncode == 0,
        "scope": "tracked_snapshot_only", "verified_at": now(),
        "behavioural_verification": "not_run", "approval": "not_checked"}
    if diary_base and semantic_base:
        db, sb = g.commit(diary_base), g.commit(semantic_base)
        bt, bst = g.tree(db), g.tree(sb)
        result["base"] = {"diary_commit": db, "semantic_commit": sb,
                          "diary_tree": bt, "semantic_tree": bst,
                          "trees_equal": bt == bst,
                          "diary_is_ancestor": g.ancestor(db, d),
                          "semantic_is_ancestor": g.ancestor(sb, s)}
        result["equal"] = result["equal"] and bt == bst and all(
            result["base"][x] for x in ("diary_is_ancestor", "semantic_is_ancestor"))
    return result


def diff_stats(g: Git, base: str, tip: str) -> dict[str, Any]:
    raw = g.run("diff", "--no-ext-diff", "--no-textconv", "--no-renames", "--numstat", "-z",
                base, tip, "--").stdout
    files = []
    for row in raw.split(b"\0"):
        if not row:
            continue
        a, d, path = row.split(b"\t", 2)
        files.append({"path": os.fsdecode(path), "added": None if a == b"-" else int(a),
                      "deleted": None if d == b"-" else int(d)})
    return {"files": files, "file_count": len(files),
            "added": sum(x["added"] or 0 for x in files),
            "deleted": sum(x["deleted"] or 0 for x in files),
            "binary_files": sum(x["added"] is None for x in files)}


def inventory(g: Git, base: str, tip: str) -> dict[str, Any]:
    b, t = g.commit(base), g.commit(tip)
    if not g.ancestor(b, t):
        raise DERError("The recorded base is not an ancestor of the tip", 1)
    shas = g.text("rev-list", "--reverse", "--topo-order", f"{b}..{t}").splitlines()
    commits = []
    for c in shas:
        parents = g.text("rev-list", "--parents", "-n", "1", c).split()[1:]
        if not parents:
            raise DERError("Unexpected root in base-to-tip range")
        commits.append({"commit": c, "parents": parents, "tree": g.tree(c),
                        "subject": g.text("show", "-s", "--format=%s", c),
                        "change": diff_stats(g, parents[0], c)})
    return {"base": b, "tip": t, "tree": g.tree(t), "commits": commits,
            "linear": all(len(x["parents"]) == 1 for x in commits),
            "final_change": diff_stats(g, b, t),
            "statistics_note": "No rename detection; merge commit churn uses first parent. "
                               "Final diff and cumulative per-commit churn are different quantities."}


def schema_validate(data: Any, schema: dict[str, Any], path: str = "$") -> None:
    """Validate the limited JSON Schema vocabulary used by this package; no remote refs."""
    if "$ref" in schema:
        raise DERError("This validator does not resolve schema references")
    types = schema.get("type")
    if types:
        types = [types] if isinstance(types, str) else types
        checks = {"object": isinstance(data, dict), "array": isinstance(data, list),
                  "string": isinstance(data, str), "integer": type(data) is int,
                  "number": type(data) in (int, float), "boolean": type(data) is bool,
                  "null": data is None}
        if not any(checks.get(t, False) for t in types):
            raise DERError(f"{path}: expected type {types}")
    if "const" in schema and canonical(data) != canonical(schema["const"]):
        raise DERError(f"{path}: wrong constant")
    if "enum" in schema and data not in schema["enum"]:
        raise DERError(f"{path}: unsupported value {data!r}")
    if isinstance(data, dict):
        missing = set(schema.get("required", [])) - data.keys()
        if missing:
            raise DERError(f"{path}: missing fields {sorted(missing)}")
        props = schema.get("properties", {})
        if schema.get("additionalProperties") is False and (set(data) - props.keys()):
            raise DERError(f"{path}: unexpected fields {sorted(set(data) - props.keys())}")
        for key, value in data.items():
            if key in props:
                schema_validate(value, props[key], f"{path}.{key}")
    if isinstance(data, list):
        if len(data) < schema.get("minItems", 0):
            raise DERError(f"{path}: too few items")
        if schema.get("uniqueItems") and len({canonical(x) for x in data}) != len(data):
            raise DERError(f"{path}: duplicate items")
        for i, value in enumerate(data):
            if "items" in schema:
                schema_validate(value, schema["items"], f"{path}[{i}]")
    if isinstance(data, str):
        if len(data) < schema.get("minLength", 0) or len(data) > schema.get("maxLength", 10**9):
            raise DERError(f"{path}: string length outside bounds")
        if "pattern" in schema and not re.search(schema["pattern"], data):
            raise DERError(f"{path}: invalid string format")
    if type(data) in (int, float):
        if data < schema.get("minimum", float("-inf")) or data > schema.get("maximum", float("inf")):
            raise DERError(f"{path}: number outside bounds")


def validate(data: Any, name: str) -> None:
    schema_validate(data, load_json(SKILL / "assets" / "schemas" / f"{name}.schema.json"))


def no_symlinks(path: Path) -> Path:
    p = Path(os.path.abspath(path.expanduser()))
    for parent in [p, *p.parents]:
        if parent.is_symlink():
            raise DERError(f"Refusing symlinked output path: {parent}")
    return p


def external_store(value: str, g: Git | None = None) -> Path:
    if not Path(value).expanduser().is_absolute():
        raise DERError("Evidence store must be an explicit absolute path")
    # Canonicalise only after rejecting symlinked path components. On Windows,
    # this also expands short 8.3 names so they compare correctly with the
    # canonical paths returned by Git.
    store = no_symlinks(Path(value)).resolve()
    if g:
        blocked = [Path(g.text("rev-parse", "--path-format=absolute", "--git-common-dir"))]
        if g.text("rev-parse", "--is-bare-repository") != "true":
            blocked.append(Path(g.text("rev-parse", "--show-toplevel")))
            records = g.run("worktree", "list", "--porcelain", "-z").stdout.split(b"\0")
            blocked.extend(Path(os.fsdecode(x[len(b"worktree "):])) for x in records
                           if x.startswith(b"worktree "))
        for root in blocked:
            root = root.resolve()
            if store == root or root in store.parents:
                raise DERError(f"Evidence store must be outside application worktrees and Git metadata: {root}")
    return store


@contextmanager
def locked(directory: Path, filename: str) -> Iterator[None]:
    directory.mkdir(parents=True, exist_ok=True)
    lock = no_symlinks(directory / filename)
    try:
        fd = os.open(str(lock), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as e:
        raise DERError(f"Occupied lock {lock}; inspect ownership before recovery", 3) from e
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(json.dumps({"pid": os.getpid(), "created_at": now()}))
            f.flush()
            os.fsync(f.fileno())
        yield
    finally:
        lock.unlink()


def init_bare(path: Path, object_format: str) -> Git:
    if object_format not in ("sha1", "sha256"):
        raise DERError("Unsupported object format")
    p = process(["git", "init", "--bare", "--quiet", f"--object-format={object_format}", str(path)])
    if p.returncode:
        raise DERError(p.stderr.decode("utf-8", "replace"))
    return Git(path)


def snapshot(args: argparse.Namespace) -> dict[str, Any]:
    g = Git(args.repo)
    store = external_store(args.store, g)
    pair, rnd = valid_id(args.pair), valid_id(args.round)
    if g.text("rev-parse", "--is-shallow-repository") == "true":
        raise DERError("A shallow source cannot provide this release's self-contained archive")
    eq = equivalence(g, args.diary, args.semantic, args.diary_base, args.semantic_base)
    if not eq["equal"]:
        raise DERError("Snapshot refused: pair/base equivalence or ancestry failed", 1)
    inv = inventory(g, eq["base"]["semantic_commit"], eq["semantic"]["tip"])
    if not inv["linear"]:
        raise DERError("Semantic range contains merge commits; inspect diary/archive ancestry", 1)
    pairdir = no_symlinks(store / "pairs" / pair)
    with locked(pairdir, ".snapshot.lock"):
        rounds = no_symlinks(pairdir / "rounds")
        rounds.mkdir(exist_ok=True)
        final = no_symlinks(rounds / rnd)
        if final.exists():
            raise DERError("Round already exists; reuse it or choose a new round ID")
        stage = Path(tempfile.mkdtemp(prefix=f".{rnd}.partial-", dir=rounds))
        try:
            fmt = g.text("rev-parse", "--show-object-format")
            with tempfile.TemporaryDirectory(prefix="der-bare-") as td:
                bare = init_bare(Path(td) / "archive.git", fmt)
                refs = {"refs/heads/diary-base": eq["base"]["diary_commit"],
                        "refs/heads/semantic-base": eq["base"]["semantic_commit"],
                        "refs/heads/diary": eq["diary"]["tip"],
                        "refs/heads/semantic": eq["semantic"]["tip"]}
                bare.run("-c", "protocol.file.allow=always", "fetch", "--no-tags",
                         "--no-recurse-submodules", "--no-write-fetch-head", str(g.path),
                         *[f"{sha}:{ref}" for ref, sha in refs.items()], timeout=600)
                bundle = stage / "history.bundle"
                bare.run("bundle", "create", str(bundle), "--all", timeout=600)
                bare.run("bundle", "verify", str(bundle), timeout=600)
            manifest = {
                "schema_version": 1, "skill_version": VERSION, "method_revision": METHOD_REVISION,
                "method_sha256": METHOD_SHA256, "stage": "archived_candidate",
                "pair_id": pair, "round_id": rnd, "created_at": now(), "object_format": fmt,
                "base": {"diary_commit": eq["base"]["diary_commit"],
                         "semantic_commit": eq["base"]["semantic_commit"],
                         "shared_tree": eq["base"]["diary_tree"]},
                "diary": eq["diary"], "semantic": eq["semantic"],
                "semantic_commits": [c["commit"] for c in inv["commits"]],
                "equivalence": {"trees_equal": True, "direct_diff_exit_code": 0},
                "bundle": {"file": "history.bundle", "sha256": file_hash(bundle), "refs": refs},
                "verification": "not_attested", "approval": "not_attested",
                "publication": "not_attested", "integration": "not_attested"}
            validate(manifest, "round")
            write_new(stage / "manifest.json", manifest)
            write_new(stage / "inventory.json", inv)
            # Destination is unique, and all cooperating writers use the same lock.
            stage.rename(final)
        except Exception:
            # This is only our private staging path, never an application worktree.
            shutil.rmtree(stage, ignore_errors=True)
            raise
    return {"manifest": str(final / "manifest.json"),
            "manifest_sha256": file_hash(final / "manifest.json"),
            "stage": "archived_candidate", "bundle_sha256": manifest["bundle"]["sha256"],
            "note": "Local archive only; behavioural verification, durable replication and approval are separate."}


def check_round(manifest_path: str) -> dict[str, Any]:
    p = Path(manifest_path).resolve()
    data = load_json(p)
    validate(data, "round")
    bundle = p.parent / data["bundle"]["file"]
    if bundle.is_symlink() or not bundle.is_file() or file_hash(bundle) != data["bundle"]["sha256"]:
        raise DERError("Bundle missing, symlinked, or digest mismatch", 1)
    expected_refs = {"refs/heads/diary-base": data["base"]["diary_commit"],
                     "refs/heads/semantic-base": data["base"]["semantic_commit"],
                     "refs/heads/diary": data["diary"]["tip"],
                     "refs/heads/semantic": data["semantic"]["tip"]}
    if data["bundle"]["refs"] != expected_refs:
        raise DERError("Bundle ref map is inconsistent with round identity", 1)
    with tempfile.TemporaryDirectory(prefix="der-check-") as td:
        g = init_bare(Path(td) / "check.git", data["object_format"])
        g.run("bundle", "verify", str(bundle), timeout=600)
        heads = dict((line.split(" ", 1)[1], line.split(" ", 1)[0]) for line in
                     g.text("bundle", "list-heads", str(bundle)).splitlines())
        if heads != expected_refs:
            raise DERError("Actual bundle refs differ from manifest", 1)
        g.run("-c", "protocol.file.allow=always", "fetch", "--no-tags", "--no-write-fetch-head",
              str(bundle), *[f"{r}:{r}" for r in expected_refs], timeout=600)
        eq = equivalence(g, data["diary"]["tip"], data["semantic"]["tip"],
                         data["base"]["diary_commit"], data["base"]["semantic_commit"])
        actual = inventory(g, data["base"]["semantic_commit"], data["semantic"]["tip"])
        if (not eq["equal"] or eq["diary"]["tree"] != data["diary"]["tree"] or
            eq["semantic"]["tree"] != data["semantic"]["tree"] or
            eq["base"]["diary_tree"] != data["base"]["shared_tree"] or
            not actual["linear"] or
            [c["commit"] for c in actual["commits"]] != data["semantic_commits"]):
            raise DERError("Archived objects do not match recorded round content/sequence", 1)
    return {"valid": True, "pair_id": data["pair_id"], "round_id": data["round_id"],
            "manifest_sha256": file_hash(p), "scope": "archive_identity_and_equivalence_only"}


def validate_review(manifest_path: str, report_path: str) -> dict[str, Any]:
    m, r = load_json(manifest_path), load_json(report_path)
    validate(m, "round")
    validate(r, "review")
    for key in ("pair_id", "round_id"):
        if m[key] != r[key]:
            raise DERError(f"Review is bound to a different {key}", 1)
    if r["manifest_sha256"] != file_hash(Path(manifest_path)) or r["semantic_tip"] != m["semantic"]["tip"]:
        raise DERError("Stale review: manifest digest or semantic tip differs", 1)
    actual = m["semantic_commits"]
    reviewed = r["reviewed_commits"]
    if any(c not in actual for c in reviewed) or len(set(reviewed)) != len(reviewed):
        raise DERError("Review contains duplicate or out-of-scope commit IDs", 1)
    if r["mode"] == "full" and r["status"] == "complete":
        if reviewed != actual or not r["orientation_done"] or not r["aggregate_done"]:
            raise DERError("Complete full review requires ordered commit coverage, orientation and aggregate pass", 1)
    if r["mode"] in ("commit", "next") and len(reviewed) > 1:
        raise DERError("Single-unit review claims more than one reviewed commit", 1)
    if r["mode"] in ("commit", "next") and r["status"] == "complete" and len(reviewed) != 1:
        raise DERError("Complete single-unit review must identify its commit", 1)
    if r["status"] == "complete" and not r["orientation_done"]:
        raise DERError("Even a complete scoped review needs overall orientation", 1)
    if r["mode"] == "aggregate" and r["status"] == "complete" and not r["aggregate_done"]:
        raise DERError("Aggregate review cannot complete without the aggregate pass", 1)
    for finding in r["findings"]:
        if finding["commit"] not in actual and finding["commit"] != m["semantic"]["tip"]:
            raise DERError("Finding refers to a commit outside the recorded series", 1)
    return {"valid": True, "mode": r["mode"], "status": r["status"],
            "scope": "report_shape_identity_and_claimed_coverage_only",
            "full_review_claim": r["mode"] == "full" and r["status"] == "complete",
            "platform_approval": False, "execution_truth_verified": False}


def ledger_read(pairdir: Path) -> tuple[list[dict[str, Any]], str | None]:
    d = pairdir / "events"
    if not d.exists():
        return [], None
    if d.is_symlink():
        raise DERError("Symlinked ledger refused")
    files = sorted(d.glob("*.json"))
    previous = None
    events = []
    for i, p in enumerate(files, 1):
        if p.name != f"{i:08d}.json" or p.is_symlink():
            raise DERError("Event sequence gap/unexpected file or symlink", 1)
        data = load_json(p)
        validate(data, "event")
        body = {k: v for k, v in data.items() if k != "event_hash"}
        if (data["sequence"] != i or data["previous_hash"] != previous or
            data["pair_id"] != pairdir.name or data["event_hash"] != digest(body)):
            raise DERError("Event chain integrity mismatch", 1)
        previous = data["event_hash"]
        events.append(data)
    return events, previous


def record(args: argparse.Namespace) -> dict[str, Any]:
    store = external_store(args.store, Git(args.repo) if args.repo else None)
    pair = valid_id(args.pair)
    pairdir = no_symlinks(store / "pairs" / pair)
    entry = load_json(args.event)
    validate(entry, "event-input")
    expected = None if args.expected_last == "none" else args.expected_last
    if expected is not None and not re.fullmatch(r"[0-9a-f]{64}", expected):
        raise DERError("Expected predecessor must be 'none' or a full SHA-256 digest")
    with locked(pairdir, ".record.lock"):
        events, previous = ledger_read(pairdir)
        if expected != previous:
            raise DERError("Stale event predecessor; re-read ledger and reconcile", 3)
        data = {"schema_version": 1, "sequence": len(events) + 1, "pair_id": pair,
                "recorded_at": now(), "previous_hash": previous, **entry}
        data["event_hash"] = digest(data)
        validate(data, "event")
        dest = no_symlinks(pairdir / "events")
        dest.mkdir(exist_ok=True)
        p = dest / f"{data['sequence']:08d}.json"
        tmp = dest / f".{data['sequence']:08d}.{os.getpid()}.pending"
        try:
            write_new(tmp, data)
            os.link(tmp, p)  # atomic publish, refuses an existing destination
        finally:
            if tmp.exists():
                tmp.unlink()
    return {"event": str(p), "event_hash": data["event_hash"], "sequence": data["sequence"],
            "note": "Recorded assertion with provenance; not independent validation or authority."}


ROUTES = {
    "status": ["state-and-evidence.md"], "prepare": ["setup-and-diary.md"],
    "work": ["setup-and-diary.md"], "plan": ["boundary-design.md"],
    "reconstruct": ["reconstruction.md"], "verify": ["verification.md"],
    "review": ["reviewing.md"], "revise": ["review-rounds.md", "test-evidence.md"],
    "round": ["review-rounds.md"], "integrate": ["integration.md"],
    "evidence": ["state-and-evidence.md"], "handoff": ["state-and-evidence.md"]}


def route(words: list[str]) -> dict[str, Any]:
    if not words or words == ["help"]:
        return {"operation": "help", "operations": list(ROUTES), "execute": False}
    command = words[0]
    if command not in ROUTES:
        raise DERError(f"Unknown skill operation {command!r}; no action taken")
    modules = ROUTES[command].copy()
    mode = words[1] if len(words) > 1 else None
    deprecated_alias = False
    modes = {"verify": ("all", "equivalence", "checkpoints", "tip"),
             "review": ("full", "next", "commit", "aggregate", "boundaries", "tests", "changes"),
             "round": ("prepare", "publish"), "integrate": ("check", "execute", "record"),
             "evidence": ("collect", "export")}
    if command in modes:
        mode = mode or ({"verify": "all", "review": "full"}.get(command))
        if mode not in modes[command]:
            raise DERError(f"Choose a {command} mode: {', '.join(modes[command])}")
    if command == "prepare":
        if words[1:] not in (["--until", "locally-prepared"], ["--until", "review-ready"]):
            raise DERError("Use prepare --until locally-prepared; automatic publication is not supported")
        deprecated_alias = words[2] == "review-ready"
        mode = "locally-prepared"
    if command == "review" and mode == "commit" and len(words) < 3:
        raise DERError("review commit requires a proposition ID or SHA")
    if command == "review" and mode == "changes":
        if len(words) != 6 or words[2] != "--from" or words[4] != "--to":
            raise DERError("Use review changes --from <round> --to <round>")
    if command == "review" and mode == "tests":
        modules.append("test-evidence.md")
    if command == "review" and mode == "boundaries":
        modules.append("boundary-design.md")
    if command == "review" and mode == "changes":
        modules.append("review-rounds.md")
    remote = (command, mode) in (("round", "publish"), ("integrate", "execute"))
    if remote:
        modules.append("host-operations.md")
    result = {"operation": command, "mode": mode, "references": ["references/" + m for m in modules],
              "remote_authority_required": remote, "execute": False}
    if command == "prepare":
        result["deprecated_alias"] = deprecated_alias
    return result


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--version", action="version", version=VERSION)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("doctor")
    q = sub.add_parser("status"); q.add_argument("--repo", required=True)
    q = sub.add_parser("equivalence")
    for f in ("repo", "diary", "semantic"):
        q.add_argument("--" + f, required=True)
    for f in ("diary-base", "semantic-base"):
        q.add_argument("--" + f)
    q = sub.add_parser("inventory")
    for f in ("repo", "base", "tip"):
        q.add_argument("--" + f, required=True)
    q = sub.add_parser("snapshot")
    for f in ("repo", "store", "pair", "round", "diary-base", "semantic-base", "diary", "semantic"):
        q.add_argument("--" + f, required=True)
    q = sub.add_parser("check-round"); q.add_argument("--manifest", required=True)
    q.add_argument("--repo", help="Optional current checkout; archive validation does not modify it")
    q = sub.add_parser("validate-review")
    q.add_argument("--manifest", required=True); q.add_argument("--report", required=True)
    q = sub.add_parser("record")
    for f in ("store", "pair", "event", "expected-last"):
        q.add_argument("--" + f, required=True)
    q.add_argument("--repo", required=True, help="Reject evidence paths inside any application worktree")
    q = sub.add_parser("ledger")
    q.add_argument("--store", required=True); q.add_argument("--pair", required=True)
    q = sub.add_parser("route"); q.add_argument("words", nargs=argparse.REMAINDER)
    return p


def main(argv: list[str] | None = None) -> int:
    try:
        args = parser().parse_args(argv)
        code = 0
        if args.cmd == "doctor":
            result = {"version": VERSION, "python": sys.version.split()[0],
                      "git": process(["git", "--version"]).stdout.decode().strip(),
                      "clients": {k: shutil.which(k) for k in ("codex", "opencode", "claude")},
                      "note": "Availability only; no live client or model validation."}
        elif args.cmd == "status":
            result = status(Git(args.repo))
        elif args.cmd == "equivalence":
            result = equivalence(Git(args.repo), args.diary, args.semantic, args.diary_base, args.semantic_base)
            code = 0 if result["equal"] else 1
        elif args.cmd == "inventory":
            result = inventory(Git(args.repo), args.base, args.tip)
        elif args.cmd == "snapshot":
            result = snapshot(args)
        elif args.cmd == "check-round":
            result = check_round(args.manifest)
            if args.repo:
                result["current_checkout"] = status(Git(args.repo))
        elif args.cmd == "validate-review":
            result = validate_review(args.manifest, args.report)
        elif args.cmd == "record":
            result = record(args)
        elif args.cmd == "ledger":
            pairdir = no_symlinks(external_store(args.store) / "pairs" / valid_id(args.pair))
            events, tip = ledger_read(pairdir)
            result = {"valid": True, "pair_id": args.pair, "event_count": len(events), "last_hash": tip}
        else:
            result = route(args.words)
        print(json.dumps(result, indent=2, ensure_ascii=True))
        return code
    except DERError as e:
        print(json.dumps({"error": str(e), "exit_code": e.code}, ensure_ascii=True))
        return e.code
    except (OSError, ValueError, KeyError) as e:
        print(json.dumps({"error": f"{type(e).__name__}: {e}", "exit_code": 2}, ensure_ascii=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
