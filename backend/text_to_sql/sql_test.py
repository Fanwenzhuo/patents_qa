import os
import sqlite3

sql_query = """
SELECT "patent_title", "publication_date" FROM patent WHERE "applicant" LIKE '%台湾积体电路制造股份有限公司%' AND "inventor" LIKE '%沈文超%' AND "patent_scope" LIKE '%电子%' 
"""


current_dir = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(current_dir, "..", "sqlite", "patents.db")
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute(sql_query)
result = cur.fetchall()
print(result)

