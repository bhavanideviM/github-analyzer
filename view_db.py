# import sqlite3

# conn = sqlite3.connect("github.db")
# cursor = conn.cursor()

# cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
# tables = cursor.fetchall()

# print("Tables found in database:")
# for table in tables:
#     print(table[0])

# conn.close()

import sqlite3
import pandas as pd

conn = sqlite3.connect("github.db")

df = pd.read_sql_query("SELECT * FROM repos", conn)

print("\nTotal Repositories Stored:", len(df))
print("\nSample Records:\n")
print(df.head(20))

conn.close()
