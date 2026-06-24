import pytest

from tools.globals import Globals, set_extra_for_logs, g


class TestGlobals:
    def setup_method(self):
        # Each test gets a fresh Globals instance to avoid cross-test pollution
        self.globals = Globals()

    def test_set_and_get_attribute(self):
        self.globals.foo = "bar"
        assert self.globals.foo == "bar"

    def test_unset_attribute_returns_none(self):
        assert self.globals.unknown_attr is None

    def test_set_default_used_when_not_set(self):
        self.globals.set_default("my_var", "default_value")
        assert self.globals.my_var == "default_value"

    def test_set_default_callable_is_invoked(self):
        self.globals.set_default("counter", list)
        result = self.globals.counter
        assert result == []

    def test_set_default_ignored_if_same_value(self):
        sentinel = object()
        self.globals.set_default("key", sentinel)
        # Should not raise — same value reference
        self.globals.set_default("key", sentinel)

    def test_set_default_raises_if_variable_already_set(self):
        self.globals.already_set = "value"
        with pytest.raises(RuntimeError, match="already set"):
            self.globals.set_default("already_set", "default")

    def test_overwrite_existing_attribute(self):
        self.globals.num = 1
        self.globals.num = 2
        assert self.globals.num == 2

    def test_multiple_independent_attributes(self):
        self.globals.a = 1
        self.globals.b = 2
        assert self.globals.a == 1
        assert self.globals.b == 2

    def test_attribute_set_to_none(self):
        self.globals.val = None
        assert self.globals.val is None

    def test_attribute_set_to_dict(self):
        self.globals.data = {"key": "value"}
        assert self.globals.data == {"key": "value"}


class TestSetExtraForLogs:
    def setup_method(self):
        # Reset the global g's extra_info_for_logs before each test
        g.extra_info_for_logs = None

    def test_set_extra_for_logs_creates_dict(self):
        set_extra_for_logs({"request_id": "123"})
        assert g.extra_info_for_logs["request_id"] == "123"

    def test_set_extra_for_logs_merges(self):
        set_extra_for_logs({"a": 1})
        set_extra_for_logs({"b": 2})
        assert g.extra_info_for_logs["a"] == 1
        assert g.extra_info_for_logs["b"] == 2

    def test_set_extra_for_logs_overwrites_key(self):
        set_extra_for_logs({"key": "old"})
        set_extra_for_logs({"key": "new"})
        assert g.extra_info_for_logs["key"] == "new"

    def test_set_extra_for_logs_empty_dict(self):
        set_extra_for_logs({})
        # Should not raise; extra_info_for_logs is a dict
        assert isinstance(g.extra_info_for_logs, dict)
