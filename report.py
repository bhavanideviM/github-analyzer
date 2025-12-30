# report.py
import sqlite3
import csv
import json
from typing import Tuple, List, Dict
from store_sqlite import get_conn




def get_summary_for_user(username: str) -> Dict:
    conn = get_conn()
    cur = conn.cursor()


    cur.execute("SELECT COUNT(*) FROM repos WHERE username = ?", (username,))
    total = cur.fetchone()[0]


    cur.execute("SELECT name, stars FROM repos WHERE username = ? ORDER BY stars DESC LIMIT 5", (username,))
    top_starred = cur.fetchall()


    cur.execute("SELECT language, COUNT(*) as cnt FROM repos WHERE username = ? GROUP BY language ORDER BY cnt DESC", (username,))
    languages = cur.fetchall()


    cur.execute("SELECT name, updated FROM repos WHERE username = ? ORDER BY updated DESC LIMIT 1", (username,))
    last_update = cur.fetchone()


    conn.close()


    return {
    "total_repos": total,
    "top_starred": [tuple(r) for r in top_starred],
    "languages": [tuple(r) for r in languages],
    "last_updated_repo": tuple(last_update) if last_update else None
    }




def get_repos_page(username: str, page: int = 1, per_page: int = 10) -> Tuple[List[Dict], int]:
    conn = get_conn()
    cur = conn.cursor()


    cur.execute("SELECT COUNT(*) FROM repos WHERE username = ?", (username,))
    total = cur.fetchone()[0]


    offset = (page - 1) * per_page
    cur.execute("SELECT name, url, stars, forks, language, created, updated, description FROM repos WHERE username = ? ORDER BY updated DESC LIMIT ? OFFSET ?", (username, per_page, offset))
    rows = cur.fetchall()
    conn.close()


    data = [dict(r) for r in rows]
    return data, total




def export_user_repos(username: str, fmt: str = "json") -> str:
    """Export repos for username as JSON or CSV. Returns path to the created file."""
    data, _ = get_repos_page(username, page=1, per_page=10**6) # get all
    safe_user = username.replace("/", "_")
    if fmt == "csv":
        path = f"{safe_user}_repos.csv"
        keys = data[0].keys() if data else ["name", "url", "stars", "forks", "language", "created", "updated", "description"]
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)
    else:
        return path