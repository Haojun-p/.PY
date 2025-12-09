def should_exit_by_user(user_input: str) -> bool:
    """判断用户是否想要结束对话，返回 True/False"""
    if not user_input:
        return False
    return user_input.strip() == "再见"


def should_exit_by_ai(ai_reply: str) -> bool:
    """判断AI的回复是否表示要结束对话，返回 True/False"""
    if not ai_reply:
        return False

    reply_cleaned = (
        ai_reply.strip()
        .replace(" ", "")
        .replace("！", "")
        .replace("!", "")
        .replace("，", "")
        .replace(",", "")
    )

    if reply_cleaned == "再见":
        return True
    if len(reply_cleaned) <= 5 and "再见" in reply_cleaned:
        return True

    return False
#