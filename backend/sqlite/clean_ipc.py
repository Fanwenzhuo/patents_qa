import sqlite3
import re
from multiprocessing import Pool, cpu_count
from tqdm import tqdm
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(current_dir, "patents.db")
TABLE = "patent"     
BATCH_SIZE = 20000    


# IPC 前缀：部(字母) + 大类(2数字) + 小类(字母)
ipc_fix_pattern = re.compile(r"([A-Z]\d{2}[A-Z])\s+(\d)")


def fix_single_ipc(ipc: str) -> str:
    """修复单个 IPC 内部错误空格"""
    return ipc_fix_pattern.sub(r"\1\2", ipc)


def clean_ipc_field(field: str) -> str:
    """修复包含多个 IPC 的字段"""
    if not field:
        return field

    # 分割（支持 ; 和 ；）
    parts = re.split(r"[;；]", field)
    cleaned = [fix_single_ipc(p.strip()) for p in parts if p.strip()]

    return "; ".join(cleaned)


def process_batch(rows):
    """子进程清洗批次"""
    result = []
    for row_id, gazette, ipc in rows:
        new_gazette = clean_ipc_field(gazette)
        new_ipc = clean_ipc_field(ipc)

        if new_gazette != gazette or new_ipc != ipc:
            result.append((new_gazette, new_ipc, row_id))
    return result


def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(f"SELECT COUNT(*) FROM {TABLE}")
    total = cursor.fetchone()[0]
    print(f"Total rows: {total}\n")

    pool = Pool(cpu_count())

    # tqdm 进度条
    pbar = tqdm(total=total, desc="Cleaning IPC")

    offset = 0
    while offset < total:

        cursor.execute(
            f"SELECT id, gazette_ipc, ipc FROM {TABLE} "
            f"LIMIT {BATCH_SIZE} OFFSET {offset}"
        )
        rows = cursor.fetchall()
        if not rows:
            break

        # 并行分片
        chunk_size = len(rows) // cpu_count() + 1
        chunks = [rows[i:i + chunk_size] for i in range(0, len(rows), chunk_size)]

        # 多进程处理
        results = pool.map(process_batch, chunks)
        updates = [item for sub in results for item in sub]

        # 更新数据库
        conn.executemany(
            f"UPDATE {TABLE} SET gazette_ipc=?, ipc=? WHERE id=?",
            updates
        )
        conn.commit()

        # 更新进度条
        pbar.update(len(rows))

        offset += BATCH_SIZE

    pbar.close()
    pool.close()
    pool.join()
    conn.close()

    print("\nAll IPC fields cleaned successfully!")


if __name__ == "__main__":
    main()
