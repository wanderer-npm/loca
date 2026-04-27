from __future__ import annotations

import logging
from typing import Any, Optional

from .loader import LocaleLoader
from .plurals import PluralEngine
from .models import TranslationResult

logger = logging.getLogger("loca.core")

_FALLBACK = "en"


class Translator:
    def __init__(
        self,
        loader: LocaleLoader,
        fallback: str = _FALLBACK,
        raise_on_missing: bool = False,
    ) -> None:
        self._loader = loader
        self._fallback = fallback
        self._raise_on_missing = raise_on_missing

    async def t(
        self,
        key: str,
        locale: str = "en",
        **kwargs: Any,
    ) -> str:
        result = await self._resolve(key, locale, **kwargs)
        return result.value

    async def t_result(
        self,
        key: str,
        locale: str = "en",
        **kwargs: Any,
    ) -> TranslationResult:
        return await self._resolve(key, locale, **kwargs)

    async def _resolve(
        self,
        key: str,
        locale: str,
        **kwargs: Any,
    ) -> TranslationResult:
        data = await self._loader.load(locale)
        val = data.get(key)
        fallback_used = False

        if val is None and locale != self._fallback:
            fallback_data = await self._loader.load(self._fallback)
            val = fallback_data.get(key)
            fallback_used = val is not None
            if val is not None:
                logger.debug(
                    "loca: key '%s' missing in '%s', used fallback '%s'",
                    key, locale, self._fallback,
                )

        if val is None:
            logger.warning("loca: missing key '%s' (locale=%s)", key, locale)
            if self._raise_on_missing:
                from .errors import MissingKey
                raise MissingKey(key, locale)
            return TranslationResult(
                key=key,
                locale=locale,
                value=key,
                fallback_used=False,
            )

        if "|" in val and "n" in kwargs:
            val = Translator._pick_plural(val, locale, kwargs["n"])

        formatted = Translator._format(val, **kwargs)

        return TranslationResult(
            key=key,
            locale=locale,
            value=formatted,
            fallback_used=fallback_used,
        )

    @staticmethod
    def _pick_plural(
        val: str,
        locale: str,
        n: int,
    ) -> str:
        forms = val.split("|")
        idx = PluralEngine.get_form(locale, n)
        return forms[min(idx, len(forms) - 1)]

    @staticmethod
    def _format(
        val: str,
        **kwargs: Any,
    ) -> str:
        if not kwargs:
            return val
        try:
            return val.format(**kwargs)
        except (KeyError, ValueError):
            return val
