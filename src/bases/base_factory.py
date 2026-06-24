import abc
from typing import Any


class BaseFactory(abc.ABC):
    """
    Базовый класс фабрики
    """

    @abc.abstractmethod
    def create(self, *args, **kwargs) -> Any:
        """
        Создать экземпляр объекта
        :return: экземпляр объекта
        """

        raise NotImplementedError
