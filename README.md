# 潜进 (HeurAMS) - 启发式辅助记忆调度器

## 概述

"潜进" (HeurAMS: Heuristic Auxiliary Memorizing Scheduler, 启发式记忆辅助调度器) 是一种基于启发式算法与认知科学理论的辅助记忆调度器, 旨在帮助用户更高效地进行记忆工作与学习规划,  
也是一种开放, 优雅, 易于扩展的间隔重复调度器实验平台, 旨在帮助研究者更高效地进行前沿记忆算法的研究.  
<p align="left">
<a href="https://github.com/pluvium27/HeurAMS" target="_blank" rel="noopener noreferrer"><img src="https://img.shields.io/badge/GitHub-fafafa?style=for-the-badge&logo=github&logoColor=181717" alt="GitHub" /></a>
<a href="https://invent.kde.org/pluv/HeurAMS" target="_blank" rel="noopener noreferrer"><img src="https://img.shields.io/badge/KDE_Invent-1D99F3?style=for-the-badge&logo=kde&logoColor=white" alt="KDE Invent" /></a>
<a href="https://gitee.com/pluv/HeurAMS" target="_blank" rel="noopener noreferrer"><img src="https://img.shields.io/badge/Gitee-C71D23?style=for-the-badge&logo=gitee&logoColor=white" alt="Gitee" /></a>
<a href="https://git.pluv27.top/pluv/HeurAMS" target="_blank" rel="noopener noreferrer"><img src="https://img.shields.io/badge/git.pluv27.top-609926?style=for-the-badge&logo=gitea&logoColor=white" alt="git.pluv27.top" /></a>
</p>

## 关于此仓库

此仓库为 "潜进" 的核心程序库在 python 语言下的实现\
包含数据模型与框架, 并内置了基于 textual 框架的前端实现 (interface 子模块)\
除了通过内置前端进行学习外, 开发者也能在 python 环境中导入 `heurams` 库或使用 `RPC` 与 `heurams` 程序库实例通讯, 使用框架构建其他辅助记忆功能前端或其他应用程序

潜进项目的所有仓库如下:

| 项目名称 | 状态 | 说明 | 包名 | 技术栈 | 目标平台 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| HeurAMS | 开发中<br/>原型可用 | 提供通用核心程序库与基本用户界面 | `heurams` | Python | 标准 Python 环境 |
| KiriMemo | 开发中<br/>原型可用 | 基于 KDE 技术的现代跨平台前端 | `org.kde.kirimemo` | C++, Qt6, Kirigami, PyOtherSide | 桌面与移动设备 |
| ArkMemo | 开发中 | 基于 ArkUI 的现代跨平台前端 | `top.pluv27.arkmemo` | ArkTS, ArkUI | 移动设备 |
| HeurStudio | 计划中 | AI 辅助的单体单元集高级创建与编辑工具 | `top.pluv27.heurstudio` | C++, Qt6, Kirigami, PyOtherSide | 桌面 |
| HeurSync | 开发中 | 用户数据同步服务器<br/>集成 Web 前端与排行榜 | `heursync` | Go, SQL | 网页与服务器 |
| HeurRepo | 开发中 | 单元集文档源服务器<br/>与单元集分享平台 | `heurrepo` | Go, SQL | 网页与服务器 |

尽管现在后三样有点画大饼的意思, 但是我们的路线是明了的  

## 特性

### 间隔重复调度器

> 许多出版物都广泛讨论了不同重复间隔对学习效果的影响. 特别是, 间隔效应被认为是一种普遍现象. 间隔效应是指, 如果重复的间隔是分散/稀疏的, 而不是集中重复, 那么学习任务的表现会更好. 因此, 有观点提出, 学习中使用的最佳重复间隔是**最长的, 但不会导致遗忘的间隔**.

- 软件开箱即用, 无需多加配置即可使用默认的 `SM-2` 算法进行学习
- 算法模块是 "潜进" 内核 (heurams.kernel) 中的一等公民, 内核天然支持插拔各型算法
- 无需安装繁杂的插件即可分单元集完成算法快速切换与调优, 研究者可以方便地修改算法模块以便捷地进行研究与测试
- 默认使用 `SM-2` 简单间隔重复算法, 此算法亦用作 `Anki` 闪卡记忆软件的默认闪卡调度器
- 还内置了 `NSP-0` 筛选用非间隔重复算法以便快速筛选记忆内容, `FSRS` 先进间隔重复算法作为效率更高的调度器, 与 `SM-15M (移植自 sm.js 项目)` 复杂间隔重复算法(逆向工程)
- 算法模块可以标记记忆项目, 也可以动态规划每个记忆单元的记忆间隔时间表, 动态跟踪记忆反馈数据, 以优化长期记忆保留率与稳定性
- 得益于项目的模块化架构与单元集结构设计, 同一个单元集可以与任意种算法共存并互通, 这对研究者及想探索/实验高效率方法的用户极其友好

### 多模态学习进程

与 Anki 的 SQLite `.apkg` 包不同, 我们坚持使用人类可读的文件夹组织单元集, 这带来了若干好处, 包括:

- 人类可读: 您可以用任意工具, 乃至一个记事本自由修改记忆载荷数据而无需打开软件
- 元数据配置: 配置自由度极高, 可以任意组合, 重造, 乃至创造新内容
- 测验, 算法与知识互相隔离: 一条知识不再是单一的闪卡, 不仅可以用若干不同的算法规划, 还可以用多种并行的谜题类型测验, 极大地提升学习效果和丰富度. 作为学习者, 您无需担忧概念复杂--仅需从云端下载单元集即可开箱即用上述特性!
- 多模态学习
  - 软件自身集成了文本转语音 (TTS) , 音频与语言模型 (LLM) 模块, 这些功能乃至功能本身都是可插拔, 可扩展, 可切换驱动的, 这为内容创建了极大的丰富度
  - 软件内置多种谜题类型, 包括选择题 (MCQ), 填空题 (Cloze) 与识别题 (Recognition), 您可在同一单元应用多种, 或是选择性启用
  - 软件天然支持动态内容生成, 支持宏驱动的模板系统, 根据上下文乃至语言模型动态生成知识点的解析
  - 在间隔重复研究尚被 SuperMemo 系列独占的时代, Wozniak 就早已表示 "如果不能理解知识, 就无需记忆它". 今天, 我们依然相信理解是记忆的基石
- 云同步与分享优化:
  - 由于记忆数据和单元集文件都是文本文件, 故可进行快速的增量同步而无需完整地上传所有文件, 并且设计天然支持版本控制
  - 如果您想分享单文件, 软件也支持导出为压缩包或合并成单文本文件以通过纯文本文件形式在 pastebin 等平台分享
- 性能提升: 得益于现代且支持分块的文件组织结构, 潜进能在保持高自由度的同时仅使用 python 就能达到敏捷且低占用的用户体验
- AI 辅助友好: 想象您有一些 `.apkg` 牌组或一大段教材内容, 您可以方便且高效率地使用 AI 工具以创建可在 HeurAMS 使用的单元集

### 内置实用用户界面

尽管不是唯一前端, 但响应式 Textual 框架构建的内置终端用户界面在多种场景下仍具有独特优势:

- 跨平台, 并支持触屏/鼠标/键盘多操作模式
- 与几乎所有现代终端模拟器相容
- 对于<a href="https://www.arewesixelyet.com/" target="_blank" rel="noopener noreferrer">支持 sixel 协议的终端模拟器</a>, 可高清显示图像内容
- 对于不支持 sixel 协议的终端模拟器, 也支持图片低清的兼容显示模式
- 可通过 textual-web 作为服务部署, 并在任意浏览器使用
- 简洁直观, 键盘友好, 全功能且高效率的用户界面设计
- 易于嵌入: 可在 getty/kmscon 中运行而无需任何桌面图形服务
- 资源占用小, 运行流畅, 不拖泥带水
- 便于测试与调试程序库

查看[屏幕截图](SCREENSHOTS.md).

## 快速开始

### 从包管理器安装

潜进 (包名是 `heurams`) 处于早期开发考虑, 尚未上架 PyPI, 但您可以用我们的基础设施安装稳定版和开发版本.

#### 稳定版本

从 `master` 分支安装, 并安装适用于用户体验的可选依赖(推荐):

```
pip install --upgrade 'heurams[basic] @ git+https://git.pluv27.top/pluv/heurams.git@master'
```

安装适用于一般计算机的通用音频模块(基于 playsound3):\
(此项不适用于 termux 环境, termux 的音频支持是内建的)

```
pip install --upgrade 'heurams[audio-playsound] @ git+https://git.pluv27.top/pluv/heurams.git@master'
```

#### 开发版本

> [!CAUTION]
> 对于部分 Linux 发行版和 Android Termux 用户:\
> 您需要先行安装 `cmake` 和 `libzmq` 才能正确安装项目的 `zmq` 依赖.\
> 例如在 termux 上先运行 `pkg install cmake clang libzmq`.\
> 项目功能本身不依赖它, 但需要该依赖用于启动可选的调试服务器.

从 `dev` 分支安装, 并安装全部可选依赖(推荐):

```
pip install --upgrade 'heurams[all] @ git+https://git.pluv27.top/pluv/heurams.git@dev'
```

#### 依赖组说明

由于部分依赖只被少数功能需要, 所以我们把可选依赖分得比较细, 前面提供的命令会安装部分可选依赖, 以下是依赖组列表:

| 依赖组 | 包含模块 | 说明 |
|--------|----------|------|
| 最小化安装 | tabulate, toml, transitions | 核心驱动程序库, 始终必需 |
| interface | textual | 基本用户界面依赖 |
| algo-fsrs | fsrs | FSRS 算法模块 |
| tts-edgetts | edge-tts | 微软文本转语音 |
| llm | llms-py | API 调用 |
| audio-playsound | playsound3 | 通用音频模块 |
| dev | zmq, pytest, pytest-cov | 开发调试与测试工具 |
| basic | [tts-edgetts], [llm], [algo-fsrs] | 适用于用户体验的较轻依赖组(推荐) |
| all | 以上所有依赖 | 完整安装组 |

### 从源码安装

我们提供原生 python 和 uv 两种安装方式.\
详见[贡献指南](CONTRIBUTING.md).

## 常见问题 (FAQ)

详见[常见问题](FAQ.md).

## 项目架构

详见[架构说明](ARCHITECTURE.md).

## 参与项目

欢迎参与到项目协作中!\
详见[贡献指南](CONTRIBUTING.md).\
关于 AI 辅助开发的说明, 请参阅 [AGENTS.md](AGENTS.md).

## 项目标识

HeurAMS 项目标识如下, 文件(位图和矢量图)位于 `./src/heurams/assets/art/` 目录.

<img src="src/heurams/assets/art/banner128-light.png" height="96px" title="位图横幅(不透明)">
<div style="display: flex; flex-wrap: wrap; gap: 5px;">
  <img src="src/heurams/assets/art/logo.svg" height="96px" title="矢量图标">
  <img src="src/heurams/assets/art/logo-mono-light.svg" height="96px" title="单色明亮矢量图标">
  <img src="src/heurams/assets/art/logo-mono-dark.svg" height="96px" title="单色暗色矢量图标">
</div>

颜色分别是: `#1660A5 (海蓝色)` `#545F70 (蓝灰色)` `#FFFFFF (单色明亮图标白色)` `#1A1A1A (单色暗色图标深黑色)` `#2f2f35 (文字颜色)`.


## 许可证

### 项目本身

本项目基于 AGPL-3.0 许可证开放源代码, 并有一个豁免本机 API 调用的附加条款, 较标准 AGPL-3.0 更松.

详见根目录下 [LICENSE](LICENSE) 文件.

### 第三方代码

项目在 `src/heurams/vendor/` 目录下嵌入或在其他位置间接使用了以下第三方代码(可能有修改):

#### SM.js (slaypni)

- 上游版本: commit `6e3bb4a` (2015年2月4日上游已停止维护)
- 引用方式: 将 coffeescript 重写为 python 并间接引用, 数学原理一致; 并对重写后代码进行逻辑, 性能与标准化 API 改进
- 位置: `src/heurams/kernel/algorithms/sm15m*.py`
- 原项目: [SM.js](https://github.com/slaypni/SM-15)
- 原版权: Copyright (c) 2014 Kazuaki Tanida
- 原许可证: MIT License

本项目受益于他们无私且优秀的工作.
