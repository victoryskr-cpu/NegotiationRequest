import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
from io import BytesIO

# -------------------------------------------------
# 기본 설정
# -------------------------------------------------
st.set_page_config(
    page_title="교섭공고 알리미",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------
# 스타일
# -------------------------------------------------
st.markdown("""
    <style>
    .header-container {
        text-align: center;
        margin-top: -20px;
        margin-bottom: 20px;
    }

    .main-title {
        font-size: 1.8rem;
        font-weight: bold;
        margin-bottom: 5px;
    }

    .sub-title {
        font-size: 1.2rem;
        color: #444;
        font-weight: 500;
    }

    .status-text {
        font-weight: bold;
        color: #ff4b4b;
        display: block;
        text-align: center;
        margin-bottom: 10px;
    }

    .stButton {
        display: flex;
        justify-content: center;
    }

    .stButton > button {
        background-color: #007BFF !important;
        color: white !important;
        border-radius: 10px !important;
        min-height: 3.5em !important;
        font-weight: 900 !important;
        font-size: 1.1rem !important;
        border: none !important;
    }

    .stButton > button:hover {
        background-color: #0056b3 !important;
        color: white !important;
    }

    .manual-title {
        font-size: 1.3rem;
        font-weight: bold;
        margin-bottom: 0px;
    }

    .manual-subtitle {
        font-size: 0.9rem;
        color: #666;
        display: block;
        margin-bottom: 10px;
    }

    .guide-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        border: 1px dashed #ff4b4b;
        margin-bottom: 20px;
        font-weight: bold;
        color: #ff4b4b;
    }

    table {
        width: 100%;
        border-collapse: collapse;
        table-layout: fixed;
    }

    th {
        text-align: center !important;
        background-color: #f8f9fa;
        padding: 10px 8px;
    }

    td {
        text-align: center !important;
        vertical-align: middle;
        padding: 10px 8px;
        word-break: break-word;
    }

    .result-table th:nth-child(1), .result-table td:nth-child(1) { width: 160px; }
    .result-table th:nth-child(2), .result-table td:nth-child(2) { width: 140px; }
    .result-table th:nth-child(3), .result-table td:nth-child(3) { width: 160px; }
    .result-table th:nth-child(4), .result-table td:nth-child(4) { width: 150px; }
    .result-table th:nth-child(5), .result-table td:nth-child(5) { width: auto; }
    </style>

    <div class="header-container">
        <h1 class="main-title">지자체 교섭요구공고 확인</h1>
        <p class="sub-title">(돌봄사업장 지역 공고 모니터링)</p>
    </div>
""", unsafe_allow_html=True)

# -------------------------------------------------
# 데이터
# -------------------------------------------------
sort_order = [
    "서울특별시", "부산광역시", "대구광역시", "울산광역시", "강원도",
    "경기도", "전라북도", "경상북도", "경상남도", "충청남도", "충청북도"
]

raw_target_data = {
    "서울특별시": [
        ["서울특별시", "https://www.seoul.go.kr/news/news_notice.do?bbsNo=277&srchText=교섭"],
        ["서울_강남", "https://www.gangnam.go.kr/notice/list.do?mid=ID05_040201&keyfield=BNI_MAIN_TITLE&keyword=교섭"],
        ["서울_강동", "https://www.gangdong.go.kr/web/newportal/notice/01?sv=교섭"],
#        ["서울_강북", "https://www.gangbuk.go.kr/portal/bbs/B0000245/list.do?menuNo=200082&bbsId=&cl1Cd=&optn5=&pageIndex=1&searchCnd2=&searchCnd=&searchWrd=%EA%B5%90%EC%84%AD"],
        ["서울_강서", "https://www.gangseo.seoul.kr/gs040301?srchKey=sj&srchText=교섭"],
        ["서울_구로", "https://www.guro.go.kr/www/selectBbsNttList.do?key=1791&bbsNo=663&searchCnd=SJ&searchKrwd=교섭"],
        ["서울_금천", "https://www.geumcheon.go.kr/portal/tblSeolGosiDetailList.do?key=294&rep=1&searchCnd=all&searchKrwd=%EA%B5%90%EC%84%AD"],
        ["서울_노원", "https://www.nowon.kr/www/user/bbs/BD_selectBbsList.do?q_bbsCode=1003&q_searchVal=%EA%B5%90%EC%84%AD"],
        ["서울_도봉", "https://www.dobong.go.kr/WDB_DEV/gosigong_go/default.asp?strSearchType=1&strSearchKeyword=%EA%B5%90%EC%84%AD"],
        ["서울_동대문", "https://www.ddm.go.kr/www/selectEminwonWebList.do?key=3291&searchCnd=notAncmtSj&searchKrwd=%EA%B5%90%EC%84%AD"],
        ["서울_동작", "https://www.dongjak.go.kr/portal/bbs/B0001297/list.do?menuNo=201317&searchCnd=1&searchWrd=%EA%B5%90%EC%84%AD"],
        ["서울_마포", "https://www.mapo.go.kr/site/main/nPortal/list?sv=%EA%B5%90%EC%84%AD"],
        ["서울_성동", "https://www.sd.go.kr/main/selectBbsNttList.do?key=1473&bbsNo=184&searchCnd=SJ&searchKrwd=%EA%B5%90%EC%84%AD"],
        ["서울_성북", "https://www.sb.go.kr/www/selectEminwonList.do?key=6977&searchCnd2=notAncmtSj&searchKrwd=교섭"],
        ["서울_영등포", "https://www.ydp.go.kr/www/selectEminwonList.do?key=2851&searchCnd=B_Subject&searchKrwd=교섭"],
        ["서울_용산", "https://www.yongsan.go.kr/portal/bbs/B0000095/list.do?menuNo=200233&searchCnd=1&searchWrd=교섭"],
        ["서울_은평", "https://www.ep.go.kr/www/selectEminwonList.do?key=754&searchCnd=notAncmtSj&searchKrwd=교섭"],
        ["서울_중랑", "https://www.jungnang.go.kr/portal/bbs/list/B0000117.do?menuNo=200475&searchWrd=교섭"]
    ],
    "부산광역시": [
        ["부산광역시", "https://www.busan.go.kr/nbgosi/list?schKeyType=A&srchText=%EA%B5%90%EC%84%AD"],
        ["부산_남구", "https://www.bsnamgu.go.kr/index.namgu?menuCd=DOM_000000105001002000&search_key=title&search_val=%EA%B5%90%EC%84%AD"],
        ["부산_동래구", "https://www.dongnae.go.kr/index.dongnae?menuCd=DOM_000000103001003000&search_key=title&search_val=%EA%B5%90%EC%84%AD"]
    ],
    "대구광역시": [
        ["대구_동구", "https://www.dong.daegu.kr/portal/saeol/gosi/list.do?mid=0201020000&searchKrwd=%EA%B5%90%EC%84%AD"],
        ["대구_달서구", "https://www.dalseo.daegu.kr/index.do?menu_id=10000104&searchKey=sj&searchKeyword=%EA%B5%90%EC%84%AD"],
        ["대구_중구", "https://www.jung.daegu.kr/new/pages/administration/page.html?mc=0159&search_key=sj&search_keyword=%EA%B5%90%EC%84%AD"]
    ],
    "울산광역시": [
        ["울산광역시", "https://www.ulsan.go.kr/u/rep/transfer/notice/list.ulsan?mId=001004002000000000"]
    ],
    "강원도": [
        ["강원특별자치도", "https://state.gwd.go.kr/portal/bulletin/notification?searchCondition=TITLE&searchKeyword=%EA%B5%90%EC%84%AD"],
        ["강원_춘천", "https://www.chuncheon.go.kr/cityhall/administrative-info/notice-info/notice-announcement/?searchCnd=SJ&searchWrd=%EA%B5%90%EC%84%AD"]
    ],
    "경기도": [
        ["경기도", "https://www.gg.go.kr/bbs/board.do?bsIdx=469&menuId=1547"],
        ["경기_구리", "https://www.guri.go.kr/www/selectGosiNttList.do?key=387&searchCnd=ALL&searchKrwd=%EA%B5%90%EC%84%AD"],
    ],
    "전라북도": [
        ["전북특별자치도", "https://www.jeonbuk.go.kr/board/list.jeonbuk?boardId=BBS_0000129&searchType=DATA_TITLE&keyword=%EA%B5%90%EC%84%AD"],
        ["전북_군산", "https://www.gunsan.go.kr/main/m141"],
        ["전북_전주", "https://www.jeonju.go.kr/planweb/board/list.9is?boardUid=9be517a7914528ce01930aa3ddc26cf0&contentUid=ff8080818990c349018b041a879f395a&searchType=dataTitle&keyword=%EA%B5%90%EC%84%AD"]
    ],
    "경상북도": [
        ["경상북도", "https://www.gb.go.kr/Main/page.do?bdName=%EA%B3%A0%EC%8B%9C%EA%B3%B5%EA%B3%A0&mnu_uid=6789&word=%EA%B5%90%EC%84%AD"],
        ["경북_칠곡", "https://www.chilgok.go.kr/portal/saeol/gosi/list.do?mId=0201030000"]
    ],
    "경상남도": [
        ["경상남도", "https://www.gyeongnam.go.kr/index.gyeong?menuCd=DOM_000000135003009001"],
        ["경남_김해", "https://www.gimhae.go.kr/03360/00023/00029.web?stype=title&sstring=%EA%B5%90%EC%84%AD"],
        ["경남_의령", "https://www.uiryeong.go.kr/board/list.uiryeong?boardId=BBS_0000070&searchType=DATA_TITLE&keyword=%EA%B5%90%EC%84%AD"],
        ["경남_창원", "https://www.changwon.go.kr/cwportal/10310/10438/10439.web?stype=title&sstring=%EA%B5%90%EC%84%AD"],
        ["경남_함안", "https://www.haman.go.kr/00960/00962.web?stype=title&sstring=%EA%B5%90%EC%84%AD"]
    ],
    "충청남도": [
        ["충청남도", "https://www.chungnam.go.kr/cnportal/province/province/list.do?searchWrd=%EA%B5%90%EC%84%AD"],
        ["충남_서산", "https://www.seosan.go.kr/www/contents.do?key=1258"],
        ["충남_아산", "https://www.asan.go.kr/main/cms/?no=257"],
        ["충남_논산", "https://nonsan.go.kr/kor/html/sub03/03010201.html"]
    ],
    "충청북도": [
        ["충청북도", "https://www.chungbuk.go.kr/www/selectGosiPblancList.do?key=422&searchKrwd=%EA%B5%90%EC%84%AD"],
        ["충북_괴산", "https://www.goesan.go.kr/www/selectBbsNttList.do?key=604&searchCnd=SJ&searchKrwd=교섭"],
        ["충북_보은", "https://www.boeun.go.kr/www/selectBbsNttList.do?key=194&bbsNo=66&searchCnd=SJ&searchKrwd=교섭"],
        ["충북_옥천", "https://www.oc.go.kr/www/selectBbsNttList.do?key=236&bbsNo=40&searchCnd=SJ&searchKrwd=교섭"],
        ["충북_음성", "https://www.eumseong.go.kr/www/selectEminwonList.do?key=352&searchCnd=B_Subject&searchKrwd=교섭"],
        ["충북_제천", "https://www.jecheon.go.kr/www/selectBbsNttList.do?key=5233&bbsNo=18&searchCnd=SJ&searchKrwd=교섭"],
        ["충북_진천", "https://www.jincheon.go.kr/home/sub.do?menukey=235&searchCnd=sj&searchKrwd=교섭"]
    ]
}

# 자동화 완료된 항목(경기도/울산광역시/경상남도)은 manual에서 제거
manual_data = [
    ["보건복지부", "https://www.mohw.go.kr/board.es?mid=a10501010200&bid=0003"],
    ["서울_강북구", "https://www.gangbuk.go.kr/portal/bbs/B0000245/list.do?menuNo=200082&bbsId=&cl1Cd=&optn5=&pageIndex=1&searchCnd2=&searchCnd=&searchWrd=%EA%B5%90%EC%84%AD"],
    ["서울_관악구", "https://www.gwanak.go.kr/site/gwanak/ex/bbsNew/List.do?typeCode=1&searchCondition=TITLE&searchKeyword=%EA%B5%90%EC%84%AD"],
    ["서울_서대문구", "https://www.sdm.go.kr/news/notice/notice.do?mode=list&srchTitle=%EA%B5%90%EC%84%AD"],
    ["서울_송파구", "https://www.songpa.go.kr/www/selectGosiList.do?key=2776&not_ancmt_se_code=&searchCnd=SJ&searchKrwd=교섭"],
    ["서울_양천구", "https://www.yangcheon.go.kr/site/yangcheon/ex/bbs/List.do?cbIdx=254#"],
    ["서울_종로구", "https://www.jongno.go.kr/portal/bbs/selectBoardList.do?bbsId=BBSMSTR_000000000271&menuNo=1756&menuId=1756"],
    ["서울_중구", "https://www.junggu.seoul.kr/content/boards/62/list?search_column=title&search_keyword=교섭"],
    ["부산_사상구", "https://www.sasang.go.kr/tour/board/list.sasang?boardId=BBS_0000001&menuIdx=75&searchCnd=0&searchWrd=%EA%B5%90%EC%84%AD"],
    ["대구광역시", "https://www.daegu.go.kr/index.do?menu_id=00000052&srchVal=%EA%B5%90%EC%84%AD&srchKey=sj"],
    ["대구_남구", "https://nam.daegu.kr/index.do?menu_id=00000851"],
    ["울산_남구", "https://www.ulsannamgu.go.kr/cop/bbs/selectSaeolGosiList.do"],
    ["울산_동구", "https://www.donggu.ulsan.kr/donggu/contents/contents.do?mId=4040100"],
    ["울산_북구", "https://www.bukgu.ulsan.kr/lay1/S1T86C456/contents.do"],
    ["울산_울주군", "https://www.ulju.ulsan.kr/ulju/saeol/gosi/list.do?mId=0403010000"],
    ["울산_중구", "https://www.junggu.ulsan.kr/index.ulsan?menuCd=DOM_000000102004001000"],
    ["경기_고양", "https://www.goyang.go.kr/www/link/BD_notice.do?se=01"],
    ["경기_광주", "https://www.gjcity.go.kr/portal/saeol/gosi/list.do?mId=0202010000"],
    ["경기_남양주", "https://www.nyj.go.kr/www/selectEminwonWebList.do?key=2492"],
    ["경기_평택", "https://www.pyeongtaek.go.kr/pyeongtaek/saeol/gosi/list.do?mid=0401020100"],
    ["경북_경주", "https://www.gyeongju.go.kr/open_content/ko/page.do?mnu_uid=423"],
    ["경북_경산", "https://www.gbgs.go.kr/open_content/ko/page.do?mnu_uid=2160&"],
    ["경북_김천", "https://www.gc.go.kr/portal/saeol/gosi/list.do?mId=1202180100"],
    ["경북_안동", "https://www.andong.go.kr/portal/saeol/gosi/list.do?mId=0401010000"],
    ["경북_구미", "https://www.gumi.go.kr/portal/saeol/gosi/list.do?seCode=01&mid=0401040000"],
    ["경북_포항", "https://www.pohang.go.kr/portal/saeol/gosi/list.do?mid=0202010000"],
    ["충남_공주", "https://www.gongju.go.kr/prog/saeolGosi/GOSI_01/sub04_03_01/list.do"],
    ["충남_당진", "https://www.dangjin.go.kr/kor/sub03_02_01_01.do"],
    ["충남_천안", "https://www.cheonan.go.kr/kor/sub02_02_01.do"],
#    ["충청북도", "https://www.chungbuk.go.kr/www/selectGosiPblancList.do?key=422&searchKrwd=%EA%B5%90%EC%84%AD"],
    ["충북_단양", "https://www.danyang.go.kr/dy21/976"],
    ["충북_영동", "https://www.yd21.go.kr/kr/html/sub02/020103.html?mode=L"],
    ["충북_증평", "http://www.jp.go.kr/kor/sub03_01_03.do"],
    ["충북_청주", "https://www.cheongju.go.kr/www/selectEminwonNoticeList.do?key=281&searchKrwd=%EA%B5%90%EC%84%AD"],
    ["충북_충주", "https://www.chungju.go.kr/www/selectEminwonList.do?key=510&ancmt_sj=%EA%B5%90%EC%84%AD"]
]

target_data = {region: sorted(sites, key=lambda x: x[0]) for region, sites in raw_target_data.items()}
manual_sites = sorted(manual_data, key=lambda x: x[0])

# -------------------------------------------------
# 유틸
# -------------------------------------------------
SESSION_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
}

MAX_WORKERS = 8

def create_session():
    session = requests.Session()
    session.headers.update(SESSION_HEADERS)
    return session

def make_result(name, url, status, detected_date="", detected_title=""):
    return {
        "지자체명": name,
        "링크": url,
        "상태": status,
        "감지일자": detected_date,
        "감지제목": detected_title
    }

def extract_text_lines(html: str):
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text("\n", strip=True)
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    return lines

def build_recent_day_patterns(days: int = 7):
    today = datetime.now(ZoneInfo("Asia/Seoul"))
    patterns = []

    for i in range(days):
        dt = today - timedelta(days=i)
        patterns.extend([
            dt.strftime("%Y-%m-%d"),
            dt.strftime("%Y.%m.%d"),
            dt.strftime("%Y/%m/%d"),
            dt.strftime("%y-%m-%d"),
            dt.strftime("%y.%m.%d"),
            dt.strftime("%y/%m/%d"),
        ])

    return list(dict.fromkeys(patterns))

def normalize_date_string(date_str: str):
    if not date_str:
        return ""

    date_str = date_str.strip().replace(".", "-").replace("/", "-")
    parts = date_str.split("-")

    try:
        if len(parts[0]) == 2:
            year = int(parts[0])
            year += 2000 if year < 70 else 1900
            return f"{year:04d}-{int(parts[1]):02d}-{int(parts[2]):02d}"
        elif len(parts[0]) == 4:
            return f"{int(parts[0]):04d}-{int(parts[1]):02d}-{int(parts[2]):02d}"
    except Exception:
        return date_str

    return date_str

def extract_date_from_text(text: str):
    if not text:
        return ""

    patterns = [
        r"\b(20\d{2}[./-]\d{2}[./-]\d{2})\b",
        r"\b(\d{2}[./-]\d{2}[./-]\d{2})\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return normalize_date_string(match.group(1))

    return ""

def extract_date_from_item(item: dict):

    priority_keys = [
        "regDt", "regdate", "date", "createdAt",
        "frstRegDt", "inputDate", "writeDate",
        "crtDt", "updDt", "bbscttRegistDe"
    ]

    for key in priority_keys:
        value = item.get(key)
        if isinstance(value, str):
            detected = extract_date_from_text(value)
            if detected:
                return detected

    for value in item.values():
        if isinstance(value, str):
            detected = extract_date_from_text(value)
            if detected:
                return detected

    return ""

def looks_like_noise(line: str):
    noise_patterns = [
        r"페이지[: ]",
        r"전체페이지",
        r"RSS",
        r"더보기",
        r"이동",
        r"검색",
        r"담당부서",
        r"조회",
        r"번호",
        r"목록",
        r"처음",
        r"다음",
        r"이전",
        r"마지막",
        r"1 10 20 30 40 50",
    ]
    return any(re.search(p, line) for p in noise_patterns)

def clean_title(line: str):
    line = re.sub(r"\s+", " ", line).strip()
    line = re.sub(r"^\d+\s*", "", line)
    return line[:120]

def extract_best_title_from_lines(lines, keyword="교섭"):
    candidates = []

    for line in lines:
        line = clean_title(line)
        if keyword in line and not looks_like_noise(line):
            candidates.append(line)

    if not candidates:
        return ""

    candidates = sorted(candidates, key=len, reverse=True)
    return candidates[0][:120]

def classify_status_from_lines(lines, keyword: str = "교섭", recent_days: int = 7):
    recent_day_patterns = build_recent_day_patterns(recent_days)

    keyword_lines = []
    for i, line in enumerate(lines):
        if keyword in line and not looks_like_noise(line):
            keyword_lines.append((i, line))

    if not keyword_lines:
        return "⚪ 결과 없음", "", ""

    first_title = clean_title(keyword_lines[0][1])

    # 1차: 신규 판정은 엄격하게 (앞뒤 1줄)
    for idx, line in keyword_lines:
        near_lines_strict = lines[max(0, idx - 1): min(len(lines), idx + 2)]
        joined_strict = " ".join(near_lines_strict)

        for day in recent_day_patterns:
            if day in joined_strict:
                detected_date = extract_date_from_text(joined_strict)
                return "🔴 신규", detected_date or normalize_date_string(day), clean_title(line)

    # 2차: 감지일자는 조금 넓게 찾기 (앞뒤 5줄)
    for idx, line in keyword_lines:
        near_lines_wide = lines[max(0, idx - 5): min(len(lines), idx + 6)]
        joined_wide = " ".join(near_lines_wide)

        detected_date = extract_date_from_text(joined_wide)
        if detected_date:
            return "🟡 기존 공고", detected_date, clean_title(line)

    # 3차: 제목 줄 자체에서 날짜 찾기
    title_date = extract_date_from_text(first_title)
    if title_date:
        return "🟡 기존 공고", title_date, first_title

    return "🟡 기존 공고", "", first_title

def analyze_response_text(name: str, url: str, text: str):
    lines = extract_text_lines(text)
    status, detected_date, detected_title = classify_status_from_lines(lines)

    if status != "⚪ 결과 없음" and (not detected_title or len(detected_title) < 8):
        detected_title = extract_best_title_from_lines(lines, keyword="교섭")

    return make_result(name, url, status, detected_date, detected_title)

def get_recent_search_window(days=90):
    today = datetime.now(ZoneInfo("Asia/Seoul")).date()
    start_date = today - timedelta(days=days)
    return start_date.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")

# -------------------------------------------------
# 전용 자동검색 함수
# -------------------------------------------------
def check_gyeongnam(name: str, url: str):
    """
    실제 확인한 POST payload 기반
    """
    session = create_session()

    try:
        start_date, end_date = get_recent_search_window(90)

        post_url = "https://www.gyeongnam.go.kr/index.gyeong?menuCd=DOM_000000135003009001"
        payload = {
            "conGosiGbn": "",
            "confmStdt": start_date,
            "confmEnddt": end_date,
            "conAnnounceNo": "",
            "conDeptNm": "",
            "conTitle": "교섭"
        }

        response = session.post(post_url, data=payload, timeout=15)
        response.raise_for_status()
        response.encoding = response.apparent_encoding or response.encoding

        return analyze_response_text(name, url, response.text)

    except requests.exceptions.Timeout:
        return make_result(name, url, "⚠️ 타임아웃")
    except requests.exceptions.HTTPError:
        return make_result(name, url, "⚠️ 접속 오류")
    except requests.exceptions.RequestException:
        return make_result(name, url, "⚠️ 요청 실패")
    except Exception:
        return make_result(name, url, "⚠️ 파싱 오류")

def check_gyeonggi(name: str, url: str):
    """
    경기도 게시판 검사 (AJAX API 기반)
    실제 응답 구조: { total, items }
    """
    session = create_session()

    try:
        api_url = "https://www.gg.go.kr/ajax/board/getList.do"

        payload = {
            "bsIdx": "469",
            "bcIdx": "0",
            "menuId": "1547",
            "isManager": "false",
            "isCharge": "false",
            "keyfield": "SUBJECTANDREMARK",
            "keyword": "교섭",
            "offset": "0",
            "limit": "10"
        }

        headers = {
            "Referer": "https://www.gg.go.kr/bbs/board.do?bsIdx=469&menuId=1547",
            "X-Requested-With": "XMLHttpRequest"
        }

        response = session.post(api_url, data=payload, headers=headers, timeout=20)
        response.raise_for_status()

        data = response.json()
        items = data.get("items", [])

        if not items:
            return make_result(name, url, "⚪ 결과 없음")

        # 교섭이 포함된 제목 우선 탐색
        for item in items:
            title = (
                item.get("subject")
                or item.get("title")
                or item.get("sj")
                or ""
            )

            if "교섭" in title:
                date = (
                    item.get("regDt")
                    or item.get("regdate")
                    or item.get("date")
                    or item.get("createdAt")
                    or ""
                )
                return make_result(name, url, "🟡 기존 공고", date, title)

        # 혹시 제목 키 이름이 다른 경우를 대비한 2차 탐색
        for item in items:
            for value in item.values():
                if isinstance(value, str) and "교섭" in value:
                    date = extract_date_from_item(item)
                    
                    return make_result(name, url, "🟡 기존 공고", date, value[:120])

        return make_result(name, url, "⚪ 결과 없음")

    except requests.exceptions.Timeout:
        return make_result(name, url, "⚠️ 타임아웃")
    except requests.exceptions.HTTPError:
        return make_result(name, url, "⚠️ 접속 오류")
    except requests.exceptions.RequestException:
        return make_result(name, url, "⚠️ 요청 실패")
    except Exception as e:
        return make_result(name, url, "⚠️ 파싱 오류", "", str(e)[:120])
        
def check_ulsan_metropolitan(name: str, url: str):
    """
    울산광역시 고시공고 전용 POST 검색
    실제 확인한 payload 기반
    """
    session = create_session()

    try:
        post_url = "https://www.ulsan.go.kr/u/rep/transfer/notice/list.ulsan?mId=001004002000000000"
        payload = {
            "srchGubun": "",
            "srchType": "srchSj",
            "srchWord": "교섭"
        }

        response = session.post(post_url, data=payload, timeout=15)
        response.raise_for_status()
        response.encoding = response.apparent_encoding or response.encoding

        return analyze_response_text(name, url, response.text)

    except requests.exceptions.Timeout:
        return make_result(name, url, "⚠️ 타임아웃")
    except requests.exceptions.HTTPError:
        return make_result(name, url, "⚠️ 접속 오류")
    except requests.exceptions.RequestException:
        return make_result(name, url, "⚠️ 요청 실패")
    except Exception:
        return make_result(name, url, "⚠️ 파싱 오류")
        
# -------------------------------------------------
# 공통 검사 함수
# -------------------------------------------------
@st.cache_data(ttl=600, show_spinner=False)
def check_site_stable(name: str, url: str):
    # 전용 자동검색 분기
    if name == "경상남도" or "gyeongnam.go.kr/index.gyeong" in url:
        return check_gyeongnam(name, url)

    if name == "경기도" or ("gg.go.kr/bbs/board.do" in url and "bsIdx=469" in url):
        return check_gyeonggi(name, url)

    if name == "울산광역시" or "ulsan.go.kr/u/rep/transfer/notice/list.ulsan" in url:
        return check_ulsan_metropolitan(name, url)

    session = create_session()

    try:
        response = session.get(url, timeout=15)
        response.raise_for_status()
        response.encoding = response.apparent_encoding or response.encoding

        return analyze_response_text(name, url, response.text)

    except requests.exceptions.Timeout:
        return make_result(name, url, "⚠️ 타임아웃")
    except requests.exceptions.HTTPError:
        return make_result(name, url, "⚠️ 접속 오류")
    except requests.exceptions.RequestException:
        return make_result(name, url, "⚠️ 요청 실패")
    except Exception:
        return make_result(name, url, "⚠️ 파싱 오류")

# -------------------------------------------------
# 엑셀 / 표시 유틸
# -------------------------------------------------
def extract_href_for_excel(value):
    if isinstance(value, str) and 'href="' in value:
        match = re.search(r'href="(.*?)"', value)
        if match:
            return match.group(1)
    return value

def to_excel(df: pd.DataFrame):
    output = BytesIO()
    df_excel = df.copy()

    if "링크" in df_excel.columns:
        df_excel["링크"] = df_excel["링크"].apply(extract_href_for_excel)

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_excel.to_excel(writer, index=False, sheet_name="교섭공고결과")

        workbook = writer.book
        worksheet = writer.sheets["교섭공고결과"]

        header_format = workbook.add_format({
            "bold": True,
            "align": "center",
            "valign": "vcenter",
            "bg_color": "#D9EAF7",
            "border": 1
        })

        cell_format = workbook.add_format({
            "align": "center",
            "valign": "vcenter",
            "border": 1,
            "text_wrap": True
        })

        for col_num, value in enumerate(df_excel.columns.values):
            worksheet.write(0, col_num, value, header_format)

        col_widths = {
            "지자체명": 18,
            "링크": 18,
            "상태": 16,
            "감지일자": 14,
            "감지제목": 70
        }

        for idx, col in enumerate(df_excel.columns):
            worksheet.set_column(idx, idx, col_widths.get(col, 20), cell_format)

    return output.getvalue()

def make_clickable_link(url: str, text: str = "이동하여 검색"):
    return f'<a href="{url}" target="_blank">{text}</a>'

def group_manual_sites(manual_sites):
    grouped = {}

    for name, url in manual_sites:
        if "_" in name:
            region_key = name.split("_")[0]
        else:
            region_key = name

        if region_key not in grouped:
            grouped[region_key] = []

        grouped[region_key].append([name, url])

    return grouped

def sort_results_by_target_order(results, target_sites):
    order_map = {name: i for i, (name, _) in enumerate(target_sites)}
    return sorted(results, key=lambda x: order_map.get(x["지자체명"], 999999))

# -------------------------------------------------
# 사이드바
# -------------------------------------------------
def on_all_clicked():
    for region in sort_order:
        st.session_state[f"sidebar_{region}"] = st.session_state["all_regions"]

st.sidebar.header("📍 검색 지역 설정")
st.sidebar.checkbox("전체 지역 선택", value=False, key="all_regions", on_change=on_all_clicked)

selected_regions = []
for region in sort_order:
    count = len(target_data[region])

    if f"sidebar_{region}" not in st.session_state:
        st.session_state[f"sidebar_{region}"] = False

    is_checked = st.sidebar.checkbox(f"{region} ({count})", key=f"sidebar_{region}")
    if is_checked and count > 0:
        selected_regions.append(region)

target_sites = []
for reg in selected_regions:
    target_sites.extend(target_data[reg])

# -------------------------------------------------
# 안내
# -------------------------------------------------
if not selected_regions:
    st.markdown(
        '<div class="guide-box">왼쪽 상단 [ > ] 화살표 눌러 지역 선택!</div>',
        unsafe_allow_html=True
    )

# -------------------------------------------------
# 실행 버튼
# -------------------------------------------------
status_placeholder = st.empty()

col1, col2, col3 = st.columns([1, 2.2, 1])
with col2:
    run_clicked = st.button("선택 지역 자동 확인 시작", use_container_width=True)

# -------------------------------------------------
# 실행
# -------------------------------------------------
if run_clicked:
    if not target_sites:
        st.warning("지역을 먼저 선택해주세요.")
    else:
        results = []
        total_count = len(target_sites)
        completed_count = 0
        progress_bar = st.progress(0)

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_map = {
                executor.submit(check_site_stable, name, url): (name, url)
                for name, url in target_sites
            }

            for future in as_completed(future_map):
                name, url = future_map[future]

                try:
                    result = future.result()
                except Exception:
                    result = make_result(name, url, "⚠️ 실행 오류")

                results.append(result)
                completed_count += 1

                percent = int((completed_count / total_count) * 100)
                status_placeholder.markdown(
                    f"<span class='status-text'>⏳ [{percent}%] 총 {total_count}개 중 {completed_count}개 완료</span>",
                    unsafe_allow_html=True
                )
                progress_bar.progress(completed_count / total_count)

        results = sort_results_by_target_order(results, target_sites)

        status_placeholder.success(f"✅ 검사 완료! (총 {len(target_sites)}개)")

        df = pd.DataFrame(results)

        df_display = df.copy()
        df_display["링크"] = df_display["링크"].apply(
            lambda x: make_clickable_link(x) if x else ""
        )

        st.download_button(
            label="📥 결과 엑셀 내려받기",
            data=to_excel(df),
            file_name=f"교섭결과_{datetime.now(ZoneInfo('Asia/Seoul')).strftime('%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        st.write(
            df_display.to_html(escape=False, index=False, classes="result-table"),
            unsafe_allow_html=True
        )

# -------------------------------------------------
# 직접 확인 리스트 (지역별 접기)
# -------------------------------------------------
st.markdown("---")
st.markdown(f"""
    <div style="display: flex; align-items: baseline; text-align: left; margin-bottom: 10px;">
        <span class="manual-title" style="margin-right: 8px;">직접 확인 리스트</span>
        <span class="manual-subtitle">({len(manual_sites)}개 지역)</span>
    </div>
""", unsafe_allow_html=True)

manual_grouped = group_manual_sites(manual_sites)

manual_region_order = [
    "보건복지부", "서울", "부산", "대구", "울산",
    "경기", "강원", "전북", "경북", "경남", "충남", "충북"
]

displayed_regions = set()

for region in manual_region_order:
    if region in manual_grouped:
        displayed_regions.add(region)
        sites = manual_grouped[region]

        with st.expander(f"{region} ({len(sites)})", expanded=False):
            region_df = pd.DataFrame(sites, columns=["지자체명", "링크"])
            region_df["링크"] = region_df["링크"].apply(
                lambda x: make_clickable_link(x)
            )
            st.write(region_df.to_html(escape=False, index=False), unsafe_allow_html=True)

for region, sites in manual_grouped.items():
    if region not in displayed_regions:
        with st.expander(f"{region} ({len(sites)})", expanded=False):
            region_df = pd.DataFrame(sites, columns=["지자체명", "링크"])
            region_df["링크"] = region_df["링크"].apply(
                lambda x: make_clickable_link(x)
            )
            st.write(region_df.to_html(escape=False, index=False), unsafe_allow_html=True)














