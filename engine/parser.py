from __future__ import annotations


from bs4 import BeautifulSoup
from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256

import re


GR_PATTERN = re.compile(r"G\.R\.\s*No\.\s*[\w\-]+", re.IGNORECASE)


@dataclass 
class ParsedCase:
    source: str
    source_url: str
    gr_no: str | None
    title: str
    decision_date: str | None
    justice: str | None
    category: str | None
    full_text: str
    clean_text: str
    text_hash: str
    
    
def clean_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def extract_gr_no(text: str) -> str | None:
    match = GR_PATTERN.search(text)
    return match.group(0) if match else None


def parse_case_html(source: str, source_url: str, html: str) -> ParsedCase:
    soup = BeautifulSoup(html, "lxml")
    text = soup.get_text("\n", strip=True)
    clean_text = clean_whitespace(text)

    title = soup.title.get_text(strip=True) if soup.title else source_url
    gr_no = extract_gr_no(clean_text)
    text_hash = sha256(clean_text.encode("utf-8")).hexdigest()

    return ParsedCase(
        source=source,
        source_url=source_url,
        gr_no=gr_no,
        title=title,
        decision_date=None,
        justice=None,
        category=None,
        full_text=text,
        clean_text=clean_text,
        text_hash=text_hash,
    )