from pathlib import Path
import json
from engine.parser import parse_case_html


def main():
    raw_root = Path("data/raw/lawphil/2026")
    processed_root = Path("data/processed")
    processed_root.mkdir(parents=True, exist_ok=True)

    for html_file in sorted(raw_root.rglob("*.html")):
        meta_file = html_file.with_suffix(".json")
        
        if not meta_file.exists():
            print(f"Skipping {html_file.name} - no metadata")
            continue
        
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
        html = html_file.read_text(encoding="utf-8")
        
        parsed = parse_case_html(meta["source"], meta["source_url"], html)
        
        output_file = processed_root / f"{parsed.text_hash}.json"
        output_file.write_text(
            json.dumps(
                {
                    "source": parsed.source,
                    "source_url": parsed.source_url,
                    "gr_no": parsed.gr_no,
                    "title": parsed.title,
                    "decision_date": parsed.decision_date,
                    "justice": parsed.justice,
                    "category": parsed.category,
                    "full_text": parsed.full_text,
                    "clean_text": parsed.clean_text,
                    "text_hash": parsed.text_hash,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        print(f"Parsed: {parsed.title}")


if __name__ == "__main__":
    main()