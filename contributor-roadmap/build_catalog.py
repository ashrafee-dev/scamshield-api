"""Build an explicit, validated issue manifest. This script never writes to GitHub."""
import importlib.util
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
spec = importlib.util.spec_from_file_location("briefs", HERE / "catalog-source.py")
briefs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(briefs)

snapshot = subprocess.check_output(
    ["git", "rev-parse", "origin/main"], cwd=ROOT, text=True,
).strip()

DEPENDENCIES = {
    "CLI-18": ["CLI-17"],
    "EVAL-09": ["EVAL-03"], "EVAL-10": ["EVAL-03"],
    "EVAL-11": ["EVAL-03"], "EVAL-12": ["EVAL-03"],
    "EVAL-13": ["EVAL-03"], "EVAL-14": ["EVAL-03"],
    "ARC-20": ["ARC-01", "ARC-16"],
    **{f"JOB-{i:02}": ["JOB-01"] for i in range(2, 21)},
}

entries = []
for area, (name, prefix, references, directory, kind, raw) in briefs.TRACKS.items():
    rows = [line.split("|") for line in raw.strip().splitlines()]
    if len(rows) != 20:
        raise ValueError(f"{area} has {len(rows)} issues, expected 20")
    for index, fields in enumerate(rows, 1):
        if len(fields) not in (5, 6):
            raise ValueError(f"Invalid fields: {fields}")
        code, slug, title, evidence, acceptance = fields[:5]
        issue_id = f"{prefix}-{index:02}"
        difficulty = {"1": "beginner", "2": "intermediate", "3": "advanced"}[code[1]]
        status = {"R": "ready", "D": "design-needed"}[code[0]]
        refs = references.split()
        for path in refs:
            if not (ROOT / path).is_file():
                raise ValueError(f"Missing source reference {path}")
        if kind == "pytest":
            output = f"{directory}/test_{slug.replace('-', '_')}.py"
            commands = [f"uv run pytest {output} -q", "uv run pylint app tests"]
            scope = f"Add the focused test file `{output}`. Change runtime code only if the acceptance criteria explicitly request a behavior fix; otherwise report newly discovered behavior separately."
        elif kind == "docs":
            output = f"{directory}/{slug}.md"
            commands = ["npm --prefix docs ci", "npm --prefix docs run build", "git diff --check"]
            scope = f"Write `{output}`; keep this contribution in its own page. Maintainers can add navigation links after merge to avoid concurrent sidebar edits."
        elif kind == "example":
            output = f"{directory}/{slug}/"
            commands = ["git diff --check"]
            scope = f"Keep the example and its README/test in `{output}`. Include its exact run and offline-test commands. Do not turn this example into a shared SDK."
        else:
            output = f"{directory}/{slug}.md"
            commands = ["git diff --check"]
            scope = f"First deliver a scoped design note at `{output}` covering the stated decision. Runtime or infrastructure implementation is not approved until maintainers accept the approach."
        if issue_id == "DOC-19":
            output = "README.md"
            scope = "Update only the concise API contract summary in `README.md`; link to existing canonical reference pages."
        entries.append({
            "id": issue_id, "area": area, "track": name, "title": title,
            "difficulty": difficulty, "status": status, "kind": kind,
            "evidence": evidence, "references": refs, "output": output,
            "scope": scope, "acceptance": acceptance.split("~"),
            "verification": commands,
            "implementation_prerequisites": DEPENDENCIES.get(issue_id, []),
            "existing_issue": int(fields[5]) if len(fields) == 6 else None,
        })

assert len(entries) == 300
assert len({item["id"] for item in entries}) == 300
assert len({item["title"].casefold() for item in entries}) == 300
assert all(len(item["acceptance"]) >= 3 for item in entries)
ids = {item["id"] for item in entries}
assert all(set(item["implementation_prerequisites"]) <= ids for item in entries)
assert all(not item["implementation_prerequisites"] for item in entries if item["status"] == "ready")
reused = [item["existing_issue"] for item in entries if item["existing_issue"]]
assert len(reused) == len(set(reused))
(HERE / "catalog.json").write_text(json.dumps({
    "schema_version": 1, "audited_revision": snapshot, "issues": entries,
}, indent=2) + "\n")
print(f"Validated {len(entries)} explicit briefs; {len(reused)} existing issues reused.")
print(f"Ready: {sum(x['status'] == 'ready' for x in entries)}; "
      f"ready beginners: {sum(x['status'] == 'ready' and x['difficulty'] == 'beginner' for x in entries)}")
