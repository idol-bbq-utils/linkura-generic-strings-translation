from pathlib import Path
import json
import random
from src.model.localization import I18nLanguage

author_exclude_keyword = ["ai", "claude", "llm"]

def get_reference_prompt(input_file: Path, locale: I18nLanguage, limit: int = 30) -> str:
    """
    Generate reference prompt from translation file
    
    Args:
        input_file: Path to translation JSON file
        locale: Target locale for translation examples
        limit: Maximum number of examples to include
        
    Returns:
        Formatted string with original text and translations
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Filter items that have translations for the specified locale
    valid_items = []
    locale_key = locale.value
    
    for item in data:
        if (isinstance(item, dict) and 
            "raw" in item and 
            "translation" in item and
            locale_key in item["translation"] and
            item["translation"][locale_key].get("text", "").strip()):
            
            # Check if author contains any excluded keywords
            author = item["translation"][locale_key].get("author", "").lower()
            if any(keyword in author for keyword in author_exclude_keyword):
                continue
            
            raw_text = item["raw"]
            translated_text = item["translation"][locale_key]["text"]
            valid_items.append((raw_text, translated_text))
    
    # Shuffle the items randomly
    random.shuffle(valid_items)
    
    # Take only the first 'limit' items
    selected_items = valid_items[:limit]
    
    # Format output as "orig: text" pairs
    result_lines = []
    for raw_text, translated_text in selected_items:
        result_lines.append(f"{raw_text}: {translated_text}")
    
    return '\n'.join(result_lines)