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
    - 专利id与URL为每条记录的最后两个元素（URL被忽略，仅用于定位位置）。
    - 若长度为3：第一个元素是专利信息。
    - 若长度大于3：最后两个元素之前的所有元素合并为专利信息。
    - 若长度不足2，则尽量显示已有字段并以“未知/无”占位。
    """
    if not results:
        return "数据库中未找到相关专利信息。"

    lines = []
    for row in results:
        row_values = list(row) if isinstance(row, (list, tuple)) else [row]

        if len(row_values) >= 2:
            patent_id = row_values[-2]
            # url = row_values[-1]  # 明确忽略 URL
            info_parts = row_values[:-2]
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


def reference_for_answer(results) -> str:
    """将数据库查询结果整理为参考文献格式：专利id：URL。

    规则：
    - 每条记录的最后两个元素分别为：专利id、URL。
    - 若长度不足2，则尽量显示已有字段并以“未知/无”占位。
    """
    if not results:
        return ""

    lines = []
    # 固定添加引用来源首行（不改变现有结构与逻辑）
    lines.append("引用来源：")
    for row in results:
        row_values = list(row) if isinstance(row, (list, tuple)) else [row]

        if len(row_values) >= 2:
            patent_id = row_values[-2]
            url = row_values[-1]
        else:
            patent_id = row_values[0] if len(row_values) == 1 else None
            url = None

        id_text = (str(patent_id).strip() if patent_id is not None else "未知") or "未知"
        url_text = (str(url).strip() if url is not None else "无") or "无"

        lines.append(f"专利id：{id_text}：{url_text}")

    return "\n".join(lines)