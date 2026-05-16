# 潜进 (HeurAMS) - 启发式辅助记忆调度器

## 概述

"潜进" (HeurAMS: Heuristic Auxiliary Memorizing Scheduler, 启发式记忆辅助调度器) 是一种基于启发式算法与认知科学理论的辅助记忆调度器, 旨在帮助用户更高效地进行记忆工作与学习规划,  
也是一种开放, 优雅, 易于扩展的间隔重复调度器实验平台, 旨在帮助研究者更高效地进行前沿记忆算法的研究.  

[详细介绍](INTRODUCTION.md) [屏幕截图](SCREENSHOTS.md)

<p align="left">
<a href="https://github.com/pluvium27/HeurAMS" target="_blank" rel="noopener noreferrer"><img src="https://img.shields.io/badge/GitHub-fafafa?style=for-the-badge&logo=github&logoColor=181717" alt="GitHub" /></a>
<a href="https://invent.kde.org/pluv/HeurAMS" target="_blank" rel="noopener noreferrer"><img src="https://img.shields.io/badge/KDE_Invent-1D99F3?style=for-the-badge&logo=kde&logoColor=white" alt="KDE Invent" /></a>
<a href="https://gitee.com/pluv/HeurAMS" target="_blank" rel="noopener noreferrer"><img src="https://img.shields.io/badge/Gitee-C71D23?style=for-the-badge&logo=gitee&logoColor=white" alt="Gitee" /></a>
<a href="https://git.pluv27.top/pluv/HeurAMS" target="_blank" rel="noopener noreferrer"><img src="https://img.shields.io/badge/git.pluv27.top-609926?style=for-the-badge&logo=gitea&logoColor=white" alt="git.pluv27.top" /></a>
</p>

## 快速开始

### 从包管理器安装

潜进 (包名是 `heurams`) 处于早期开发考虑, 尚未上架 PyPI, 但您可以用 pip 支持的 git 协议安装稳定版和开发版本, 这要求您的电脑上安装了 python 环境 (建议版本 3.12.13 及之后).

#### 面向用户的安装

从稳定的 `master` 分支安装, 并安装适用于用户体验的可选依赖(推荐):

```
pip install --upgrade 'heurams[basic] @ https://git.pluv27.top/pluv/HeurAMS/archive/master.zip'
```

从较前沿, 大致稳定的 `dev` 分支安装, 并安装适用于用户体验的可选依赖(如果您追求较前沿的改进):

```
pip install --upgrade 'heurams[basic] @ https://git.pluv27.top/pluv/HeurAMS/archive/dev.zip'
```

安装适用于一般计算机的通用音频模块(基于 playsound3):\
(此项不适用于 termux 环境, termux 的音频支持是内建的)

```
pip install --upgrade 'heurams[audio-playsound] @ https://git.pluv27.top/pluv/HeurAMS/archive/master.zip'
```

#### 面向开发者的安装

> [!CAUTION]
> 对于部分 Linux 发行版和 Android Termux 用户:\
> 您需要先行安装 `cmake` 和 `libzmq` 才能正确安装项目的 `zmq` 依赖.\
> 例如在 termux 上先运行 `pkg install cmake clang libzmq`.\
> 项目功能本身不依赖它, 但需要该依赖用于启动可选的调试服务器.

从 `dev` 分支进行基于 git 的可编辑安装, 并安装全部可选依赖(推荐):

```
pip install --upgrade 'heurams[all] @ https://git.pluv27.top/pluv/HeurAMS/archive/dev.zip'
```

> 您也可以从 `refactor/...` 等特定分支安装

[依赖组说明](INTRODUCTION.md#包依赖组说明)

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
