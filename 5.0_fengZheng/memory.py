import json
import os
from typing import List


# 角色名到记忆文件名的映射（使用当前文件夹内的两个 JSON 文件）
ROLE_MEMORY_FILES = {
    "工程师": "engineer_memory.json",
    "历史学家": "historian_memory.json",
    "物理学家": "physicist_memory.json",
}

BASE_DIR = os.path.dirname(__file__)


def _load_json_list(file_path: str) -> List[str]:
    """
    从 JSON 文件中读取内容列表。
    支持两种结构：
    1. [ { "content": "..." }, ... ]
    2. [ "一句话", "另一句", ... ]
    """
    if not os.path.exists(file_path):
        print(f"⚠ 记忆文件不存在: {file_path}")
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"⚠ 记忆文件加载失败: {e}")
        return []

    contents: List[str] = []

    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                content = str(item.get("content", "")).strip()
            else:
                content = str(item).strip()
            if content:
                contents.append(content)
    else:
        # 其他结构，直接转成字符串
        text = str(data).strip()
        if text:
            contents.append(text)

    return contents


def load_role_memory(role_name: str, max_examples: int = 100) -> str:
    """
    加载指定角色的记忆内容，并整理成带编号的示例文本。

    Args:
        role_name: 角色名
        max_examples: 最多使用多少条示例

    Returns:
        str: 多行文本，每行一条示例，如：
            1. 第一条
            2. 第二条
    """
    file_name = ROLE_MEMORY_FILES.get(role_name)
    if not file_name:
        return ""

    file_path = os.path.join(BASE_DIR, file_name)
    contents = _load_json_list(file_path)

    if not contents:
        return ""

    if len(contents) > max_examples:
        contents = contents[:max_examples]
        print(f"  [提示] 记忆内容较多，已选择前 {max_examples} 条作为示例")

    numbered = [f"{i + 1}. {c}" for i, c in enumerate(contents)]
    memory_text = "\n".join(numbered)

    print(f"✓ 已加载角色 '{role_name}' 的记忆: 使用 {len(numbered)} 条示例")

    return memory_text
#