from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from .core import Translator


class RelativeTime:
    def __init__(
        self,
        translator: Translator,
    ) -> None:
        self._t = translator

    async def format(
        self,
        dt: datetime,
        locale: str = "en",
        now: Optional[datetime] = None,
    ) -> str:
        ref = now or datetime.now(timezone.utc)

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        if ref.tzinfo is None:
            ref = ref.replace(tzinfo=timezone.utc)

        delta = ref - dt
        total_seconds = int(delta.total_seconds())
        future = total_seconds < 0
        total_seconds = abs(total_seconds)

        key_prefix = "time.in" if future else "time.ago"

        if total_seconds < 45:
            return await self._t.t("time.just_now", locale)

        if total_seconds < 90:
            n = 1
            unit = "minute"
        elif total_seconds < 3600:
            n = round(total_seconds / 60)
            unit = "minute"
        elif total_seconds < 86400:
            n = round(total_seconds / 3600)
            unit = "hour"
        elif total_seconds < 2_592_000:
            n = round(total_seconds / 86400)
            unit = "day"
        elif total_seconds < 31_536_000:
            n = round(total_seconds / 2_592_000)
            unit = "month"
        else:
            n = round(total_seconds / 31_536_000)
            unit = "year"

        key = f"{key_prefix}.{unit}s"
        return await self._t.t(key, locale, n=n)

    @staticmethod
    def utcnow() -> datetime:
        return datetime.now(timezone.utc)
