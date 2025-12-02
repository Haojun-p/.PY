from api import call_zhipu_api
from roles import get_role_prompt, get_break_rules


def _ensure_system_initialized(history, role_name: str):
    """如果还没有 system 消息，则初始化角色设定和结束规则。"""
    if history and history[0].get("role") == "system":
        return

    role_prompt = get_role_prompt(role_name)
    break_rules = get_break_rules()
    system_message = role_prompt + "\n\n" + break_rules
    history.clear()
    history.append({"role": "system", "content": system_message})


def chat_once(history, user_input: str, role_name: str = "宋曙延") -> str:
    """
    进行一次对话交互，返回AI的回复内容。

    Args:
        history: 对话历史列表（会在函数内部被更新）
        user_input: 用户输入内容
        role_name: 当前扮演的角色名称
    """
    _ensure_system_initialized(history, role_name)

    # 添加用户消息
    history.append({"role": "user", "content": user_input})

    # 调用 API
    result = call_zhipu_api(history)
    assistant_reply = result["choices"][0]["message"]["content"]

    # 添加 AI 回复到历史
    history.append({"role": "assistant", "content": assistant_reply})

    return assistant_reply
