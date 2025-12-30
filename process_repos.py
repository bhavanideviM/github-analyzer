# process_repos.py
from typing import List, Dict


REPO_FIELDS = [
"name",
"html_url",
"stargazers_count",
"forks_count",
"language",
"created_at",
"updated_at",
"description"
]


def extract_repo_info(raw_repos: List[Dict], username: str = None) -> List[Dict]:
    processed = []
    for r in raw_repos:
        processed.append({
        "username": username,
        "name": r.get("name"),
        "url": r.get("html_url"),
        "stars": r.get("stargazers_count") or 0,
        "forks": r.get("forks_count") or 0,
        "language": r.get("language") or "",
        "created": r.get("created_at"),
        "updated": r.get("updated_at"),
        "description": r.get("description") or ""
        })
        return processed