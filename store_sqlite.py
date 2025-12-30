# store_sqlite.py
import sqlite3
from typing import List, Dict


DB_PATH = "github.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def create_table():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS repos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    name TEXT,
    url TEXT,
    stars INTEGER,
    forks INTEGER,
    language TEXT,
    created TEXT,
    updated TEXT,
    description TEXT
    )
    """)
    conn.commit()
    conn.close()


# def insert_repos(repos: List[Dict]):
#     conn = get_conn()
#     cur = conn.cursor()
#     rows = [(
#     r.get("username"), r.get("name"), r.get("url"), r.get("stars"), r.get("forks"),
#     r.get("language"), r.get("created"), r.get("updated"), r.get("description")
#     ) for r in repos]


#     cur.executemany("""
#     INSERT INTO repos (username, name, url, stars, forks, language, created, updated, description)
#     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
#     """, rows)
#     conn.commit()
#     conn.close()

def insert_repos(username: str, repos: List[Dict]):
    conn = get_conn()
    cur = conn.cursor()

    rows = []
    for r in repos:
        rows.append((
            username,
            r.get("name"),
            r.get("html_url"),
            r.get("stargazers_count", 0),
            r.get("forks_count", 0),
            r.get("language"),
            r.get("created_at"),
            r.get("updated_at"),
            r.get("description")
        ))

    cur.executemany("""
    INSERT INTO repos 
    (username, name, url, stars, forks, language, created, updated, description)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, rows)

    conn.commit()
    conn.close()


def clear_repos_by_user(username: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM repos WHERE username = ?", (username,))
    conn.commit()
    conn.close()