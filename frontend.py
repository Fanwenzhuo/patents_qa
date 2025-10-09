import streamlit as st
from backend.generate import generate_answer

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.append(str(ROOT))


# 页面配置
st.set_page_config(
    page_title="专利问答助手",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        border-bottom: 1px solid #e0e0e0;
        margin-bottom: 2rem;
    }
    
    .chat-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 0 1rem;
    }
    
    .user-message {
        background-color: #007bff;
        color: white;
        padding: 12px 16px;
        border-radius: 18px 18px 4px 18px;
        margin: 8px 0;
        margin-left: 20%;
        word-wrap: break-word;
    }
    
    .assistant-message {
        background-color: #f1f3f4;
        color: #333;
        padding: 12px 16px;
        border-radius: 18px 18px 18px 4px;
        margin: 8px 0;
        margin-right: 20%;
        word-wrap: break-word;
    }
    
    .input-container {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: white;
        padding: 1rem;
        border-top: 1px solid #e0e0e0;
        z-index: 1000;
    }
    
    .stTextInput > div > div > input {
        border-radius: 25px;
        padding: 12px 20px;
        font-size: 16px;
    }
    
    .stButton > button {
        border-radius: 25px;
        padding: 8px 20px;
        font-weight: 500;
    }
    
    .loading-dots {
        display: inline-block;
    }
    
    .loading-dots::after {
        content: '';
        animation: dots 1.5s steps(4, end) infinite;
    }
    
    @keyframes dots {
        0%, 20% { content: ''; }
        40% { content: '.'; }
        60% { content: '..'; }
        80%, 100% { content: '...'; }
    }
</style>
""", unsafe_allow_html=True)

# 初始化会话状态
if "messages" not in st.session_state:
    st.session_state.messages = []

if "is_loading" not in st.session_state:
    st.session_state.is_loading = False

if "clear_input" not in st.session_state:
    st.session_state.clear_input = False

def add_message(role, content):
    """添加消息到聊天记录"""
    st.session_state.messages.append({"role": role, "content": content})

def display_messages():
    """显示聊天消息"""
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="assistant-message">{message["content"]}</div>', unsafe_allow_html=True)

def main():
    # 主标题
    st.markdown("""
    <div class="main-header">
        <h1>🔍 专利问答助手</h1>
        <p>基于大模型的智能专利检索与问答系统</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 聊天容器
    with st.container():
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        # 显示欢迎消息
        if not st.session_state.messages:
            st.markdown("""
            <div class="assistant-message">
                👋 您好！我是专利问答助手，可以帮助您检索和分析专利信息。
                <br><br>
                <strong>您可以问我：</strong>
                <br>• 查找特定公司的专利
                <br>• 搜索特定技术领域的专利
                <br>• 查询某个时间段的专利申请
                <br>• 分析专利发明人信息
                <br><br>
                请在下方输入您的问题，我会为您提供详细的专利信息。
            </div>
            """, unsafe_allow_html=True)
        else:
            display_messages()
        
        # 显示加载状态
        if st.session_state.is_loading:
            st.markdown("""
            <div class="assistant-message">
                <span class="loading-dots">正在思考中</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 输入区域
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([6, 1])
    
    with col1:
        # 在实例化输入框之前，根据标志清空输入
        if st.session_state.get("clear_input"):
            st.session_state.user_input = ""
            st.session_state.clear_input = False
        user_input = st.text_input(
            "请输入您的问题：",
            placeholder="例如：查找日立化成工业股份有限公司的专利",
            key="user_input",
            label_visibility="collapsed"
        )
    
    with col2:
        send_button = st.button("发送", type="primary", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 处理用户输入
    if send_button and user_input:
        # 添加用户消息
        add_message("user", user_input)
        st.session_state.is_loading = True
        
        # 下次渲染前清空输入框
        st.session_state.clear_input = True
        
        # 重新运行以显示用户消息
        st.rerun()
    
    # 处理AI回复
    if st.session_state.is_loading and st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        try:
            # 获取最后一个用户消息
            last_user_message = st.session_state.messages[-1]["content"]
            
            # 生成AI回复
            with st.spinner("正在检索专利信息..."):
                ai_response = generate_answer(last_user_message)
            
            # 添加AI回复
            add_message("assistant", ai_response)
            st.session_state.is_loading = False
            
            # 重新运行以显示AI回复
            st.rerun()
            
        except Exception as e:
            error_message = f"抱歉，处理您的问题时出现了错误：{str(e)}"
            add_message("assistant", error_message)
            st.session_state.is_loading = False
            st.rerun()

if __name__ == "__main__":
    main()
