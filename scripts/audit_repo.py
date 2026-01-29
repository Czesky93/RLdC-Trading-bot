#!/usr/bin/env python3
import ast
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List, Dict, Set, Tuple


ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

EXCLUDE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "__pycache__",
}

PLACEHOLDER_TOKENS = [
    "your_email@example.com",
    "your_password",
    "GOOGLE_CLIENT_ID",
    "GOOGLE_CLIENT_SECRET",
]

README_FILE_REFERENCES = [
    "docs/SETUP_UBUNTU.md",
    "installer.py",
    "master_ai_trader.py",
    "web_portal.py",
    "ai_optimizer.py",
    "rldc_quantum_ai.py",
    "demo_trading.py",
    "telegram_ai_bot.py",
    "zordon_ai.py",
    "ultimate_ai.py",
]


def iter_python_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*.py"):
        if any(part in EXCLUDE_DIRS for part in path.parts):
            continue
        yield path


def parse_imports(tree: ast.AST) -> Dict[str, Set[str]]:
    imports: Dict[str, Set[str]] = {"modules": set(), "aliases": set()}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports["modules"].add(alias.name)
                if alias.asname:
                    imports["aliases"].add(alias.asname)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports["modules"].add(node.module)
    return imports


def detect_top_level_calls(tree: ast.AST) -> List[str]:
    calls = []
    for node in tree.body:
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            calls.append(ast.unparse(node.value) if hasattr(ast, "unparse") else "call()")
    return calls


def scan_missing_imports(tree: ast.AST, imports: Dict[str, Set[str]]) -> List[str]:
    used_roots: Set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            used_roots.add(node.value.id)

    alias_to_module = {
        "pd": "pandas",
        "np": "numpy",
    }
    direct_modules = {
        "os",
        "json",
        "requests",
        "tweepy",
        "telepot",
        "ta",
        "gym",
        "pyotp",
    }

    missing = []
    for root in used_roots:
        module = alias_to_module.get(root, root)
        if module in direct_modules or root in alias_to_module:
            if module not in imports["modules"] and root not in imports["aliases"]:
                missing.append(module)
    return sorted(set(missing))


def scan_placeholders(source: str) -> List[str]:
    return [token for token in PLACEHOLDER_TOKENS if token in source]


def scan_config_json_reference(source: str) -> bool:
    return "config.json" in source


def collect_issues() -> Tuple[List[Dict], List[str]]:
    issues = []
    config_json_files = list(ROOT.glob("**/config.json"))
    has_config_json = len(config_json_files) > 0
    top_level_calls_summary = []
    self_path = Path(__file__).resolve()

    for file_path in iter_python_files(ROOT):
        if file_path.resolve() == self_path:
            continue
        source = file_path.read_text(encoding="utf-8", errors="ignore")
        try:
            tree = ast.parse(source)
        except SyntaxError as exc:
            issues.append(
                {
                    "file": str(file_path.relative_to(ROOT)),
                    "type": "syntax_error",
                    "detail": str(exc),
                }
            )
            continue

        imports = parse_imports(tree)
        missing_imports = scan_missing_imports(tree, imports)
        if missing_imports:
            issues.append(
                {
                    "file": str(file_path.relative_to(ROOT)),
                    "type": "missing_imports",
                    "detail": missing_imports,
                }
            )

        placeholders = scan_placeholders(source)
        if placeholders:
            issues.append(
                {
                    "file": str(file_path.relative_to(ROOT)),
                    "type": "placeholder_tokens",
                    "detail": placeholders,
                }
            )

        if scan_config_json_reference(source) and not has_config_json:
            issues.append(
                {
                    "file": str(file_path.relative_to(ROOT)),
                    "type": "missing_config_json",
                    "detail": "config.json referenced but not found in repo",
                }
            )

        top_level_calls = detect_top_level_calls(tree)
        if top_level_calls:
            top_level_calls_summary.append(
                {
                    "file": str(file_path.relative_to(ROOT)),
                    "calls": top_level_calls,
                }
            )

    missing_files = []
    for file_ref in README_FILE_REFERENCES:
        if not (ROOT / file_ref).exists():
            missing_files.append(file_ref)

    if missing_files:
        issues.append(
            {
                "file": "README.md",
                "type": "missing_referenced_files",
                "detail": missing_files,
            }
        )

    return issues, top_level_calls_summary


def render_markdown(issues: List[Dict], top_level_calls: List[Dict]) -> str:
    lines = []
    lines.append("# RLdC Repo Audit Report")
    lines.append("")
    lines.append(f"Generated: {datetime.now(timezone.utc).isoformat()}")
    lines.append("")
    if not issues:
        lines.append("✅ No issues detected by heuristic checks.")
        return "\n".join(lines)

    lines.append("## Issues")
    for issue in issues:
        lines.append(f"- **{issue['type']}** in `{issue['file']}`: {issue['detail']}")

    if top_level_calls:
        lines.append("")
        lines.append("## Top-level calls (possible side effects on import)")
        for entry in top_level_calls:
            calls_preview = ", ".join(entry["calls"])
            lines.append(f"- `{entry['file']}`: {calls_preview}")

    return "\n".join(lines)


def main() -> int:
    issues, top_level_calls = collect_issues()
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "issues": issues,
        "top_level_calls": top_level_calls,
    }
    json_path = REPORTS_DIR / "audit_report.json"
    md_path = REPORTS_DIR / "audit_report.md"
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    md_path.write_text(render_markdown(issues, top_level_calls), encoding="utf-8")
    print(f"Wrote {json_path} and {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
