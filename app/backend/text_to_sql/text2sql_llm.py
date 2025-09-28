import sys
import os
import sqlite3
import re
from opencc import OpenCC

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, "..", "..", "..")
sys.path.append(project_root)

from app.backend.components.llm import llm
from app.backend.components.text2sql_prompts import prompt

# 获取数据库路径
DB_PATH = os.path.join(current_dir, "..", "sqlite", "patents_add.db")

def to_traditional_chinese(text: str) -> str:
    """
    将输入的简体中文问题转换为繁体中文
    """
    # s2t: Simplified Chinese to Traditional Chinese
    converter = OpenCC('s2tw')
    result = converter.convert(text)
    # 映射表：你可以自己扩展
    replacements = {
        "臺": "台",
        "制": "製",
    }
    for old, new in replacements.items():
        result = result.replace(old, new)
    return result

def extract_sql(text: str) -> str:
  
    # 去掉前后空格
    text = text.strip()

    # 去掉末尾分号
    if text.endswith(';'):
        text = text[:-1].strip()

    # 如果首尾是双引号，去掉它们
    if text.startswith('"') and text.endswith('"'):
        text = text[1:-1]

    # 正则提取第一个 SELECT 开头的语句
    match = re.search(r"(SELECT.*?)(?:;|\Z)", text, re.IGNORECASE | re.DOTALL)
    if match:
        sql = match.group(1).strip()
    else:
        sql = text.strip()

    # --- 强制转换：将指定字段的 "=" 替换为 "LIKE '%...%'" ---
    # 定义需要模糊匹配的字段（根据你的表结构）
    fuzzy_fields = [
        "公开日期", "申请号", "公开号", "专利名", 
        "申请人", "发明人", "代理人", "摘要", "专利范围", "详细说明"
    ]

    for field in fuzzy_fields:
        # 匹配模式： "字段" = '值'  或  "字段" = "值"
        # 注意：字段名带双引号，值可能是单引号或双引号
        pattern = rf'("{re.escape(field)}")\s*=\s*(\'[^\']*\'|"[^"]*")'
        
        def replace_match(m):
            field_part = m.group(1)
            value_part = m.group(2)
            # 如果是单引号包围的值
            if value_part.startswith("'"):
                return f'{field_part} LIKE \'%{value_part[1:-1]}%\''
            else:
                return f'{field_part} LIKE "%{value_part[1:-1]}%"'
        
        # 执行替换
        sql = re.sub(pattern, replace_match, sql, flags=re.IGNORECASE)

    # --- 格式清理 ---
    sql = sql.replace('\\"', '"')  # 处理转义双引号
    sql = sql.strip()

    return sql

def text2sql(question: str) -> str:
    question = to_traditional_chinese(question)
    print("转繁体后的问题:", question)
    try:
        # 构建提示词
        formatted_prompt = prompt.format(question=question)
        
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

# def test_text2sql():
#     """
#     测试文本到SQL转换功能
#     """
#     test_questions = [
#         "日立化成工业股份有限公司2003年发表的专利是什么？",
#     ]
    
#     for i, question in enumerate(test_questions, 1):
#         print(f"问题: {question}")
        
#         try:
#             sql = text2sql(question)
#             result = run_query(sql)
#             print(f"查询结果: {result}")
            
#         except Exception as e:
#             print(f"错误: {e}")

# if __name__ == "__main__":
#     # 运行测试
#     test_text2sql()


