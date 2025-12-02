import requests


def call_zhipu_api(messages, model: str = "glm-4-flash"):
    """
    调用智谱AI聊天接口

    Args:
        messages: 对话历史列表，[{"role": "...", "content": "..."}, ...]
        model: 使用的模型名称

    Returns:
        dict: API 返回的 JSON 数据

    Raises:
        Exception: 调用失败时抛出异常
    """
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

    headers = {
        "Authorization": "1732aa9845ec4ce09dca7cd10e02d209.dA36k1HPTnFk7cLU",
        "Content-Type": "application/json",
    }

    data = {
        "model": model,
        "messages": messages,
        "temperature": 0.2,  # 与原 4.2_memory_clonebot.py 保持一致
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()
    raise Exception(f"API调用失败: {response.status_code}, {response.text}")
