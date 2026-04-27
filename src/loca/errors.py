class LocaError(Exception):
    pass


class MissingLocale(LocaError):
    def __init__(
        self,
        locale: str,
    ) -> None:
        self.locale = locale
        super().__init__(f"locale '{locale}' could not be found")


class MissingKey(LocaError):
    def __init__(
        self,
        key: str,
        locale: str,
    ) -> None:
        self.key = key
        self.locale = locale
        super().__init__(f"key '{key}' missing in locale '{locale}'")


class InvalidLocaleFile(LocaError):
    def __init__(
        self,
        path: str,
        reason: str,
    ) -> None:
        self.path = path
        super().__init__(f"invalid locale file at '{path}': {reason}")
