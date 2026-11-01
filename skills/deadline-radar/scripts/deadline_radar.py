#!/usr/bin/env python3
"""Compares upcoming deadlines with recent commits in a public GitHub repository.

Standard library only. Reads a local JSON file and, if a repository is named, makes one
unauthenticated request to the public GitHub API. Prints JSON. Stores nothing.

Deadlines file: [{"name": "Project milestone", "due": "2026-11-20"}]
Try it without a file: deadline_radar.py --demo --repo owner/name
"""
import argparse
import datetime as dt
import json
import re
import sys
import urllib.error
import urllib.request

REPO_NAME = re.compile(r"^[\w.-]+/[\w.-]+$")
DEMO_DAYS = (("Demo milestone", 2), ("Demo reading response", 6), ("Demo final proposal", 20))


def classify(days_left, days_since_commit, warn_days, stale_days):
    """overdue, at_risk, due_soon, on_track or later."""
    if days_left < 0:
        return "overdue"
    if days_left > warn_days:
        return "later"
    if days_since_commit is None:
        return "due_soon"
    return "at_risk" if days_since_commit >= stale_days else "on_track"


def load_deadlines(path, today):
    with open(path, encoding="utf-8") as handle:
        items = json.load(handle)
    if not isinstance(items, list):
        raise ValueError("the deadlines file must contain a JSON list")
    return [{"name": str(item["name"]), "due": dt.date.fromisoformat(item["due"])} for item in items]


def demo_deadlines(today):
    return [{"name": name, "due": today + dt.timedelta(days=days)} for name, days in DEMO_DAYS]


def days_since_last_commit(repo, now):
    """Days since the newest commit, or None when the repository has no commits."""
    if not REPO_NAME.match(repo):
        raise ValueError("repo must look like owner/name")
    request = urllib.request.Request(f"https://api.github.com/repos/{repo}/commits?per_page=1", headers={
        "Accept": "application/vnd.github+json", "User-Agent": "deadline-radar-skill"})
    with urllib.request.urlopen(request, timeout=20) as response:
        commits = json.load(response)
    if not commits:
        return None
    when = dt.datetime.fromisoformat(commits[0]["commit"]["committer"]["date"].replace("Z", "+00:00"))
    return round((now - when).total_seconds() / 86400, 1)


def build_report(deadlines, today, days_since_commit, repo, warn_days, stale_days, repo_error=None):
    rows = []
    for item in sorted(deadlines, key=lambda d: d["due"]):
        days_left = (item["due"] - today).days
        rows.append({"name": item["name"], "due": item["due"].isoformat(), "days_left": days_left,
                     "status": classify(days_left, days_since_commit, warn_days, stale_days)})
    report = {"today": today.isoformat(), "deadlines": rows,
              "repo": {"name": repo, "days_since_commit": days_since_commit} if repo else None}
    if repo_error:
        report["repo"]["error"] = repo_error
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--file", help="JSON list of deadlines, each with name and due (YYYY-MM-DD)")
    source.add_argument("--demo", action="store_true", help="use sample deadlines dated from today")
    parser.add_argument("--repo", help="public GitHub repository, as owner/name")
    parser.add_argument("--warn-days", type=int, default=3, help="days before a deadline to start warning")
    parser.add_argument("--stale-days", type=float, default=2, help="days without a commit that count as stale")
    args = parser.parse_args()

    today = dt.date.today()
    try:
        deadlines = demo_deadlines(today) if args.demo else load_deadlines(args.file, today)
    except (OSError, ValueError, KeyError, TypeError) as error:
        sys.exit(f"Could not read deadlines: {error}")

    days_since_commit, repo_error = None, None
    if args.repo:
        try:
            days_since_commit = days_since_last_commit(args.repo, dt.datetime.now(dt.timezone.utc))
        except (OSError, ValueError, KeyError, IndexError) as error:
            repo_error = f"could not read repository activity: {type(error).__name__}"
    print(json.dumps(build_report(deadlines, today, days_since_commit, args.repo, args.warn_days,
                                  args.stale_days, repo_error), indent=2))


if __name__ == "__main__":
    main()
