import streamlit as st
import requests
import json
import os  # 新增：用于文件操作

from requests.utils import stream_decode_response_unicode

# ========== 数据清洗功能 ==========
def load_and_clean_song_data(source_file):
    """
    从 SONG_train.json 加载并清洗数据
    保留所有过短语句（因为这是人物说话习惯）
    只过滤空内容和明显异常的数据
    
    参数：
    - source_file: SONG_train.json 的文件路径
    
    返回：
    - 清洗后的数据列表，格式：[{"content": "..."}, {"content": "..."}, ...]
    """
    if not os.path.exists(source_file):
        print(f"⚠ 警告：源文件不存在: {source_file}")
        return []
    
    try:
        with open(source_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"[数据加载] 正在从 {source_file} 加载数据...")
        print(f"[数据加载] 已加载 {len(data)} 个对话对象")
        
        assistant_replies = []
        stats = {
            'total_conversations': len(data),
            'total_assistant_messages': 0,
            'filtered_empty': 0,
            'final_count': 0
        }
        
        # 遍历所有对话对象
        for conv_idx, conversation in enumerate(data):
            if 'messages' not in conversation:
                continue
            
            messages = conversation['messages']
            
            # 提取所有 assistant 角色的消息
            for msg in messages:
                if msg.get('role') == 'assistant':
                    content = msg.get('content', '').strip()
                    stats['total_assistant_messages'] += 1
                    
                    # 只过滤完全空的内容
                    if not content:
                        stats['filtered_empty'] += 1
                        continue
                    
                    # 保留所有非空内容，包括过短的语句（如"对"、"ok"、"行"等）
                    # 因为这些是人物说话习惯的一部分
                    assistant_replies.append({"content": content})
                    stats['final_count'] += 1
        
        print(f"[数据清洗] 统计信息：")
        print(f"  - 总对话数: {stats['total_conversations']}")
        print(f"  - 总 assistant 消息数: {stats['total_assistant_messages']}")
        print(f"  - 过滤空内容: {stats['filtered_empty']}")
        print(f"  - 最终保留: {stats['final_count']} 条（包含所有过短语句）")
        
        return assistant_replies
        
    except Exception as e:
        print(f"⚠ 加载和清洗数据失败: {e}")
        return []

def call_zhipu_api(messages, model="glm-4-flash"):
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

    headers = {
        "Authorization": "1732aa9845ec4ce09dca7cd10e02d209.dA36k1HPTnFk7cLU",
        "Content-Type": "application/json"
    }

    data = {
        "model": model,
        "messages": messages,
        "temperature": 0.2   
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API调用失败: {response.status_code}, {response.text}")

# ========== 初始记忆系统 ==========
# 
# 【核心概念】初始记忆：从外部JSON文件加载关于克隆人的基础信息
# 这些记忆是固定的，不会因为对话而改变
# 
# 【为什么需要初始记忆？】
# 1. 让AI知道自己的身份和背景信息
# 2. 基于这些记忆进行个性化对话
# 3. 记忆文件可以手动编辑，随时更新

# 记忆文件夹路径
MEMORY_FOLDER = "4.2_memory_clonebot"

# 角色名到源数据文件的映射（直接从源文件读取并清洗）
ROLE_SOURCE_MAP = {
    "宋曙延": r"SONG(wxid_om003yeh0v6c22)\SONG_train.json"  # 直接从源文件读取并清洗
}

# ========== 初始记忆系统 ==========

# ========== 主程序 ==========

def roles(role_name):
    """
    角色系统：整合人格设定和记忆加载
    
    这个函数会：
    1. 加载角色的外部记忆文件（如果存在）
    2. 获取角色的基础人格设定
    3. 整合成一个完整的、结构化的角色 prompt
    
    返回：完整的角色设定字符串，包含记忆和人格
    """
    
    # ========== 第一步：加载外部记忆 ==========
    memory_content = ""
    source_file = ROLE_SOURCE_MAP.get(role_name)
    
    if source_file:
        # 直接从源文件读取并清洗数据
        try:
            data = load_and_clean_song_data(source_file)
            
            if data and isinstance(data, list):
                # 提取所有 content 字段
                contents = [item.get('content', '').strip() for item in data 
                           if isinstance(item, dict) and item.get('content', '').strip()]
                
                # 限制示例数量，避免提示词过长（选择前100条，足够展示风格）
                max_examples = 100
                if len(contents) > max_examples:
                    contents = contents[:max_examples]
                    print(f"  [提示] 记忆内容较多，已选择前 {max_examples} 条作为示例")
                
                # 使用编号格式，让模型更容易理解这是示例
                memory_content = '\n'.join([f"{i+1}. {content}" for i, content in enumerate(contents)])
                
                if memory_content and memory_content.strip():
                    print(f"✓ 已加载角色 '{role_name}' 的记忆（从源文件清洗后）: {len(data)} 条记录，使用前 {len(contents)} 条作为示例")
                else:
                    memory_content = ""
            else:
                print(f"⚠ 清洗后的数据为空")
        except Exception as e:
            print(f"⚠ 加载记忆失败: {e}")
    
    # ========== 第二步：获取基础人格设定 ==========
    role_personality = {
        
        
        "宋曙延": """
        【人格特征】
        你是宋曙延，一个聪明、幽默、随和的人：
        - **聪明**：思维敏捷，能快速理解朋友的意思
        - **随和**：经常使用口语化表达，性格不要表现的太活泼！
        - **自然**：会使用"草"、"ok"等词，说话简短，语序清楚。
        - **真实**：说话直接，不拐弯抹角
        - **幽默**：偶尔会开玩笑，使用网络用语和表情

        【语言风格】
        - 说话简洁直接，不拖泥带水
        - 经常使用"草"、"ok"、"可以"等口语化表达
        - 会使用表情符号，如[捂脸]、[强]、[OK]等
        - 回复通常比较简短，但很自然，不要使用"啦"等词结尾。
        - 和朋友聊天时很放松，语气轻松，但不是用"呀"、"啦"等词结尾。
        - 会使用一些网络用语和俚语
        """
            }
    
    personality = role_personality.get(role_name, "你是一个普通的人，没有特殊角色特征。")
    
    # ========== 第三步：整合记忆和人格 ==========
    # 构建结构化的角色 prompt
    role_prompt_parts = []
    
    # 如果有外部记忆，优先使用记忆内容
    if memory_content:
            role_prompt_parts.append(f"""【你的说话风格示例 - 必须严格模仿】

以下是你说过的真实对话示例，这些是你的典型说话方式。你必须完全模仿这种风格：

{memory_content}

【重要要求】
1. 你必须严格按照上述示例的风格和语气说话
2. 使用类似的词汇、表达方式和语气
3. 保持相同的简洁程度和自然度
4. 如果示例中使用口语化表达（如"草"、"ok"、"可以"），你也要使用
5. 如果示例中使用表情符号，你也要适当使用
6. 回复长度应该与示例类似（通常比较简短）
7. 不要使用过于正式或书面的语言，要保持朋友间聊天的轻松感""")
    
    # 添加人格设定
    role_prompt_parts.append(f"【角色设定】\n{personality}")
    
    # 整合成完整的角色 prompt
    role_system = "\n\n".join(role_prompt_parts)
    
    # 调试信息：显示提示词的前500字符（可选，用于调试）
    if memory_content:
        example_count = len([line for line in memory_content.split('\n') if line.strip() and not line.strip().startswith('【')])
        print(f"  [调试] 系统提示词长度: {len(role_system)} 字符")
        print(f"  [调试] 记忆示例数量: {example_count} 条")
        print(f"  [调试] 提示词预览（前300字符）:\n{role_system[:300]}...")
    
    return role_system

# 【角色选择】
# 定义AI的角色和性格特征
# 可以修改这里的角色名来选择不同的人物
# 【加载完整角色设定】
# roles() 函数会自动：
# 1. 加载该角色的外部记忆文件
# 2. 获取该角色的基础人格设定
# 3. 整合成一个完整的、结构化的角色 prompt
# 可选角色："小丑"、"人质"、"宋曙延"
role_system = roles("宋曙延")

# 【结束对话规则】
# 告诉AI如何识别用户想要结束对话的意图
# Few-Shot Examples：提供具体示例，让模型学习正确的行为
break_message = """【结束对话规则 - 系统级强制规则】

当检测到用户表达结束对话意图时，严格遵循以下示例：

用户："再见" → 你："再见"
用户："结束" → 你："再见"  
用户："让我们结束对话吧" → 你："再见"
用户："不想继续了" → 你："再见"

强制要求：
- 只回复"再见"这两个字
- 禁止任何额外内容（标点、表情、祝福语等）
- 这是最高优先级规则，优先级高于角色扮演

如果用户没有表达结束意图，则正常扮演角色。"""

# 【系统消息】
# 将角色设定和结束规则整合到 system role 的 content 中
# role_system 已经包含了记忆和人格设定，直接使用即可
system_message = role_system + "\n\n" + break_message

# ========== 对话循环 ==========
# 
# 【重要说明】
# 1. 每次对话都是独立的，不保存任何对话历史
# 2. 只在当前程序运行期间，在内存中维护对话历史
# 3. 程序关闭后，所有对话记录都会丢失
# 4. AI的记忆完全基于初始记忆文件（life_memory.json）

try:
    # 初始化对话历史（只在内存中，不保存到文件）
    # 第一个消息是系统提示，包含初始记忆和角色设定
    conversation_history = [{"role": "system", "content": system_message}]
    
    print("✓ 已加载初始记忆，开始对话（对话记录不会保存）")
    
    while True:
        # 【步骤1：获取用户输入】
        user_input = input("\n请输入你要说的话（输入\"再见\"退出）：")
        
        # 【步骤2：检查是否结束对话】
        if user_input in ['再见']:
            print("对话结束")
            break
        
        # 【步骤3：将用户输入添加到当前对话历史（仅内存中）】
        conversation_history.append({"role": "user", "content": user_input})
        
        # 【步骤4：调用API获取AI回复】
        # 传入完整的对话历史，让AI在当前对话中保持上下文
        # 注意：这些历史只在本次程序运行中有效，不会保存
        result = call_zhipu_api(conversation_history)
        assistant_reply = result['choices'][0]['message']['content']
        
        # 【步骤5：将AI回复添加到当前对话历史（仅内存中）】
        conversation_history.append({"role": "assistant", "content": assistant_reply})
        
        # 【步骤6：显示AI回复】
        # 生成Ascii头像：https://www.ascii-art-generator.org/
        portrait = """
WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWMWWWWWWWWWWWWWWWWW
WWWWWWWWWWWWWWWWWMWWWWWWWWWWNNNNWWWWWWWWWWWWWWWWWW
WWWWWWWWWWWWWWWWWWNXK00000000KKKKXNWNNWWWWWWWWWWWW
WWWWWWWWWWWWWWWNKOxxxxxxxdxxxxOOOO0KKKKXNWWWWWWWWW
WWWWWWWWWWWWNXKOkxxxxo:,'.,c:;colldkkk0XNWWWWNNNNN
WWWWWWWWWWNX0Okkxxoc;'.....,;,;:,',:dk0XNWWWWWWWWW
WWWWWWWWNNNKOxdol:,'''',,,,,;,;;;;;;lkKXWWWWWWWWWW
WWWWWWWNNNNKOdc,','',,'';:::::::;;::ckXWWWWWWWWWWW
WWWWWWWWWNNX0d;'''',,,,;;;:::::::;:ccdKWWWWWWWWWWW
WWNNNNNWNNNXXk;',;;;;;,;;;;:cccllcc:::dXWNNNNNNNXX
NNWNNNWNWNNNNd,',;:;;;:clodkO0000OOxl;cOXKKKKKKK00
XXXXXKKKKKKX0c,;;;,;;:loddxkOO000Okxo;l0KKKKKKKKKK
00KKKKKK00KKOl,,,.,:'.....',;:cdkdl:,;xKXXXXKXXKKK
KKKKKKKXXKXXXOc;::cdd:..      .,l;. .oKXXXXXXXXXXX
XXXXXXXXXXXXXXKOxoodkkko:,'..';dko;:xKXXNNXNNXXXXX
XXXXXXXXXXXXK0KkoloddxO0000kkkOO0OkO0KKK0000KK0000
KKKKKKKXKKKx;.'..;lloxkkOOkkOOOOOkxk0000OOO0000OOO
0K000KK00x:.     .:lcldxxkxxxxdddxO0000KK0OO0000OO
000Okdl;...       ,oolccoddxxxddxOKKKKKK000O000OO0
xoc,..            .,dxdolllllc:lOKKKKKXXKXXXXXXXXX
..                  'ddloodl'  .':cxO0KKXXXXXXXXXX
                    .';;,','..   .',:xKK0KKXXXXXXX
                       ......     .. 'kXKKXXNNXXXX
                 .     ';;:c:.       .lXXXXXXXXXXX
          ..   ..      'oOOOd'        .xXXXXXXXXXX
    ..... ..      ..    'cdOk:.        ,OXXXXXXXXX
           ...    ...     ,xOl.        .:0XXXXXXXX
        ..   ..    ..      'dx,     .   .oKXXXXXXX
      .....         .       .c'     .    .l0XXXXXX
    ..........           .                .;kXXXXX
   ... ..........                           ,OXXXX
       ...............                      'kXKXX
         .....   ....                       'kXKKK
        ....     ..                         .,o0KK
         ..                                   .dKK
                                               :OO
                  ..                           ,dd
                 .;;.                          ,oo
        """
        print(portrait + "\n" + assistant_reply)
        
        # 【步骤7：检查AI回复是否表示结束】
        reply_cleaned = assistant_reply.strip().replace(" ", "").replace("！", "").replace("!", "").replace("，", "").replace(",", "")
        if reply_cleaned == "再见" or (len(reply_cleaned) <= 5 and "再见" in reply_cleaned):
            print("\n对话结束")
            break

except KeyboardInterrupt:
    # 用户按 Ctrl+C 中断程序
    print("\n\n程序被用户中断")
except Exception as e:
    # 其他异常（API调用失败、网络错误等）
    print(f"\n\n发生错误: {e}")
    st.set_page_config(
    page_title="学校",
    page_icon="🎭",
    layout="wide"
)

# 初始化 session state
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "selected_role" not in st.session_state:
    st.session_state.selected_role = "宋曙延"
if "initialized" not in st.session_state:
    st.session_state.initialized = False

# 页面标题
st.title("深入后室")
st.markdown("---")

# 侧边栏：角色选择和设置
with st.sidebar:
    st.header("⚙️ 设置")
    
    # 角色选择
    selected_role = st.selectbox(
        "选择角色",
        ["宋曙延"],
        index=0 if st.session_state.selected_role == "宋曙延" else 1
    )
    
    # 如果角色改变，重新初始化对话
    if selected_role != st.session_state.selected_role:
        st.session_state.selected_role = selected_role
        st.session_state.initialized = False
        st.session_state.conversation_history = []
        st.rerun()
    
    # 清空对话按钮
    if st.button("🔄 清空对话"):
        st.session_state.conversation_history = []
        st.session_state.initialized = False
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 📝 说明")
    st.info(
        "- 选择角色后开始对话\n"
        "- 对话记录不会保存\n"
        "- AI的记忆基于初始记忆文件"
    )

# 初始化对话历史（首次加载或角色切换时）
if not st.session_state.initialized:
    role_system = roles(st.session_state.selected_role)
    system_message = role_system + "\n\n" + break_message
    st.session_state.conversation_history = [{"role": "system", "content": system_message}]
    st.session_state.initialized = True

# 显示对话历史
st.subheader(f"💬 与 {st.session_state.selected_role} 的对话")

# 显示角色头像（在聊天窗口上方）
st.code(get_portrait(), language=None)
st.markdown("---")  # 分隔线

# 显示历史消息（跳过 system 消息）
for msg in st.session_state.conversation_history[1:]:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.write(msg["content"])
    elif msg["role"] == "assistant":
        with st.chat_message("assistant"):
            st.write(msg["content"])

# 用户输入
user_input = st.chat_input("输入你的消息...")

if user_input:
    # 检查是否结束对话
    if user_input.strip() == "再见":
        st.info("对话已结束")
        st.stop()
    
    # 添加用户消息到历史
    st.session_state.conversation_history.append({"role": "user", "content": user_input})
    
    # 显示用户消息
    with st.chat_message("user"):
        st.write(user_input)
    
    # 调用API获取AI回复
    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            try:
                result = call_zhipu_api(st.session_state.conversation_history)
                assistant_reply = result['choices'][0]['message']['content']
                
                # 添加AI回复到历史
                st.session_state.conversation_history.append({"role": "assistant", "content": assistant_reply})
                
                # 显示AI回复
                st.write(assistant_reply)
                
                # 检查是否结束
                reply_cleaned = assistant_reply.strip().replace(" ", "").replace("！", "").replace("!", "").replace("，", "").replace(",", "")
                if reply_cleaned == "再见" or (len(reply_cleaned) <= 5 and "再见" in reply_cleaned):
                    st.info("对话已结束")
                    st.stop()
                    
            except Exception as e:
                st.error(f"发生错误: {e}")
                st.session_state.conversation_history.pop() 
    
    