#!/usr/bin/env python3
from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label, Markdown, Static

import heurams.services.version as version
from heurams.context import *


class AboutScreen(Screen):

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with ScrollableContainer(id="about_container"):
            yield Label("[b]关于与版本信息[/b]")
            about_text = f"""
# 关于 "潜进"  

版本 {version.ver} {version.stage.capitalize()}
  
开发代号: {version.codename.capitalize()}  

一个基于启发式算法的开放源代码记忆调度器, 旨在帮助用户更高效地进行记忆工作与学习规划.  

以 AGPL-3.0 开放源代码  

开发人员:  

- Wang Zhiyu([@pluvium27](https://github.com/pluvium27)): 项目作者  

特别感谢:

- [Piotr A. Woźniak](https://supermemo.guru/wiki/Piotr_Wozniak): SuperMemo-2 算法
- [Thoughts Memo](https://www.zhihu.com/people/L.M.Sherlock): 文献参考

# 参与贡献

我们是一个年轻且包容的社区, 由技术人员, 设计师, 文书工作者, 以及创意人员共同构成,  

通过我们协力开发的软件为所有人谋取福祉.  

上述工作不可避免地让我们确立了下列价值观 (取自 KDE 宣言):  

 - 开放治理 确保更多人能参与我们的领导和决策进程;  

 - 自由软件 确保我们的工作成果随时能为所有人所用;  

 - 多样包容 确保所有人都能加入社区并参加工作;  

 - 创新精神 确保新思路能不断涌现并服务于所有人;  

 - 共同产权 确保我们能团结一致;  

 - 迎合用户 确保我们的成果对所有人有用.  

综上所述, 在为我们共同目标奋斗的过程中, 我们认为上述价值观反映了我们社区的本质, 是我们始终如一地保持初心的关键所在.  

这是一项立足于协作精神的事业, 它的运作和产出不受任何单一个人或者机构的操纵.  

我们的共同目标是为人人带来高品质的辅助记忆 & 学习软件.

不管您来自何方, 我们都欢迎您加入社区并做出贡献.
"""

            # """
            # 学术数据

            # "潜进" 的用户数据可用于科学方面的研究, 我们将在未来版本添加学术数据的收集和展示平台
            # """
            yield Markdown(about_text, classes="about-markdown")

            yield Button(
                "返回主界面",
                id="back_button",
                variant="primary",
                classes="back-button",
            )
        yield Footer()

    def action_go_back(self):
        self.app.pop_screen()

    def on_button_pressed(self, event) -> None:
        event.stop()
        if event.button.id == "back_button":
            self.action_go_back()
