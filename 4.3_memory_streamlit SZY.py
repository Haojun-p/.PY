import streamlit as st
import requests
import json
import os  # 新增：用于文件操作

from requests.utils import stream_decode_response_unicode

def call_zhipu_api(messages, model="glm-4-flash"):
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

    headers = {
        "Authorization": "1732aa9845ec4ce09dca7cd10e02d209.dA36k1HPTnFk7cLU",
        "Content-Type": "application/json"
    }

    data = {
        "model": model,
        "messages": messages,
        "temperature": 0.5   
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

# 角色名到记忆文件名的映射
ROLE_MEMORY_MAP = {
    "宋曙延": "SONG_train.json",
    "吴杰": "SONG_dev.json"
}

# ========== 初始记忆系统 ==========

# ========== ASCII 头像 ==========
def get_portrait():
    """返回 ASCII 艺术头像"""
    return """
kkkkkkkkkkkkkkkkkOXXk:;oKNNNNXX0OOOOOOOOO0KK000OOKKK00KK0KK0OkOOOOkO0KNNNNNXkc,:x0OOkkkkkkkkkkkkkkkk
kkkkkkkkkkkkkkkkOKXKxl::dKNNWNNXK0OOOO0KXXXXKKK0KKKKKKKKKKKK0OOOOO0KXNWWNNKkc,;ck0OOOOOkkkkkkkkkkkkk
kkkkkkkkkkkkkkkk0XXKxloclOXNNNNXK0KKKKXXXXXXXXXXXXXXXXXXKKKKKK00O0XNNNNNNKkl;,clk0kOOOOOOOOOOkkkkkkk
kkkkkkOOOOOOOOOOKKKKxlolcd0KXXXXXXXNNNXNNNNNNNNNNNNNNXXXXXXXKKKKKKKXXXXXKOdc,:coOOxO0OOOOOOOOOOOOOOk
OOOOOOOOOOOOOOO0KK0XOlcc:lk0KKXNNNNNNNNNNNNNWWWWWWWNNNNNXXXXXXKKKKK0KKK0Oxl,,::d0Odk0OOOOOOOOOOOOOOO
OOOOOOOOOOOOOOO0K00KKkl:;:d0KXXXXXXNNNNNWWWWWWWWWWWWWWNNNXXXXXXKKK00000Oko;'':d00xok0000OOOOOOOOOOOO
OOOOOOOOOOOO00OKKOkOKX0xld0XXKKKXXXNNNNWWWWWWWWWWWWWWWWWWNNNNXXXKK0000Okkdc;oOKKkolx000000000OOOOOOO
OOOOOOOO0O000000KkoxOKXXXXXKKKKXXXXNNNNWWWWWWWWWWWWWWWWWWNNNNXXXKK00OOOkdxkk000Odllk0000000000000OOO
OOOO000000000000KOoldOKXXK000KKKKXXXXNNNWWWWWWWWWWWWWWWWWNNNXXXXK00OkkkdloxkOkkdccdOK0K0000000000000
0000000000000000KKxllkXK0K0kkO0000KKXXNNNNNWWWWWWWWWWNNNNNNNXXKK0Okkxxdl:lddxxdccokKKKKKKKKK00000000
000000000000000KK00xd0K0OOkxddxkOOkOKKXXXXNNNNNNNNNNNXXXXXXXKK0Okxddolc;:llodxocoxk0KKKKKKKKKK000000
000000000KKKKKK0kxdx0K0Okxxxxdooxkkkxk0KKKKKXXKKKKKKKKKKKK000Oxdoool:;,;:cllllcodood0XKKKKKKKKKK0000
000000KKKKKKKKK0kdld00kkxddxO0OkddxkOkkkkkkOO0000000000OOkxxxxxdolc:clll::::::coolokKXXXXXXXXKKKKK00
000KKKKKKKKKKKKKKOxk00xddddk0KKKK0OOOKKK00000KKXXXXXXXK000OO00Okxxxkkkxoc;;;;;:oxk0XXNXXXXXXXXXKKKK0
KKKKKKKKKKKXXXXXXNNXXOddddxO00KKXXXNNNNNNNWWWWWWNNNWWNNNNNNXXXXKKK00Okxdl:,,,,:d0KKKXNNNNNNNNXXXKKKK
KKKKKKKXXXXXXXXXNXNNX0doodkOOkxdddxxkOKXXNNNNNNNNNNNNNNNNNXXK0kddollloool:,'',:dxkkOKNNNNNNNNNXXKKKK
KKKKKXXXXXXXNNNNNK00OkxoldkOkdollcc:;;:cldk0KXXXXXXXXXK0Oxoc:,,,,;:::cclc;,'',:clodOXNNNNNNNNNXXXXKK
KKKXXXXXXXNNNXXXXK0OOkxdodkOOkkkOOOOkdlc::clxO0KKKKK0Oxoc:;;:coxxkkxddool:;,;;:ccox0KKKXXNNNNNNXXXXK
XXXXXXXXXXXK0OkOOOOkOOOkxxxxxxddxxkkkkkxdooooxkO000Okxoloddxxkkkxddoollllllloodxdxkkkxxkk0XNNNNNNNXX
XXXXXXXXXKOOkxddddololllc;,,clcdkdcll;;:ccoddxk000OOkxddddoo:,;;:ll:;;;'.'':lc::;:cccloddxOXNNNNNNNN
XXXXXXXNKOOOOkxddl:;:ccc:,',lodOx;,l:..,,';ldxO0KKK0Oxdoc,,;';c,.;l:;;:'..';:::,'',:cloddxkKNNNNNNNN
XXXXNNNNXOOOkkkkkkdc:c:;;,,oxllo:,....;ol;,codxkOOkkxdol,,c:,c,...;;,:oc..;;;;;''';:lodxxxkKNNNWWNNN
XXNNNNNWNKOOOOkxdol:,',;;,;dxl:::;,,';ldo:;:lllllllllccc,;odc;,,,,,,';xl.';;,'...',;lxkkkk0NWWWWWWWW
NNNNNNWWWX0OO0Oxl:,''.',:;;oxlcc:;;;:clloc::::lxkkkko:::,;odoc:;;;;;,cdc',;,'.....',lkOOkOKWWWWWWWWW
NNNNNNWWN0xxxxxxxol:,'',;::colcc::::::cc:;;:;:kXXXXXOl;;;,;:ccc:;::;;cc;::,,......':ldxxxdOXWWWWWWWW
NNWWWWWNKxooooddddxdc;,,;:cllc;,,,,,,;;;;::;;oO0XXK0kdc;;:;,,,,,,,',:cll:;,'....',;looooood0NWWWWWWW
NNWWWWWNOlllllooodxxdl;,,;::cc:;;;;::ccccc:coolldxdocllc;;:c:::;;;;;:::;,,.....';:cllllllllkNWWWWWWW
NNNNNNWXxcccccllldxxxdlc:;oo::;,,,;;;;;::lx0kc,''','.':xxl:;,;;;,,,,,;,''.....';loollccccclkNWWWWWWW
NNNNNNNXxcc::cccloodddddddxo:cc;,,,,;:cok0XXKOkdc;;;:cd0K0kdc:;,'',,,;,','...',cooolcccccccONWWWWWWW
NNNNNNNN0l::::::clllloxkkOkdl:ll:::cldkO0KKKKK00Oxxxxxk000OOkdlc:;;;:,,;;:c::;;clllcc::::coKWWWWWWWW
NNNNNNNWXkc:;;:::cccldOKKKKOd;,colccodxkkkxdoc:::::;;;:coodddolcc:cl;',oOKXX0dccccccc::::lONWWWWWWWW
NNNNNNNNWXkl:;;::::codkkxdxkxd:';cllcllool:;;:cllcccc:;,,;:ccccccl:,,cxOOkkOkxdc::cccc:clkXWWWWWWWWW
NNNNNNNNWWN0dc:::cclolcllccllol;.';cllc::ccclccccccccc::c::::clc:,..;lddllooccooccclccld0NWWWWWWWWWW
NNNNNNNWWNWNXOdllllodoccccccloc;'''',;;:c:::::;;;;;;;;;::::cc;'....';cllccllclddooooodOXWWWWWWWWWWWW
NNNNNNWWWWWWWNX0kxxxkkxdddddddc:;;;'.  .';cccloddddoolcccc;,.   ..,;:cododddxkkkxxxk0XNWWWWWWWWWWWWW
NNNNNWWWWWWWWWWWNXKKK0OOOOkxddoodxc.     ..,:clooooollc;,...     .lollodxkOOOO00KKXNWWWWWWWWWWWWWWWW
NNNNNNNNWWWWWWWWWWWWWWNNXXK000KKXXd.     .....',,,,,,'.....      .,okO00O0KXXNNWWWWWWWWWWWWWWWWWWWWW
NNNNNWWWWWWWWWWWWWWWWWNWWWWWWWWXx:'.      ................         .,dKWWWWWWWWWWWWWWWWWWWWWWWWWWWWW
NNNWWWWWWWWWWWWWWWWWWWWWWWWWNN0l.   .       ............             .:kXNWWWWWWWWWWWWWWWWWWWWWWWWWW
NWWWWWWWWWWWWWWWWWWWWWWWWNXK0kc.                 ...                 ..':okKNWWWWWWWWWWWWWWWWWWWWWWW
NNNWWWWWWWWWWWWWWWWWWNXKOxxxxo,.                                      .....,:ox0XNWWWWWWWWWWWWWWWWWW
NNWWWWWWWWWWWWWNXKOxlcclodoc'                                        ........':ldOXNWWWWWWWWWWWWWW

    """

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
                    
                    if memory_content and memory_content.strip():
                        # Streamlit 中使用 st.write 或静默加载
                        pass  # 记忆加载成功，不需要打印
                    else:
                        memory_content = ""
            else:
                pass  # 记忆文件不存在，静默处理
        except Exception as e:
                pass  # 加载失败，静默处理
    
    # ========== 第二步：获取基础人格设定 ==========
    role_personality = {
        "吴杰": """
        【人格特征】
        你是吴杰，一个聪明、幽默、随和的人：
        - **聪明**：思维敏捷，能快速理解朋友的意思
        - **随和**：经常使用口语化表达，性格不要表现的太活泼！
        - **自然**：会使用"草"、"ok"等词，说话简短，语序清楚。
        - **真实**：说话直接，不拐弯抹角，语气上会表现得冷漠一些
        - **幽默**：偶尔会开玩笑，使用网络用语和表情

        【语言风格】
        - 说话简洁直接，不拖泥带水
        - 经常使用"没问题"、"ok"、"好"等口语化表达
        - 会使用表情符号，如[捂脸]、[强]、[OK]等
        - 回复通常比较简短，但很自然，不要使用"啦"等词结尾。
        - 和朋友聊天时很放松，语气轻松，但不是用"呀"、"啦"等词结尾。
        - 会使用一些网络用语和俚语
        - 用"铲"代指游戏"金铲铲之战"、用"go"代指游戏"cs go"吴杰喜欢玩这两个游戏。
        """,
        
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
        - 会使用一些网络用语和俚语。用"铲"代指游戏"金铲铲之战"、用"go"代指游戏"cs go"
        """
            }
            
    
    personality = role_personality.get(role_name, "你是一个普通的人，没有特殊角色特征。")
    
    # ========== 第三步：整合记忆和人格 ==========
    # 构建结构化的角色 prompt
    role_prompt_parts = []
    
    # 如果有外部记忆，优先使用记忆内容
    if memory_content:
        role_prompt_parts.append(f"""【你的说话风格示例】
以下是你说过的话，你必须模仿这种说话风格和语气：

{memory_content}

在对话中，你要自然地使用类似的表达方式和语气。""")
    
    # 添加人格设定
    role_prompt_parts.append(f"【角色设定】\n{personality}")
    
    # 整合成完整的角色 prompt
    role_system = "\n\n".join(role_prompt_parts)
    
    return role_system

# 【结束对话规则】
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

# ========== Streamlit Web 界面 ==========
st.set_page_config(
    page_title="微信对话",
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
st.title("微信对话")
st.markdown("---")

# 侧边栏：角色选择和设置
with st.sidebar:
    st.header("⚙️ 设置")
    
    # 角色选择
    selected_role = st.selectbox(
        "选择角色",
        ["吴杰", "宋曙延"],
        index=0 if st.session_state.selected_role == "吴杰" else 1
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