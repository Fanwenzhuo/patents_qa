import json
from backend.components.llm import llm
from backend.components.prompts import chat_prompt_template
from backend.text_to_sql.text2sql_llm import text2sql
from backend.query import run_query, format_results_exclude_url, reference_for_answer


def generate_answer(question: str, history=None) -> dict:
    # 生成 SQL
    sql_query = text2sql(question)
    
    # 检查是否是查全表的语句，如果是则置空
    if sql_query and sql_query.strip().upper().startswith('SELECT *'):
        sql_query = ""
    
    if not sql_query:
        return {
            "content": "抱歉，我无法根据问题生成有效的SQL查询。",
            "text": "",
            "source_title": "",
            "source_url": "",
            "source_file": ""
        }

    # 执行 SQL 查询
    results = run_query(sql_query)
    
    # 构建上下文
    context = format_results_exclude_url(results)
    print("context:", context)

    # 构建带上下文的 prompt 并调用 LLM
    chain = chat_prompt_template | llm
    response = chain.invoke({
        "question": question,
        "sql": sql_query,
        "context": context
    })

    # 构建参考信息
    refs = reference_for_answer(results)
    
    # 从引用中提取字段
    source_title = refs.get("source_title", "") if isinstance(refs, dict) else ""
    source_url = refs.get("source_url", "") if isinstance(refs, dict) else ""

    # 返回 JSON 格式的结果
    result_json =  {
        "content": "patent:" + (response.content if hasattr(response, "content") else str(response)),
        "text": context,
        "source_title": source_title,
        "source_url": source_url,
        "source_file": ""
    }

    return json.dumps(result_json, ensure_ascii=False, indent=2)



if __name__ == "__main__":
    question = "给出截止2025年6月31日IPC包含H01L21/02的台湾“本国公开”专利数量？"
    answer = generate_answer(question)
    print(answer)
