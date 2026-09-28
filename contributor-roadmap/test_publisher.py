"""Offline checks for the bulk publisher's consequential safeguards."""
import importlib.util
from pathlib import Path
import sys

import pytest

spec = importlib.util.spec_from_file_location("publisher", Path(__file__).with_name("publish.py"))
publisher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publisher)


def test_default_run_never_contacts_github(monkeypatch):
    def unexpected(*_args, **_kwargs):
        raise AssertionError("Dry run attempted a remote operation")
    monkeypatch.setattr(publisher, "gh", unexpected)
    monkeypatch.setattr(publisher.subprocess, "run", unexpected)
    monkeypatch.setattr(sys, "argv", ["publish.py"])
    publisher.main()


def test_resume_recognizes_closed_and_edited_issues():
    remote = [{"number": 123, "url": "https://example.com/123", "state": "CLOSED",
               "body": publisher.marker("TXT-01") + "\nContributor-edited acceptance criteria"}]
    result = publisher.reconcile_markers([{"id": "TXT-01"}], remote)
    assert result["TXT-01"]["number"] == 123


def test_duplicate_remote_marker_stops_instead_of_choosing_one():
    remote = [{"number": number, "url": f"https://example.com/{number}",
               "body": publisher.marker("TXT-01")} for number in (123, 124)]
    with pytest.raises(ValueError, match="Duplicate remote marker"):
        publisher.reconcile_markers([{"id": "TXT-01"}], remote)


def test_advanced_proposals_never_get_newcomer_labels():
    labels = publisher.labels_for({"area": "auth", "difficulty": "advanced",
                                   "status": "design-needed", "kind": "decision"})
    assert "good first issue" not in labels
    assert "help wanted" not in labels


def test_original_issue_is_preserved_and_dependencies_linked():
    catalog = publisher.load_plan()
    item = next(entry for entry in catalog["issues"] if entry["id"] == "CLI-18")
    body = publisher.render(item, catalog["audited_revision"],
                            {"CLI-17": {"number": 456}}, "Original acceptance criteria")
    assert "Original acceptance criteria" in body
    assert "CLI-17 (#456)" in body
    assert "not an approved runtime change" in body
