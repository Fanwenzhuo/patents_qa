import os
import sqlite3
import re

current_dir = os.path.dirname(os.path.abspath(__file__))

from backend.components.llm import llm
from backend.components.text2sql_prompts import text2sql_template

# 获取数据库路径
DB_PATH = os.path.join(current_dir, "..", "sqlite", "patents.db")

 

import re

def extract_sql(text: str) -> str:
    text = text.strip()
    if text.endswith(';'):
        text = text[:-1].strip()
    if text.startswith('"') and text.endswith('"'):
        text = text[1:-1]

    match = re.search(r"(SELECT.*?)(?:;|\Z)", text, re.IGNORECASE | re.DOTALL)
    if match:
        sql = match.group(1).strip()
    else:
        sql = text.strip()

    fuzzy_fields = [
        "公开日期", "申请号", "公开号", "专利名", "申请人", "关键词", "URL", "发明人",
        "代理人", "摘要", "专利范围", "详细说明", "优先权", "公报IPC", "IPC"
    ]

    # 第一步：标准化字段名为双引号形式
    for field in fuzzy_fields:
        escaped_field = re.escape(field)
        pattern = rf'''[`"]?{escaped_field}[`"]?'''
        pattern = rf'(?<!\w){pattern}(?!\w)'

        # 替换为双引号形式
        sql = re.sub(pattern, f'"{field}"', sql, flags=re.IGNORECASE)

    # 第二步：对标准化后的 SQL 执行模糊替换
    for field in fuzzy_fields:
        # 现在字段一定是双引号，所以可以直接匹配
        pattern = rf'("{re.escape(field)}")\s*=\s*(\'[^\']*\'|"[^"]*")'
        
        def replace_match(m):
            field_part = m.group(1)      # 一定是 "字段"
            value_part = m.group(2)      # '值' 或 "值"
            raw_value = value_part[1:-1]
            if value_part.startswith("'"):
                return f'{field_part} LIKE \'%{raw_value}%\''
            else:
                return f'{field_part} LIKE "%{raw_value}%"'
        
        sql = re.sub(pattern, replace_match, sql, flags=re.IGNORECASE)

    sql = sql.replace('\\"', '"').strip()
    return sql

def ensure_select_id_url(sql: str) -> str:
    """确保 SELECT 语句的投影列表中包含 "id" 与 "URL" 两个字段。

    - 若 SELECT 列表中包含 * 或 任意 table.*，则认为已包含所有列，不做修改。
    - 若已显式包含 id 或 URL（大小写不敏感，支持是否加引号、是否带表前缀/别名），则不重复添加。
    - 仅处理最外层简单 SELECT ... FROM ... 的场景，无法保证嵌套/复杂子查询的完备性。
    """
    try:
        pattern = re.compile(r"^\s*select\s+(distinct\s+)?(.*?)\s+from\s", re.IGNORECASE | re.DOTALL)
        match = pattern.search(sql)
        if not match:
            return sql

        select_list = match.group(2).strip()

        # 如果包含 * 或 table.*，视为已包含所有列
        has_star = bool(re.search(r"(^|[,\s])\*([,\s]|$)", select_list)) or bool(re.search(r"\.[\s]*\*", select_list))
        if has_star:
            return sql

        # 判断是否已包含 id / URL（忽略大小写，允许可选表前缀与引号）
        id_present = bool(re.search(r"(?i)(?:\b\w+\s*\.\s*)?\"?id\"?(?!\w)", select_list))
        url_present = bool(re.search(r"(?i)(?:\b\w+\s*\.\s*)?\"?url\"?(?!\w)", select_list))

        to_add = []
        if not id_present:
            to_add.append('"id"')
        if not url_present:
            to_add.append('"URL"')

        if not to_add:
            return sql

        # 安全地在 select 列表后面追加新列（保持原有大小写/格式）
        new_select_list = f"{select_list}, {', '.join(to_add)}"
        start, end = match.start(2), match.end(2)
        new_sql = sql[:start] + new_select_list + sql[end:]
        return new_sql
    except Exception:
        # 出现异常时，回退为原 SQL，避免阻断流程
        return sql

def text2sql(question: str) -> str:
    question = question.strip()
    print("问题:", question)
    try:
        # 构建提示词
        formatted_prompt = text2sql_template.format(question=question)
        
        # 调用大模型生成SQL
        response = llm.invoke(formatted_prompt)
        print("大模型原始输出:", response.content)

        # 提取 SQL
        sql_query = extract_sql(response.content)
        print("提取的SQL:", sql_query)

        # 强制包含 id 与 URL 字段
        sql_query = ensure_select_id_url(sql_query)
        print("追加id/URL后的SQL:", sql_query)

        # 验证 SQL 是否以 SELECT 开头
        if not sql_query.upper().startswith('SELECT'):
            raise ValueError(f"生成的SQL不是SELECT查询语句: {sql_query}")
            
        return sql_query
        
    except Exception as e:
        raise Exception(f"生成SQL查询失败: {str(e)}")
