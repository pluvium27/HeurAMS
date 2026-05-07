"""Tests for heurams.services.hasher"""

from heurams.services.hasher import get_md5, hash


class TestGetMD5:
    def test_known_value(self):
        # MD5 of "hello" is known
        assert get_md5("hello") == "5d41402abc4b2a76b9719d911017c592"

    def test_empty_string(self):
        assert get_md5("") == "d41d8cd98f00b204e9800998ecf8427e"

    def test_unicode(self):
        result = get_md5("中文测试")
        assert isinstance(result, str)
        assert len(result) == 32

    def test_different_inputs_differ(self):
        assert get_md5("abc") != get_md5("abcd")


class TestHash:
    def test_hash_delegates_to_md5(self):
        assert hash("hello") == get_md5("hello")
