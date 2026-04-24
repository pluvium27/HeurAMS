# 贡献指南与二次开发

欢迎为此项目做出贡献!

## 开发规范

分支划分:

- `main` 分支: 稳定版本, 仅当稳定版本释出或修补版本时将 `dev` 合并到 `main` 上
- `dev` 分支: 主线开发版本, 自身仅用于非重构的问题修复和整合功能分支
- 功能与重构分支: 从 `dev` 分支创建, 命名格式为 `feature/描述` 或 `fix/描述` 或 `refactor/v版本号`
- 不要将功能与重构分支先应被合并至 `dev` 后在 `dev` 完成文档开发后再释出至 `main`

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
- 格式化不是必需的, 可以整合入一次 `style` 提交, 但 `main` 和 `dev` 分支上的代码应尽量整洁, 以便合并时审查

提交消息:

- 使用简体中文或英文撰写清晰的提交消息
- 提交消息格式: 遵循 [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) 规范, 建议使用 `koji` 工具

合并方式:

- 为了一致性和可追溯性, 项目自 v0.4.0 重构后重新初始化仓库起就禁止使用 Fast-forward 合并
- 可以设置 `git config merge.ff false`

## 设置开发环境

```bash
# 克隆仓库
git clone https://git.pluv27.top/pluv/HeurAMS
cd HeurAMS

# 可能需要切换到 dev 分支
git checkout dev

# 如果决定使用 uv (推荐)

## 首先要安装uv, 例如通过 pip 或者其他包管理器
python3 -m pip install uv

uv sync # 同步开发运行环境

uv run heurams # 验证包安装

uv run tui # 启动 TUI

# 如果决定使用原生 python 环境 (不推荐, 但我们保留了这种方式以便在不便支持 uv 与硬链接的环境和文件系统(例如 termux)运行 HeurAMS)

## 安装依赖并将 HeurAMS 安装为本地包
python3 -m pip install -r requirements.txt
python3 -m pip install -e .

python3 -m heurams # 验证安装
python3 -m heurams.__interface__ # 启动 TUI
```

## 许可证与外部引用

贡献者拥有其贡献部分的版权同意其贡献将在 AGPL-3.0 许可证下发布.

如果您认为有必要引入其他开源的 vendor, 请在 PR 中注明或手动联系以便我们审查 vendor 许可证并更改此处和网站上的关于与版权声明

如果您认为有必要引入其他专有的网络服务(就像现在项目中的 edgetts), 请也在 PR 中注明

如果您认为有必要升级某个依赖或运行环境的版本, 请也在 PR 中注明

## 新的用户界面前端与其他语言移植

HeurAMS 被设计为一个可独立于前端的程序库, 这意味着:

- 我们的内置 Textual TUI 前端不是唯一可用的前端

- 您可以在自己的项目中以独立进程/服务调用 HeurAMS (但不能在代码中链接), 而免于受 AGPL-3.0 "污染". 为了这点, 我们正在完善可选择启用的跨进程 RPC 模块, 这将成为潜进内核的跨平台标准件.

- 如果您有一个自己开发的且可用的 HeurAMS 前端 (例如我们暂未实现的 flutter 前端), 并且以 AGPL-3.0/GPL-3.0 开放源代码, 可以联系我们将它转移到 HeurAMS 的官方仓库中以便共同维护, 您将保留您的版权并可主导该仓库下的开发工作 :)

- 如果您通过独立进程/服务调用方式开发了另外的软件, 开源但不愿使用 AGPL-3.0/GPL-3.0 许可证, 也可以联系我们, 我们乐于将您的项目链接添加到友链中

- 如果您想创建程序库的其他语言 (例如 dart 或 rust) 版本以协助此语言下的方便集成, 并且同样以 AGPL-3.0/GPL-3.0 开放源代码, 也可以联系我们将它转移到 HeurAMS 的官方仓库中以便共同维护, 您将保留您的版权并可主导该仓库下的开发工作 :)

## 软件开发之外的贡献

即使您不是软件开发人员, 我们也欢迎您加入贡献!

您可以:

- 协助创建各种语言的翻译来翻译软件的界面 (但我们目前还没有 i18n 平台, 所以如果您想贡献翻译, 可能需要手动联系我们)
- 制作图像、主题、音效乃至制作开放的记忆单元集给其他用户使用
- 改进软件配套的文档
- 维护软件的开发/交流群组
- 给其他用户答疑解惑或分享自己的经验
- 在讨论区提出新想法或反馈问题

您的角色您来定!
