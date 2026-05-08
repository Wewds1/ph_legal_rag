import json
import os
from pathlib import Path
from typing import Optional
import google.generativeai as genai
from engine.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure GenAI
genai.configure(api_key=settings.llm_api_key)

BATCH_SIZE = 5 
PROCESSED_DIR = Path("data/processed")

def translate_text(text: str, target_lang: str = "Filipino") -> Optional[str]:
    """Translate text using GenAI.
    
    Args:
        text: English text to translate
        target_lang: Target language (Filipino/Tagalog)
    
    Returns:
        Translated text or None on error
    """
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        prompt = f"Translate the following legal text to {target_lang}. Keep legal terminology accurate:\n\n{text[:2000]}"
        response = model.generate_content(prompt)
        return response.text if response else None
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return None


def process_case_file(filepath: Path) -> bool:
    """Translate a single case JSON file and save back.
    
    Args:
        filepath: Path to case JSON file
    
    Returns:
        True if successful
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            case_data = json.load(f)
        
        # Skip if already translated
        if "tagalog_text" in case_data:
            logger.info(f"Skipping {filepath.name} (already translated)")
            return True
        
        logger.info(f"Translating {filepath.name}...")
        
        # Translate title
        if "title" in case_data and case_data["title"]:
            case_data["tagalog_title"] = translate_text(case_data["title"])
        
        # Translate full_text (first 2000 chars for cost control; truncate long texts)
        if "full_text" in case_data and case_data["full_text"]:
            case_data["tagalog_text"] = translate_text(case_data["full_text"])
        
        # Write back to file
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(case_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✓ Translated {filepath.name}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to process {filepath.name}: {e}")
        return False


def main():
    """Translate all case files in data/processed/"""
    
    # Collect all JSON files
    case_files = sorted(PROCESSED_DIR.glob("*.json"))
    logger.info(f"Found {len(case_files)} case files to translate")
    
    # Process in batches
    success_count = 0
    for i, filepath in enumerate(case_files):
        if process_case_file(filepath):
            success_count += 1
        
        # Batch pause every N files (rate limiting)
        if (i + 1) % BATCH_SIZE == 0:
            logger.info(f"Batch {i + 1}/{len(case_files)} done. Pausing...")
            import time
            time.sleep(2)  # 2-second pause between batches
    
    logger.info(f"\n✓ Translation complete: {success_count}/{len(case_files)} cases translated")


if __name__ == "__main__":
    main()