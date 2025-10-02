import argparse
import sys
from pathlib import Path
from src.generate import analyze
from src import gentodo, generate
from src.model.localization import I18nLanguage
from src.translate import translate_file, claude
import os

i18n = [lang.value for lang in I18nLanguage]
i18n_map = {lang.value: lang for lang in I18nLanguage}
OUTPUT_DIR = Path("data")
RAW_DIR = Path("raw")
README_FILE = Path("README.md")


def command_gentodo(args):
    """From raw file to translation todo file"""
    gentodo.gen(Path(args.input_file), RAW_DIR)

def command_translate(args):
    """
    Translation tool, providing basic large model API translation interface

    And user also can translated by handmade
    """
    if args.file:
        client = claude.setup_client(os.environ["ANTHROPIC_API_KEY"], os.environ["ANTHROPIC_BASE_URL"])
        limit = args.limit if hasattr(args, 'limit') and args.limit else None
        translate_file(client, Path(args.file), i18n_map.get(args.locale, I18nLanguage.ZH_CN), limit=limit)
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