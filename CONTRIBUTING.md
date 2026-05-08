# 贡献指南与二次开发

欢迎支持此项目!

目前, 项目仓库主服务器为<a href="https://git.pluv27.top/pluv/HeurAMS" target="_blank" rel="noopener noreferrer">作者的 Gitea 实例</a>, 以保证可用性并同时接受来自多个社区的协作, 并在 <a href="https://github.com/pluvium27/HeurAMS" target="_blank" rel="noopener noreferrer">GitHub</a> 和 <a href="https://invent.kde.org/pluv/HeurAMS" target="_blank" rel="noopener noreferrer">KDE Invent</a> 设置了镜像同步.  

这丝毫不影响项目接受来自 <a href="https://github.com/pluvium27/HeurAMS" target="_blank" rel="noopener noreferrer">GitHub</a> 和 <a href="https://invent.kde.org/pluv/HeurAMS" target="_blank" rel="noopener noreferrer">KDE Invent</a> 的 PR, 在 GitHub 与 KDE Invent 所接受的 PR 会保留贡献者标识并按原样同步回所有平台, 欢迎在任意平台为项目做出贡献.  

> [!NOTE]
> 我们已经开始着手于基于 KDE 用户界面框架 `Kirigami` 的现代跨平台前端开发, 称作 "KiriMemo", 包名是 "org.kde.kirimemo", 但其并非 KDE 项目\
> 它通过 `PyOtherSide` 直接复用 python 内核, 为 Windows, Linux, macOS, Android, iOS 和 Plasma Mobile 提供现代用户界面
> 如果您善于开发 C++, QML, Qt 与 KDE 框架, 欢迎加入到 KiriMemo 项目的开发

## 开发规范

分支划分:

- `dev` 分支(也是默认分支): 主线开发分支, 自身仅用于非重构的问题修复和整合功能分支, 拉取请求在该分支合并
- `master` 分支: 稳定版本, 仅当稳定版本释出或修补版本时将 `dev` 合并到 `master` 上
- 功能与重构分支: 从 `dev` 分支创建, 命名格式为 `feature/描述` 或 `fix/描述` 或 `refactor/v版本号`
- 功能与重构分支应先合并至 `dev`, 再合并至 `master`

代码格式化:

- 安装工具:
  ```bash
  python -m pip install black autoflake mdformat
  ```
- 对于 Python, 使用 `black` 与 `autoflake` 格式化\
  命令:
  ```bash
  # black 的多线程在某些环境下有兼容性问题
  black . --workers=1
  ```
  ```bash
  # autoflake 注意排除 __init__.py
  autoflake --in-place --remove-all-unused-imports --recursive ./src/ --exclude __init__.py
  ```
- 对于 Markdown, 使用 `mdformat` 格式化
  命令:
  ```bash
  mdformat --number .
  ```
- 对于 Textual CSS, 可以使用 `prettier` 格式化
- 格式化不是必需的, 可以整合入一次 `style` 提交, 但 `master` 和 `dev` 分支上的代码应尽量整洁, 以便合并时审查

提交消息:

- 使用简体中文或英文撰写清晰的提交消息
- 提交消息格式: 遵循 [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) 规范, 建议使用 `koji` 工具

合并方式:

- 为了一致性和可追溯性, 项目自 v0.4.0 重构后重新初始化仓库起就禁止使用 Fast-forward 合并
- 可以设置 `git config merge.ff false`

## 设置开发环境

```bash
git clone https://git.pluv27.top/pluv/HeurAMS # 默认分支为 dev, 所以不必切换分支

cd HeurAMS

# 如果决定使用 uv (推荐)

python3 -m pip install uv

uv sync --all-extras # 同步开发运行环境

uv run heurams # 验证包安装

uv run heurams-tui # 启动 TUI

# 如果决定使用原生 python 环境 (不推荐, 但我们保留了这种方式以便在不便支持 uv 与硬链接的环境和文件系统(例如 termux)上运行)

python3 -m pip install -e .[all] # 安装依赖并将 HeurAMS 安装为本地包

python3 -m heurams # 验证安装

python3 -m heurams.interface # 启动 TUI
```

## 许可证与外部引用

贡献者拥有其贡献部分的版权同意其贡献将在 AGPL-3.0 许可证(包括附加的本机 API 调用豁免条款)下发布.

如有以下情况, 请在 PR 描述中注明:

- 如果需要引入其他开源 vendor
- 如果需要引入其他专有的网络服务(例如当前项目中的 edgetts)
- 如果需要升级某个依赖或运行环境的版本

## 新的用户界面前端

HeurAMS 被设计为一个可独立于前端的程序库, 这意味着:

- 我们的内置 Textual TUI 前端不是唯一可用的前端

- 如果您有一个自己开发的且可用的 HeurAMS 前端 (例如未实现的 Flutter 前端), 并且以 AGPL-3.0/GPL-3.0 开放源代码, 可以联系我们将它转移到 HeurAMS 的官方仓库中以便共同维护, 您将保留您的版权并可主导该仓库下的开发工作 :)

- 您还可以在自己的项目中以独立进程/服务调用 HeurAMS, 根据 AGPL-3.0 及本项目的附加许可条款, 如果调用发生在同一主机上且不涉及外部网络转发, 则可豁免许可证规定的特定义务而免于受 AGPL-3.0 "污染". 为了这点, 我们正在完善可选择启用的跨进程 RPC 模块, 这将成为潜进内核的跨平台标准件.

- 如果您通过独立进程/服务调用方式开发了另外的软件, 开源但不愿使用 AGPL-3.0/GPL-3.0 许可证, 也可以联系我们, 我们乐于将您的项目链接添加到友链中

## 软件开发之外的贡献

即使您不是软件开发人员, 我们也欢迎您加入贡献!

您可以:

- 协助创建或核对各种语言的翻译来翻译软件的界面和文档
- 制作开放的记忆单元集(包括但不限于文字、图像、音效)给其他用户使用
- 改进软件配套的文档
- 给其他用户答疑解惑或分享自己的经验
- 在讨论区提出新想法或反馈问题

您的角色您来定!
