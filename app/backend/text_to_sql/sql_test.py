import os
import sqlite3

sql_query = """
SELECT "摘要" FROM datalist WHERE "申请人" LIKE '%台灣積體電路製造股份有限公司%' AND "专利名" LIKE '%半導體製造%' LIMIT 2
"""

current_dir = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(current_dir, "..", "sqlite", "patents_add.db")
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute(sql_query)
result = cur.fetchone()[0]
print(result)