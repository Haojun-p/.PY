"""对话显示模块"""
import streamlit as st


def display_conversation_history(conversation_history):
    """
    显示对话历史
    
    Args:
        conversation_history: 对话历史列表
    """
    # 显示历史消息（跳过 system 消息）
    for msg in conversation_history[1:]:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.write(msg["content"])
        elif msg["role"] == "assistant":
            with st.chat_message("assistant"):
                st.write(msg["content"])


