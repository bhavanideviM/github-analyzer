from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import asyncio
import aiohttp
from fastapi.responses import RedirectResponse
from store_sqlite import insert_repos, clear_repos_by_user
import sqlite3
from fastapi.responses import HTMLResponse



from fetch_repos import fetch_all_repos
from process_repos import extract_repo_info
from store_sqlite import create_table, insert_repos, clear_repos_by_user
from report import get_summary_for_user


app = FastAPI()

GITHUB_API = "https://api.github.com"

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# Ensure database table exists at startup
create_table()


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# @app.post("/analyze")
# async def analyze(request: Request, username: str = Form(...)):
#     """Trigger fetching and processing of a user's repos and redirect to results page."""
#     username = username.strip()
#     if not username:
#         raise HTTPException(status_code=400, detail="username required")


#     # Clear any previous data for same user (optional)
#     clear_repos_by_user(username)


#     # Fetch all repos from GitHub (may take time depending on repo count)
#     repos = await fetch_all_repos(username)


#     if not repos:
#     # still redirect to results page which shows "no repos"
#         return RedirectResponse(url=f"/results/{username}", status_code=303)


#     processed = extract_repo_info(repos, username)
#     # insert_repos(processed)
#     clear_repos_by_user(username)
#     insert_repos(username, processed)



#     return RedirectResponse(url=f"/results/{username}", status_code=303)

@app.post("/analyze")
async def analyze(request: Request):
    form = await request.form()
    username = form.get("username")

    all_repos = []
    page = 1

    headers = {
        "Accept": "application/vnd.github+json"
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        while True:
            url = f"{GITHUB_API}/users/{username}/repos?per_page=100&page={page}&sort=updated"

            async with session.get(url) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    raise Exception(f"GitHub API Error: {resp.status} - {text}")

                data = await resp.json()

            # ❗ SAFETY CHECK
            if not isinstance(data, list):
                raise Exception(f"Invalid API response: {data}")

            if not data:
                break

            for repo in data:
                all_repos.append({
                    "name": repo.get("name"),
                    "stars": repo.get("stargazers_count", 0),
                    "forks": repo.get("forks_count", 0),
                    "language": repo.get("language"),
                    "url": repo.get("html_url")
                })

            if len(data) < 100:
                break

            page += 1

    clear_repos_by_user(username)
    insert_repos(username, all_repos)

    return RedirectResponse(f"/results/{username}", status_code=303)



@app.get("/results/{username}")
async def results(request: Request, username: str, page: int = 1, per_page: int = 10):
    """Render paginated repos list and controls. Pagination is server-side reading from SQLite."""
    # We'll render template which fetches data via JS endpoints
    summary = get_summary_for_user(username)
    return templates.TemplateResponse("results.html", {"request": request, "username": username, "summary": summary, "page": page, "per_page": per_page})


@app.get("/api/repos/{username}")
async def api_repos(username: str, page: int = 1, per_page: int = 10):
    """Return JSON list of repos for a user (from SQLite) with pagination."""
    # read directly using report helper (which returns paginated rows)
    from report import get_repos_page
    data, total = get_repos_page(username, page, per_page)
    return {"repos": data, "total": total, "page": page, "per_page": per_page}


@app.get("/report/{username}")
async def report_page(request: Request, username: str):
    summary = get_summary_for_user(username)
    return templates.TemplateResponse("report.html", {"request": request, "username": username, "summary": summary})

@app.get("/db-view", response_class=HTMLResponse)
async def db_view(request: Request):
    conn = sqlite3.connect("github.db")
    cur = conn.cursor()
    cur.execute("SELECT name, stars, forks, language FROM repos")
    rows = cur.fetchall()
    conn.close()

    return templates.TemplateResponse("db_view.html", {
        "request": request,
        "rows": rows
    })


@app.get("/download/{username}/{fmt}")
async def download(username: str, fmt: str):
    """Serve JSON or CSV export created on-the-fly from SQLite."""
    from report import export_user_repos
    path = export_user_repos(username, fmt)
    return FileResponse(path, filename=path.split('/')[-1])