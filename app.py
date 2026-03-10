import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import re

# 1. 페이지 설정
st.set_page_config(page_title="교섭공고 알리미", page_icon="🔍", layout="wide", initial_sidebar_state="expanded")

# 2. CSS 교정: 빈 박스 방지 및 완벽 중앙 정렬
st.markdown("""
    <style>
        .block-container { max-width: 900px !important; margin: auto !important; padding-top: 2rem; }
        .header-container { text-align: center; margin-bottom: 30px; }
        .main-title { font-size: 2.2rem; font-weight: bold; margin-bottom: 10px; }
        .sub-title { font-size: 1.3rem; color: #666; }
        
        /* 버튼 중앙 정렬 */
        div.stButton { display: flex; justify-content: center; margin: 30px 0; }
        div.stButton > button {
            width: 100% !important; max-width: 500px; height: 3.5rem !important;
            font-size: 1.4rem !important; font-weight: bold !important;
            background-color: #007bff !important; color: white !important;
            border-radius: 12px !important; border: none !important;
        }

        /* 수동 리스트 박스: 내용이 있을 때만 예쁘게 */
        .manual-wrapper {
            margin-top: 40px;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 15px;
            border: 1px solid #eee;
        }
        .manual-title { font-size: 1.1rem; font-weight: bold; margin-bottom: 15px; text-align: center; color: #333; }
        .link-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            text-align: center;
        }
        .link-item a { text-decoration: none; color: #007bff; font-size: 15px; }
        .link-item a:hover { text-decoration: underline; }

        /* 테이블 정중앙 */
        .stTable { margin: auto !important; }
    </style>
""", unsafe_allow_html=True)

# 3. 데이터 (활동가님의 전체 리스트 포함 - 에러 방지용 한 줄 처리)
sort_order = ["서울특별시", "부산광역시", "대구광역시", "울산광역시", "강원도", "전라북도", "경상북도", "경상남도", "충청남도", "충청북도"]
target_data = {
    "서울특별시": [["서울특별시", "https://www.seoul.go.kr/news/news_notice.do?bbsNo=277&srchText=교섭"], ["서울_강남", "https://www.gangnam.go.kr/notice/list.do?mid=ID05_040201&keyfield=BNI_MAIN_TITLE&keyword=교섭"], ["서울_강동", "https://www.gangdong.go.kr/web/newportal/notice/01?sv=교섭"], ["서울_강서", "https://www.gangseo.seoul.kr/gs040301?srchKey=sj&srchText=교섭"], ["서울_구로", "https://www.guro.go.kr/www/selectBbsNttList.do?key=1791&bbsNo=663&searchCnd=SJ&searchKrwd=교섭"], ["서울_금천", "https://www.geumcheon.go.kr/portal/tblSeolGosiDetailList.do?key=294&rep=1&searchCnd=all&searchKrwd=%EA%B5%90%EC%84%AD"], ["서울_노원", "https://www.nowon.kr/www/user/bbs/BD_selectBbsList.do?q_bbsCode=1003&q_searchVal=%EA%B5%90%EC%84%AD"], ["서울_도봉", "https://www.dobong.go.kr/WDB_DEV/gosigong_go/default.asp?strSearchType=1&strSearchKeyword=%EA%B5%90%EC%84%AD"], ["서울_동대문", "https://www.ddm.go.kr/www/selectEminwonWebList.do?key=3291&searchCnd=notAncmtSj&searchKrwd=%EA%B5%90%EC%84%AD"], ["서울_동작", "https://www.dongjak.go.kr/portal/bbs/B0001297/list.do?menuNo=201317&searchCnd=1&searchWrd=%EA%B5%90%EC%84%AD"], ["서울_마포", "https://www.mapo.go.kr/site/main/nPortal/list?sv=%EA%B5%90%EC%84%AD"], ["서울_성동", "https://www.sd.go.kr/main/selectBbsNttList.do?key=1473&bbsNo=184&searchCnd=SJ&searchKrwd=%EA%B5%90%EC%84%AD"], ["서울_성북", "https://www.sb.go.kr/www/selectEminwonList.do?key=6977&searchCnd2=notAncmtSj&searchKrwd=교섭"], ["서울_영등포", "https://www.ydp.go.kr/www/selectEminwonList.do?key=2851&searchCnd=B_Subject&searchKrwd=교섭"], ["서울_용산", "https://www.yongsan.go.kr/portal/bbs/B0000095/list.do?menuNo=200233&searchCnd=1&searchWrd=교섭"], ["서울_은평", "https://www.ep.go.kr/www/selectEminwonList.do?key=754&searchCnd=notAncmtSj&searchKrwd=교섭"], ["서울_중랑", "https://www.jungnang.go.kr/portal/bbs/list/B0000117.do?menuNo=200475&searchWrd=교섭"]],
    "부산광역시": [["부산광역시", "https://www.busan.go.kr/nbgosi/list?schKeyType=A&srchText=%EA%B5%90%EC%84%AD"], ["부산_남구", "https://www.bsnamgu.go.kr/index.namgu?menuCd=DOM_000000105001002000&search_key=title&search_val=%EA%B5%90%EC%84%AD"], ["부산_동래구", "https://www.dongnae.go.kr/index.dongnae?menuCd=DOM_000000103001003000&search_key=title&search_val=%EA%B5%90%EC%84%AD"]],
    "대구광역시": [["대구_동구", "https://www.dong.daegu.kr/portal/saeol/gosi/list.do?mid=0201020000&searchKrwd=%EA%B5%90%EC%84%AD"], ["대구_달서구", "https://www.dalseo.daegu.kr/index.do?menu_id=10000104&searchKey=sj&searchKeyword=%EA%B5%90%EC%84%AD"], ["대구_중구", "https://www.jung.daegu.kr/new/pages/administration/page.html?mc=0159&search_key=sj&search_keyword=%EA%B5%90%EC%84%AD"]],
    "울산광역시": [], "강원도": [["강원특별자치도", "https://state.gwd.go.kr/portal/bulletin/notification?searchCondition=TITLE&searchKeyword=%EA%B5%90%EC%84%AD"], ["강원_춘천", "https://www.chuncheon.go.kr/cityhall/administrative-info/notice-info/notice-announcement/?searchCnd=SJ&searchWrd=%EA%B5%90%EC%84%AD"]],
    "전라북도": [["전북특별자치도", "https://www.jeonbuk.go.kr/board/list.jeonbuk?boardId=BBS_0000129&searchType=DATA_TITLE&keyword=%EA%B5%90%EC%84%AD"], ["전북_군산", "https://www.gunsan.go.kr/main/m141"], ["전북_전주", "https://www.jeonju.go.kr/planweb/board/list.9is?boardUid=9be517a7914528ce01930aa3ddc26cf0&contentUid=ff8080818990c349018b041a879f395a&searchType=dataTitle&keyword=%EA%B5%90%EC%84%AD"]],
    "경상북도": [["경상북도", "https://www.gb.go.kr/Main/page.do?bdName=%EA%B3%A0%EC%8B%9C%EA%B3%B5%EA%B3%A0&mnu_uid=6789&word=%EA%B5%90%EC%84%AD"], ["경북_칠곡", "https://www.chilgok.go.kr/portal/saeol/gosi/list.do?mId=0201030000"]],
    "경상남도": [["경남_김해", "https://www.gimhae.go.kr/03360/00023/00029.web?stype=title&sstring=%EA%B5%90%EC%84%AD"], ["경남_의령", "https://www.uiryeong.go.kr/board/list.uiryeong?boardId=BBS_0000070&searchType=DATA_TITLE&keyword=%EA%B5%90%EC%84%AD"], ["경남_창원", "https://www.changwon.go.kr/cwportal/10310/10438/10439.web?stype=title&sstring=%EA%B5%90%EC%84%AD"], ["경남_함안", "https://www.haman.go.kr/00960/00962.web?stype=title&sstring=%EA%B5%90%EC%84%AD"]],
    "충청남도": [["충청남도", "https://www.chungnam.go.kr/cnportal/province/province/list.do?searchWrd=%EA%B5%90%EC%84%AD"], ["충남_서산", "https://www.seosan.go.kr/www/contents.do?key=1258"], ["충남_아산", "https://www.asan.go.kr/main/cms/?no=257"], ["충남_논산", "https://nonsan.go.kr/kor/html/sub03/03010201.html"]],
    "충청북도": [["충북_괴산", "https://www.goesan.go.kr/www/selectBbsNttList.do?key=604&searchCnd=SJ&searchKrwd=교섭"], ["충북_보은", "https://www.boeun.go.kr/www/selectBbsNttList.do?key=194&bbsNo=66&searchCnd=SJ&searchKrwd=교섭"], ["충북_옥천", "https://www.oc.go.kr/www/selectBbsNttList.do?key=236&bbsNo=40&searchCnd=SJ&searchKrwd=교섭"], ["충북_음성", "https://www.eumseong.go.kr/www/selectEminwonList.do?key=352&searchCnd=B_Subject&searchKrwd=교섭"], ["충북_제천", "https://www.jecheon.go.kr/www/selectBbsNttList.do?key=5233&bbsNo=18&searchCnd=SJ&searchKrwd=교섭"], ["충북_진천", "https://www.jincheon.go.kr/home/sub.do?menukey=235&searchCnd=sj&searchKrwd=교섭"]]
}

# 4. 기능 로직
def check_site(name, url):
    try:
        res = requests.get(url, timeout=10, verify=False)
        return [name, "🟡 확인 완료"] if "교섭" in res.text else [name, "⚪ 결과 없음"]
    except: return [name, "⚠️ 확인 불가"]

# 5. 메인 화면
st.markdown("<div class='header-container'><div class='main-title'>지자체 교섭요구공고 확인</div><div class='sub-title'>(돌봄사업장 지역 공고 모니터링)</div></div>", unsafe_allow_html=True)

# 사이드바에서 지역 선택
st.sidebar.header("📍 지역 선택")
selected_regions = [reg for reg in sort_order if st.sidebar.checkbox(reg, key=reg)]

# 자동 검색 결과 (위)
if st.button("🚀 선택 지역 자동 확인 시작"):
    if not selected_regions:
        st.error("지역을 선택해주세요!")
    else:
        all_sites = []
        for reg in selected_regions: all_sites.extend(target_data[reg])
        results = [check_site(n, u) for n, u in all_sites]
        st.table(pd.DataFrame(results, columns=["지자체명", "검색 상태"]))

# 수동 리스트 (아래 - 지역을 선택했을 때만 박스가 생성되도록 수정)
if selected_regions:
    st.markdown("<div class='manual-wrapper'><div class='manual-title'>🔗 선택 지역 게시판 바로가기 (수동)</div><div class='link-grid'>", unsafe_allow_html=True)
    for reg in selected_regions:
        for name, url in target_data[reg]:
            st.markdown(f"<div class='link-item'><a href='{url}' target='_blank'>{name}</a></div>", unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)
