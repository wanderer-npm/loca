from typing import Callable


class PluralEngine:
    _rules: dict[str, Callable[[int], int]] = {
        "en":    lambda n: 0 if n == 1 else 1,
        "de":    lambda n: 0 if n == 1 else 1,
        "es":    lambda n: 0 if n == 1 else 1,
        "it":    lambda n: 0 if n == 1 else 1,
        "nl":    lambda n: 0 if n == 1 else 1,
        "sv":    lambda n: 0 if n == 1 else 1,
        "hi":    lambda n: 0 if n == 1 else 1,
        "pt-BR": lambda n: 0 if n == 1 else 1,
        "fr":    lambda n: 0 if n <= 1 else 1,
        "ru": lambda n: (
            0 if n % 10 == 1 and n % 100 != 11 else
            1 if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14 else
            2
        ),
        "uk": lambda n: (
            0 if n % 10 == 1 and n % 100 != 11 else
            1 if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14 else
            2
        ),
        "pl": lambda n: (
            0 if n == 1 else
            1 if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14 else
            2 if n % 10 >= 5 or n % 10 == 0 or 12 <= n % 100 <= 14 else
            3
        ),
        "ar": lambda n: (
            0 if n == 0 else
            1 if n == 1 else
            2 if n == 2 else
            3 if 3 <= n % 100 <= 10 else
            4 if 11 <= n % 100 <= 99 else
            5
        ),
        "tr":    lambda n: 0,
        "ja":    lambda n: 0,
        "ko":    lambda n: 0,
        "zh-CN": lambda n: 0,
        "zh-TW": lambda n: 0,
    }

    @staticmethod
    def get_form(
        locale: str,
        n: int,
    ) -> int:
        rule = PluralEngine._rules.get(
            locale,
            lambda n: 0 if n == 1 else 1,
        )
        return rule(abs(int(n)))

    @staticmethod
    def register(
        locale: str,
        rule: Callable[[int], int],
    ) -> None:
        PluralEngine._rules[locale] = rule

    @staticmethod
    def registered() -> list[str]:
        return list(PluralEngine._rules.keys())
