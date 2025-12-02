from logic import should_exit_by_user, should_exit_by_ai
from chat import chat_once


PORTRAIT = """
WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWMWWWWWWWWWWWWWWWWW

"""


def main(role_name: str = "宋曙延"):
    """
    主程序入口：初始化对话历史，运行主循环。

    逻辑基本等价于原 `4.2_memory_clonebot.py` 的命令行对话循环：
    - 不保存对话到文件，所有历史仅存在于内存
    - 通过角色记忆 + 人格设定构造 system 提示词
    - 根据用户或 AI 的“再见”判断结束对话
    """
    conversation_history = []

    print("✓ 已加载初始记忆，开始对话（对话记录不会保存）")

    try:
        while True:
            user_input = input('\n请输入你要说的话（输入"再见"退出）：')

            # 用户主动结束
            if should_exit_by_user(user_input):
                print("对话结束")
                break

            # 调用一次对话
            assistant_reply = chat_once(conversation_history, user_input, role_name=role_name)

            # 打印头像 + 回复
            print(PORTRAIT + "\n" + assistant_reply)

            # 根据 AI 回复判断是否结束
            if should_exit_by_ai(assistant_reply):
                print("\n对话结束")
                break

    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
    except Exception as e:
        print(f"\n\n发生错误: {e}")


if __name__ == "__main__":
    main()
#