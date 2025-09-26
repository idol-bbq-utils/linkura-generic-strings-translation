
import json
import re
from pathlib import Path

def extract_japanese_texts(data):
    """
    Extract Japanese text from JSON data
    Converts Unicode escape sequences to UTF-8 and filters for Japanese characters
    """
    import re
    
    japanese_texts = []
    
    def decode_unicode_escapes(text):
        """Safely decode Unicode escape sequences in text"""
        def replace_unicode(match):
            try:
                code = int(match.group(1), 16)
                return chr(code)
            except (ValueError, OverflowError):
                return match.group(0)  # Return original if can't decode
        
        # Handle \uXXXX patterns
        unicode_pattern = re.compile(r'\\u([0-9a-fA-F]{4})')
        return unicode_pattern.sub(replace_unicode, text)
    
    def process_item(item):
        if isinstance(item, dict):
            # Look for 'value' field in dictionary items
            if 'value' in item:
                text = item['value']
                if isinstance(text, str) and text.strip():
                    # Convert Unicode escape sequences to actual characters
                    decoded_text = decode_unicode_escapes(text)
                    # Check if text contains Japanese characters
                    if is_japanese_text(decoded_text):
                        japanese_texts.append(decoded_text)
            # Recursively process other values
            for value in item.values():
                process_item(value)
        elif isinstance(item, list):
            for element in item:
                process_item(element)
        elif isinstance(item, str) and item.strip():
            # Process string directly
            decoded_text = decode_unicode_escapes(item)
            if is_japanese_text(decoded_text):
                japanese_texts.append(decoded_text)
    
    process_item(data)
    return japanese_texts


def is_japanese_text(text):
    """
    Check if text contains Japanese characters (Hiragana, Katakana, Kanji)
    检查文本是否包含日文字符（平假名、片假名、汉字）
    """
    if not text:
        return False
    
    # Japanese Unicode ranges:
    # Hiragana: U+3040-U+309F
    # Katakana: U+30A0-U+30FF
    # CJK Unified Ideographs (Kanji): U+4E00-U+9FAF
    # Full-width characters: U+FF00-U+FFEF
    japanese_ranges = [
        (0x3040, 0x309F),  # Hiragana
        (0x30A0, 0x30FF),  # Katakana
        (0x4E00, 0x9FAF),  # CJK Unified Ideographs (Kanji)
        (0xFF00, 0xFFEF),  # Full-width forms
    ]
    
    for char in text:
        char_code = ord(char)
        for start, end in japanese_ranges:
            if start <= char_code <= end:
                return True
    return False

def gen(input_file: Path, output_dir: Path):
    if not input_file.exists():
        print(f"Error: Input file {input_file} not found")
        return 1
    
    try:
        # Read input JSON file
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract Japanese text from the data
        japanese_texts = extract_japanese_texts(data)
        
        # Remove duplicates while preserving order
        unique_texts = list(dict.fromkeys(japanese_texts))
        
        print(f"Found {len(japanese_texts)} total Japanese texts")
        print(f"Found {len(unique_texts)} unique Japanese texts")
        
        # Write to RAW_DIR
        raw_output_path = output_dir / f"{input_file.stem}_raw.json"
        with open(raw_output_path, 'w', encoding='utf-8') as f:
            json.dump(unique_texts, f, ensure_ascii=False, indent=4)
        print(f"Raw output written to: {raw_output_path}")
        
        # Check and update OUTPUT_DIR (data directory)
        from pathlib import Path
        data_dir = Path("data")
        if data_dir.exists():
            data_output_path = data_dir / f"{input_file.stem}.json"
            _update_output_dir_file(data_output_path, unique_texts)
        else:
            print(f"OUTPUT_DIR (data) does not exist, skipping data directory update")
        
        return 0
        
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in {input_file}: {e}")
        return 1
    except Exception as e:
        print(f"Error processing file: {e}")
        return 1


def _update_output_dir_file(output_path: Path, new_texts: list):
    """
    Check if file exists in OUTPUT_DIR and update it with new content if needed
    """
    try:
        existing_texts = []
        
        # Read existing file if it exists
        if output_path.exists():
            with open(output_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                if isinstance(existing_data, list):
                    existing_texts = existing_data
                print(f"Found existing file with {len(existing_texts)} entries: {output_path}")
        
        # Extract existing text strings for comparison
        # Handle both formats: simple strings and dict objects with "raw" field
        existing_text_strings = []
        for item in existing_texts:
            if isinstance(item, dict) and "raw" in item:
                existing_text_strings.append(item["raw"])
            elif isinstance(item, str):
                existing_text_strings.append(item)
        
        # Find new texts that don't exist in the current file
        existing_set = set(existing_text_strings)
        new_unique_texts = [text for text in new_texts if text not in existing_set]
        
        if new_unique_texts:
            # Create properly formatted objects for new texts
            new_objects = []
            for text in new_unique_texts:
                new_objects.append({
                    "raw": text,
                    "translation": {}
                })
            
            # Append new objects to the end
            updated_texts = existing_texts + new_objects
            
            # Write updated content back to file
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(updated_texts, f, ensure_ascii=False, indent=2)
            
            print(f"Updated {output_path}: added {len(new_unique_texts)} new entries")
            print(f"Total entries in file: {len(updated_texts)}")
        else:
            print(f"No new entries to add to {output_path}")
            
    except json.JSONDecodeError as e:
        print(f"Error reading existing file {output_path}: {e}")
        # If existing file is corrupted, create new one with proper format
        new_objects = []
        for text in new_texts:
            new_objects.append({
                "raw": text,
                "translation": {}
            })
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(new_objects, f, ensure_ascii=False, indent=2)
        print(f"Created new file due to read error: {output_path}")
    except Exception as e:
        print(f"Error updating output file {output_path}: {e}")
