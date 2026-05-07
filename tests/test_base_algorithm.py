"""Tests for heurams.kernel.algorithms.base.BaseAlgorithm"""

from copy import deepcopy

import pytest

from heurams.kernel.algorithms import BaseAlgorithm
from heurams.services import timer


class TestBaseAlgorithmDefaults:
    def test_defaults_have_required_keys(self):
        required = {
            "real_rept",
            "rept",
            "interval",
            "last_date",
            "next_date",
            "is_activated",
            "last_modify",
        }
        assert required.issubset(BaseAlgorithm.defaults.keys())

    def test_defaults_last_modify_is_reasonable(self):
        # defaults is evaluated at module import, not test time
        ts = BaseAlgorithm.defaults["last_modify"]
        assert isinstance(ts, float)
        assert ts > 1e9  # reasonable UNIX timestamp


class TestBaseAlgorithmMethods:
    def test_revisor_does_nothing(self):
        d = {"SM-2": {"rept": 0}}
        BaseAlgorithm.revisor(d, feedback=5)
        # Base.revisor is a no-op — dict unchanged
        assert d["SM-2"]["rept"] == 0

    def test_is_due_returns_one(self):
        assert BaseAlgorithm.is_due({}) == 1

    def test_get_rating_returns_empty(self):
        assert BaseAlgorithm.get_rating({}) == ""

    def test_nextdate_returns_negative_one(self):
        assert BaseAlgorithm.nextdate({}) == -1


class TestBaseAlgorithmIntegrity:
    def test_check_integrity_valid(self, sample_algodata_sm2):
        # BaseAlgorithm.algo_name is "BaseAlgorithm", not "SM-2"
        data = {"BaseAlgorithm": sample_algodata_sm2["SM-2"]}
        assert BaseAlgorithm.check_integrity(data) == 1

    def test_check_integrity_invalid(self):
        assert BaseAlgorithm.check_integrity({"SM-2": {}}) == 0

    def test_check_integrity_missing_key(self):
        assert BaseAlgorithm.check_integrity({}) == 0
