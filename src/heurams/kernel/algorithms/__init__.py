"""算法模块

自动发现并加载所有算法实现, 提供统一的算法注册表. 
"""

import importlib
import pkgutil
from pathlib import Path

from .base import BaseAlgorithm

__path__ = [str(Path(__file__).parent)]

for _finder, _name, _ispkg in pkgutil.iter_modules(__path__):
    if _name == "base":
        continue
    importlib.import_module(f".{_name}", __package__)

algorithms = BaseAlgorithm.get_registry()
