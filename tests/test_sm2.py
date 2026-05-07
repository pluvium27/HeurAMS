"""Tests for heurams.kernel.algorithms.sm2.SM2Algorithm"""

from copy import deepcopy

import pytest

from heurams.kernel.algorithms import algorithms
from heurams.services import timer


@pytest.fixture
def algo():
    return algorithms["SM-2"]


@pytest.fixture
def algodata(sample_algodata_sm2):
    return sample_algodata_sm2


class TestSM2Defaults:
    def test_defaults_have_efactor(self, algo):
        assert algo.defaults["efactor"] == 2.5

    def test_algo_name(self, algo):
        assert algo.algo_name == "SM-2"


class TestSM2Revisor:
    def test_feedback_negative_one_skips(self, algo, algodata):
        """feedback == -1 should be a no-op."""
        d = deepcopy(algodata)
        algo.revisor(d, feedback=-1)
        assert d == algodata  # unchanged

    def test_good_feedback_increases_efactor(self, algo, algodata):
        d = deepcopy(algodata)
        ef_before = d["SM-2"]["efactor"]
        algo.revisor(d, feedback=5)
        assert d["SM-2"]["efactor"] > ef_before

    def test_bad_feedback_resets_rept(self, algo, algodata):
        d = deepcopy(algodata)
        d["SM-2"]["rept"] = 5
        algo.revisor(d, feedback=2)
        assert d["SM-2"]["rept"] == 0
        assert d["SM-2"]["interval"] == 1

    def test_efactor_minimum_floor(self, algo, algodata):
        d = deepcopy(algodata)
        d["SM-2"]["efactor"] = 0.5
        algo.revisor(d, feedback=2)
        assert d["SM-2"]["efactor"] >= 1.3

    def test_rept_increments_on_good_feedback(self, algo, algodata):
        d = deepcopy(algodata)
        algo.revisor(d, feedback=4)
        assert d["SM-2"]["rept"] == 1

    def test_new_activation_resets_state(self, algo, algodata):
        d = deepcopy(algodata)
        d["SM-2"]["rept"] = 10
        d["SM-2"]["efactor"] = 3.0
        algo.revisor(d, feedback=5, is_new_activation=True)
        assert d["SM-2"]["rept"] == 0
        assert d["SM-2"]["efactor"] == 2.5

    def test_interval_at_rept_zero(self, algo, algodata):
        d = deepcopy(algodata)
        algo.revisor(d, feedback=2)
        assert d["SM-2"]["interval"] == 1

    def test_interval_at_rept_one(self, algo, algodata):
        d = deepcopy(algodata)
        # rept=0 + feedback>=3 -> rept becomes 1 -> interval=6
        algo.revisor(d, feedback=5)
        assert d["SM-2"]["interval"] == 6

    def test_interval_for_rept_gt_one(self, algo, algodata):
        d = deepcopy(algodata)
        d["SM-2"]["rept"] = 2
        d["SM-2"]["interval"] = 6
        d["SM-2"]["efactor"] = 2.0
        algo.revisor(d, feedback=5)
        # efactor 2.0 + 0.1(feedback=5) = 2.1; interval = round(6 * 2.1) = 13
        assert d["SM-2"]["interval"] == 13

    def test_real_rept_always_increments(self, algo, algodata):
        d = deepcopy(algodata)
        algo.revisor(d, feedback=5)
        assert d["SM-2"]["real_rept"] == 1
        algo.revisor(d, feedback=0)
        assert d["SM-2"]["real_rept"] == 2


class TestSM2DueDate:
    def test_is_due_when_past(self, algo, algodata, timer_context):
        d = deepcopy(algodata)
        d["SM-2"]["next_date"] = 100  # far in the past
        assert algo.is_due(d) is True

    def test_not_due_when_future(self, algo, algodata, timer_context):
        d = deepcopy(algodata)
        d["SM-2"]["next_date"] = 999999  # far in the future
        assert algo.is_due(d) is False

    def test_nextdate_returns_stored(self, algo, algodata):
        d = deepcopy(algodata)
        d["SM-2"]["next_date"] = 12345
        assert algo.nextdate(d) == 12345

    def test_revisor_updates_dates(self, algo, algodata, timer_context):
        d = deepcopy(algodata)
        algo.revisor(d, feedback=5)
        assert d["SM-2"]["last_date"] == timer.get_daystamp()
        assert d["SM-2"]["next_date"] > timer.get_daystamp()


class TestSM2Rating:
    def test_get_rating_returns_efactor(self, algo, algodata):
        d = deepcopy(algodata)
        d["SM-2"]["efactor"] = 2.5
        assert algo.get_rating(d) == "2.5"
