import requests
import json
import random

from requests.utils import stream_decode_response_unicode
from KEDA import text_to_speech 

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
import random

import random

import random

#import random

import random

import random

import random

# 6人双狼局规则（预言家自主查验+无其他身份显示）
role_system = [
    "- 6人双狼局狼人杀规则：",
    "1. 玩家：你（A）、B、C、D、E、F，身份为2狼人、3平民、1预言家。",
    "2. 你的身份只会是平民或预言家，不会是狼人。",
    "3. 核心流程：天黑→技能阶段（双狼刀人→预言家查验）→天亮→遗言→发言→投票。",
    "4. 关键规则：",
    "   - 被刀、被投出局的玩家可留1句遗言（最后1轮除外），出局后无法参与后续游戏；",
    "   - 若你是预言家，天黑时可自主选择查验1名玩家身份（不可查自己）；",
    "5. 胜利条件：",
    "   - 好人：投出两个狼人，或存活到最后；",
    "   - 狼人：淘汰所有好人，或让好人数量≤狼人数量。"
]

# 初始化游戏（修复身份分配逻辑+隐藏其他身份）
all_players = ["A", "B", "C", "D", "E", "F"]
your_role = random.choice(["平民", "平民", "平民", "预言家"])

# 生成剩余身份（仅内部使用，不显示）
remaining_roles = []
remaining_roles.extend(["狼人", "狼人"])
if your_role == "平民":
    remaining_roles.extend(["平民", "平民"])
else:
    remaining_roles.extend(["平民", "平民", "平民"])
if your_role != "预言家":
    remaining_roles.append("预言家")
random.shuffle(remaining_roles)

# 构建玩家身份字典（仅内部使用）
player_roles = {"A": your_role}
for i, player in enumerate(all_players[1:]):
    player_roles[player] = remaining_roles[i]

# 关键角色标识（仅内部使用，不显示）
alive_players = all_players.copy()
out_players = []
wolves = [p for p, r in player_roles.items() if r == "狼人"]
prophet = [p for p, r in player_roles.items() if r == "预言家"][0]
current_round = 1
max_rounds = 8
found_wolves = []

# 发言模板
speech_templates = {
    "平民": [
        "我是平民，没特殊信息，{}的发言一直在回避关键问题，很可疑。",
        "昨晚出局的是{}，结合他的遗言，我觉得{}和{}中有狼人。",
        "预言家赶紧给线索！目前已找出1狼{}，剩下的狼大概率在{}里。",
        "双狼肯定会互相掩护，大家别被跟风发言的人带节奏。"
    ],
    "预言家": [
        "我是预言家！昨晚查验了{}，他是{}，这局先投他！",
        "我查了{}是好人，{}的发言明显有问题，大概率是另一只狼。",
        "已确认{}是狼，现在重点查{}，大家跟着我投票，别错投好人。"
    ],
    "狼人": [
        "我是平民，{}的发言太像预言家了，狼人今晚肯定刀他，大家先投他！",
        "{}被投出局太冤了，我觉得{}才是狼，他一直在带节奏误导大家。",
        "已找出1狼{}，剩下的狼应该是{}，大家跟我投，别让他跑了。",
        "预言家怎么还不跳身份？再藏着好人就要输了，我怀疑{}是预言家。"
    ]
}

# 遗言模板
last_words_templates = {
    "平民": [
        "我是平民！{}和{}肯定是双狼，他们一直在互相打掩护，大家一定要投对！",
        "冤死！我没查到任何线索，但{}的行为很反常，预言家赶紧查他！",
        "双狼应该是{}和{}，可惜没机会验证了，大家相信我，别被他们骗了！"
    ],
    "预言家": [
        "我是预言家！已查{}是{}，{}是{}，剩下的狼就是{}，大家别选错！",
        "预言家出局了... 最后线索：{}是狼，{}是好人，重点盯紧{}！",
        "双狼之一是{}，我本来想查{}的，可惜没机会了，大家跟着这个线索投！"
    ],
    "狼人": [
        "我是平民啊！怎么被投了... 其实{}才是狼，他一直假装好人带节奏！",
        "可惜没帮好人找出狼... {}的线索是假的，他根本不是预言家，大家别信！",
         "冤死！{}和{}的发言都有问题，肯定有一只狼在里面，大家再仔细想想！"
    ]
}

# 运行游戏（仅显示你的身份）
print("=== 6人双狼局狼人杀（无身份暴露版） ===")
for line in role_system:
    print(line)
print(f"\n你的初始身份：{your_role}")
print(f"游戏目标：找出两只狼人，全部投出即可胜利！")

while current_round <= max_rounds and len([p for p in alive_players if player_roles[p] != "狼人"]) > len([p for p in alive_players if player_roles[p] == "狼人"]):
    print(f"\n=== 第{current_round}回合 ===")
    round_out_players = []
    prophet_check_result = None
    checked_player = None
    
    # 天黑阶段
    print("\n【天黑】：所有玩家闭眼，技能阶段开始...")
    
    # 1. 双狼刀人（仅显示刀杀结果，不显示狼人身份）
    knife_target = None
    if len([w for w in wolves if w in alive_players]) >= 1:
        available_targets = [p for p in alive_players if p != "A" and p not in wolves]
        knife_target = random.choice(available_targets) if available_targets else random.choice(alive_players)
        print(f"【天黑结果】：有玩家被刀，{knife_target}出局")
        round_out_players.append(knife_target)
    else:
        print("【天黑结果】：无玩家被刀")
    
    # 2. 预言家查验（仅你可见结果，不显示其他信息）
    if prophet in alive_players:
        if your_role == "预言家":
            print(f"\n【你的预言家行动】：当前存活玩家（可查验）：{','.join([p for p in alive_players if p != 'A'])}")
            checked_player = input("请输入你要查验的玩家（不可查自己）：").strip().upper()
            while checked_player not in alive_players or checked_player == "A":
                checked_player = input(f"无效选择！请选择存活玩家（不可查自己）：{','.join([p for p in alive_players if p != 'A'])}：").strip().upper()
        else:
            checked_player = random.choice([p for p in alive_players if p != prophet])
        
        prophet_check_result = player_roles[checked_player]
        if your_role == "预言家":
            print(f"【你的查验结果】：{checked_player}的身份是{prophet_check_result}（仅你可见）")
    
    # 处理出局玩家
    for player in round_out_players:
        if player in alive_players:
            alive_players.remove(player)
            out_players.append(player)
    
    # 天亮阶段
    print(f"\n【天亮】：存活玩家：{','.join(alive_players)} | 出局玩家：{','.join(out_players)}")
    print(f"已找出狼人：{','.join(found_wolves) if found_wolves else '无'} | 剩余待找狼人：{len(wolves) - len(found_wolves)}只")
    
    # 1. 遗言阶段（仅显示遗言内容，不显示发言者身份）
    if current_round < max_rounds and round_out_players:
        print("\n【遗言阶段】：")
        for player in round_out_players:
            role = player_roles[player]
            template = random.choice(last_words_templates[role])
            target1 = random.choice(all_players)
            target2 = random.choice([p for p in all_players if p != target1])
            target3 = random.choice([p for p in all_players if p != target1 and p != target2])
            if role == "预言家" and checked_player:
                last_words = template.format(checked_player, prophet_check_result, target1, target2)
            else:
                last_words = template.format(target1, target2, target3)
            print(f"   - 出局玩家：{last_words}")
    
    # 2. 发言阶段（仅显示发言内容，不显示发言者身份）
    print("\n1. 发言阶段：")
    for player in alive_players:
        if player == "A":
            continue
        target1 = random.choice(alive_players) if alive_players else "A"
        target2 = random.choice([p for p in alive_players if p != target1]) if len(alive_players) > 1 else "B"
        last_out = out_players[-1] if out_players else target1
        found_wolf_str = found_wolves[0] if found_wolves else "无"
        
        role = player_roles[player]
        template = random.choice(speech_templates[role])
        if "{}" in template:
            if role == "预言家" and checked_player:
                speech = template.format(checked_player, prophet_check_result, target2)
            elif role == "狼人":
                speech = template.format(target1, last_out, found_wolf_str, target2)
            else:
                speech = template.format(target1, last_out, target2, found_wolf_str)
        else:
            speech = template
        print(f"   - {player}：{speech}")
    
    # 你的发言
    print(f"\n你的发言：")
    if your_role == "预言家" and checked_player:
        ref_template = random.choice(speech_templates["预言家"]).format(checked_player, prophet_check_result, target2)
    else:
        found_wolf_ref = found_wolves[0] if found_wolves else "无"
        ref_template = random.choice(speech_templates["平民"]).format(target1, last_out, target2, found_wolf_ref)
    
    your_speech = input(f"参考模板：{ref_template}\n请输入你的发言：")
    print(f"   - A：{your_speech}")
    
    # 3. 投票阶段
    print(f"\n2. 投票阶段（存活玩家：{','.join(alive_players)}）：")
    user_vote = input("请输入你要投出局的玩家：").strip().upper()
    while user_vote not in alive_players or user_vote == "A":
        user_vote = input(f"无效投票！请选择存活玩家（不能投自己）：{','.join(alive_players)}：").strip().upper()
    
    # 处理投票结果
    print(f"投票结果：{user_vote}被投出局")
    round_out_players.append(user_vote)
    alive_players.remove(user_vote)
    out_players.append(user_vote)
    
    # 投票出局遗言
    if current_round < max_rounds:
        role = player_roles[user_vote]
        template = random.choice(last_words_templates[role])
        target1 = random.choice(all_players)
        target2 = random.choice([p for p in all_players if p != target1])
        if role == "预言家" and checked_player:
            last_words = template.format(checked_player, prophet_check_result, target1, target2)
        else:
            last_words = template.format(target1, target2, random.choice(all_players))
        print(f"【遗言】：出局玩家：{last_words}")
    
    # 验证是否投中狼人（仅提示结果，不显示具体身份）
    if user_vote in wolves:
        found_wolves.append(user_vote)
        print(f"\n✅ 恭喜！你投中了一只狼人，已找出{len(found_wolves)}/{len(wolves)}只狼")
        if len(found_wolves) == len(wolves):
            print("\n=== 游戏结束 ===")
            print(f"你成功找出两只狼人，好人阵营胜利！")
            exit()
    else:
        print(f"❌ 很遗憾，你投出的不是狼人")
    
    # 检查数量平衡
    good_guys = len([p for p in alive_players if p not in wolves])
    remaining_wolves = len([p for p in alive_players if p in wolves])
    if good_guys <= remaining_wolves:
        print("\n=== 游戏结束 ===")
        print(f"好人数量不足，狼人阵营胜利！")
        exit()
    
    current_round += 1
    print(f"\n【第{current_round-1}回合结束】：当前存活{len(alive_players)}人，已找出{len(found_wolves)}只狼，剩余{max_rounds - current_round + 1}回合")

# 回合结束
print("\n=== 游戏结束 ===")
if current_round > max_rounds:
    print(f"{max_rounds}回合已结束，仅找出{len(found_wolves)}只狼（目标2只），好人阵营失败！")
else:
    print(f"狼人淘汰所有好人，狼人阵营胜利！")
# 维护对话历史
conversation_history = [
    {"role": "system", "content": game_system}
]

# 多轮对话循环
while True:
    user_input = input("请输入你要说的话：")
    
    # 添加用户消息到历史
    conversation_history.append({"role": "user", "content": user_input})
    
    # 调用API
    result = call_zhipu_api(conversation_history)
    assistant_reply = result['choices'][0]['message']['content']
    
    # 添加助手回复到历史
    conversation_history.append({"role": "assistant", "content": assistant_reply})
    
    # 打印回复
    print(assistant_reply)
    
     # TTS语音播放
    # 需要安装playsound：pip install playsound
    text_to_speech(assistant_reply)
    
    # 检查是否猜对（模型回复"再见"）
    if "再见" in assistant_reply:
        print(f"\n游戏结束！正确答案是：{current_role}")
        break