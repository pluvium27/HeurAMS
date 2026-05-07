"""Tests for heurams.kernel.algorithms.nsp0.NSP0Algorithm"""

from copy import deepcopy

import pytest

from heurams.kernel.algorithms import algorithms
from heurams.services import timer


@pytest.fixture
def algo():
    return algorithms["NSP-0"]


@pytest.fixture
def algodata(sample_algodata_nsp0):
    return sample_algodata_nsp0


class TestNSP0Defaults:
    def test_defaults_have_important(self, algo):
        assert algo.defaults["important"] == 0

    def test_algo_name(self, algo):
        assert algo.algo_name == "NSP-0"


class TestNSP0Revisor:
    def test_negative_one_skip(self, algo, algodata):
        d = deepcopy(algodata)
        algo.revisor(d, feedback=-1)
        assert d == algodata

    def test_feedback_three_or_less_sets_interval_one(self, algo, algodata):
        for fb in (0, 1, 2, 3):
            d = deepcopy(algodata)
            algo.revisor(d, feedback=fb)
            assert d["NSP-0"]["interval"] == 1
            assert d["NSP-0"]["important"] == 1

    def test_feedback_greater_than_three_sets_infinite_interval(self, algo, algodata):
        for fb in (4, 5):
            d = deepcopy(algodata)
            algo.revisor(d, feedback=fb)
            assert d["NSP-0"]["interval"] == float("inf")
            assert d["NSP-0"]["important"] == 0

    def test_revisor_updates_dates(self, algo, algodata, timer_context):
        d = deepcopy(algodata)
        algo.revisor(d, feedback=3)
        assert d["NSP-0"]["last_date"] == timer.get_daystamp()
        assert d["NSP-0"]["next_date"] == timer.get_daystamp() + 1


class TestNSP0IsDue:
    def test_due_when_past(self, algo, algodata, timer_context):
        d = deepcopy(algodata)
        d["NSP-0"]["next_date"] = 100
        assert algo.is_due(d) is True

    def test_not_due_when_future(self, algo, algodata, timer_context):
        d = deepcopy(algodata)
        d["NSP-0"]["next_date"] = 999999
        assert algo.is_due(d) is False

    def test_nextdate_returns_stored(self, algo, algodata):
        d = deepcopy(algodata)
        d["NSP-0"]["next_date"] = 42
        assert algo.nextdate(d) == 42
