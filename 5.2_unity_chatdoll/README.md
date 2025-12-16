# 5.2 Unity Chatdoll - 虚拟角色语音交互

数字媒体艺术课程示范项目 - 实现 VRM 虚拟角色的实时语音交互，包含 TTS 语音合成、口型同步和自动眨眼。

## 功能特性

- 🎤 监听 JSONBin.io 实时获取文本消息
- 🔊 **Fish Audio** TTS 中文语音合成（HTTP API，简单稳定）
- 👄 uLipSync 口型同步驱动
- 👁️ VRM10 自动眨眼
- 🎭 VRM 1.0 模型支持

> **注意：** 本项目使用 Fish Audio TTS，不需要科大讯飞或 NativeWebSocket。

## 快速开始

### 1. 安装依赖包

按以下顺序导入 unitypackage：

| 包名 | 版本 | 下载 |
|------|------|------|
| UniTask | 2.5.10+ | [GitHub](https://github.com/Cysharp/UniTask) |
| UniVRM | 0.130.1+ | [GitHub](https://github.com/vrm-c/UniVRM) |
| ChatdollKit | 0.8.15+ | [GitHub](https://github.com/uezo/ChatdollKit) |
| uLipSync | 3.1.4+ | [GitHub](https://github.com/hecomi/uLipSync) |

### 2. 配置宏定义

1. `Edit → Project Settings → Player`
2. `Other Settings → Scripting Define Symbols`
3. 添加：`USE_VRM10`
4. 点击 Apply

### 3. 准备 VRM 模型

将你的 VRM 1.0 模型放入 `Assets/Models/` 文件夹。

推荐来源：
- [VRoid Hub](https://hub.vroid.com/)
- [Booth](https://booth.pm/)
- [VRoid Studio](https://vroid.com/studio)

### 4. 配置 API

#### JSONBin.io
1. 注册 https://jsonbin.io
2. 创建 Bin，获取 **Bin ID** 和 **Access Key**
3. 配置 Python 后端写入 JSONBin（参考 `5_backend_101/jsonbin.py`）

#### Fish Audio TTS
1. 注册 https://fishspeech.net
2. 获取 **API Key**（个人版有免费额度）
3. 选择声音模型，获取 **Reference ID**
4. 在 Unity Inspector 中配置到 `Fish Audio Speech Synthesizer` 组件

### 5. 场景配置

打开 `Assets/Scenes/Chatdoll.unity`

#### ChatDoll 物体
| 组件 | 配置项 |
|------|--------|
| Model Controller | Avatar Model → 你的 VRM 模型 |
| Json Bin Listener | Bin ID, Access Key |
| Fish Audio Speech Synthesizer | API Key, Reference ID |
| U Lip Sync | Profile → uLipSync-Profile-Sample-Female |
| VRM10 Blink | (使用默认值) |

#### VRM 模型物体
| 组件 | 配置项 |
|------|--------|
| U Lip Sync Expression VRM | 配置 A/I/U/E/O 口型映射 |

#### U Lip Sync 事件连接
在 ChatDoll 的 `U Lip Sync` 组件中：
- `On Lip Sync Update` → 拖入 VRM 模型
- 选择函数：`uLipSyncExpressionVRM.OnLipSyncUpdate`

## 项目结构

```
5.2_unity_chatdoll/
├── Assets/
│   ├── Scripts/                    # 原创脚本
│   │   ├── JsonBinListener.cs      # JSONBin 轮询监听
│   │   ├── FishAudioSpeechSynthesizer.cs  # Fish Audio TTS
│   │   └── VRM10Blink.cs           # VRM 眨眼控制
│   ├── Scenes/
│   │   └── Chatdoll.unity          # 主场景
│   └── Models/                     # VRM 模型（需自行准备）
├── ProjectSettings/                # Unity 项目设置
└── Packages/                       # 包管理配置
```

## 工作流程

```
Python 后端生成回复 
  ↓
写入 JSONBin.io
  ↓
Unity JsonBinListener 轮询检测（每2秒）
  ↓
检测到新消息
  ↓
Fish Audio TTS 生成语音（HTTP API）
  ↓
角色说话 + uLipSync 口型同步 + 自动眨眼
```

## 技术栈

- **TTS**: Fish Audio（HTTP REST API，无需 WebSocket）
- **口型同步**: uLipSync + VRM Expression
- **模型格式**: VRM 1.0
- **通信**: JSONBin.io（轻量级数据同步）

## 常见问题

### 口型不同步
- 检查 `U Lip Sync` 的 Profile 是否设置
- 检查 `On Lip Sync Update` 事件是否正确连接

### 眨眼不工作
- 确认添加了 `VRM10Blink` 组件（不是普通的 `Blink`）
- 确认 `USE_VRM10` 宏定义已添加

### TTS 报错 401
- 检查 Fish Audio API Key 是否正确
- 确认 API Key 没有多余空格

### TTS 报错 402
- Fish Audio 配额不足，需要充值或等待重置

## 许可证

原创代码部分采用 MIT 许可证。第三方包请遵循各自的许可协议。
