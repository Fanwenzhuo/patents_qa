from langchain_community.chat_models import ChatTongyi
from dotenv import load_dotenv
import os


# 加载环境变量
load_dotenv()

# 读取阿里云 API Key
ALIYUN_API_KEY = os.getenv("DASHSCOPE_API_KEY")

# 初始化 Qwen 模型
llm = ChatTongyi(
    model="qwen-turbo",  
    temperature=0,
    max_retries=2,
    dashscope_api_key=ALIYUN_API_KEY,
    # enable_thinking=False
)
# # 直接调用
# response = llm.invoke("你好，请用一句话介绍你的版本。")
# print(response.content)
