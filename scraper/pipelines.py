from __future__ import annotations

from datetime import datetime, UTC
from hashlib import sha256
from pathlib import Path
import json


RAW_ROOT = Path("data/raw/lawphil")


class RawHtmlPipeline:
    def process_item(self, item, spider):
        fetched_at = datetime.now(UTC).isoformat()
        html = item["html"]
        digest = sha256(html.encode("utf-8")).hexdigest()
        subdir = RAW_ROOT / datetime.now(UTC).strftime("%Y")
        subdir.mkdir(parents=True, exist_ok=True)

        html_path = subdir / f"{digest}.html"
        meta_path = subdir / f"{digest}.json"

        html_path.write_text(html, encoding="utf-8")
        meta_path.write_text(
            json.dumps(
                {
                    "source": item["source"],
                    "source_url": item["source_url"],
                    "fetched_at": fetched_at,
                    "http_status": item["http_status"],
                    "title_raw": item.get("title_raw"),
                    "html_hash": digest,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        return item