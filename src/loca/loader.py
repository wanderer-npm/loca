from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
from typing import Optional

from .errors import InvalidLocaleFile, MissingLocale

logger = logging.getLogger("loca.loader")


def _builtin_dir() -> str:
    return os.path.join(os.path.dirname(__file__), "locales")


def _flatten(
    obj: dict,
    prefix: str = "",
) -> dict[str, str]:
    out: dict[str, str] = {}
    for k, v in obj.items():
        full = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict) and k != "_meta":
            out.update(_flatten(v, full))
        else:
            out[full] = v
    return out


class LocaleLoader:
    def __init__(
        self,
        locales_dir: Optional[str] = None,
    ) -> None:
        self._dir = locales_dir or _builtin_dir()
        self._cache: dict[str, dict[str, str]] = {}

    async def load(
        self,
        locale: str,
    ) -> dict[str, str]:
        if locale in self._cache:
            return self._cache[locale]

        path = os.path.join(self._dir, f"{locale}.json")

        if not os.path.isfile(path):
            if locale != "en":
                logger.warning(
                    "loca: locale '%s' not found, falling back to 'en'",
                    locale,
                )
                return await self.load("en")
            raise MissingLocale(locale)

        try:
            loop = asyncio.get_event_loop()
            raw = await loop.run_in_executor(None, self._read_file, path)
            flat = _flatten(raw)
            self._cache[locale] = flat
            return flat
        except json.JSONDecodeError as exc:
            raise InvalidLocaleFile(path, str(exc)) from exc

    def _read_file(
        self,
        path: str,
    ) -> dict:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)

    async def preload(
        self,
        locales: list[str],
    ) -> None:
        await asyncio.gather(*[self.load(loc) for loc in locales])

    def invalidate(
        self,
        locale: Optional[str] = None,
    ) -> None:
        if locale:
            self._cache.pop(locale, None)
        else:
            self._cache.clear()

    def available(self) -> list[str]:
        try:
            return sorted(
                f[:-5]
                for f in os.listdir(self._dir)
                if f.endswith(".json") and not f.startswith("_")
            )
        except FileNotFoundError:
            return []

    def is_loaded(
        self,
        locale: str,
    ) -> bool:
        return locale in self._cache
