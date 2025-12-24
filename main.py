import argparse
import sys
from pathlib import Path
from src.generate import analyze
from src import gentodo, generate
from src.model.localization import I18nLanguage
from src.translate import translate_file
from src.translate.translator import create_translator
import os

i18n = [lang.value for lang in I18nLanguage]
i18n_map = {lang.value: lang for lang in I18nLanguage}
OUTPUT_DIR = Path("data")
RAW_DIR = Path("raw")
README_FILE = Path("README.md")


def command_gentodo(args):
    """From raw file to translation todo file"""
    
    input_dir = args.input if hasattr(args, 'input') and args.input else RAW_DIR
    output_dir = args.output if hasattr(args, 'output') and args.output else OUTPUT_DIR
    
    print(f"Extracting Japanese content from {input_dir} to {output_dir}")
    
    try:
        gentodo.gen(Path(input_dir), Path(output_dir))
        print("gentodo command completed successfully!")
        return 0
    except Exception as e:
        print(f"Error executing gentodo: {e}")
        return 1

def command_translate(args):
    """
    Translation tool, providing basic large model API translation interface

    And user also can translated by handmade
    """
    if args.file:
        # Get API credentials from arguments or environment variables
        api_key = args.api_key if hasattr(args, 'api_key') and args.api_key else os.environ.get("ANTHROPIC_API_KEY")
        base_url = args.base_url if hasattr(args, 'base_url') and args.base_url else os.environ.get("ANTHROPIC_BASE_URL")
        model_id = args.model_id if hasattr(args, 'model_id') and args.model_id else None
        provider = args.provider if hasattr(args, 'provider') and args.provider else "claude"
        
        if not api_key:
            print("Error: API key is required. Set ANTHROPIC_API_KEY environment variable or use --api-key argument.")
            return 1
        
        # Create translator instance
        translator = create_translator(
            provider=provider,
            api_key=api_key,
            base_url=base_url,
            model_id=model_id
        )
        
        limit = args.limit if hasattr(args, 'limit') and args.limit else None
        
        # if file is directory
        if Path(args.file).is_dir():
            for file in Path(args.file).glob("*.json"):
                print(f"Translating file: {file}")
                translate_file(translator, file, i18n_map.get(args.locale, I18nLanguage.ZH_CN), limit=limit)
        else:
            translate_file(translator, Path(args.file), i18n_map.get(args.locale, I18nLanguage.ZH_CN), limit=limit)
    return 0

def command_generate(args):
    """Generate translated files and merge translations"""
    if args.raw_file and args.trans_file:
        # Merge translations into target file
        raw_file = Path(args.raw_file)
        trans_file = Path(args.trans_file)
        target_file = OUTPUT_DIR / "stringliteral.json"
        
        result = generate.merge_translations(
            raw_file=raw_file,
            trans_file=trans_file,
            target_file=target_file,
            locale=args.locale,
            author=args.author
        )
        
        if result != 0:
            return result
            
        print(f"Translations merged successfully for locale: {args.locale}")
    
    # Generate progress reports
    if OUTPUT_DIR.exists():
        (total, translated) = analyze.analyze_translation_progress(RAW_DIR, OUTPUT_DIR, locale=args.locale)
        analyze.write_translation_progress(README_FILE, total, translated, locale=args.locale)
        print(f"Progress report updated in {README_FILE}")
    
    return 0

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Linkura Translation Tool Template",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--locale', '-l',
        default='zh-CN',
        choices=i18n,
        help='Translation locale'
    )
    
    subparsers = parser.add_subparsers(
        dest='command',
        metavar='COMMAND'
    )
    # gentodo
    parser_gentodo = subparsers.add_parser(
        'gentodo',
        help='From raw file to translation todo file',
    )
    parser_gentodo.add_argument(
        '--input-file', '-i',
        required=True,
        help='Path to input JSON file (e.g., stringliteral.json)'
    )
    parser_gentodo.set_defaults(func=command_gentodo)
    
    # translate
    parser_translate = subparsers.add_parser(
        'translate',
        help='Translation tool, providing basic large model API translation interface',
    )
    parser_translate.add_argument(
        '--file', '-f',
        help='Path to the input file containing text to translate'
    )
    parser_translate.add_argument(
        '--limit',
        type=int,
        help='Maximum number of items to translate (default: translate all untranslated items)'
    )
    parser_translate.add_argument(
        '--api-key',
        help='API key for the LLM service (default: read from ANTHROPIC_API_KEY env var)'
    )
    parser_translate.add_argument(
        '--base-url',
        help='Base URL for the API endpoint (default: read from ANTHROPIC_BASE_URL env var)'
    )
    parser_translate.add_argument(
        '--model-id',
        help='Model identifier to use (default: uses provider default model)'
    )
    parser_translate.add_argument(
        '--provider',
        default='claude',
        choices=['claude', 'deepseek', 'qwen'],
        help='LLM provider to use (default: claude)'
    )
    parser_translate.set_defaults(func=command_translate)
    
    # generate
    parser_generate = subparsers.add_parser(
        'generate',
        help='Generate translated files and merge translations',
    )
    parser_generate.add_argument(
        '--raw-file', '-r',
        help='Path to raw text file (JSON array of strings)'
    )
    parser_generate.add_argument(
        '--trans-file', '-t',
        help='Path to translation file (JSON array of strings)'
    )
    parser_generate.add_argument(
        '--author', '-a',
        default='',
        help='Author name for the translations'
    )
    parser_generate.set_defaults(func=command_generate)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        return args.func(args)
    except Exception as e:
        print(f"Error occurred while executing command: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())