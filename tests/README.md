# HeurAMS 测试指南

## 概览

HeurAMS 使用 [pytest](https://docs.pytest.org/) 作为测试框架, 测试文件统一存放在项目根目录的 `tests/` 目录下。

- **测试框架**: pytest >= 8.0.0
- **覆盖率**: pytest-cov >= 6.0.0
- **配置**: `pyproject.toml` 中的 `[tool.pytest.ini_options]`
- **所有测试纯单元测试** — 不涉及 I/O、网络或真实文件系统依赖

## 运行测试

```bash
# 从项目根目录运行全部测试
uv run pytest

# 显示详细测试名
uv run pytest -v

# 运行单个测试文件
uv run pytest tests/test_sm2.py

# 按关键词筛选
uv run pytest -k "revisor"

# 带覆盖率报告
uv run pytest --cov=heurams

# 生成 HTML 覆盖率报告
uv run pytest --cov=heurams --cov-report=html
```

当前全部 **128 个测试** 通过 (0.2s)。

## 测试套件结构

所有 9 个测试文件平铺在 `tests/` 目录下:

| 文件 | 用例数 | 测试对象 |
|---|---|---|
| `test_base_algorithm.py` | 7 | `kernel.algorithms.base.BaseAlgorithm` |
| `test_sm2.py` | 16 | `kernel.algorithms.sm2.SM2Algorithm` |
| `test_nsp0.py` | 9 | `kernel.algorithms.nsp0.NSP0Algorithm` |
| `test_electron.py` | 18 | `kernel.particles.electron.Electron` |
| `test_lict.py` | 29 | `kernel.auxiliary.lict.Lict` |
| `test_evalizor.py` | 8 | `kernel.auxiliary.evalizor.Evalizer` |
| `test_epath.py` | 11 | `services.epath` |
| `test_hasher.py` | 5 | `services.hasher` |
| `test_textproc.py` | 7 | `services.textproc` |

## 共享 Fixtures (`conftest.py`)

`tests/conftest.py` 提供了四个全局 fixture:

- **`timer_config`** — 返回一个 `ConfigDict`, 其中计时器被覆写为确定值 (`daystamp=20000`, `timestamp=1e9`), 使算法测试不依赖系统时钟
- **`timer_context`** — 通过 `ConfigContext` 上下文管理器在测试期间应用计时器覆写
- **`sample_algodata_sm2`** — 一份预激活状态的 SM-2 `algodata` 字典 (deepcopy, 防止 fixture 污染)
- **`sample_algodata_nsp0`** — 同上, 针对 NSP-0

## 测试模式与约定

### 组织方式

- 测试全部使用 **class-based 组织** (例如 `TestSM2Revisor`, `TestElectronInit`)
- 每个测试类聚焦一个模块的一个方面 (默认值、方法、边界情况、属性等)
- 类名以 `Test` 开头, 方法名以 `test_` 开头

### 数据隔离

- 使用 `deepcopy(algodata)` 防止 fixture 突变在测试间泄漏
- 算法测试依赖 `timer_context` fixture 以获得确定性日期/时间

### 断言风格

- 仅使用标准 `assert` 语句, 无第三方断言库
- 异常测试使用 `pytest.raises()`

### 自定义标记

`pyproject.toml` 中定义了以下 pytest 标记 (当前尚未使用):

- `slow` — 慢速测试, 可用 `-m "not slow"` 跳过
- `integration` — 集成测试

## 覆盖率现状

**已有测试覆盖的模块:**

- `kernel.algorithms.base` — 完整
- `kernel.algorithms.sm2` — 完整
- `kernel.algorithms.nsp0` — 完整
- `kernel.particles.electron` — 完整
- `kernel.auxiliary.lict` — 完整
- `kernel.auxiliary.evalizor` — 完整
- `services.epath` — 完整
- `services.hasher` — 完整
- `services.textproc` — 完整

**尚无测试覆盖的模块 (欢迎贡献):**

- `kernel.particles.atom`, `nucleon`, `orbital`
- `kernel.reactor` (router, procession, expander)
- `kernel.puzzles` (所有题型)
- `kernel.algorithms.sm15m`, `kernel.algorithms.fsrs`
- `services.config`, `services.timer`, `services.logger`, `services.audio_service`, `services.tts_service`,
  `services.favorite_service`, `services.attic`
- `interface/` (完整 TUI)
- `providers/` (所有提供者后端)
- `repolib.repo`

## 编写新测试

1. 在 `tests/` 下创建 `test_<模块名>.py` 文件
2. 文件头部加模块文档字符串
3. 按功能划分测试类 (每个类一个测试主题)
4. 算法相关测试使用 `timer_context` fixture 保证确定性
5. 使用 `deepcopy` 保护共享 fixture
6. 运行 `uv run pytest tests/test_<模块名>.py -v` 验证

示例结构:

```python
"""Tests for heurams.module.submodule.SomeClass"""

import pytest
from heurams.module.submodule import SomeClass


class TestSomeClassInit:
    def test_defaults(self):
        ...


class TestSomeClassMethod:
    def test_normal_case(self):
        ...

    def test_edge_case(self):
        ...
```

## 开发环境设置

参考 [CONTRIBUTING.md](../CONTRIBUTING.md):

```bash
uv sync --all-extras     # 安装开发依赖
uv run pytest            # 运行测试
```
