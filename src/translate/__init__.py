from pathlib import Path
from ..model.localization import I18nLanguage
import src.translate.prompt.zh_cn as zh_cn
from src.translate.prompt import get_reference_prompt
import json
from typing import List, Iterator
import anthropic


prompt_module_map = {
    I18nLanguage.ZH_CN: zh_cn
}

def translate_file(api_client: anthropic.Anthropic, file: Path, target_language: I18nLanguage, chunk_size: int = 48, limit: int = None) -> None:
    """
    Translate a file containing text entries to the specified language with chunked processing.
    
    Args:
        api_client: Anthropic API client
        file: Path to the input file containing text entries
        target_language: Target language for translation
        chunk_size: Number of texts to process in each chunk (default: 24)
        limit: Maximum number of items to translate (default: None, translate all)
    """
    prompt_module = prompt_module_map.get(target_language)
    if not prompt_module:
        raise ValueError(f"No translation prompt module found for {target_language.value}")
    
    # Read the input file
    with open(file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Filter out texts that are already translated for the target locale
    locale_key = target_language.value
    untranslated_items = []
    
    for item in data:
        if (isinstance(item, dict) and 
            "raw" in item and 
            "translation" in item):
            
            # Check if translation exists and is not empty
            if (locale_key not in item["translation"] or 
                not item["translation"][locale_key].get("text", "").strip()):
                untranslated_items.append(item)
    
    if not untranslated_items:
        print(f"All texts are already translated for {target_language.value}")
        return
    
    print(f"Found {len(untranslated_items)} untranslated items for {target_language.value}")
    
    # Apply limit if specified
    if limit is not None and limit > 0:
        original_count = len(untranslated_items)
        untranslated_items = untranslated_items[:limit]
        print(f"Limited to {len(untranslated_items)} items (original: {original_count})")
    
    # Get base prompt and reference examples
    base_prompt = prompt_module.prompt
    translate_reference = get_reference_prompt(file, target_language, 40)

    
    # Process texts in chunks
    for chunk_idx, chunk in enumerate(_chunk_items(untranslated_items, chunk_size)):
        print(f"Processing chunk {chunk_idx + 1} with {len(chunk)} items...")
        
        # Extract raw texts for this chunk
        raw_texts = [item["raw"] for item in chunk]
        
        # Create prompt for this chunk
        texts_array_str = json.dumps(raw_texts, ensure_ascii=False, indent=2)
        
        full_prompt = f"""{base_prompt}

## Translation Reference Examples:
{translate_reference}

## Original Texts to Translate:
{texts_array_str}

## Output Format:
Return ONLY a JSON array of translated texts in the same order as the original array. Do not include any explanatory text. Do not return markdown code format, just json string
Example format: ["translated text 1", "translated text 2", ...]
"""
        
        # print(f"Prompt for chunk {chunk_idx + 1}:")
        # print("=" * 50)
        # print(full_prompt)
        # print("=" * 50)
        
        # Call translation API
        model_id = "claude-sonnet-4-20250514"
        message = api_client.messages.create(
            model=model_id,
            max_tokens=4000,
            messages=[
                {"role": "user", "content": full_prompt}
            ]
        )
        response = message.content[0].text
        
        try:
            # Parse JSON response to get translated texts array
            translated_texts = json.loads(response.strip())
            
            if not isinstance(translated_texts, list):
                print(f"Warning: API response is not a list for chunk {chunk_idx + 1}")
                continue
                
            if len(translated_texts) != len(raw_texts):
                print(f"Warning: Translation count mismatch for chunk {chunk_idx + 1}. Expected {len(raw_texts)}, got {len(translated_texts)}")
                continue
            
            # Update the untranslated items with translations
            for i, item in enumerate(chunk):
                if i < len(translated_texts):
                    # Ensure translation structure exists
                    if locale_key not in item["translation"]:
                        item["translation"][locale_key] = {}
                    
                    # Fill in the translation
                    item["translation"][locale_key]["text"] = translated_texts[i]
                    item["translation"][locale_key]["author"] = model_id
            
            # Write updated data back to file after each chunk
            try:
                with open(file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print(f"Successfully translated and saved {len(translated_texts)} items in chunk {chunk_idx + 1}")
            except Exception as e:
                print(f"Error writing file after chunk {chunk_idx + 1}: {e}")
                # Continue processing other chunks even if one write fails
                continue
            
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response for chunk {chunk_idx + 1}: {e}")
            print(f"Response content: {response}")
            continue
        except Exception as e:
            print(f"Error processing chunk {chunk_idx + 1}: {e}")
            continue
    
    print(f"Translation process completed for file: {file}")
    print(f"Total chunks processed: {chunk_idx + 1}")



def _chunk_items(items: List[dict], chunk_size: int) -> Iterator[List[dict]]:
    """
    Split items into chunks of specified size.
    
    Args:
        items: List of items to chunk
        chunk_size: Size of each chunk
        
    Yields:
        List of items for each chunk
    """
    for i in range(0, len(items), chunk_size):
        yield items[i:i + chunk_size]
