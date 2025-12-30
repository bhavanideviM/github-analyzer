import os
import httpx

GITHUB_API = "https://api.github.com"
TOKEN = os.getenv("GITHUB_TOKEN")


async def fetch_page(username: str, page: int = 1, per_page: int = 100):
    url = f"{GITHUB_API}/users/{username}/repos"
    params = {"page": page, "per_page": per_page, "sort": "updated"}
    headers = {"Accept": "application/vnd.github+json"}

    if TOKEN:
        headers["Authorization"] = f"token {TOKEN}"

    async with httpx.AsyncClient(timeout=30) as client:
        res = await client.get(url, params=params, headers=headers)
        if res.status_code == 404:
            return []
        res.raise_for_status()
        return res.json()


async def fetch_all_repos(username: str):
    all_repos = []
    page = 1

    while True:
        repos = await fetch_page(username, page=page, per_page=100)
        if not repos:
            break

        all_repos.extend(repos)

        if len(repos) < 100:
            break

        page += 1

    return all_repos
