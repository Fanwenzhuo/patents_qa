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
DB_PATH = os.path.join(current_dir, "..", "sqlite", "patents.db")



