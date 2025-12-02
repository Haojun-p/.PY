"""对话处理逻辑模块"""
from api import call_zhipu_api


def check_end_conversation(user_input=None, assistant_reply=None):
    """
    检查是否结束对话
    
    Args:
        user_input: 用户输入（可选）
        assistant_reply: AI回复（可选）
    
    Returns:
        bool: 如果应该结束对话返回True，否则返回False
    """
    if user_input:
        if user_input.strip() == "再见":
            return True
    
    if assistant_reply:
        reply_cleaned = assistant_reply.strip().replace(" ", "").replace("！", "").replace("!", "").replace("，", "").replace(",", "")
        if reply_cleaned == "再见" or (len(reply_cleaned) <= 5 and "再见" in reply_cleaned):
            return True
    
    return False


def process_user_input(user_input, conversation_history):
    """
    处理用户输入，获取AI回复
    
    Args:
        user_input: 用户输入
        conversation_history: 对话历史
    
    Returns:
        tuple: (assistant_reply, should_end)
            - assistant_reply: AI回复内容
            - should_end: 是否应该结束对话
    """
    # 检查是否结束对话
    if check_end_conversation(user_input=user_input):
        return None, True
    
    # 添加用户消息到历史
    conversation_history.append({"role": "user", "content": user_input})
    
    # 调用API获取AI回复
    try:
        result = call_zhipu_api(conversation_history)
        assistant_reply = result['choices'][0]['message']['content']
        
        # 添加AI回复到历史
        conversation_history.append({"role": "assistant", "content": assistant_reply})
        
        # 检查是否结束
        should_end = check_end_conversation(assistant_reply=assistant_reply)
        
        return assistant_reply, should_end
        
    except Exception as e:
        # 如果出错，移除刚添加的用户消息
        conversation_history.pop()
        raise e

