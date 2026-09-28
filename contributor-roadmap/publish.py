"""Validate locally or explicitly publish the audited roadmap through authenticated gh."""
import argparse
import json
from pathlib import Path
import subprocess
import time

HERE = Path(__file__).resolve().parent
REPO = "ashrafee-dev/scamshield-api"
BASE = f"https://github.com/{REPO}"
MARKER_PREFIX = "<!-- scamshield-roadmap:"


def gh(*args, payload=None):
    command = ["gh", *args]
    if payload is not None:
        command += ["--input", "-"]
    result = subprocess.run(
        command, input=json.dumps(payload) if payload is not None else None,
        text=True, capture_output=True, check=False, timeout=120,
    )
    if result.returncode:
        # Stop on ambiguous writes. A fresh invocation reconciles stable markers first.
        raise RuntimeError(f"GitHub operation failed; resume safely after inspection:\n{result.stderr}")
    return json.loads(result.stdout) if result.stdout.strip() else None


def marker(issue_id):
    return f"{MARKER_PREFIX}{issue_id} -->"


def labels_for(item):
    labels = ["contributor-roadmap", f"area:{item['area']}",
              f"difficulty:{item['difficulty']}", f"status:{item['status']}"]
    if item["status"] == "ready":
        labels.append("help wanted")
        if item["difficulty"] == "beginner":
            labels.append("good first issue")
    else:
        labels.append("question")
    if item["kind"] in ("docs", "decision", "evaluation"):
        labels.append("documentation")
    return labels


def render(item, revision, published, original=None):
    ready = item["status"] == "ready"
    intro = (
        "This is a focused contribution against current `main`. No unmerged feature PR is required."
        if ready else
        "This is a design proposal, not an approved runtime change or a beginner implementation task. "
        "Discuss the scope and compatibility with a maintainer first; it may be closed as not planned."
    )
    refs = "\n".join(
        f"- [`{path}`]({BASE}/blob/{revision}/{path})" for path in item["references"]
    )
    criteria = "\n".join(f"- [ ] {criterion}" for criterion in item["acceptance"])
    commands = "\n".join(item["verification"])
    prerequisite_ids = item["implementation_prerequisites"]
    prerequisites = "None. Keep the PR based on current upstream `main`."
    if prerequisite_ids:
        prerequisites = "Implementation requires these decisions first: " + ", ".join(
            f"{dep} (#{published[dep]['number']})" if dep in published else dep
            for dep in prerequisite_ids
        ) + ". The design discussion itself can proceed independently."
    testing_note = {
        "pytest": "Create the named focused test file before running its command. Tests must be deterministic, mock external services, and avoid paid calls. Run `bash scripts/check.sh` before submitting a Python change.",
        "docs": "Build the docs site locally. Verify the described commands against current source; explicitly report platform steps you could not execute. Do not run paid examples as a build check.",
        "example": "Include exact run and offline-test commands in the example README. Demonstrate success and a meaningful failure using a fake local service; do not contact the real paid API in tests.",
        "evaluation": "The first deliverable is a reviewable evaluation design. Validate examples locally with synthetic/replayed data; no benchmark accuracy or paid execution is implied by this issue.",
        "decision": "This command checks patch hygiene only, not design correctness. Review each decision criterion with a maintainer; validate any proposed config locally before it becomes an implementation task.",
    }[item["kind"]]
    body = f"""{marker(item['id'])}
## {item['id']} · {item['track']}

**Difficulty:** {item['difficulty']} · **Status:** {item['status']}

{intro}

### Why this is useful
{item['evidence']}

### Start here
Source audit: `{revision[:12]}`. Read these files on current `main` too, because paths may change after the audit:
{refs}

### Scope and intended output
{item['scope']}

### Acceptance criteria
{criteria}

### Verification
```sh
{commands}
```
{testing_note}

### Dependencies
{prerequisites}

### Out of scope
- Unrelated refactors, broad formatting, endpoint renames, or extra dependencies without agreement.
- Live cloud provisioning, paid model calls, real private messages, or credentials in fixtures/logs.
- Implementing neighboring roadmap issues in the same PR.

### Getting help and submitting
Comment with your intended approach and ask when expected behavior is unclear. Check for an existing PR before starting; there is no deadline for a volunteer contribution. A useful reproduction or partial finding is welcome.

Use the issue's criteria as the review checklist. Include the commands actually run and any limitations. Link the issue; use `Fixes` only when its entire agreed scope is complete. If `CONTRIBUTING.md` is not yet on main, the contributor-roadmap PR provides the onboarding guide.
"""
    if original:
        body += f"\n<details><summary>Original issue before the source audit (historical context)</summary>\n\n{original}\n\n</details>\n"
    return body


def load_plan():
    catalog = json.loads((HERE / "catalog.json").read_text())
    items = catalog["issues"]
    assert len(items) == 300
    assert len({item["id"] for item in items}) == 300
    assert len({item["title"].casefold() for item in items}) == 300
    for item in items:
        assert len(item["acceptance"]) >= 3 and item["references"] and item["verification"]
        if item["status"] == "ready":
            assert not item["implementation_prerequisites"]
        if "good first issue" in labels_for(item):
            assert item["status"] == "ready" and item["difficulty"] == "beginner"
    return catalog


def reconcile_markers(items, remote):
    published = {}
    for item in items:
        matches = [issue for issue in remote if marker(item["id"]) in (issue["body"] or "")]
        if len(matches) > 1:
            raise ValueError(f"Duplicate remote marker for {item['id']}; inspect before resuming")
        if matches:
            issue = matches[0]
            published[item["id"]] = {"number": issue["number"], "url": issue["url"]}
    return published


def write_index(items, published):
    lines = ["# GitHub issue index", "", "300 scoped opportunities; status labels on GitHub are authoritative.", ""]
    for track in dict.fromkeys(item["track"] for item in items):
        lines += [f"## {track}", "", "| ID | Issue | Difficulty | Initial status |", "| --- | --- | --- | --- |"]
        for item in (entry for entry in items if entry["track"] == track):
            link = published.get(item["id"], {})
            title = f"[{item['title']}]({link['url']})" if link else item["title"]
            lines.append(f"| {item['id']} | {title} | {item['difficulty']} | {item['status']} |")
        lines.append("")
    (HERE / "INDEX.md").write_text("\n".join(lines))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--publish", action="store_true")
    parser.add_argument("--delay", type=float, default=3.0)
    args = parser.parse_args()
    catalog = load_plan()
    items = catalog["issues"]
    snapshot = {item["number"]: item for item in json.loads((HERE / "existing-snapshot.json").read_text())}
    audit = json.loads((HERE / "existing-audit.json").read_text())
    reused = {item["existing_issue"] for item in items if item["existing_issue"]}
    closed = {int(number) for group in ("close_completed", "close_not_planned") for number in audit[group]}
    pending = {int(number) for number in audit["leave_for_contributor_pr"]}
    assert not reused & closed and reused | closed | pending == set(snapshot)
    bodies = {item["id"]: render(item, catalog["audited_revision"], {},
                               snapshot.get(item["existing_issue"], {}).get("body")) for item in items}
    assert all(len(body) < 60000 for body in bodies.values())
    print(f"Validated 300 issues: {len(reused)} reused, {300-len(reused)} new; {len(closed)} resolved old issues.", flush=True)
    if not args.publish:
        return
    if args.delay < 3:
        raise ValueError("Keep at least three seconds between writes to respect GitHub content limits")

    subprocess.run(["gh", "auth", "status"], check=True, capture_output=True, timeout=30)
    # Source of truth on resume: remote markers, not just a local checkpoint.
    remote = gh("issue", "list", "--repo", REPO, "--state", "all", "--limit", "2000",
                "--json", "number,title,body,url,state,labels")
    by_number = {issue["number"]: issue for issue in remote}
    published = reconcile_markers(items, remote)

    def write(endpoint, payload, method="POST"):
        result = gh("api", f"repos/{REPO}/{endpoint}", "--method", method, payload=payload)
        time.sleep(args.delay)
        return result

    def checkpoint():
        (HERE / "published.json").write_text(json.dumps(published, indent=2) + "\n")
        write_index(items, published)

    existing_labels = {label["name"] for label in gh("label", "list", "--repo", REPO, "--limit", "200", "--json", "name")}
    desired_labels = {
        "contributor-roadmap": ("Roadmap item with a scoped contributor brief", "1d76db"),
        "status:ready": ("Scoped work against main; no unmerged prerequisite", "0e8a16"),
        "status:design-needed": ("Discuss and approve the design before implementation", "fbca04"),
        "status:blocked": ("Wait for an explicit prerequisite before implementation", "b60205"),
        "difficulty:beginner": ("Small locally verifiable contribution with clear guidance", "c2e0c6"),
        "difficulty:intermediate": ("Requires familiarity with tests or a subsystem", "bfd4f2"),
        "difficulty:advanced": ("Architecture security concurrency or cloud experience needed", "d4c5f9"),
    }
    for item in items:
        desired_labels[f"area:{item['area']}"] = (item["track"], "c5def5")
    for name, (description, color) in desired_labels.items():
        if name not in existing_labels:
            write("labels", {"name": name, "description": description, "color": color})

    milestones = gh("api", f"repos/{REPO}/milestones?state=all&per_page=100")
    milestone_numbers = {entry["title"]: entry["number"] for entry in milestones}
    for item in items:
        title = f"Contributor roadmap: {item['track']}"
        if title not in milestone_numbers:
            created = write("milestones", {"title": title, "description":
                "Contributor work area, not a release deadline. Ready issues are actionable; design proposals require maintainer agreement."})
            milestone_numbers[title] = created["number"]

    for item in items:
        if item["id"] in published:
            continue  # Never overwrite a published issue that contributors may have edited.
        existing = by_number.get(item["existing_issue"])
        if item["existing_issue"] and (not existing or existing["state"] != "OPEN"):
            raise ValueError(f"Existing #{item['existing_issue']} changed state; reconcile before publishing")
        if existing and existing["body"] != snapshot[item["existing_issue"]]["body"]:
            raise ValueError(f"Existing #{item['existing_issue']} body changed since audit; preserve and review it")
        payload = {
            "title": item["title"],
            "body": render(item, catalog["audited_revision"], published, existing["body"] if existing else None),
            "labels": labels_for(item),
            "milestone": milestone_numbers[f"Contributor roadmap: {item['track']}"],
        }
        if existing:
            # Preserve useful preexisting labels; correct misleading newcomer/status labels.
            preserved = {label["name"] for label in existing["labels"]
                         if label["name"] not in {"good first issue", "help wanted"}
                         and not label["name"].startswith(("status:", "difficulty:", "area:"))}
            payload["labels"] = sorted(set(payload["labels"]) | preserved)
            result = write(f"issues/{existing['number']}", payload, "PATCH")
        else:
            result = write("issues", payload)
        published[item["id"]] = {"number": result["number"], "url": result["html_url"]}
        checkpoint()
        print(f"[{len(published)}/300] {item['id']} {result['html_url']}", flush=True)

    for group, reason in (("close_completed", "completed"), ("close_not_planned", "not_planned")):
        for number, evidence in audit[group].items():
            issue = by_number[int(number)]
            if issue["state"] == "CLOSED":
                continue
            if issue["body"] != snapshot[int(number)]["body"]:
                raise ValueError(f"Issue #{number} changed since audit; do not close automatically")
            note = (f"\n\n---\n### Maintainer source audit\n{evidence}\n\n"
                    f"Verified against `{catalog['audited_revision'][:12]}` after #86 and #88. "
                    "Closing the obsolete request so newcomers are not assigned already-resolved work. "
                    "The original report above is preserved.\n")
            write(f"issues/{number}", {"state": "closed", "state_reason": reason,
                                       "body": issue["body"] + note}, "PATCH")
            print(f"Reconciled existing issue #{number}: {reason}", flush=True)
    checkpoint()
    print("Published all 300 roadmap issues and reconciled existing issues.", flush=True)


if __name__ == "__main__":
    main()
