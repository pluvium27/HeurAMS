# 潜进 (HeurAMS) - 启发式辅助记忆调度器

## 概述

"潜进" (HeurAMS: Heuristic Auxiliary Memorizing Scheduler, 启发式记忆辅助调度器) 是一个基于启发式算法与认知科学理论的辅助记忆调度器, 旨在帮助用户更高效地进行记忆工作与学习规划, 也是一个开放, 优雅, 易于扩展的间隔重复调度器实验平台, 旨在帮助研究者更高效地进行前沿记忆算法的研究.

## 项目结构

这个仓库是 "潜进" 的核心程序库在 python 语言下的实现  
包含数据模型与框架, 并内置了基于 textual 框架的前端实现 (interface 子模块)  
除了通过内置前端进行学习外, 开发者也能在 python 环境中导入 `heurams` 库, 使用框架构建其他辅助记忆功能前端或其他应用程序  

## 特性

### 间隔重复调度器

> 许多出版物都广泛讨论了不同重复间隔对学习效果的影响. 特别是, 间隔效应被认为是一种普遍现象. 间隔效应是指, 如果重复的间隔是分散/稀疏的, 而不是集中重复, 那么学习任务的表现会更好. 因此, 有观点提出, 学习中使用的最佳重复间隔是**最长的, 但不会导致遗忘的间隔**.

- 采用经实证的 SM-2 间隔迭代算法, 此算法亦用作 Anki 闪卡记忆软件的默认闪卡调度器
- 动态规划每个记忆单元的记忆间隔时间表
- 动态跟踪记忆反馈数据, 优化长期记忆保留率与稳定性

### 学习进程优化

- 元数据配置: 支持配置详细附加数据
- 自然语音: 集成文本转语音 (TTS) 功能, 支持"电台"回顾功能
- 多种谜题类型: 选择题 (MCQ), 填空题 (Cloze), 识别题 (Recognition)
- 动态内容生成: 支持宏驱动的模板系统, 根据上下文动态生成题目
- 云同步支持: 通过多种协议同步数据到远程服务器

### 实用用户界面

- 响应式 Textual 框架构建的跨平台 TUI 界面
- 支持触屏/鼠标/键盘多操作模式
- 简洁直观的复习流程设计

## 快速开始

### 从源码安装

1. 克隆仓库:

   ```bash
   git clone https://gitea.imwangzhiyu.xyz/ajax/HeurAMS
   cd HeurAMS
   ```

1. 安装依赖:

   ```bash
   pip install -r requirements.txt
   ```

1. 以开发模式安装包:

   ```bash
   pip install -e .
   ```

## 项目结构

### 架构图(待更新 0.5.0)

以下 Mermaid 图展示了 HeurAMS 的主要组件及其关系:

```mermaid
graph TB
    subgraph "用户界面层 (TUI)"
        TUI[Textual TUI]
        Widgets[界面组件]
        Screens[应用屏幕]
    end

    subgraph "服务层"
        Config[配置管理]
        Logger[日志系统]
        Timer[时间服务]
        AudioService[音频服务]
        TTSService[TTS服务]
        SyncService[同步服务]
        OtherServices[其他服务]
    end

    subgraph "内核层"
        Algorithms[算法模块]
        Particles[数据模型]
        Puzzles[谜题模块]
        Reactor[调度反应器]
    end

    subgraph "提供者层"
        AudioProvider[音频提供者]
        TTSProvider[TTS提供者]
        OtherProviders[其他提供者]
    end

    subgraph "数据层"
        Files[本地文件数据]
    end

    subgraph "上下文管理"
        Context[ConfigContext]
        CtxVar[config_var]
    end

    TUI --> Config
    TUI --> Logger
    TUI --> AudioService
    TUI --> TTSService
    TUI --> OtherServices
    Config --> Files
    Config --> Context
    AudioService --> AudioProvider
    TTSService --> TTSProvider
    OtherServices --> OtherProviders
    Reactor --> Algorithms
    Reactor --> Particles
    Reactor --> Puzzles
    Particles --> Files
    Algorithms --> Files
```

## 参与项目

欢迎参与到项目协作中! 请参阅 [CONTRIBUTING.md](CONTRIBUTING.md) 了解贡献指南.

## 许可证

### 项目本身

本项目基于 AGPL-3.0 许可证开源. 详见根目录下 [LICENSE](LICENSE) 文件.

### 第三方代码

项目在 `src/heurams/vendor/` 目录下嵌入了以下第三方代码(可能有修改):

#### py-fsrs

- 上游版本: 6.3.1
- 位置: `src/heurams/vendor/pyfsrs/`
- 原项目: [py-fsrs](https://github.com/open-spaced-repetition/py-fsrs)
- 原许可证: Copyright (c) 2026 Open Spaced Repetition Contributors
- 原许可证: MIT License, 详见 `src/heurams/vendor/pyfsrs/LICENSE`

本项目受益于他们无私且优秀的工作
