"""记忆文件加载模块"""
import json
import os
from .config import MEMORY_FOLDER, ROLE_MEMORY_MAP


def load_memory(role_name):
    """
    加载角色的外部记忆文件
    
    Args:
        role_name: 角色名称
    
    Returns:
        str: 记忆内容字符串，如果加载失败则返回空字符串
    """
    memory_content = ""
    memory_file = ROLE_MEMORY_MAP.get(role_name)
    
    if memory_file:
        memory_path = os.path.join(MEMORY_FOLDER, memory_file)
        try:
            if os.path.exists(memory_path):
                with open(memory_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # 处理数组格式的聊天记录：[{ "content": "..." }, { "content": "..." }, ...]
                    if isinstance(data, list):
                        # 提取所有 content 字段，每句换行
                        contents = [item.get('content', '') for item in data if isinstance(item, dict) and item.get('content')]
                        memory_content = '\n'.join(contents)
                    # 处理字典格式：{ "content": "..." }
                    elif isinstance(data, dict):
                        memory_content = data.get('content', str(data))
                    else:
                        memory_content = str(data)
                    
                    if not memory_content or not memory_content.strip():
                        memory_content = ""
            else:
                pass  # 记忆文件不存在，静默处理
        except Exception as e:
            pass  # 加载失败，静默处理
    
    return memory_content


