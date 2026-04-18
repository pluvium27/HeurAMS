# 贡献指南

欢迎为此项目做出贡献!\
本项目是一个开源项目, 我们鼓励社区成员参与改进.

## 开发规范

1. 分支划分:
   - `main` 分支: 稳定版本
   - `dev` 分支: 开发版本
   - 功能分支: 从 `dev` 分支创建, 命名格式为 `feature/描述` 或 `fix/描述` 或 `refactor/描述`
1. 代码风格:
   - 请使用 Black 格式化代码
   - 遵循 PEP 8 规范
   - 添加适当的文档字符串
1. 提交消息:
   - 使用简体中文或英文撰写清晰的提交消息
   - 格式: 遵循 Conventional Commits 规范
1. 合并方式:
   - 不使用 Fast-forward 合并
   - 可以设置 `git config merge.ff false`

## 设置开发环境

```bash
# 克隆仓库
git clone https://gitea.imwangzhiyu.xyz/ajax/HeurAMS

cd HeurAMS

# 你可能需要切换分支

# 安装依赖
pip install -r requirements.txt

# 安装开发版本
pip install -e .
```

## 许可证

贡献者同意其贡献将在 AGPL-3.0 许可证下发布.
