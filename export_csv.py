import sqlite3
import pandas as pd

conn = sqlite3.connect("github.db")
df = pd.read_sql_query("SELECT * FROM repos", conn)

df.to_csv("github_repos_dataset.csv", index=False)

conn.close()

print("CSV Exported Successfully → github_repos_dataset.csv")
