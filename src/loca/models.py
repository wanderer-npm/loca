from pydantic import BaseModel, Field


class LocaleMeta(BaseModel):
    code: str
    name: str
    native_name: str
    rtl: bool = False
    author: str = ""
    version: str = "1.0"


class TranslationResult(BaseModel):
    key: str
    locale: str
    value: str
    fallback_used: bool = False


class DateFormatConfig(BaseModel):
    short: str = Field(default="%m/%d/%Y")
    long: str = Field(default="%B %d, %Y")
    full: str = Field(default="%A, %B %d, %Y")
    time_12h: str = Field(default="%I:%M %p")
    time_24h: str = Field(default="%H:%M")
    datetime_short: str = Field(default="%m/%d/%Y %H:%M")
