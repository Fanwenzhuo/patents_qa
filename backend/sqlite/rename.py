import sqlite3

# 连接到数据库（如果不存在会自动创建）
conn = sqlite3.connect('/home/fanwenzhuo/Documents/project/patents_qa/backend/sqlite/patents.db')
cursor = conn.cursor()

# 修改表名：将 'users' 改为 'customers'
# cursor.execute("ALTER TABLE datalist RENAME TO patent")
cursor.execute("ALTER TABLE patent RENAME COLUMN 公报IPC TO 公报ipc")

# 提交更改并关闭连接
conn.commit()
conn.close()