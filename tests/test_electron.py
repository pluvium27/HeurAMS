"""Tests for heurams.kernel.particles.electron.Electron"""

from copy import deepcopy

import pytest

from heurams.kernel.algorithms import algorithms
from heurams.kernel.particles.electron import Electron
from heurams.services import timer


class TestElectronInit:
    def test_default_algo_is_sm2(self, timer_context):
        e = Electron("test-id", {})
        assert e.algoname == "SM-2"
        assert e.ident == "test-id"

    def test_specific_algo(self, timer_context):
        e = Electron("test-id", {}, algo_name="NSP-0")
        assert e.algoname == "NSP-0"

    def test_integrity_check_fills_defaults(self, timer_context):
        e = Electron("test-id", {})
        assert "SM-2" in e.algodata
        assert e.algodata["SM-2"]["efactor"] == 2.5

    def test_existing_data_preserved(self, timer_context):
        data = {
            "SM-2": {
                "efactor": 1.5,
                "rept": 3,
                "real_rept": 5,
                "interval": 10,
                "last_date": 100,
                "next_date": 200,
                "is_activated": 1,
                "last_modify": 1e9,
            }
        }
        e = Electron("test-id", data)
        assert e.algodata["SM-2"]["efactor"] == 1.5
        assert e.algodata["SM-2"]["rept"] == 3


class TestElectronActivation:
    def test_activate_sets_flag(self, timer_context):
        e = Electron("test-id", {})
        assert e.is_activated() == 0
        e.activate()
        assert e.is_activated() == 1

    def test_is_due_requires_activation(self, timer_context):
        e = Electron("test-id", {})
        e.algodata["SM-2"]["next_date"] = 0  # past
        assert e.is_due() == 0  # not activated

        e.activate()
        assert e.is_due() == 1

    def test_is_due_returns_false_when_not_due(self, timer_context):
        e = Electron("test-id", {})
        e.activate()
        e.algodata["SM-2"]["next_date"] = 999999
        assert e.is_due() is False


class TestElectronModify:
    def test_modify_valid_key(self, timer_context):
        e = Electron("test-id", {})
        e.modify("efactor", 3.0)
        assert e.algodata["SM-2"]["efactor"] == 3.0

    def test_modify_invalid_key_raises(self, timer_context):
        e = Electron("test-id", {})
        with pytest.raises(AttributeError):
            e.modify("nonexistent", 42)


class TestElectronRevisor:
    def test_revisor_delegates_to_algo(self, timer_context):
        e = Electron("test-id", {})
        e.activate()
        e.algodata["SM-2"]["next_date"] = 0
        assert e.is_due() == 1

        e.revisor(quality=5)
        # After good review, interval > 0
        assert e.algodata["SM-2"]["interval"] >= 1

    def test_revisor_nsp0(self, timer_context):
        e = Electron("test-id", {}, algo_name="NSP-0")
        e.activate()
        e.algodata["NSP-0"]["next_date"] = 0
        assert e.is_due() == 1

        e.revisor(quality=3)  # bad feedback
        assert e.algodata["NSP-0"]["interval"] == 1


class TestElectronProperties:
    def test_rept(self, timer_context):
        e = Electron("test-id", {})
        assert e.rept() == 0

    def test_rept_real(self, timer_context):
        e = Electron("test-id", {})
        assert e.rept(real_rept=True) == 0

    def test_get_rating(self, timer_context):
        e = Electron("test-id", {})
        rating = e.get_rating()
        assert isinstance(rating, str)

    def test_nextdate_returns_int(self, timer_context):
        e = Electron("test-id", {})
        nd = e.nextdate()
        assert isinstance(nd, int)

    def test_hash(self, timer_context):
        e = Electron("test-id", {})
        assert hash(e) == hash("test-id")

    def test_len(self, timer_context):
        e = Electron("test-id", {})
        assert len(e) == len(algorithms["SM-2"].defaults)


class TestElectronGetSetItem:
    def test_getitem_ident(self, timer_context):
        e = Electron("test-id", {})
        assert e["ident"] == "test-id"

    def test_getitem_algo_key(self, timer_context):
        e = Electron("test-id", {})
        assert e["efactor"] == 2.5

    def test_getitem_missing_key_raises(self, timer_context):
        e = Electron("test-id", {})
        with pytest.raises(KeyError):
            _ = e["nonexistent"]

    def test_setitem_valid_key(self, timer_context):
        e = Electron("test-id", {})
        e["efactor"] = 3.5
        assert e["efactor"] == 3.5

    def test_setitem_ident_raises(self, timer_context):
        e = Electron("test-id", {})
        with pytest.raises(AttributeError):
            e["ident"] = "new-id"


class TestElectronFromData:
    def test_from_data_creates_electron(self, timer_context):
        data = {"SM-2": {}}
        e = Electron.from_data(("my-ident", data), algo_name="SM-2")
        assert e.ident == "my-ident"
        assert e.algoname == "SM-2"
        assert "SM-2" in e.algodata
