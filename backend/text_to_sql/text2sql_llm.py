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

        # 验证 SQL 是否以 SELECT 开头
        if not sql_query.upper().startswith('SELECT'):
            raise ValueError(f"生成的SQL不是SELECT查询语句: {sql_query}")
            
        return sql_query
        
    except Exception as e:
        raise Exception(f"生成SQL查询失败: {str(e)}")

def run_query(sql_query: str):
    # 检查数据库文件是否存在
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"数据库文件不存在: {DB_PATH}")
    
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(sql_query)
        result = cur.fetchall()
        print(f'查询结果：{result}')
        return result
    except sqlite3.Error as e:
        raise sqlite3.Error(f"SQL执行错误: {str(e)}")
    finally:
        if conn:
            conn.close()

