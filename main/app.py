"""Streamlit主程序入口"""
import streamlit as st
from roles import get_role_system
from chat import get_portrait, display_conversation_history
from logic import BREAK_MESSAGE, process_user_input


# ========== Streamlit Web 界面 ==========
st.set_page_config(
    page_title="微信对话",
    page_icon="🎭",
    layout="wide"
)

# 初始化 session state
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "selected_role" not in st.session_state:
    st.session_state.selected_role = "宋曙延"
if "initialized" not in st.session_state:
    st.session_state.initialized = False

# 页面标题
st.title("微信对话")
st.markdown("---")

# 侧边栏：角色选择和设置
with st.sidebar:
    st.header("⚙️ 设置")
    
    # 角色选择
    selected_role = st.selectbox(
        "选择角色",
        ["吴杰", "宋曙延"],
        index=0 if st.session_state.selected_role == "吴杰" else 1
    )
    
    # 如果角色改变，重新初始化对话
    if selected_role != st.session_state.selected_role:
        st.session_state.selected_role = selected_role
        st.session_state.initialized = False
        st.session_state.conversation_history = []
        st.rerun()
    
    # 清空对话按钮
    if st.button("🔄 清空对话"):
        st.session_state.conversation_history = []
        st.session_state.initialized = False
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 📝 说明")
    st.info(
        "- 选择角色后开始对话\n"
        "- 对话记录不会保存\n"
        "- AI的记忆基于初始记忆文件"
    )

# 初始化对话历史（首次加载或角色切换时）
if not st.session_state.initialized:
    role_system = get_role_system(st.session_state.selected_role)
    system_message = role_system + "\n\n" + BREAK_MESSAGE
    st.session_state.conversation_history = [{"role": "system", "content": system_message}]
    st.session_state.initialized = True

# 显示对话历史
st.subheader(f"💬 与 {st.session_state.selected_role} 的对话")

# 显示角色头像（在聊天窗口上方）
st.code(get_portrait(), language=None)
st.markdown("---")  # 分隔线

# 显示历史消息
display_conversation_history(st.session_state.conversation_history)

# 用户输入
user_input = st.chat_input("输入你的消息...")

if user_input:
    # 显示用户消息
    with st.chat_message("user"):
        st.write(user_input)
    
    # 处理用户输入并获取AI回复
    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            try:
                assistant_reply, should_end = process_user_input(
                    user_input, 
                    st.session_state.conversation_history
                )
                
                if should_end:
                    st.info("对话已结束")
                    st.stop()
                
                # 显示AI回复
                st.write(assistant_reply)
                    
            except Exception as e:
                st.error(f"发生错误: {e}")


