"""国际化支持模块

基于 GNU gettext, 并使用英文 (en_US) 作为 msgid 的基础语言.
"""

import gettext
import os
from pathlib import Path
import locale
from heurams.context import rootdir

_LOCALE_DIR = rootdir / "locale"

_DEFAULT_LOCALE = "en_US"
_translation = gettext.NullTranslations()

def setup_locale(_locale: str | None = None) -> None:
    """获得翻译项.

    如果没有找到对应的 locale, 就回退到原始 msgid.
    """
    global _translation
    if _locale is None:
        _locale = locale.getlocale()[0]
    try:
        _translation = gettext.translation(
            "heurams", localedir=str(_LOCALE_DIR), languages=[_locale], fallback=True
        )
    except FileNotFoundError:
        _translation = gettext.NullTranslations()


def _(message: str) -> str:
    """执行翻译的函数"""
    return _translation.gettext(message)

# 导入时初始化
setup_locale()