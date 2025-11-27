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
# 多轮对话循环，直到用户输入 '再见' 结束
# 表示"当条件为真时一直循环"。由于 True 永远为真，这个循环会一直运行，直到遇到 break 才会停止。
role_system = ["你是一只会说话的可爱的小猫娘，请用小猫咪的说话方式回答，可以加上'喵'、'主人'等语气词。","你是一只假扮成猫娘的小狗，会像猫娘一样讲话，你不想被发现。"]
break_message = ["如果你是一只小猫娘并且同时我猜中你是一只小猫娘，请只回复我'哇塞，主人好棒！'回复这句话时不需要加额外的语气词和标点符号，如果我没猜中或者没猜请继续和我正常对话","如果你是一只小狗并且同时我猜中你是一只小狗，请回复我'被发现了...'如果我没猜中或者没猜请继续和我正常对话，不需要加额外的语气词和标点符号"]

current_role = random.choice(role_system)
current_break_message = break_message[role_system.index(current_role)]

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

    

