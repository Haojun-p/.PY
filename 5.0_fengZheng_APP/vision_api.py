import base64
import requests
from typing import Dict, Optional
from PIL import Image
import io


def image_to_base64(image) -> str:
    if isinstance(image, Image.Image):
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        img_bytes = buffered.getvalue()
    elif isinstance(image, bytes):
        img_bytes = image
    else:
        return ""
    return base64.b64encode(img_bytes).decode()


def analyze_image_with_ai(image, api_key: str = None) -> Dict:
    try:
        from api import call_zhipu_api
    except ImportError:
        return {"error": "API模块未找到"}
    
    img_base64 = image_to_base64(image)
    if not img_base64:
        return {"error": "图片转换失败"}
    
    prompt = """你是一位城市环境分析专家。用户会描述一张城市地点的照片，请根据描述分析以下内容：

1. 是否有道路、马路、街道
2. 是否有河流、水域
3. 是否有桥梁、天桥、斑马线等过街设施
4. 交通流量情况（车辆、行人）
5. 地形特征（是否适合建造过街设施）

请提供详细的分析，包括：
- 道路情况：是否有道路及类型
- 水域情况：是否有河流或水域
- 过街设施：现有的过街设施类型
- 交通流量：评估交通流量等级（低/中/高）
- 改造建议：是否适合建桥、天桥或斑马线，并说明原因
- 详细描述：整体环境特征和改造可行性分析

注意：由于无法直接查看图片，请根据用户可能提供的描述或场景特征，给出专业的分析和建议。"""
    
    try:
        messages = [
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        result = call_zhipu_api(messages, model="glm-4-flash")
        reply = result["choices"][0]["message"]["content"]
        
        return {
            "success": True,
            "analysis": reply,
            "raw": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

