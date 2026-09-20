"""Deterministic typed architecture data from declared contracts and Python metadata."""

import ast
import hashlib
import importlib.util
import json
import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Module:
    """A Python module and its top-level definitions, with a repository-relative path."""

    name: str
    path: str
    package: bool
    definitions: tuple[str, ...]


@dataclass(frozen=True)
class Interface:
    """A public declaration's static signature, bases or annotated field shape.

    Names are module-qualified. Syntax is normalised with ast.unparse; inherited
    and dynamically created members are not inferred. Constructors are included.
    """

    name: str
    kind: str
    declaration: str


def interfaces(tree: ast.Module, module: str) -> tuple[Interface, ...]:
    """Extract public declarations without evaluating annotations or importing code."""
    values = []

    def visit(nodes: list[ast.stmt], owner: str) -> None:
        for node in nodes:
            name = getattr(node, "name", None)
            if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                name = node.target.id
            if not name or (name.startswith("_") and name != "__init__"):
                continue
            qualified = f"{owner}.{name}"
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
                returns = f" -> {ast.unparse(node.returns)}" if node.returns else ""
                decorators = "".join(f"@{ast.unparse(item)} " for item in node.decorator_list)
                declaration = f"{decorators}{prefix} {name}({ast.unparse(node.args)}){returns}"
                values.append(Interface(qualified, "callable", declaration))
            elif isinstance(node, ast.ClassDef):
                bases = [ast.unparse(item) for item in (*node.bases, *node.keywords)]
                values.append(Interface(qualified, "class", f"class {name}({', '.join(bases)})"))
                visit(node.body, qualified)
            elif isinstance(node, ast.AnnAssign):
                values.append(Interface(qualified, "field", ast.unparse(node)))

    visit(tree.body, module)
    return tuple(sorted(values, key=lambda item: (item.name, item.declaration)))


@dataclass(frozen=True)
class Import:
    """A static import from a source module to a resolved target module."""

    source: str
    target: str


@dataclass(frozen=True)
class Boundary:
    """A declared Tach module and its permitted module dependencies."""

    name: str
    allowed_dependencies: tuple[str, ...]


@dataclass(frozen=True)
class Contract:
    """An Import Linter declaration, retaining fields relevant to its contract kind."""

    name: str
    kind: str
    modules: tuple[str, ...]
    sources: tuple[str, ...]
    forbidden: tuple[str, ...]


@dataclass(frozen=True)
class Snapshot:
    """Versioned architecture declarations and static Python metadata.

    Ordering is deterministic for unchanged input. This describes declared rules
    and syntax; it is not proof that architecture checks have passed.
    """

    schema_version: int
    source_digest: str
    source_roots: tuple[str, ...]
    root_module: str
    forbid_cycles: bool
    ignore_type_checking_imports: bool
    boundaries: tuple[Boundary, ...]
    contracts: tuple[Contract, ...]
    modules: tuple[Module, ...]
    imports: tuple[Import, ...]
    interfaces: tuple[Interface, ...]


def snapshot(root: Path) -> Snapshot:
    """Inspect architecture declarations and Python syntax without imports.

    Args:
        root: Project checkout containing tach.toml, pyproject.toml and source roots.

    Returns:
        A deterministic snapshot with repository-relative paths and no capture time.
        Imports include nested and type-checking blocks; dynamic imports are absent.
        Reading declarations does not execute or validate their architecture checks.
    """
    tach = tomllib.loads((root / "tach.toml").read_text(encoding="utf-8"))
    project = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    modules = []
    imports = set()
    declarations = []
    for source_root in tach["source_roots"]:
        source = root / source_root
        for path in sorted(source.rglob("*.py")):
            relative = path.relative_to(source).with_suffix("")
            package = relative.name == "__init__"
            name = ".".join(relative.parts[:-1] if package else relative.parts)
            tree = ast.parse(path.read_text(encoding="utf-8"))
            declarations.extend(interfaces(tree, name))
            modules.append(
                Module(
                    name,
                    path.relative_to(root).as_posix(),
                    package,
                    tuple(
                        sorted(
                            node.name
                            for node in tree.body
                            if isinstance(
                                node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
                            )
                        )
                    ),
                )
            )
            # Include nested and type-checking imports; dynamic imports are outside this snapshot.
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.update((name, alias.name) for alias in node.names)
                elif isinstance(node, ast.ImportFrom):
                    target = "." * node.level + (node.module or "")
                    if node.level:
                        target = importlib.util.resolve_name(
                            target, name if package else name.rpartition(".")[0]
                        )
                    imports.add((name, target))
    return Snapshot(
        3,
        source_fingerprint(root),
        tuple(tach["source_roots"]),
        tach["root_module"],
        tach["forbid_circular_dependencies"],
        tach["ignore_type_checking_imports"],
        tuple(Boundary(item["path"], tuple(item["depends_on"])) for item in tach["modules"]),
        tuple(
            Contract(
                item["name"],
                item["type"],
                tuple(item.get("modules", [])),
                tuple(item.get("source_modules", [])),
                tuple(item.get("forbidden_modules", [])),
            )
            for item in project["tool"]["importlinter"]["contracts"]
        ),
        tuple(modules),
        tuple(Import(*edge) for edge in sorted(imports)),
        tuple(declarations),
    )


def delta(before: dict, after: dict) -> dict:
    """Compare architecture snapshots using complete record identity.

    Args:
        before: Earlier snapshot serialised as a mapping.
        after: Later snapshot using the same schema version.

    Returns:
        Sorted removals and additions for changed records, plus old/new settings.
        A changed record appears in both lists; no rename or move is inferred.

    Raises:
        ValueError: The snapshot schema versions differ.
    """
    if before["schema_version"] != after["schema_version"]:
        raise ValueError("Architecture schema versions must match.")
    changes = {}
    for key in ("boundaries", "contracts", "modules", "imports", "interfaces"):
        if key not in before and key not in after:
            continue  # Retain comparison of archived schema-1 snapshots.
        old = {json.dumps(item, sort_keys=True) for item in before[key]}
        new = {json.dumps(item, sort_keys=True) for item in after[key]}
        changes[key] = {
            "removed": [json.loads(item) for item in sorted(old - new)],
            "added": [json.loads(item) for item in sorted(new - old)],
        }
    settings = ("source_roots", "root_module", "forbid_cycles", "ignore_type_checking_imports")
    changes["settings"] = {
        key: {"before": before[key], "after": after[key]}
        for key in settings
        if before[key] != after[key]
    }
    return {"schema_version": before["schema_version"], "changes": changes}


def source_fingerprint(root: Path) -> str:
    """Identify exact declared source/config/lock content, normalising checkout newlines.

    Include file names to detect moves/additions/removals and all Python bodies to
    detect behaviour-only changes absent from the static dependency projection.
    """
    tach = tomllib.loads((root / "tach.toml").read_text(encoding="utf-8"))
    paths = {root / name for name in ("tach.toml", "pyproject.toml", "uv.lock")}
    for source in tach["source_roots"]:
        paths.update(
            path
            for path in (root / source).rglob("*")
            if path.suffix in {".py", ".sql", ".html", ".css", ".js"}
        )
    paths.update(
        path for path in (root / "config").rglob("*") if path.suffix in {".json", ".yaml", ".toml"}
    )
    digest = hashlib.sha256()
    for path in sorted(paths):
        digest.update(path.relative_to(root).as_posix().encode() + b"\0")
        digest.update(path.read_text(encoding="utf-8").encode() + b"\0")
    return digest.hexdigest()
