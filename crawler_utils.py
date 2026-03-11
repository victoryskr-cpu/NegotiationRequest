import re
import time
from typing import Dict, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    )
}


def safe_text(value: Optional[str]) -> str:
    return (value or "").strip()


def sleep_brief(sec: float = 0.15):
    time.sleep(sec)


def merge_headers(extra_headers: Optional[Dict] = None) -> Dict:
    headers = dict(DEFAULT_HEADERS)
    if extra_headers:
        headers.update(extra_headers)
    return headers


def fetch_response(
    url: str,
    method: str = "GET",
    params: Optional[Dict] = None,
    data: Optional[Dict] = None,
    json_data: Optional[Dict] = None,
    headers: Optional[Dict] = None,
    timeout: int = 15,
) -> requests.Response:
    merged_headers = merge_headers(headers)
    method = method.upper()

    if method == "POST":
        response = requests.post(
            url,
            params=params,
            data=data,
            json=json_data,
            headers=merged_headers,
            timeout=timeout,
        )
    else:
        response = requests.get(
            url,
            params=params,
            headers=merged_headers,
            timeout=timeout,
        )

    response.raise_for_status()
    return response


def fetch_html_soup(
    url: str,
    method: str = "GET",
    params: Optional[Dict] = None,
    data: Optional[Dict] = None,
    headers: Optional[Dict] = None,
    timeout: int = 15,
) -> BeautifulSoup:
    response = fetch_response(
        url=url,
        method=method,
        params=params,
        data=data,
        headers=headers,
        timeout=timeout,
    )
    return BeautifulSoup(response.text, "html.parser")


def normalize_link(base_url: str, href: str) -> str:
    if not href:
        return ""
    return urljoin(base_url, href)


def extract_date_from_text(text: str) -> str:
    if not text:
        return ""

    text = text.strip()

    patterns = [
        r"(20\d{2}[./-]\d{1,2}[./-]\d{1,2})",
        r"(20\d{2}년\s*\d{1,2}월\s*\d{1,2}일)",
        r"(20\d{2}\s*\.\s*\d{1,2}\s*\.\s*\d{1,2})",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            raw = match.group(1)
            normalized = (
                raw.replace("년", ".")
                   .replace("월", ".")
                   .replace("일", "")
                   .replace("-", ".")
                   .replace("/", ".")
            )
            normalized = re.sub(r"\s+", "", normalized)
            normalized = re.sub(r"\.+", ".", normalized).strip(".")
            return normalized

    return ""


def extract_date_from_item(item: Dict) -> str:
    candidates = [
        item.get("date", ""),
        item.get("date_text", ""),
        item.get("raw_text", ""),
        item.get("title", ""),
    ]

    for text in candidates:
        found = extract_date_from_text(text)
        if found:
            return found
    return ""


def make_result_item(
    region: str,
    title: str,
    link: str,
    date_text: str = "",
    raw_text: str = "",
    source_url: str = "",
) -> Dict:
    item = {
        "region": safe_text(region),
        "title": safe_text(title),
        "link": safe_text(link),
        "date": extract_date_from_text(date_text) if date_text else "",
        "date_text": safe_text(date_text),
        "raw_text": safe_text(raw_text),
        "source_url": safe_text(source_url),
    }
    if not item["date"]:
        item["date"] = extract_date_from_item(item)
    return item


def contains_keyword(text: str, keyword: str) -> bool:
    return safe_text(keyword) in safe_text(text)


def dedupe_results(items):
    seen = set()
    deduped = []

    for item in items:
        key = (
            item.get("region", ""),
            item.get("title", ""),
            item.get("link", ""),
            item.get("date", ""),
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)

    return deduped