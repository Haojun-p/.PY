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
    
    prompt = """请分析这张图片，识别以下内容：
1. 是否有道路、马路、街道
2. 是否有河流、水域
3. 是否有桥梁、天桥、斑马线等过街设施
4. 交通流量情况（车辆、行人）
5. 地形特征（是否适合建造过街设施）

请用JSON格式返回，包含：
- has_road: 是否有道路
- has_river: 是否有河流
- has_crossing: 是否有过街设施
- traffic_level: 交通流量（低/中/高）
- suitable_for_bridge: 是否适合建桥
- suitable_for_overpass: 是否适合建天桥
- suitable_for_crosswalk: 是否适合建斑马线
- description: 详细描述"""
    
    try:
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{img_base64}"
                        }
                    }
                ]
            }
        ]
        
        result = call_zhipu_api(messages, model="glm-4-vision-preview")
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

