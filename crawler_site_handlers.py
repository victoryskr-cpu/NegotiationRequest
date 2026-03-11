import re
from typing import Dict, List, Optional
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


# =========================================================
# 공통 유틸
# =========================================================

def safe_text(value: Optional[str]) -> str:
    return (value or "").strip()


def extract_date_from_text(text: str) -> str:
    """
    기존 프로젝트 함수가 이미 있다면 이 함수는 제거하고 기존 것을 import해서 쓰세요.
    """
    if not text:
        return ""

    text = text.strip()

    patterns = [
        r"(20\d{2}[./-]\d{1,2}[./-]\d{1,2})",
        r"(20\d{2}년\s*\d{1,2}월\s*\d{1,2}일)",
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
                   .replace(" ", "")
            )
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
        result = extract_date_from_text(text)
        if result:
            return result
    return ""


def make_result_item(
    region: str,
    title: str,
    link: str,
    date_text: str = "",
    raw_text: str = "",
) -> Dict:
    return {
        "region": region,
        "title": safe_text(title),
        "link": safe_text(link),
        "date": extract_date_from_text(date_text) if date_text else "",
        "date_text": safe_text(date_text),
        "raw_text": safe_text(raw_text),
    }


def fetch_html(url: str, method: str = "GET", params=None, data=None, headers=None, timeout: int = 15):
    merged_headers = dict(DEFAULT_HEADERS)
    if headers:
        merged_headers.update(headers)

    if method.upper() == "POST":
        response = requests.post(url, params=params, data=data, headers=merged_headers, timeout=timeout)
    else:
        response = requests.get(url, params=params, headers=merged_headers, timeout=timeout)

    response.raise_for_status()
    return response


def parse_html_board_generic(config: Dict) -> List[Dict]:
    """
    config 예시:
    {
        "region": "부산_사상구",
        "url": "...",
        "method": "GET",
        "headers": {},
        "params": {},
        "list_selector": "...",
        "row_selector": "...",
        "title_selector": "...",
        "date_selector": "...",
        "link_selector": "a",
        "keyword": "교섭",
    }
    """
    response = fetch_html(
        url=config["url"],
        method=config.get("method", "GET"),
        params=config.get("params"),
        data=config.get("data"),
        headers=config.get("headers"),
    )

    soup = BeautifulSoup(response.text, "html.parser")

    base_url = config["url"]
    region = config["region"]
    keyword = config.get("keyword", "교섭")

    list_selector = config.get("list_selector", "")
    row_selector = config.get("row_selector", "")
    title_selector = config.get("title_selector", "")
    date_selector = config.get("date_selector", "")
    link_selector = config.get("link_selector", "a")

    root = soup.select_one(list_selector) if list_selector else soup
    if root is None:
        raise ValueError(f"[{region}] list_selector not found: {list_selector}")

    rows = root.select(row_selector) if row_selector else []
    if not rows:
        raise ValueError(f"[{region}] row_selector not found or empty: {row_selector}")

    results = []

    for row in rows:
        title_node = row.select_one(title_selector) if title_selector else None
        if not title_node:
            continue

        title = safe_text(title_node.get_text(" ", strip=True))
        if keyword not in title:
            continue

        link_node = row.select_one(link_selector) if link_selector else title_node
        href = ""
        if link_node and link_node.has_attr("href"):
            href = urljoin(base_url, link_node["href"])

        date_text = ""
        if date_selector:
            date_node = row.select_one(date_selector)
            if date_node:
                date_text = safe_text(date_node.get_text(" ", strip=True))

        raw_text = safe_text(row.get_text(" ", strip=True))

        item = make_result_item(
            region=region,
            title=title,
            link=href,
            date_text=date_text,
            raw_text=raw_text,
        )
        if not item["date"]:
            item["date"] = extract_date_from_item(item)

        results.append(item)

    return results


# =========================================================
# 사이트별 템플릿
# 실제 selector/url은 확인 후 채우면 됨
# =========================================================

def crawl_busan_sasang() -> List[Dict]:
    config = {
        "region": "부산_사상구",
        "url": "",  # TODO: 실제 게시판 URL
        "method": "GET",
        "headers": {},
        "params": {},
        "list_selector": "",     # TODO
        "row_selector": "",      # TODO
        "title_selector": "",    # TODO
        "date_selector": "",     # TODO
        "link_selector": "a",
        "keyword": "교섭",
    }
    return parse_html_board_generic(config)


def crawl_gyeonggi_namyangju() -> List[Dict]:
    config = {
        "region": "경기_남양주",
        "url": "",  # TODO
        "method": "GET",
        "headers": {},
        "params": {},            # 검색어 GET 파라미터면 여기에 반영
        "list_selector": "",     # TODO
        "row_selector": "",      # TODO
        "title_selector": "",    # TODO
        "date_selector": "",     # TODO
        "link_selector": "a",
        "keyword": "교섭",
    }
    return parse_html_board_generic(config)


def crawl_chungbuk_chungju() -> List[Dict]:
    config = {
        "region": "충북_충주",
        "url": "",  # TODO
        "method": "GET",
        "headers": {},
        "params": {},
        "list_selector": "",     # TODO
        "row_selector": "",      # TODO
        "title_selector": "",    # TODO
        "date_selector": "",     # TODO
        "link_selector": "a",
        "keyword": "교섭",
    }
    return parse_html_board_generic(config)


# =========================================================
# 고난도 후보용 템플릿
# =========================================================

def crawl_daegu_placeholder() -> List[Dict]:
    """
    대구광역시는 POST/AJAX/API 가능성이 높아서
    먼저 Network 확인 후 별도 구현 권장.
    """
    raise NotImplementedError("대구광역시는 POST/AJAX 구조 확인 후 구현 필요")


def crawl_cheongju_placeholder() -> List[Dict]:
    """
    청주도 POST/AJAX 가능성이 높음.
    검색 요청 구조 먼저 확인 권장.
    """
    raise NotImplementedError("충북_청주는 검색 요청 구조 확인 후 구현 필요")


# =========================================================
# region -> handler 매핑
# =========================================================

SITE_HANDLER_MAP = {
    "부산_사상구": crawl_busan_sasang,
    "경기_남양주": crawl_gyeonggi_namyangju,
    "충북_충주": crawl_chungbuk_chungju,

    # 향후 구현
    "대구광역시": crawl_daegu_placeholder,
    "충북_청주": crawl_cheongju_placeholder,
}


def run_site_handler(region: str) -> List[Dict]:
    handler = SITE_HANDLER_MAP.get(region)
    if not handler:
        raise ValueError(f"등록된 site handler가 없습니다: {region}")
    return handler()