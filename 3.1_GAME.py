import requests
import json
import random
import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading

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

class GameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("门前来客 - 游戏")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)  # 设置最小窗口尺寸
        self.root.configure(bg="#2b2b2b")
        
        # 游戏设置
        self.role_system = ["人类", "窃皮者"]
        self.current_role = random.choice(self.role_system)
        self.game_over = False
        
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

现在开始游戏，等待用户提问或决定是否开门。"""

        # 维护对话历史
        self.conversation_history = [
            {"role": "system", "content": self.game_system}
        ]
        
        self.setup_ui()
        
        # 确保窗口完全显示后再初始化
        self.root.update_idletasks()
        self.root.after(50, self.show_welcome_message)
    
    def setup_ui(self):
        # 标题栏
        title_frame = tk.Frame(self.root, bg="#2b2b2b", pady=10)
        title_frame.pack(fill=tk.X)
        
        # 使用通用字体设置
        import sys
        if sys.platform == "win32":
            title_font = ("微软雅黑", 18, "bold")
            status_font = ("微软雅黑", 10)
            chat_font = ("微软雅黑", 11)
        else:
            title_font = ("Arial", 18, "bold")
            status_font = ("Arial", 10)
            chat_font = ("Arial", 11)
        
        title_label = tk.Label(
            title_frame, 
            text="🚪 门前来客 🚪", 
            font=title_font,
            bg="#2b2b2b",
            fg="#ffffff"
        )
        title_label.pack()
        
        status_label = tk.Label(
            title_frame,
            text="游戏进行中...",
            font=status_font,
            bg="#2b2b2b",
            fg="#aaaaaa"
        )
        status_label.pack()
        self.status_label = status_label
        
        # 创建主容器，使用grid布局确保正确的空间分配
        main_container = tk.Frame(self.root, bg="#2b2b2b")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # 配置grid权重，确保对话区域可以扩展，输入区域固定
        main_container.grid_rowconfigure(0, weight=1)  # 对话区域可扩展
        main_container.grid_rowconfigure(1, weight=0)  # 输入区域固定大小
        main_container.grid_columnconfigure(0, weight=1)
        
        # 对话显示区域 - 放在主容器中，占据大部分空间
        chat_frame = tk.Frame(main_container, bg="#2b2b2b", padx=10, pady=10)
        chat_frame.grid(row=0, column=0, sticky="nsew")
        
        # 添加对话区域标题
        chat_label = tk.Label(
            chat_frame,
            text="💬 对话记录",
            font=status_font,
            bg="#2b2b2b",
            fg="#ffffff",
            anchor="w"
        )
        chat_label.pack(fill=tk.X, pady=(0, 5))
        
        # 对话显示文本框，添加边框使其更明显
        text_container = tk.Frame(chat_frame, bg="#4a9eff", padx=2, pady=2)
        text_container.pack(fill=tk.BOTH, expand=True)
        
        self.chat_display = scrolledtext.ScrolledText(
            text_container,
            wrap=tk.WORD,
            font=chat_font,
            bg="#1e1e1e",
            fg="#ffffff",
            insertbackground="#ffffff",
            state=tk.DISABLED,
            padx=15,
            pady=15,
            relief=tk.FLAT,
            bd=0
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        
        # 输入区域 - 放在主容器底部，使用grid确保始终可见
        input_frame = tk.Frame(main_container, bg="#2b2b2b", padx=15, pady=15)
        input_frame.grid(row=1, column=0, sticky="ew")  # 固定在底部，水平填充
        
        # 添加输入提示标签
        input_label = tk.Label(
            input_frame,
            text="💬 输入消息：",
            font=status_font,
            bg="#2b2b2b",
            fg="#ffffff"
        )
        input_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # 输入框容器，添加边框效果
        entry_container = tk.Frame(input_frame, bg="#4a9eff", padx=2, pady=2)
        entry_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.input_entry = tk.Entry(
            entry_container,
            font=chat_font,
            bg="#ffffff",
            fg="#000000",
            insertbackground="#000000",
            relief=tk.SOLID,
            bd=1,
            state=tk.NORMAL,  # 明确设置为正常状态
            exportselection=True,  # 允许选择和复制
            takefocus=True  # 允许获得焦点
        )
        self.input_entry.pack(fill=tk.BOTH, expand=True, ipady=10, padx=5)
        
        # 绑定所有必要的事件
        self.input_entry.bind("<Return>", lambda e: self.send_message())
        self.input_entry.bind("<Button-1>", lambda e: self.ensure_input_enabled())
        self.input_entry.bind("<FocusIn>", lambda e: self.on_input_focus_in())
        self.input_entry.bind("<Key>", lambda e: self.on_input_key())  # 监听按键事件
        
        # 延迟设置焦点，确保UI完全加载
        self.root.after(200, lambda: self.ensure_input_enabled())
        
        # 发送按钮容器
        button_container = tk.Frame(input_frame, bg="#2b2b2b")
        button_container.pack(side=tk.LEFT, padx=(10, 0))
        
        send_button = tk.Button(
            button_container,
            text="发送",
            font=(chat_font[0], chat_font[1], "bold"),
            bg="#4a9eff",
            fg="#ffffff",
            activebackground="#3a8eef",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            padx=25,
            pady=12,
            command=self.send_message,
            cursor="hand2"
        )
        send_button.pack()
    
    def ensure_input_enabled(self):
        """确保输入框可用并获取焦点"""
        if not self.game_over:
            try:
                # 确保输入框状态正常
                current_state = str(self.input_entry.cget("state"))
                if current_state != "normal":
                    self.input_entry.config(state=tk.NORMAL)
                
                # 强制获取焦点
                self.input_entry.focus_set()
                self.input_entry.icursor(tk.END)  # 将光标移到末尾
                
                # 更新UI
                self.root.update_idletasks()
            except Exception as e:
                print(f"输入框启用错误: {e}")
    
    def on_input_focus_in(self):
        """输入框获得焦点时的处理"""
        self.input_entry.config(insertbackground="#000000")
        self.ensure_input_enabled()
    
    def on_input_key(self):
        """输入框按键事件处理"""
        # 确保输入框始终可用
        if str(self.input_entry.cget("state")) != "normal" and not self.game_over:
            self.input_entry.config(state=tk.NORMAL)
    
    def show_welcome_message(self):
        # 确保对话区域可见
        self.root.update_idletasks()  # 强制更新UI
        
        # 确保输入框可用并获取焦点
        self.input_entry.config(state=tk.NORMAL)
        self.input_entry.focus_set()
        
        welcome_text = "🎮 游戏开始！\n\n"
        welcome_text += "有人在你家门口敲门...\n"
        welcome_text += "你需要通过对话来判断门外的是'人类'还是'窃皮者'。\n"
        welcome_text += "小心，做出错误的选择可能会让你失去一切...\n\n"
        welcome_text += "💡 提示：你可以提问、观察，或者直接决定是否开门。\n"
        welcome_text += "=" * 50 + "\n\n"
        
        self.append_to_chat(welcome_text)
        
        # 发送初始消息给AI（延迟执行，避免阻塞UI初始化）
        self.root.after(500, self.send_initial_ai_message)
    
    def send_initial_ai_message(self):
        """发送初始消息触发AI的第一条回复"""
        # 直接调用process_message，它会处理消息添加
        threading.Thread(target=self.process_initial_message, daemon=True).start()
    
    def process_initial_message(self):
        """处理初始AI消息"""
        try:
            # 添加初始用户消息
            self.conversation_history.append({"role": "user", "content": "开始游戏"})
            
            # 调用API
            result = call_zhipu_api(self.conversation_history)
            assistant_reply = result['choices'][0]['message']['content']
            
            # 添加助手回复到历史
            self.conversation_history.append({"role": "assistant", "content": assistant_reply})
            
            # 在主线程中更新UI
            self.root.after(0, self.update_chat_with_ai_response, assistant_reply, "开始游戏")
            
        except Exception as e:
            error_msg = f"无法连接到AI服务：{str(e)}\n请检查网络连接或API配置。"
            self.root.after(0, lambda: self.append_to_chat(f"⚠️ {error_msg}\n\n"))
            self.root.after(0, lambda: self.status_label.config(text="连接失败", fg="#ff4444"))
            self.root.after(0, lambda: self.input_entry.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.input_entry.focus_set())  # 确保输入框可用并聚焦
    
    def append_to_chat(self, text, tag=None):
        self.chat_display.config(state=tk.NORMAL)
        if tag:
            self.chat_display.insert(tk.END, text, tag)
        else:
            self.chat_display.insert(tk.END, text)
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def send_message(self):
        if self.game_over:
            messagebox.showinfo("游戏已结束", "游戏已经结束，请重新启动程序开始新游戏。")
            return
        
        # 确保输入框可用
        self.ensure_input_enabled()
        
        # 获取用户输入
        try:
            user_input = self.input_entry.get().strip()
        except:
            # 如果获取失败，尝试重新启用输入框
            self.ensure_input_enabled()
            user_input = self.input_entry.get().strip()
        
        if not user_input:
            return
        
        # 显示用户消息
        self.append_to_chat(f"【你】{user_input}\n\n", "user")
        self.input_entry.delete(0, tk.END)
        
        # 临时禁用输入（但保持可见）
        self.input_entry.config(state=tk.DISABLED)
        self.status_label.config(text="AI正在思考...", fg="#ffaa00")
        
        # 在新线程中调用API
        threading.Thread(target=self.process_message, args=(user_input,), daemon=True).start()
    
    def process_message(self, user_input):
        try:
            # 添加用户消息到历史
            self.conversation_history.append({"role": "user", "content": user_input})
            
            # 调用API
            result = call_zhipu_api(self.conversation_history)
            assistant_reply = result['choices'][0]['message']['content']
            
            # 添加助手回复到历史
            self.conversation_history.append({"role": "assistant", "content": assistant_reply})
            
            # 在主线程中更新UI
            self.root.after(0, self.update_chat_with_ai_response, assistant_reply, user_input)
            
        except Exception as e:
            self.root.after(0, self.show_error, str(e))
    
    def update_chat_with_ai_response(self, assistant_reply, user_input):
        # 显示AI回复
        self.append_to_chat(f"【门外来客】{assistant_reply}\n\n", "ai")
        
        # 播放TTS语音（在后台线程中执行，不阻塞UI）
        if TTS_AVAILABLE:
            # 清理文本，移除特殊字符和标记，只保留对话内容
            clean_text = assistant_reply.strip()
            # 移除常见的标记符号
            clean_text = clean_text.replace("【", "").replace("】", "")
            # 在后台线程中播放语音
            threading.Thread(target=self.play_tts, args=(clean_text,), daemon=True).start()
        
        # 重新启用输入并设置焦点（延迟一点确保UI更新完成）
        self.root.after(100, lambda: self.ensure_input_enabled())
        self.status_label.config(text="游戏进行中...", fg="#aaaaaa")
        
        # 检查是否猜对（模型回复"再见"）
        if "再见" in assistant_reply:
            self.end_game(f"游戏结束！正确答案是：{self.current_role}")
            return
        
        # 检查用户是否决定开门
        if "开门" in user_input:
            if self.current_role == "窃皮者":
                result_text = "\n💀 你死了。门缝里伸出的手冰冷而湿粘，你的皮肤被换走了。\n"
            else:
                result_text = "\n✅ 你很安全。门外只是疲惫的人类旅人，他感激地点了点头。\n"
            self.end_game(result_text + f"\n游戏结束！正确答案是：{self.current_role}")
    
    def play_tts(self, text):
        """在后台线程中播放TTS语音"""
        try:
            if TTS_AVAILABLE and text:
                # 过滤掉太短的文本或只有标点的文本
                if len(text.strip()) > 0:
                    text_to_speech(text)
            else:
                if not TTS_AVAILABLE:
                    print("TTS不可用，跳过语音播放")
        except Exception as e:
            # TTS失败不影响游戏，只打印错误
            print(f"TTS播放失败: {e}")
            import traceback
            traceback.print_exc()
    
    def end_game(self, message):
        self.game_over = True
        self.append_to_chat("=" * 50 + "\n")
        self.append_to_chat(message + "\n")
        self.append_to_chat("=" * 50 + "\n")
        self.status_label.config(text="游戏已结束", fg="#ff4444")
        self.input_entry.config(state=tk.DISABLED)
        messagebox.showinfo("游戏结束", message)
    
    def show_error(self, error_msg):
        self.append_to_chat(f"❌ 错误：{error_msg}\n\n")
        self.input_entry.config(state=tk.NORMAL)
        self.input_entry.focus_set()  # 错误后重新聚焦
        self.status_label.config(text="发生错误", fg="#ff4444")
        messagebox.showerror("错误", f"API调用失败：{error_msg}")

def main():
    try:
        root = tk.Tk()
        app = GameGUI(root)
        root.mainloop()
    except Exception as e:
        import traceback
        error_msg = f"程序启动失败：\n{str(e)}\n\n{traceback.format_exc()}"
        print(error_msg)
        # 尝试显示错误对话框
        try:
            root = tk.Tk()
            root.withdraw()  # 隐藏主窗口
            messagebox.showerror("启动错误", error_msg)
        except:
            pass

if __name__ == "__main__":
    main()