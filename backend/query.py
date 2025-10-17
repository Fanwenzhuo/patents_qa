import os
import sqlite3

current_dir = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(current_dir, "sqlite", "patents.db")



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


def format_results_exclude_url(results) -> str:
    """将数据库查询结果整理为适合模型理解的自然语言（不含URL）：专利id、专利信息。

    规则：
    - 每条记录的最后三个元素分别为：专利id、URL、专利名。
    - 输出忽略 URL 与 专利名，仅保留 专利id 与 其它信息字段。
    - 若长度>=3：id 使用倒数第3个；信息为“除去最后三项的所有字段”。
    - 若长度不足3，则尽量显示已有字段并以“未知/无”占位。
    """
    if not results:
        return "数据库中未找到相关专利信息。"

    lines = []
    for row in results:
        row_values = list(row) if isinstance(row, (list, tuple)) else [row]

        if len(row_values) >= 3:
            patent_id = row_values[-3]
            # 忽略倒数第二(URL)与倒数第一(专利名)
            info_parts = row_values[:-3]
        else:
            patent_id = None
            info_parts = row_values

        info_text = "；".join(
            str(v).strip() for v in info_parts if v is not None and str(v).strip() != ""
        )
        info_text = info_text if info_text != "" else "无"

        id_text = (str(patent_id).strip() if patent_id is not None else "未知") or "未知"

        line = f"专利id：{id_text}，专利信息：{info_text}"
        lines.append(line)

    return "\n".join(lines)

def reference_for_answer(results):

    """将数据库查询结果整理为 JSON 形式：

    返回：{
        "source_title": ["专利id：<name_text>", ...],
        "source_url": ["专利id：<url_text>", ...]
    }

    规则（与上游 ensure_select_id_url 保持一致）：
    - 每条记录的最后三个元素分别为：专利id、URL、专利名。
    - 若长度不足3，则尽量显示已有字段并以“未知/无”占位。
    """
    if not results:
        return {"source_title": [], "source_url": []}

    source_title_list = []
    source_url_list = []

    for row in results:
        row_values = list(row) if isinstance(row, (list, tuple)) else [row]

        if len(row_values) >= 3:
            patent_id = row_values[-3]
            url = row_values[-2]
            patent_name = row_values[-1]
        elif len(row_values) == 2:
            patent_id = row_values[0]
            url = row_values[1]
            patent_name = None
        elif len(row_values) == 1:
            patent_id = row_values[0]
            url = None
            patent_name = None
        else:
            patent_id = None
            url = None
            patent_name = None

        id_text = (str(patent_id).strip() if patent_id is not None else "未知") or "未知"
        url_text = (str(url).strip() if url is not None else "无") or "无"
        name_text = (str(patent_name).strip() if patent_name is not None else "无") or "无"

        source_title_list.append(f"专利id：{id_text}：{name_text}")
        source_url_list.append(f"专利id：{id_text}：{url_text}")

    return {"source_title": source_title_list, "source_url": source_url_list}