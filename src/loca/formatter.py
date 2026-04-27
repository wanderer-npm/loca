from __future__ import annotations

from datetime import datetime
from typing import Literal

from .loader import LocaleLoader

_DATE_OVERRIDES: dict[str, dict[str, str]] = {
    "de": {
        "short": "%d.%m.%Y",
        "long": "%d. %B %Y",
        "full": "%A, %d. %B %Y",
        "datetime_short": "%d.%m.%Y %H:%M",
    },
    "fr": {
        "short": "%d/%m/%Y",
        "long": "%d %B %Y",
        "full": "%A %d %B %Y",
        "datetime_short": "%d/%m/%Y %H:%M",
    },
    "it": {
        "short": "%d/%m/%Y",
        "long": "%d %B %Y",
        "full": "%A %d %B %Y",
        "datetime_short": "%d/%m/%Y %H:%M",
    },
    "nl": {
        "short": "%d-%m-%Y",
        "long": "%d %B %Y",
        "full": "%A %d %B %Y",
        "datetime_short": "%d-%m-%Y %H:%M",
    },
    "ru": {
        "short": "%d.%m.%Y",
        "long": "%d %B %Y",
        "full": "%A, %d %B %Y",
        "datetime_short": "%d.%m.%Y %H:%M",
    },
    "uk": {
        "short": "%d.%m.%Y",
        "long": "%d %B %Y",
        "full": "%A, %d %B %Y",
        "datetime_short": "%d.%m.%Y %H:%M",
    },
    "pl": {
        "short": "%d.%m.%Y",
        "long": "%d %B %Y",
        "full": "%A, %d %B %Y",
        "datetime_short": "%d.%m.%Y %H:%M",
    },
    "tr": {
        "short": "%d.%m.%Y",
        "long": "%d %B %Y",
        "full": "%A, %d %B %Y",
        "datetime_short": "%d.%m.%Y %H:%M",
    },
    "sv": {
        "short": "%Y-%m-%d",
        "long": "%d %B %Y",
        "full": "%A %d %B %Y",
        "datetime_short": "%Y-%m-%d %H:%M",
    },
    "pt-BR": {
        "short": "%d/%m/%Y",
        "long": "%d de %B de %Y",
        "full": "%A, %d de %B de %Y",
        "datetime_short": "%d/%m/%Y %H:%M",
    },
    "ar": {
        "short": "%d/%m/%Y",
        "long": "%d %B %Y",
        "full": "%A %d %B %Y",
        "datetime_short": "%d/%m/%Y %H:%M",
    },
}

_CJK_LOCALES = {"ja", "ko", "zh-CN", "zh-TW"}

DateStyle = Literal["short", "long", "full", "datetime_short"]
TimeStyle = Literal["12h", "24h"]


class DateFormatter:
    def __init__(
        self,
        loader: LocaleLoader,
    ) -> None:
        self._loader = loader

    async def format_date(
        self,
        dt: datetime,
        style: DateStyle = "long",
        locale: str = "en",
    ) -> str:
        if locale in _CJK_LOCALES:
            return DateFormatter._format_cjk(dt, style, locale)

        overrides = _DATE_OVERRIDES.get(locale, {})
        defaults = {
            "short": "%m/%d/%Y",
            "long": "%B %d, %Y",
            "full": "%A, %B %d, %Y",
            "datetime_short": "%m/%d/%Y %H:%M",
        }
        pattern = overrides.get(style) or defaults.get(style, "%Y-%m-%d")
        return dt.strftime(pattern)

    async def format_time(
        self,
        dt: datetime,
        style: TimeStyle = "24h",
        locale: str = "en",
    ) -> str:
        if style == "12h":
            return dt.strftime("%I:%M %p").lstrip("0")
        return dt.strftime("%H:%M")

    @staticmethod
    def _format_cjk(
        dt: datetime,
        style: DateStyle,
        locale: str,
    ) -> str:
        y, m, d = dt.year, dt.month, dt.day

        if locale in ("ja",):
            if style == "short":
                return f"{y}/{m:02d}/{d:02d}"
            if style in ("long", "full"):
                return f"{y}年{m}月{d}日"
            return f"{y}/{m:02d}/{d:02d} {dt.hour:02d}:{dt.minute:02d}"

        if locale in ("ko",):
            if style == "short":
                return f"{y}.{m:02d}.{d:02d}"
            if style in ("long", "full"):
                return f"{y}년 {m}월 {d}일"
            return f"{y}.{m:02d}.{d:02d} {dt.hour:02d}:{dt.minute:02d}"

        # zh-CN / zh-TW
        if style == "short":
            return f"{y}/{m:02d}/{d:02d}"
        if style in ("long", "full"):
            return f"{y}年{m}月{d}日"
        return f"{y}/{m:02d}/{d:02d} {dt.hour:02d}:{dt.minute:02d}"


class NumberFormatter:
    _formats: dict[str, tuple[str, str]] = {
        "en":    (",", "."),
        "fr":    (" ", ","),
        "de":    (".", ","),
        "es":    (".", ","),
        "it":    (".", ","),
        "nl":    (".", ","),
        "pt-BR": (".", ","),
        "ru":    (" ", ","),
        "uk":    (" ", ","),
        "pl":    (" ", ","),
        "tr":    (".", ","),
        "sv":    (" ", ","),
        "ar":    (",", "."),
        "ja":    (",", "."),
        "ko":    (",", "."),
        "zh-CN": (",", "."),
        "zh-TW": (",", "."),
        "hi":    (",", "."),
    }

    @staticmethod
    def format_int(
        n: int,
        locale: str = "en",
    ) -> str:
        sep, _ = NumberFormatter._formats.get(locale, (",", "."))
        return f"{n:,}".replace(",", sep)

    @staticmethod
    def format_float(
        n: float,
        decimals: int = 2,
        locale: str = "en",
    ) -> str:
        sep, dec = NumberFormatter._formats.get(locale, (",", "."))
        formatted = f"{n:,.{decimals}f}"
        formatted = formatted.replace(",", "TSEP").replace(".", dec).replace("TSEP", sep)
        return formatted
