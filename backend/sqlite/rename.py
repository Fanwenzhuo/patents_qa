import sqlite3

# 连接到数据库（如果不存在会自动创建）
conn = sqlite3.connect('/home/fanwenzhuo/Documents/project/patents_qa/backend/sqlite/patents.db')
cursor = conn.cursor()

# 字段重命名映射：中文字段名 -> 英文字段名
field_rename_mapping = [
    ("申请日期", "application_date"),
    ("公开日期", "publication_date"),
    ("申请号", "application_number"),
    ("公开号", "publication_number"),
    ("专利名", "patent_title"),
    ("申请人", "applicant"),
    ("关键词", "keywords"),
    ("发明人", "inventor"),
    ("代理人", "agent"),
    ("摘要", "abstract"),
    ("专利范围", "patent_scope"),
    ("详细说明", "detailed_description"),
    ("优先权", "priority"),
    ("公报ipc", "gazette_ipc"),
    # ipc 字段保持不变
]

# 执行字段重命名
for old_name, new_name in field_rename_mapping:
    try:
        cursor.execute(f'ALTER TABLE patent RENAME COLUMN "{old_name}" TO "{new_name}"')
        print(f"成功重命名字段: {old_name} -> {new_name}")
    except sqlite3.OperationalError as e:
        print(f"重命名字段失败 {old_name} -> {new_name}: {e}")

# 提交更改并关闭连接
conn.commit()
conn.close()
print("数据库字段重命名完成！")