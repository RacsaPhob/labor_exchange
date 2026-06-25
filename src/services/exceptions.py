class ObjectExistsException(Exception):
    """
    Ошибка: Объект существует в системе
    """

    pass


class ObjectDoesntExistsException(Exception):
    """
    Ошибка: Объекта не существует в системе
    """

    pass


class NoPermissionException(Exception):
    """
    Ошибка: Недостаточно прав доступа
    """

    pass


class SystemLogicError(Exception):
    """
    Ошибка: Неверная логика работы системы
    """

    pass
