from typing import Dict, List, Literal, TypedDict
from dataclasses import dataclass
from enum import Enum

class I18nLanguage(Enum):
    ZH_CN = "zh-CN"
    EN = "en"
    

class I18nContent(TypedDict):
    text: str
    author: str

I18n = Dict[I18nLanguage, I18nContent]

@dataclass
class TranslatedItem:
    raw: str
    translation: I18n

Data = List[TranslatedItem]