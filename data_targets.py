from copy import deepcopy
from typing import List, Dict, Tuple


# =========================================================
# 기존 자동화 완료 대상
# =========================================================

raw_target_data = [
    {
        "region": "경상남도",
        "label": "경상남도",
        "url": "",
        "crawl_type": "post",
        "method": "POST",
        "status": "verified",
        "enabled": True,
    },
    {
        "region": "울산광역시",
        "label": "울산광역시",
        "url": "",
        "crawl_type": "post",
        "method": "POST",
        "status": "verified",
        "enabled": True,
    },
    {
        "region": "경기도",
        "label": "경기도",
        "url": "",
        "crawl_type": "ajax",
        "method": "POST",
        "status": "verified",
        "enabled": True,
    },
]


# =========================================================
# 기존 manual_data 예시
# 실제 프로젝트에 맞게 기존 manual_data를 여기에 두면 됨
# =========================================================

manual_data = [
    {"region": "서울_강북구", "label": "서울 강북구"},
    {"region": "서울_관악구", "label": "서울 관악구"},
    {"region": "서울_서대문구", "label": "서울 서대문구"},
    {"region": "서울_송파구", "label": "서울 송파구"},
    {"region": "서울_중구", "label": "서울 중구"},
    {"region": "부산_사상구", "label": "부산 사상구"},
    {"region": "대구광역시", "label": "대구광역시"},
    {"region": "경기_남양주", "label": "경기 남양주"},
    {"region": "충북_청주", "label": "충북 청주"},
    {"region": "충북_충주", "label": "충북 충주"},

    # 예시: 남은 수동 확인 대상
    {"region": "전북_전주", "label": "전북 전주"},
    {"region": "경기_의정부", "label": "경기 의정부"},
]


# =========================================================
# 1차 자동화군
# =========================================================

FIRST_AUTOMATION_BATCH = [
    "서울_강북구",
    "서울_관악구",
    "서울_서대문구",
    "서울_송파구",
    "서울_중구",
    "부산_사상구",
    "대구광역시",
    "경기_남양주",
    "충북_청주",
    "충북_충주",
]


# =========================================================
# 지역별 초기 preset
# url / selector / params는 실제 분석 후 채움
# =========================================================

TARGET_PRESET_MAP = {
    "서울_강북구": {
        "label": "서울 강북구",
        "crawl_type": "html",
        "method": "GET",
        "risk": "medium",
        "notes": "서울 구청형. HTML/GET 검색 가능성.",
    },
    "서울_관악구": {
        "label": "서울 관악구",
        "crawl_type": "html",
        "method": "GET",
        "risk": "medium",
        "notes": "서울 구청형. 검색 결과 페이지 구조 확인 필요.",
    },
    "서울_서대문구": {
        "label": "서울 서대문구",
        "crawl_type": "html",
        "method": "GET",
        "risk": "medium",
        "notes": "서울 구청형. 목록형 HTML 가능성.",
    },
    "서울_송파구": {
        "label": "서울 송파구",
        "crawl_type": "html",
        "method": "GET",
        "risk": "medium",
        "notes": "게시물 수 많을 수 있어 페이지네이션 주의.",
    },
    "서울_중구": {
        "label": "서울 중구",
        "crawl_type": "html",
        "method": "GET",
        "risk": "medium",
        "notes": "검색 form 구조 확인 필요.",
    },
    "부산_사상구": {
        "label": "부산 사상구",
        "crawl_type": "html",
        "method": "GET",
        "risk": "low",
        "notes": "빠른 성공 후보. 표준 HTML 게시판 가능성.",
    },
    "대구광역시": {
        "label": "대구광역시",
        "crawl_type": "post",
        "method": "POST",
        "risk": "high",
        "notes": "광역시 사이트. POST/AJAX/API 가능성 높음.",
    },
    "경기_남양주": {
        "label": "경기 남양주",
        "crawl_type": "html",
        "method": "GET",
        "risk": "low",
        "notes": "표준 시청 게시판이면 빠르게 처리 가능.",
    },
    "충북_청주": {
        "label": "충북 청주",
        "crawl_type": "post",
        "method": "POST",
        "risk": "high",
        "notes": "대형 시청 사이트. POST/API 가능성.",
    },
    "충북_충주": {
        "label": "충북 충주",
        "crawl_type": "html",
        "method": "GET",
        "risk": "low",
        "notes": "중형 지자체 게시판 표준 구조 가능성.",
    },
}


# =========================================================
# 우선순위
# =========================================================

PRIORITY_ORDER = {
    "부산_사상구": 1,
    "경기_남양주": 2,
    "충북_충주": 3,
    "서울_강북구": 4,
    "서울_관악구": 5,
    "서울_서대문구": 6,
    "서울_송파구": 7,
    "서울_중구": 8,
    "충북_청주": 9,
    "대구광역시": 10,
}


# =========================================================
# 공통 후보 생성
# =========================================================

def build_candidate_target(region: str) -> Dict:
    preset = TARGET_PRESET_MAP.get(region, {})

    return {
        "region": region,
        "label": preset.get("label", region.replace("_", " ")),
        "url": preset.get("url", ""),
        "crawl_type": preset.get("crawl_type", "html"),   # html / post / ajax / js
        "method": preset.get("method", "GET"),            # GET / POST
        "search_keyword": "교섭",
        "status": "candidate",                            # candidate / verified / failed
        "risk": preset.get("risk", "medium"),
        "notes": preset.get("notes", ""),

        # 테스트 결과
        "last_test_result": None,                         # success / partial / fail
        "last_test_message": "",

        # HTML 파싱용
        "list_selector": "",
        "row_selector": "",
        "title_selector": "",
        "date_selector": "",
        "link_selector": "",

        # 검색 / 페이지
        "search_param": "",
        "page_param": "",
        "page_start": 1,
        "max_pages": 3,

        # POST
        "post_url": "",
        "post_data_template": {},

        # AJAX
        "ajax_url": "",
        "ajax_params_template": {},

        # 요청 헤더
        "headers": {},

        # 상세 페이지 필요 여부
        "requires_detail": False,
        "detail_date_selector": "",

        # 실행 여부
        "enabled": True,
    }


def build_candidate_target_data(regions: List[str]) -> List[Dict]:
    return [build_candidate_target(region) for region in regions]


def sort_candidates_by_priority(candidate_target_data: List[Dict]) -> List[Dict]:
    return sorted(
        candidate_target_data,
        key=lambda x: PRIORITY_ORDER.get(x.get("region"), 999)
    )


# =========================================================
# manual_data 분리
# =========================================================

def split_manual_data(
    manual_data: List[Dict],
    automation_regions: List[str]
) -> Tuple[List[Dict], List[Dict]]:
    region_set = set(automation_regions)

    manual_backup_data = [
        deepcopy(item)
        for item in manual_data
        if item.get("region") in region_set
    ]

    remaining_manual_data = [
        deepcopy(item)
        for item in manual_data
        if item.get("region") not in region_set
    ]

    return remaining_manual_data, manual_backup_data


# =========================================================
# 후보 상태 갱신
# =========================================================

def update_candidate_status(
    candidate_target_data: List[Dict],
    region: str,
    test_result: str,
    message: str = ""
) -> List[Dict]:
    updated = []

    for item in candidate_target_data:
        new_item = deepcopy(item)

        if new_item.get("region") == region:
            new_item["last_test_result"] = test_result
            new_item["last_test_message"] = message

            if test_result == "success":
                new_item["status"] = "verified"
            elif test_result == "partial":
                new_item["status"] = "candidate"
            elif test_result == "fail":
                new_item["status"] = "failed"

        updated.append(new_item)

    return updated


# =========================================================
# verified만 raw_target_data에 편입
# =========================================================

def merge_verified_targets(
    raw_target_data: List[Dict],
    candidate_target_data: List[Dict]
) -> List[Dict]:
    existing_regions = {item.get("region") for item in raw_target_data}
    merged = deepcopy(raw_target_data)

    for item in candidate_target_data:
        if item.get("status") == "verified" and item.get("region") not in existing_regions:
            merged.append(deepcopy(item))

    return merged


def extract_failed_targets(candidate_target_data: List[Dict]) -> List[Dict]:
    return [
        deepcopy(item)
        for item in candidate_target_data
        if item.get("status") == "failed"
    ]


# =========================================================
# 1차 자동화군 준비
# =========================================================

def prepare_first_automation_batch(
    current_raw_target_data: List[Dict],
    current_manual_data: List[Dict],
) -> Dict[str, List[Dict]]:
    candidate_target_data = build_candidate_target_data(FIRST_AUTOMATION_BATCH)
    candidate_target_data = sort_candidates_by_priority(candidate_target_data)

    remaining_manual_data, manual_backup_data = split_manual_data(
        manual_data=current_manual_data,
        automation_regions=FIRST_AUTOMATION_BATCH
    )

    failed_target_data = extract_failed_targets(candidate_target_data)

    return {
        "raw_target_data": deepcopy(current_raw_target_data),
        "manual_data": remaining_manual_data,
        "manual_backup_data": manual_backup_data,
        "candidate_target_data": candidate_target_data,
        "failed_target_data": failed_target_data,
    }


# =========================================================
# 검증 완료 후 final 반영
# =========================================================

def finalize_verified_targets(
    current_raw_target_data: List[Dict],
    candidate_target_data: List[Dict]
) -> Dict[str, List[Dict]]:
    updated_raw_target_data = merge_verified_targets(current_raw_target_data, candidate_target_data)
    failed_target_data = extract_failed_targets(candidate_target_data)

    return {
        "raw_target_data": updated_raw_target_data,
        "candidate_target_data": candidate_target_data,
        "failed_target_data": failed_target_data,
    }


# =========================================================
# 다음 자동화 후보 추천
# =========================================================

def recommend_next_candidates(current_manual_data: List[Dict], limit: int = 10) -> List[Dict]:
    preferred_prefixes = ["서울_", "경기_", "충북_"]

    def score(item: Dict) -> int:
        region = item.get("region", "")
        if any(region.startswith(prefix) for prefix in preferred_prefixes):
            return 0
        return 1

    return sorted(current_manual_data, key=score)[:limit]


# =========================================================
# 단독 실행 예시
# =========================================================

if __name__ == "__main__":
    prepared = prepare_first_automation_batch(
        current_raw_target_data=raw_target_data,
        current_manual_data=manual_data,
    )

    candidate_target_data = prepared["candidate_target_data"]
    manual_backup_data = prepared["manual_backup_data"]
    manual_data_after = prepared["manual_data"]

    print("=== candidate_target_data ===")
    for item in candidate_target_data:
        print(
            item["region"],
            item["status"],
            item["risk"],
            item["crawl_type"]
        )

    print("\n=== manual_backup_data ===")
    for item in manual_backup_data:
        print(item["region"])

    print("\n=== remaining manual_data ===")
    for item in manual_data_after:
        print(item["region"])