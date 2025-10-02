glossary = {
    # character
    "おとむねこずえ": "Kozue Otomune",
    "ゆうぎりつづり": "Tsuzuri Yugiri",
    "ふじしまめぐみ": "Megumi Fujishima",
    "ひのしたかほ": "Kaho Hinoshita",
    "むらのさやか": "Sayaka Murano",
    "おおさわるりの": "Rurino Osawa",
    "ももせぎんこ": "Ginko Momose",
    "かちまちこすず": "Kosuzu Kachimachi",
    "あんようじひめ": "Hime Anyoji",
    "セラス やなぎだ リリエンフェルト": "Ceras Yanagida Lilienfeld",
    "かつらぎいずみ": "Izumi Katsuragi",
    # hasu
    "蓮ノ空": "Hasu no Sora",
    "スクールアイドル": "School Idol",
    "ラブライブ！": "Love Live!",
    "スリーズブーケ": "Cerise Bouquet",
    "DOLLCHESTRA": "DOLLCHESTRA",
    "みらくらぱーく！": "Mira-Cra Park!",
    # game
    "ボルテージ": "Voltage",
    "メンタル": "Mental",
    "クエストライブ": "Quest Live",
    "デイリーライブ": "Daily Live",
    "ドリームライブ": "Dream Live",
    "スキルハート": "Skill Heart",
}
glossary_entries = '\n'.join([f"- {k} - {v}" for k, v in glossary.items()])

prompt_base = """##Character
You are an experienced localization translator, and you need to translate the basic game description text into English.

## Goal
Translate Japanese into **English** (do not translate into other languages), ensuring that the language is natural and fluent, and that the context is coherent, while corresponding to each line of content.
"""

prompt = f"""{prompt_base}
## Detailed Requirements
- Language: Translate Japanese into the target language.
- Number of lines: The output should have the same number of lines as the input. Do not output any additional explanatory text.
- Special symbols: <br> represents a line break, and should be preserved if needed.
- Correspondence: Each line of translation should correspond to the original text, without merging multiple lines or splitting a single line into multiple lines.
- Specific translations: Use the following translations for specific names and terms:
- For text enclosed in quotation marks such as 《 “ 『 「 etc., especially song titles, please retain the original content.
{glossary_entries}

Additionally, users may provide supplementary specific translation terms, which you should adhere to if provided.
"""