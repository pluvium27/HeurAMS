"""仓库创建向导界面"""

from pathlib import Path

import toml
from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.screen import Screen
from textual.widgets import (Button, Footer, Header, Input, Label, Markdown,
                             Select)

from heurams.context import config_var
from heurams.services.version import ver


class RepoCreatorScreen(Screen):
    BINDINGS = [("q", "go_back", "返回")]
    SUB_TITLE = "仓库创建向导"

    def __init__(self) -> None:
        super().__init__(name=None, id=None, classes=None)

    def search_templates(self):
        from pathlib import Path

        from heurams.context import config_var

        template_dir = Path(config_var.get()["paths"]["template_dir"])
        templates = list()
        for i in template_dir.iterdir():
            if i.name.endswith(".toml"):
                try:
                    import toml

                    with open(i, "r") as f:
                        dic = toml.load(f)
                        desc = dic["__metadata__.attribution"]["desc"]
                        templates.append(desc + " (" + i.name + ")")
                except Exception as e:
                    templates.append(f"无描述模板 ({i.name})")
                    print(e)
        return templates

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with ScrollableContainer(id="vice_container"):
            yield Label(f"[b]空白单元集创建向导\n")
            yield Markdown(
                "> 提示: 你可能注意到当选中文本框时底栏和操作按键绑定将被覆盖  \n只需选中(使用鼠标或 Tab)选择框即可恢复底栏功能"
            )
            yield Markdown("1. 键入单元集名称")
            yield Input(placeholder="单元集名称", id="name_input")
            yield Markdown(
                "> 单元集名称不应与现有单元集重复.  \n> 新的单元集文件将创建在 ./nucleon/你输入的名称.toml"
            )
            yield Label(f"\n")
            yield Markdown("2. 选择单元集模板")
            LINES = self.search_templates()
            """带有宏支持的空白单元集 ({ver})
古诗词模板单元集 ({ver})
英语词汇和短语模板单元集 ({ver})
"""
            yield Select.from_values(LINES, prompt="选择类型", id="template_select")
            yield Markdown("> 新单元集的版本号将和主程序版本保持同步")
            yield Label(f"\n")
            yield Markdown("3. 输入常见附加元数据 (可选)")
            yield Input(placeholder="作者", id="author_input")
            yield Input(placeholder="内容描述", id="desc_input")
            yield Button(
                "新建空白单元集",
                id="submit_button",
                variant="primary",
                classes="start-button",
            )
        yield Footer()

    def on_mount(self):
        self.query_one("#submit_button").focus()

    def action_go_back(self):
        self.app.pop_screen()

    def action_quit_app(self):
        self.app.exit()

    def on_button_pressed(self, event) -> None:
        event.stop()
        if event.button.id == "submit_button":
            # 获取输入值
            name_input = self.query_one("#name_input")
            template_select = self.query_one("#template_select")
            author_input = self.query_one("#author_input")
            desc_input = self.query_one("#desc_input")

            name = name_input.value.strip()  # type: ignore
            author = author_input.value.strip()  # type: ignore
            desc = desc_input.value.strip()  # type: ignore
            selected = template_select.value  # type: ignore

            # 验证
            if not name:
                self.notify("单元集名称不能为空", severity="error")
                return

            # 获取配置路径
            config = config_var.get()
            nucleon_dir = Path(config["paths"]["nucleon_dir"])
            template_dir = Path(config["paths"]["template_dir"])

            # 检查文件是否已存在
            nucleon_path = nucleon_dir / f"{name}.toml"
            if nucleon_path.exists():
                self.notify(f"单元集 '{name}' 已存在", severity="error")
                return

            # 确定模板文件
            if selected is None:
                self.notify("请选择一个模板", severity="error")
                return
            # selected 是描述字符串, 格式如 "描述 (filename.toml)"
            # 提取文件名
            import re

            match = re.search(r"\(([^)]+)\)$", selected)
            if not match:
                self.notify("模板选择格式无效", severity="error")
                return
            template_filename = match.group(1)
            template_path = template_dir / template_filename
            if not template_path.exists():
                self.notify(f"模板文件不存在: {template_filename}", severity="error")
                return

            # 加载模板
            try:
                with open(template_path, "r", encoding="utf-8") as f:
                    template_data = toml.load(f)
            except Exception as e:
                self.notify(f"加载模板失败: {e}", severity="error")
                return

            # 更新元数据
            metadata = template_data.get("__metadata__", {})
            attribution = metadata.get("attribution", {})
            if author:
                attribution["author"] = author
            if desc:
                attribution["desc"] = desc
            attribution["name"] = name
            # 可选: 设置版本
            attribution["version"] = ver
            metadata["attribution"] = attribution
            template_data["__metadata__"] = metadata

            # 确保 nucleon_dir 存在
            nucleon_dir.mkdir(parents=True, exist_ok=True)

            # 写入新文件
            try:
                with open(nucleon_path, "w", encoding="utf-8") as f:
                    toml.dump(template_data, f)
            except Exception as e:
                self.notify(f"保存单元集失败: {e}", severity="error")
                return

            self.notify(f"单元集 '{name}' 创建成功")
            self.app.pop_screen()
