from typing import Set, Tuple
from pathlib import Path
import os
import json


def load_json_as_sets(file_path: Path, key = "raw") -> Set[str]:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        if not isinstance(data, list):
            raise ValueError("Invalid `data` / `raw` json format")
        res = set()
        for item in data:
            if isinstance(item, str):
                res.add(item)
            elif isinstance(item, dict):
                res.add(item[key])
        return res

def load_locale_count(file_path: Path, locale = "zh-CN") -> int:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        if not isinstance(data, list):
            raise ValueError("Invalid locale json format")
        count = 0
        for item in data:
            if not isinstance(item, dict):
                continue
            if locale in item["translation"] and item["translation"][locale]["text"]:
                count += 1
        return count

def analyze_translation_progress(raw_dir: Path, output_dir: Path, locale: str = "zh-CN")-> Tuple[int, int]: 
    raw_strings = set()
    # read raw_dir/*.json & output_dir/*_locale.json
    for filename in os.listdir(raw_dir):
        if filename.endswith(".json"):
            file_path = os.path.join(raw_dir, filename)
            raw_strings.update(load_json_as_sets(file_path, "raw"))
    translated_strings = 0
    for filename in os.listdir(output_dir):
        if filename.endswith(f".json"):
            file_path = os.path.join(output_dir, filename)
            raw_strings.update(load_json_as_sets(file_path, "raw"))
            translated_strings += load_locale_count(file_path, locale)

    total = len(raw_strings)
    translated = translated_strings
    return (total, translated)

def write_translation_progress(readme_file: Path, total: int, translated: int, locale: str = "zh-CN"):
    """
    更新README.md中的翻译进度badge
    
    Args:
        total: 总字符串数
        translated: 已翻译字符串数
        locale: 语言代码
    """
    # 生成新的badge URL
    sheilds_locale = locale.replace('-', '--')
    badge_url = f"![translation {locale}](https://img.shields.io/badge/translation_{sheilds_locale}-{translated}%2F{total}-blue)"

    try:
        with open(readme_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        # 如果README.md不存在，创建一个基本的结构
        lines = [
            "# translation\n",
            "\n",
            "---\n",
            "\n", 
            "## translation progress\n",
            "\n",
            "---\n"
        ]
    
    # 查找translation progress section
    start_idx = None
    end_idx = None
    
    for i, line in enumerate(lines):
        if "## translation progress" in line.lower():
            start_idx = i
        elif start_idx is not None and line.strip() == "---":
            end_idx = i
            break
    
    if start_idx is None:
        # 如果没有找到translation progress section，在文件末尾添加
        lines.extend([
            "\n",
            "## translation progress\n",
            "\n",
            f"{badge_url}\n",
            "\n",
            "---\n"
        ])
    else:
        # 在translation progress section中查找现有的badge
        locale_found = False
        badge_pattern = f"translation_{sheilds_locale}"
        
        # 搜索现有的locale badge并替换
        for i in range(start_idx + 1, end_idx if end_idx else len(lines)):
            if badge_pattern in lines[i]:
                lines[i] = f"{badge_url}\n"
                locale_found = True
                break
        
        # 如果没有找到现有的locale badge，添加新的
        if not locale_found:
            if end_idx is not None:
                # 在 --- 之前插入新的badge
                lines.insert(end_idx, f"{badge_url}\n")
            else:
                # 如果没有结束标记，在section末尾添加
                lines.append(f"{badge_url}\n")
                lines.append("---\n")
    
    # 写回文件
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"Update {locale} translation progress: {translated}/{total} ({translated/total*100:.1f}%)")
