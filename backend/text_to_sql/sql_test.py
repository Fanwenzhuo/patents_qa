import os
import sqlite3

sql_query = """
SELECT COUNT(*) FROM patent WHERE "publication_date" LIKE '2020%' AND "ipc" LIKE '%H01L21/02%' AND "keywords" LIKE '%本国公开%'
"""


current_dir = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(current_dir, "..", "sqlite", "patents.db")
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute(sql_query)
result = cur.fetchall()
print(result)

