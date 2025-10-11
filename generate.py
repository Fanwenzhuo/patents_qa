from backend.components.llm import llm
from backend.components.prompts import chat_prompt_template
from backend.text_to_sql.text2sql_llm import text2sql, extract_sql, run_query


def generate_answer(question: str, history=None) -> str:
    # Step 1: 生成 SQL
    sql_query = text2sql(question)
    if not sql_query:
        return "抱歉，我无法根据问题生成有效的SQL查询。"

    # Step 2: 提取并执行 SQL
    sql = extract_sql(sql_query)  # 从输出中提取纯 SQL
    if not sql:
        return "无法提取SQL语句。"

    results = run_query(sql)
    
    if not results:
        context = "数据库中未找到相关专利信息。"
    else:
        context = "查询结果：\n"
    if isinstance(results, int):  # 处理 COUNT(*) 这种情况
        context += f"{results}\n"
    else:
        for i, row in enumerate(results, 1):
            context += f"{i}. {str(row)}\n"


    # Step 3: 构建带上下文的 prompt 并调用 LLM
    chain = chat_prompt_template | llm

    # 注意：你的 chat_prompt_template 需要支持 {context}、{question} 和 {sql}
    response = chain.invoke({
        "question": question,
        "sql": sql,
        "context": context
    })
    
    return response.content

if __name__ == "__main__":
    question = "给出台湾积体电路制造股份有限公司，半导体制造方法的相关专利摘要，不少于2篇。"
    answer = generate_answer(question)
    print(answer)
