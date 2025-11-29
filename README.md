1.zhipu大模型：——————————————————————————————————————————————————
import requests
import json

def call_zhipu_api(messages, model="glm-4-flash"):
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

    headers = {
        "Authorization": "Bearer 9fce314157754e0491c32dcf33f8963f.uWyUwPde8tYVHww7",
        "Content-Type": "application/json"
    }

    data = {
        "model": model,
        "messages": messages,
        "temperature": 0.8
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API调用失败: {response.status_code}, {response.text}")
其中：第一步是api调用，进入官网并注册账号，得到自己的API和密钥，在合适的地方替换。
     "temperature": 0.8代表情绪，越趋近于0表示机器人越保守，越趋近于1表示机器人越激进。（回答）


2.角色提示词：——————————————————————————————————————————————
# 系统提示词
        self.game_system = f"""你正在玩"门前来客"游戏。场景：你（模型）正站在用户家门口敲门，身份是：{self.current_role}。

背景设定：
1. "人类"是无害访客；"窃皮者"是危险生物，能够伪装成人类，企图骗用户开门后夺走皮肤。
2. 你必须一直待在门外，通过敲门和对话给出线索，引导用户判断是否要开门。

对话规则：
- 保持角色说话，不得直接说出"我是{self.current_role}"或"我不是XX"。
- 尽量用氛围描写、语气、行为暗示身份，让用户自行推断。
- 不要给出除"人类""窃皮者"以外的身份选项。
- 用户如果明确说出"你是{self.current_role}"，你只回复"再见"并结束游戏。
- 当用户表达"我要开门""我决定开门"等等时：
  * 如果你是"窃皮者"，冷酷地回复"你死了"，再附上一段描写，并结束游戏。
  * 如果你是"人类"，真诚地回复"你很安全"，再附上一段描写，并结束游戏。
- 如果用户拒绝开门或继续犹豫，保持神秘感继续给提示。

参考：
- 人类可以提到温暖、求助、正常社交动机，但不要显得过度完美。
- 窃皮者可以表现出诡异、模仿痕迹、对人体的奇怪兴趣，但仍在努力伪装。

3.1循环：——————————————————————————————————————————————————————————————————
while True:    
    user_input = input("请猜猜我是谁：")
    messages = [
        {"role": "system", "content": current_role + "。" + current_break_message},
        {"role": "user", "content": user_input}
    ]
    result = call_zhipu_api(messages)
    reply=result['choices'][0]['message']['content']
    print(reply)
    if reply =="被发现了...":
        print("对话结束。")
        break
    if reply =="哇塞，主人好棒！":
        print("奖励一条小鱼")
        break
使用while true函数让对话一直延续。


3.2角色选择：——————————————————————————————————————————————————————————————————
role_system = ["你是一只会说话的可爱的小猫娘，请用小猫咪的说话方式回答，可以加上'喵'、'主人'等语气词。","你是一只假扮成猫娘的小狗，会像猫娘一样讲话，你不想被发现。"]
break_message = ["如果你是一只小猫娘并且同时我猜中你是一只小猫娘，请只回复我'哇塞，主人好棒！'回复这句话时不需要加额外的语气词和标点符号，如果我没猜中或者没猜请继续和我正常对话","如果你是一只小狗并且同时我猜中你是一只小狗，请回复我'被发现了...'如果我没猜中或者没猜请继续和我正常对话，不需要加额外的语气词和标点符号"]

current_role = random.choice(role_system)
current_break_message = break_message[role_system.index(current_role)]


3.3语音输出：——————————————————————————————————————————————————————————————————

首先注册科大，购买语音包，在程序中替换ID和KEY。

APPID = 'bf102b96'  # 替换为你的APPID
APIKEY = '49426fda2fe583210b63dff977f4d1f3'  # 替换为你的APIKey
APISECRET = 'N2RjY2I0NzhmOGFjNWMxYWI5YTdkMjA5'  # 替换为你的APISecret
REQURL = 'wss://cbm01.cn-huabei-1.xf-yun.com/v1/private/mcd9m97e6'
导入科大tts模块——

# 可选导入TTS模块
try:
    from KEDA import text_to_speech
    TTS_AVAILABLE = True
except ImportError as e:
    TTS_AVAILABLE = False
    print(f"警告：TTS模块未找到（ImportError），语音功能将不可用: {e}")
except Exception as e:
    TTS_AVAILABLE = False
    print(f"警告：TTS模块导入失败（{type(e).__name__}），语音功能将不可用: {e}")
    import traceback
    traceback.print_exc()







4.1记忆系统知识点：————————————————————————————————————————————————————————————————————————
MEMORY_FILE = "conversation_memory.json"

def load_memory():
     从JSON文件加载对话历史
     os.path.exists() 检查文件是否存在
    if os.path.exists(MEMORY_FILE):
        try:
             使用 'r' 模式打开文件（只读模式）
             encoding='utf-8' 确保中文正确显示
            with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                 json.load() 将JSON文件内容解析为Python字典
                data = json.load(f)
                
                 data.get('history', []) 的含义：
                 - 如果 data 字典中有 'history' 键，返回对应的值
                 - 如果没有 'history' 键，返回默认值 []（空列表）
                 这样可以避免 KeyError 错误
                history = data.get('history', [])
                
                print(f"✓ 已加载 {len(history)} 条历史对话")
                return history
        except Exception as e:
             如果读取或解析失败（文件损坏、格式错误等），捕获异常
            print(f"⚠ 加载记忆失败: {e}，将使用新的对话历史")
            return []
    else:
         文件不存在，说明是第一次运行，返回空列表
        print("✓ 未找到记忆文件，开始新对话")
        return []

def save_memory(conversation_history, role_system):
     保存对话历史到JSON文件
    try:
         导入datetime模块获取当前时间
        from datetime import datetime
        
         构造要保存的数据结构
        data = {
            "role_system": role_system,  # 保存角色设定
            "history": conversation_history,  # 保存完整对话历史
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 保存更新时间
        }
        
         使用 'w' 模式打开文件（写入模式，会覆盖原有内容）
         encoding='utf-8' 确保中文正确保存
        with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
             json.dump() 将Python对象写入JSON文件
             ensure_ascii=False: 不将非ASCII字符转义（中文直接保存，不变成 \\uXXXX）
             indent=2: 格式化输出，每个层级缩进2个空格，让文件更易读
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✓ 已保存 {len(conversation_history)} 条对话到记忆文件")
    except Exception as e:
         如果保存失败（磁盘空间不足、权限问题等），捕获异常并提示
        print(f"⚠ 保存记忆失败: {e}")





4.2SONG_train.json 数据清洗说明————————————————————————————————————————————————————————————————

 📋 数据清洗需要注意的要点

### 1. 数据结构理解
- `SONG_train.json` 是一个数组，包含多个对话对象
- 每个对话对象有 `messages` 字段，包含完整的对话历史
- 每条消息有 `role`（system/user/assistant）和 `content` 字段
- **目标**：提取所有 `role="assistant"` 的 `content`，作为说话风格示例

### 2. **数据清洗检查点**

#### ✅ 检查点1：过滤空内容
- **问题**：有些 assistant 消息的 content 可能为空字符串或只包含空格
- **处理**：使用 `strip()` 去除首尾空格，检查是否为空
- **影响**：空内容对模型学习没有帮助，应该过滤

#### ✅ 检查点2：过滤过短内容
- **问题**：有些回复可能只有1-2个字符，可能是误输入或无效数据
- **处理**：设置 `min_length` 参数（建议值：1-3）
- **影响**：太短的内容可能无法体现说话风格

#### ✅ 检查点3：过滤过长内容
- **问题**：有些回复可能异常长（超过500字符），可能是异常数据
- **处理**：设置 `max_length` 参数（建议值：200-500）
- **影响**：过长的内容可能包含异常信息，影响模型学习

#### ✅ 检查点4：过滤纯符号内容
- **问题**：有些内容可能只包含标点符号或特殊字符
- **处理**：检查去除标点后是否为空
- **影响**：纯符号对学习说话风格没有帮助

#### ✅ 检查点5：去重（可选）
- **问题**：同一句话可能在不同对话中重复出现
- **处理**：可以使用 `set` 去重，但**建议不去重**
- **原因**：重复的句子说明这是常用表达，对学习说话风格有价值

### 3. **数据质量分析**

在清洗前，建议先运行 `analyze_data_quality()` 函数：
- 查看平均长度、最短、最长、中位数
- 查看长度分布（1-10字符、11-50字符等）
- 根据分析结果调整 `min_length` 和 `max_length` 参数

### 4. **输出格式**

清洗后的数据格式应该符合 `4.2_memory_clonebot.py` 的期望：

```json
[
  {"content": "突然想到了"},
  {"content": "无敌了"},
  {"content": "走吗"},
  ...
]
```

这是一个数组，每个元素是一个对象，包含 `content` 字段。

 🚀 使用步骤

 步骤1：运行数据清洗脚本

```bash
python clean_song_data.py
```

这会：
1. 分析数据质量
2. 提取所有 assistant 回复
3. 应用清洗规则
4. 保存到 `4.2_memory_clonebot\songshuyan_memory.json`

 步骤2：检查输出文件

打开 `4.2_memory_clonebot\songshuyan_memory.json`，确认：
- 格式正确（数组格式）
- 内容符合预期（都是宋曙延的回复）
- 没有异常数据

 步骤3：运行聊天机器人

```bash
python 4.2_memory_clonebot.py
```

机器人会自动加载 `songshuyan_memory.json` 中的说话风格示例。

 📊 数据统计示例

清洗完成后，你会看到类似这样的统计：

```
📊 数据清洗统计：
  - 总对话数: 100
  - 总 assistant 消息数: 250
  - 过滤空内容: 5
  - 过滤过短内容: 2
  - 过滤过长内容: 1
  - 最终保留: 242 条
```

 ⚠️ 注意事项

1. **保留原始数据**：清洗前先备份 `SONG_train.json`
2. **参数调整**：根据数据质量分析结果调整 `min_length` 和 `max_length`
3. **多次清洗**：如果第一次清洗结果不理想，可以调整参数重新清洗
4. **数据量**：确保最终保留的数据量足够（建议至少100条以上）

## 🔧 自定义清洗规则

如果需要添加自定义清洗规则，可以在 `clean_song_data()` 函数中添加：

```python
# 示例：过滤包含特定关键词的内容
if "敏感词" in content:
    continue

# 示例：只保留包含中文字符的内容
import re
if not re.search(r'[\u4e00-\u9fff]', content):
    continue
```

## 📝 应用到 clonebot 的流程

1. **数据清洗**：运行 `clean_song_data.py` → 生成 `songshuyan_memory.json`
2. **角色配置**：在 `4.2_memory_clonebot.py` 中已添加"宋曙延"角色
3. **运行测试**：运行 `4.2_memory_clonebot.py`，选择"宋曙延"角色
4. **效果验证**：观察机器人是否模仿了宋曙延的说话风格


4.3前端网页转化
# Streamlit前端核心代码
import streamlit as st
关键知识点整理：

页面配置：使用st.set_page_config()设置标题、图标和布局

会话状态：使用st.session_state管理对话历史和状态

布局组件：

st.title()- 主标题

st.sidebar- 侧边栏容器

st.markdown()- 支持Markdown格式

交互组件：

st.selectbox()- 下拉选择框

st.button()- 按钮

st.chat_input()- 聊天输入框

消息显示：

st.chat_message()- 聊天消息容器

with语句块 - 组织相关UI元素

状态反馈：

st.spinner()- 加载指示器

st.error()- 错误提示

