# loca

Async i18n library for Python 3.11+. Translation lookup, pluralization, relative time, date and number formatting — no framework dependencies.

---

## Installation

```bash
pip install loca
```

Local development:

```bash
git clone https://github.com/slug-discord/loca
cd loca
pip install -e ".[dev]"
```

---

## Quick Start

```python
import asyncio
from loca import LocaleLoader, Translator

async def main():
    loader = LocaleLoader()
    tr = Translator(loader)

    print(await tr.t("ping.checking", locale="en"))
    # Pinging...

    print(await tr.t("ping.checking", locale="fr"))
    # Verification en cours...

    print(await tr.t("error.not_found", locale="de", thing="user"))
    # Konnte user nicht finden.

asyncio.run(main())
```

---

## Translation Files

One JSON file per locale. Keys are dot-accessible — nested objects flatten to `"time.ago.days"` at load time.

```json
{
  "_meta": {
    "code": "en",
    "name": "English",
    "native_name": "English",
    "rtl": false
  },
  "welcome": "Welcome, {name}!",
  "items": {
    "count": "{n} item|{n} items"
  }
}
```

Plural strings use `|` as a separator. Pass `n=` and the right form is picked automatically:

```python
await tr.t("items.count", locale="en", n=1)  # "1 item"
await tr.t("items.count", locale="en", n=5)  # "5 items"
```

Languages with more than two plural forms use more pipes. Russian, for example, has three:

```json
"days": "{n} день|{n} дня|{n} дней"
```

---

## Custom Locale Directory

```python
loader = LocaleLoader(locales_dir="/app/translations")
```

Files must be named `{locale-code}.json`. Any locale not found falls back to `en`.

---

## Translator

```python
Translator(loader, fallback="en", raise_on_missing=False)
```

```python
# Returns string
await tr.t("key", locale="fr", n=3, name="Alice")

# Returns TranslationResult with metadata
result = await tr.t_result("key", locale="fr", n=3)
result.value          # translated string
result.fallback_used  # True if en fallback was used
```

By default, missing keys return the key name as-is. Pass `raise_on_missing=True` to raise `MissingKey` instead.

---

## Pluralization

`PluralEngine` maps a count to the correct form index for each locale. `Translator.t()` calls it automatically when you pass `n=` — you'd only use it directly for custom logic.

```python
from loca import PluralEngine

PluralEngine.get_form("en", 1)   # 0  (singular)
PluralEngine.get_form("en", 5)   # 1  (plural)
PluralEngine.get_form("ru", 11)  # 2  (genitive plural)
PluralEngine.get_form("ar", 3)   # 3  (few)
```

Register a custom rule:

```python
PluralEngine.register("ga", lambda n: 0 if n == 1 else 1 if n == 2 else 2)
```

---

## Built-in Locales

| Code | Language | Plural Forms |
|------|----------|:---:|
| `en` | English | 2 |
| `fr` | French | 2 |
| `de` | German | 2 |
| `es` | Spanish | 2 |
| `it` | Italian | 2 |
| `nl` | Dutch | 2 |
| `pt-BR` | Portuguese (Brazil) | 2 |
| `sv` | Swedish | 2 |
| `hi` | Hindi | 2 |
| `ru` | Russian | 3 |
| `uk` | Ukrainian | 3 |
| `pl` | Polish | 4 |
| `ar` | Arabic | 6 |
| `tr` | Turkish | 1 |
| `ja` | Japanese | 1 |
| `ko` | Korean | 1 |
| `zh-CN` | Chinese (Simplified) | 1 |
| `zh-TW` | Chinese (Traditional) | 1 |

Each built-in locale includes keys for `time.*`, `ping.*`, and `error.*`.

---

## Relative Time

```python
from loca import RelativeTime
from datetime import datetime, timezone, timedelta

rt = RelativeTime(tr)

past = datetime.now(timezone.utc) - timedelta(hours=3)
await rt.format(past, locale="en")   # "3 hours ago"
await rt.format(past, locale="fr")   # "il y a 3 heures"
await rt.format(past, locale="ru")   # "3 часа назад"

future = datetime.now(timezone.utc) + timedelta(days=2)
await rt.format(future, locale="en") # "in 2 days"
```

Thresholds: under 45 seconds is "just now", under 90 seconds rounds to 1 minute, then minutes up to 1 hour, hours up to 24 hours, days up to 30 days, months up to 365 days, then years. Future dates produce "in N ..." equivalents.

---

## Date Formatting

```python
from loca import DateFormatter
from datetime import datetime

fmt = DateFormatter(loader)
dt = datetime(2024, 6, 15, 14, 30)

await fmt.format_date(dt, style="short",          locale="en")  # "06/15/2024"
await fmt.format_date(dt, style="long",           locale="en")  # "June 15, 2024"
await fmt.format_date(dt, style="full",           locale="de")  # "Samstag, 15. Juni 2024"
await fmt.format_date(dt, style="datetime_short", locale="de")  # "15.06.2024 14:30"

await fmt.format_time(dt, style="24h")  # "14:30"
await fmt.format_time(dt, style="12h")  # "2:30 PM"
```

CJK locales produce locale-correct output regardless of style:

```python
await fmt.format_date(dt, style="long", locale="ja")  # "2024年6月15日"
await fmt.format_date(dt, style="long", locale="ko")  # "2024년 6월 15일"
```

---

## Number Formatting

```python
from loca import NumberFormatter

NumberFormatter.format_int(1_000_000, locale="en")     # "1,000,000"
NumberFormatter.format_int(1_000_000, locale="de")     # "1.000.000"
NumberFormatter.format_int(1_000_000, locale="fr")     # "1 000 000"

NumberFormatter.format_float(1234.5, decimals=2, locale="en")  # "1,234.50"
NumberFormatter.format_float(1234.5, decimals=2, locale="de")  # "1.234,50"
```

---

## LocaleLoader

| Method | Description |
|--------|-------------|
| `await loader.load(locale)` | Load and cache a locale |
| `await loader.preload(["en", "fr"])` | Load multiple locales in parallel |
| `loader.invalidate(locale=None)` | Clear one locale or the full cache |
| `loader.available()` | List `.json` files in the locale directory |
| `loader.is_loaded(locale)` | Check if locale is cached |

Preload at startup to avoid cold-load latency on first request:

```python
async def startup():
    await loader.preload(["en", "fr", "de", "es", "ru", "ja"])
```

---

## Errors

```python
from loca.errors import MissingLocale, MissingKey, InvalidLocaleFile
```

- `MissingLocale` — locale file not found, no fallback available
- `MissingKey` — key missing with `raise_on_missing=True`
- `InvalidLocaleFile` — JSON parse error in locale file

---

## Adding a Locale

1. Create `locales/xx.json` with at minimum the `_meta` block and `time.*` keys.
2. Register a plural rule via `PluralEngine.register("xx", lambda n: ...)`.
3. Add date format overrides to `formatter._DATE_OVERRIDES` if the locale uses non-US date order.

---

## License

MIT
