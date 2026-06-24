import pytest

from services.exceptions import (
    NoPermissionException,
    ObjectDoesntExistsException,
    ObjectExistsException,
    SystemLogicError,
)


class TestObjectExistsException:
    def test_is_exception_subclass(self):
        assert issubclass(ObjectExistsException, Exception)

    def test_can_be_raised_and_caught(self):
        with pytest.raises(ObjectExistsException):
            raise ObjectExistsException("object already exists")

    def test_message_preserved(self):
        msg = "item with id=1 already exists"
        exc = ObjectExistsException(msg)
        assert str(exc) == msg

    def test_caught_as_base_exception(self):
        with pytest.raises(Exception):
            raise ObjectExistsException()


class TestObjectDoesntExistsException:
    def test_is_exception_subclass(self):
        assert issubclass(ObjectDoesntExistsException, Exception)

    def test_can_be_raised_and_caught(self):
        with pytest.raises(ObjectDoesntExistsException):
            raise ObjectDoesntExistsException("not found")

    def test_message_preserved(self):
        msg = "item with id=99 not found"
        exc = ObjectDoesntExistsException(msg)
        assert str(exc) == msg

    def test_caught_as_base_exception(self):
        with pytest.raises(Exception):
            raise ObjectDoesntExistsException()


class TestNoPermissionException:
    def test_is_exception_subclass(self):
        assert issubclass(NoPermissionException, Exception)

    def test_can_be_raised_and_caught(self):
        with pytest.raises(NoPermissionException):
            raise NoPermissionException("access denied")

    def test_message_preserved(self):
        msg = "user does not have role admin"
        exc = NoPermissionException(msg)
        assert str(exc) == msg


class TestSystemLogicError:
    def test_is_exception_subclass(self):
        assert issubclass(SystemLogicError, Exception)

    def test_can_be_raised_and_caught(self):
        with pytest.raises(SystemLogicError):
            raise SystemLogicError("invalid state transition")

    def test_message_preserved(self):
        msg = "cannot complete operation in current state"
        exc = SystemLogicError(msg)
        assert str(exc) == msg

    def test_all_exceptions_are_distinct(self):
        types = [
            ObjectExistsException,
            ObjectDoesntExistsException,
            NoPermissionException,
            SystemLogicError,
        ]
        # Ensure they are distinct classes
        assert len(set(types)) == len(types)

    def test_exceptions_not_interchangeable(self):
        with pytest.raises(ObjectExistsException):
            raise ObjectExistsException()

        # ObjectDoesntExistsException is NOT caught as ObjectExistsException
        with pytest.raises(ObjectDoesntExistsException):
            try:
                raise ObjectDoesntExistsException()
            except ObjectExistsException:
                pass  # This should NOT execute
