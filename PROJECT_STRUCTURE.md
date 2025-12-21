# 项目结构说明

## 目录结构

```
.
├── api/                    # API调用模块
│   ├── __init__.py
│   └── zhipu_api.py       # 智谱AI API调用
│
├── memory/                 # 记忆系统模块
│   ├── __init__.py
│   ├── config.py          # 记忆配置（文件夹路径、角色映射）
│   └── loader.py          # 记忆文件加载器
│
├── roles/                 # 角色系统模块
│   ├── __init__.py
│   ├── personalities.py   # 角色人格设定数据
│   └── role_manager.py    # 角色管理器（整合记忆和人格）
│
├── chat/                  # 聊天相关模块
│   ├── __init__.py
│   ├── portrait.py        # ASCII头像
│   └── display.py         # 对话显示功能
│
├── logic/                 # 业务逻辑模块
│   ├── __init__.py
│   ├── rules.py           # 对话规则（结束对话规则等）
│   └── conversation.py    # 对话处理逻辑
│
└── main/                  # 主程序入口
    ├── __init__.py
    └── app.py             # Streamlit主程序
```

## 模块说明

### api/
负责与外部API的交互，目前包含智谱AI的API调用功能。

### memory/
负责加载和管理角色的初始记忆文件，从JSON文件中读取角色的历史对话记录。

### roles/
负责角色系统的管理，包括：
- 角色人格设定
- 整合记忆和人格设定生成完整的角色prompt

### chat/
负责聊天界面的显示相关功能，包括ASCII头像和对话历史显示。

### logic/
包含业务逻辑处理，如：
- 对话处理
- 结束对话检测
- 对话规则定义

### main/
Streamlit应用的主入口，整合所有模块，提供完整的Web界面。

## 运行方式

运行主程序：
```bash
streamlit run main/app.py
```

## 模块依赖关系

```
main/app.py
  ├── roles (角色系统)
  │   └── memory (记忆加载)
  ├── chat (显示功能)
  └── logic (业务逻辑)
      └── api (API调用)
```













