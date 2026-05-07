"""
Pytest shared fixtures for HeurAMS test suite.

Provides:
- timer_config: A ConfigDict with deterministic timer overrides for reproducible tests.
- timer_context: A ConfigContext that applies timer_config for the duration of a test.
- sample_algodata_sm2: A fresh SM-2 algodata dict.
- sample_algodata_nsp0: A fresh NSP-0 algodata dict.
"""

import pathlib
from copy import deepcopy

import pytest

from heurams.context import ConfigContext, config_var, workdir
from heurams.kernel.algorithms import algorithms, nsp0
from heurams.services.config import ConfigDict


@pytest.fixture
def timer_config():
    """A ConfigDict with deterministic timer overrides (daystamp=20000, timestamp=1e9).

    This allows reproducible algorithm tests without relying on wall-clock time.
    """
    # Use the real config path as base, then overlay timer overrides
    config = ConfigDict(workdir / "data" / "config")
    # Override timer values in-place via the nested ConfigDict
    timer_cfg = config["services"]["timer"]
    timer_cfg["daystamp_override"] = 20000
    timer_cfg["timestamp_override"] = 1000000000.0
    return config


@pytest.fixture
def timer_context(timer_config):
    """Context manager fixture that applies the timer overrides."""
    with ConfigContext(timer_config):
        yield


@pytest.fixture
def sample_algodata_sm2():
    """A fresh SM-2 algodata dict (pre-activation)."""
    algo = algorithms["SM-2"]
    return {algo.algo_name: deepcopy(algo.defaults)}


@pytest.fixture
def sample_algodata_nsp0():
    """A fresh NSP-0 algodata dict (pre-activation)."""
    algo = algorithms["NSP-0"]
    return {algo.algo_name: deepcopy(algo.defaults)}
