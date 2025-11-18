import os
import sqlite3

sql_query = """
SELECT * FROM patent WHERE "applicant" LIKE '%祥硕%' 
"""


current_dir = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(current_dir, "..", "sqlite", "patents.db")
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute(sql_query)
result = cur.fetchall()
print(result)

