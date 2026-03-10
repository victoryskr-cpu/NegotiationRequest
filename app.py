import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import re

# 페이지 설정
st.set_page_config(page_title="교섭공고 알리미", page_icon="🔍", layout="wide")

# 헤더 디자인
st.markdown("""
    <style>
    .header-container { text-align: center; margin-top: -20px; margin-bottom: 20px; }
    .main-title { font-size: 2.2rem; font-weight: bold; line-height: 1.2; margin-bottom: 5px; }
    .sub-title { font-size: 1.2rem; color: #666; font-weight: normal; line-height: 1.0; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #f0f2f6; }
    </style>
    <div class="header-container">
        <h1 class="main-title">지자체 교섭요구공고 확인</h1>
        <h3 class="sub-title">(돌봄사업장 지역 공고 모니터링)</h3>
    </div>
""", unsafe_allow_html=True)

# 1. 자동 확인 데이터 (광역별 분리 및 가나다 정렬)
raw_target_data = {
    "서울특별시": [
        ["서울특별시", "https://www.seoul.go.kr/news/news_notice.do?bbsNo=277&srchText=교섭"],
        ["강남구", "https://www.gangnam.go.kr/notice/list.do?mid=ID05_040201&keyfield=BNI_MAIN_TITLE&keyword=교섭"],
        ["강동구", "https://www.gangdong.go.kr/web/newportal/notice/01?sv=교섭"],
        ["강서구", "https://www.gangseo.seoul.kr/gs040301?srchKey=sj&srchText=교섭"],
        ["구로구", "https://www.guro.go.kr/www/selectBbsNttList.do?key=1791&bbsNo=663&searchCnd=SJ&searchKrwd=교섭"],
        ["금천구", "https://www.geumcheon.go.kr/portal/tblSeolGosiDetailList.do?key=294&rep=1&searchCnd=all&searchKrwd=%EA%B5%90%EC%84%AD"],
        ["노원구", "https://www.nowon.kr/www/user/bbs/BD_selectBbsList.do?q_bbsCode=1003&q_searchVal=%EA%B5%90%EC%84%AD"],
        ["도봉구", "https://www.dobong.go.kr/WDB_DEV/gosigong_go/default.asp?strSearchType=1&strSearchKeyword=%EA%B5%90%EC%84%AD"],
        ["동대문구", "https://www.ddm.go.kr/www/selectEminwonWebList.do?key=3291&searchCnd=notAncmtSj&searchKrwd=%EA%B5%90%EC%84%AD"],
        ["동작구", "https://www.dongjak.go.kr/portal/bbs/B0001297/list.do?menuNo=201317&searchCnd=1&searchWrd=%EA%B5%90%EC%84%AD"],
        ["마포구", "https://www.mapo.go.kr/site/main/nPortal/list?sv=%EA%B5%90%EC%84%AD"],
        ["성동구", "https://www.sd.go.kr/main/selectBbsNttList.do?key=1473&bbsNo=184&searchCnd=SJ&searchKrwd=%EA%B5%90%EC%84%AD"],
        ["성북구", "https://www.sb.go.kr/www/selectEminwonList.do?key=6977&searchCnd2=notAncmtSj&searchKrwd=%EA%B5%90%EC%84%AD"],
        ["영등포구", "https://www.ydp.go.kr/www/selectEminwonList.do?key=2851&searchCnd=B_Subject&searchKrwd=%EA%B5%90%EC%84%AD"],
        ["용산구", "https://www.yongsan.go.kr/portal/bbs/B0000095/list.do?menuNo=200233&searchCnd=1&searchWrd=%EA%B5%90%EC%84%AD"],
        ["은평구", "https://www.ep.go.kr/www/selectEminwonList.do?key=754&searchCnd=notAncmtSj&searchKrwd=%EA%B5%90%EC%84%AD"],
        ["중랑구", "https://www.jungnang.go.kr/portal/bbs/list/B0000117.do?menuNo=200475&searchWrd=%EA%B5%90%EC%84%AD"]
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
    "울산광역시": [],
    "경기도": [
        ["경기_양주", "https://www.yangju.go.kr/www/selectEminwonList.do?key=4075&searchCnd=B_Subject&searchKrwd=%EA%B5%90%EC%84%AD"],
        ["경기_양평", "https://www.yp21.go.kr/www/selectBbsNttList.do?key=1119&bbsNo=5&searchCnd=SJ&searchKrwd=%EA%B5%90%EC%84%AD"],
        ["경기_포천", "https://www.pocheon.go.kr/www/selectEminwonList.do?key=12563&searchCnd=notAncmtSj&searchKrwd=%EA%B5%90%EC%84%AD"]
    ],
    "강원도": [
        ["강원특별자치도", "https://state.gwd.go.kr/portal/bulletin/notification?searchCondition=TITLE&searchKeyword=%EA%B5%90%EC%84%AD"],
        ["강원_춘천", "https://www.chuncheon.go.kr/cityhall/administrative-info/notice-info/notice-announcement/?searchCnd=SJ&searchWrd=%EA%B5%90%EC%84%AD"]
    ],
    "충청북도": [
        ["충북_괴산", "https://www.goesan.go.kr/www/selectBbsNttList.do?key=604&searchCnd=SJ&searchKrwd=%EA%B5%90%EC%84%AD"],
        ["충북_보은", "https://www.boeun.go.kr/www/selectBbsNttList.do?key=194&bbsNo=66&searchCnd=SJ&searchKrwd=%EA%B5%90%EC%84%AD"],
        ["충북_옥천", "https://www.oc.go.kr/www/selectBbsNttList.do?key=236&bbsNo=40&searchCnd=SJ&searchKrwd=%EA%B5%90%EC%84%AD"],
        ["충북_음성", "https://www.eumseong.go.kr/www/selectEminwonList.do?key=352&searchCnd=B_Subject&searchKrwd=%EA%B5%90%EC%84%AD"],
        ["충북_제천", "https://www.jecheon.go.kr/www/selectBbsNttList.do?key=5233&bbsNo=18&searchCnd=SJ&searchKrwd=%EA%B5%90%EC%84%AD"],
        ["충북_진천", "https://www.jincheon.go.kr/home/sub.do?menukey=235&searchCnd=sj&searchKrwd=%EA%B5%90%EC%84%AD"]
    ],
    "충청남도": [
        ["충청남도", "https://www.chungnam.go.kr/cnportal/province/province/list.do?searchWrd=%EA%B5%90%EC%84%AD"],
        ["충남_서산", "https://www.seosan.go.kr/www/contents.do?key=1258"],
        ["충남_아산", "https://www.asan.go.kr/main/cms/?no=257"],
        ["충남_논산", "https://nonsan.go.kr/kor/html/sub03/03010201.html"]
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
        ["경남_김해", "https://www.gimhae.go.kr/03360/00023/00029.web?stype=title&sstring=%EA%B5%90%EC%84%AD"],
        ["경남_의령", "https://www.uiryeong.go.kr/board/list.uiryeong?boardId=BBS_0000070&searchType=DATA_TITLE&keyword=%EA%B5%90%EC%84%AD"],
        ["경남_창원", "https://www.changwon.go.kr/cwportal/10310/10438/10439.web?stype=title&sstring=%EA%B5%90%EC%84%AD"],
        ["경남_함안", "https://www.haman.go.kr/00960/00962.web?stype=title&sstring=%EA%B5%90%EC%84%AD"]
    ]
}

# 가나다순 정렬 및 데이터 가공
target_data = {region: sorted(sites, key=lambda x: x[0]) for region, sites in raw_target_data.items()}

# 사이드바 설정
st.sidebar.header("📍 검색 지역 설정")

# 전체 선택/해제 로직
select_all = st.sidebar.checkbox("전체 지역 선택", value=False)

selected_regions = []
for region in target_data.keys():
    # 광역명 옆에 데이터 개수 표시 (예: 서울특별시 (17))
    count = len(target_data[region])
    label = f"{region} ({count})"
    
    # 전체 선택이 체크되어 있으면 각 항목도 체크, 아니면 개별 선택
    is_checked = st.sidebar.checkbox(label, value=select_all)
    if is_checked and count > 0:
        selected_regions.append(region)

# 실행용 타겟 리스트 구성
target_sites = []
for reg in selected_regions:
    target_sites.extend(target_data[reg])

# [기존 check_site_stable 함수 및 결과 출력 로직 동일]
def check_site_stable(name, url, recent_dates):
    headers = { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36" }
    try:
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=15, verify=False, allow_redirects=True)
        response.encoding = response.apparent_encoding 
        content = response.text
        main_content = re.sub(r'<script.*?</script>|<style.*?</style>|<header.*?</header>|<footer.*?</footer>|<nav.*?</nav>', '', content, flags=re.DOTALL)
        
        fail_indicators = ['검색된 결과가 없습니다', '등록된 게시물이 없습니다', '조회된 내역이 없습니다', '데이터가 없습니다', '0건</span>', '0건</td>', '>0건<', '검색결과가 없습니다', '검색결과 0건']
        if any(indicator in main_content for indicator in fail_indicators):
            return [name, url, "⚪ 결과 없음"]

        for date in recent_dates:
            dot_date = date.replace('-', '.')
            short_dot_date = dot_date[2:]
            patterns = [f"교섭.{{0,200}}({date}|{dot_date}|{short_dot_date})", f"({date}|{dot_date}|{short_dot_date}).{{0,200}}교섭"]
            if any(re.search(p, main_content, re.DOTALL) for p in patterns):
                return [name, url, "🔴 신규 가능성 높음"]

        if "교섭" in main_content:
            return [name, url, "🟡 기존 공고 존재"]
        return [name, url, "⚪ 결과 없음"]
    except:
        return [name, url, "⚠️ 확인 요망 (접속 지연)"]

# 메인 UI
col1, col2, col3 = st.columns([1,2,1])
with col2:
    if st.button("🚀 선택 지역 공고 확인 시작"):
        if not target_sites:
            st.warning("선택된 지역이 없습니다. 사이드바에서 지역을 선택해주세요.")
        else:
            recent_dates = [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
            results = []
            progress_text = st.empty()
            bar = st.progress(0)
            
            for i, (name, url) in enumerate(target_sites):
                progress_text.text(f"확인 중: {name} ({i+1}/{len(target_sites)})")
                results.append(check_site_stable(name, url, recent_dates))
                bar.progress((i + 1) / len(target_sites))
                time.sleep(0.05)

            df = pd.DataFrame(results, columns=["지자체명", "링크", "상태"])
            df['링크'] = df['링크'].apply(lambda x: f'<a href="{x}" target="_blank">게시판 이동</a>')
            st.success(f"총 {len(target_sites)}개 사이트 검사 완료!")
            st.write(df.to_html(escape=False), unsafe_allow_html=True)

