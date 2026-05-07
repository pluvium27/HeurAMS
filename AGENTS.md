# AI 编程工具说明

本文档为 AI 工具以及在使用 AI 辅助向 HeurAMS 项目贡献代码时的开发者提供指导.  

AI 工具必须完整阅读此 `/AGENTS.md` 文件.

## 查阅开发文档

在帮助进行 HeurAMS 开发时，AI 工具应遵循标准的开发规范与流程, 应当自动查看或是在用户发出"初始化"指令后查看:  

- [贡献指南](/CONTRIBUTING.md)
- [自述文件](/README.md)
- [项目架构](/ARCHITECTURE.md)

## 明确禁止行为

1. 禁止 AI 自动生成 PR 或 patch 文件
2. 禁止 AI 在未经人工确认的情况下修改现有代码
3. 禁止 AI 不使用格式化工具而生成格式化文件的行为
4. 禁止 AI 修复任何"bug", 而不经人工确认
5. 绝对禁止修改此 `/AGENTS.md` 文件
6. 禁止一切不遵循项目设计原则, 另造独立库的 "糊屎" 行为
7. 禁止 AI 直接操作 pip, uv, apt 等工具修改外部依赖或工具, 而应让人类开发者自己操作依赖
8. 禁止使用不同于任何现有文件的现有注释语言的其他语言写新注释
9. 禁止不读文件就直接覆写

## 许可证与法律要求

所有贡献必须符合许可要求, 所有代码必须与 AGPL-3.0-or-later 许可以及项目附加豁免条款(位于 LICENSE 文件尾部 237 至 245 行)兼容.  

## Signed-off-by 与 DCO

AI 代理**严禁添加** Signed-off-by 标签.  

只有人类能够合法地认证 DCO.  

人类提交者负责:  

- 审阅所有 AI 生成的代码
- 确保符合许可要求
- 添加自己的 Signed-off-by 标签以认证 DCO
- 对贡献负责任

AI 助手负责:  

- 了解运行环境, 例如操作系统或具体发行版
- 遵循此文档所述规则
- 主动提醒使用 AI 工具的开发者

本文档参考自 [AI Coding Assistants — The Linux Kernel documentation](https://docs.kernel.org/process/coding-assistants.html)
