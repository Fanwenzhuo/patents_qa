from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os


# 加载环境变量
load_dotenv()

# 读取 OpenAI 兼容环境变量
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")  

# 初始化 OpenAI 格式的 Chat 模型
llm = ChatOpenAI(
    model="qwen-plus",  # 可按需改为任意兼容的模型名
    temperature=0,
    max_retries=2,
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_BASE_URL
)
# # 直接调用
# response = llm.invoke("你好，请用一句话介绍你的版本。")
# print(response.content)
