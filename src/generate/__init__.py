import json
from pathlib import Path

def merge_translations(raw_file: Path, trans_file: Path, target_file: Path, locale: str, author: str = ""):
    """
    Merge raw file and translation file into target JSON file with locale and author info
    
    Args:
        raw_file: Path to raw text file (JSON array of strings)
        trans_file: Path to translation file (JSON array of strings) 
        target_file: Path to target file (data/stringliteral.json)
        locale: Locale code (e.g., 'zh', 'en', 'ja')
        author: Author name for the translations
    """
    try:
        # Read raw texts
        if not raw_file.exists():
            print(f"Error: Raw file {raw_file} not found")
            return 1
            
        with open(raw_file, 'r', encoding='utf-8') as f:
            raw_texts = json.load(f)
            
        if not isinstance(raw_texts, list):
            print(f"Error: Raw file should contain a JSON array")
            return 1
            
        # Read translations
        if not trans_file.exists():
            print(f"Error: Translation file {trans_file} not found") 
            return 1
            
        with open(trans_file, 'r', encoding='utf-8') as f:
            translations = json.load(f)
            
        if not isinstance(translations, list):
            print(f"Error: Translation file should contain a JSON array")
            return 1
            
        if len(raw_texts) != len(translations):
            print(f"Warning: Raw texts ({len(raw_texts)}) and translations ({len(translations)}) count mismatch")
            
        # Read existing target data
        existing_data = []
        if target_file.exists():
            try:
                with open(target_file, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                if not isinstance(existing_data, list):
                    existing_data = []
            except json.JSONDecodeError:
                print(f"Warning: Target file {target_file} contains invalid JSON, starting fresh")
                existing_data = []
                
        # Create mapping of existing entries by raw text for quick lookup
        existing_map = {}
        for entry in existing_data:
            if isinstance(entry, dict) and 'raw' in entry:
                existing_map[entry['raw']] = entry
                
        # Process translation and merge
        updated_count = 0
        added_count = 0
        
        for i, raw_text in enumerate(raw_texts):
            translation = translations[i] if i < len(translations) else ""
            
            if raw_text in existing_map:
                # Update existing entry
                entry = existing_map[raw_text]
                if 'translation' not in entry:
                    entry['translation'] = {}
                
                # Update translation for this locale
                entry['translation'][locale] = {
                    'text': translation,
                    'author': author
                }
                updated_count += 1
            else:
                # Create new entry
                new_entry = {
                    'raw': raw_text,
                    'translation': {
                        locale: {
                            'text': translation,
                            'author': author
                        }
                    }
                }
                existing_data.append(new_entry)
                existing_map[raw_text] = new_entry
                added_count += 1
                
        # Write back to target file
        target_file.parent.mkdir(parents=True, exist_ok=True)
        with open(target_file, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
            
        print(f"Merge completed:")
        print(f"  - Added {added_count} new entries")
        print(f"  - Updated {updated_count} existing entries")
        print(f"  - Total entries: {len(existing_data)}")
        print(f"  - Target file: {target_file}")
        
        return 0
        
    except Exception as e:
        print(f"Error merging translations: {e}")
        return 1