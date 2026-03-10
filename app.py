import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import re
from io import BytesIO

# 1. 페이지 설정
st.set_page_config(
    page_title="교섭공고 알리미", 
    page_icon="🔍", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. CSS 스타일 설정 (버튼 정중앙 배치 및 테이블 스타일)
st.markdown("""
    <style>
        .header-container { text-align: center; margin-bottom: 20px; }
        .main-title { font-size: 2.2rem; font-weight: bold; margin-bottom: 0px; }
        .sub-title { font-size: 24px; font-weight: bold; color: #555; margin-top: 5px; margin-bottom: 30px; }
        .status-text { font-size: 18px; font-weight: bold; color: #ff4b4b; margin-bottom: 15px; text-align: center; }
        
        /* 버튼을 화면 정중앙으로 */
        div.stButton {
            display: flex;
            justify-content: center;
            margin: 30px 0;
        }
        
        div.stButton > button {
            width: 450px !important;
            height: 4rem !important;
            font-size: 1.6rem !important;
            font-weight: bold !important;
            background-color: #007bff !important;
            color: white !important;
            border-radius: 12px !important;
            border: none !important;
            box-shadow: 0px 4px 15px rgba(0, 123, 255, 0.4) !important;
        }

        /* 결과 테이블 중앙 정렬 및 너비 조정 */
        .result-table {
            margin-left: auto;
            margin-right: auto;
            border-collapse: collapse;
            width: 90%;
            text-align: center;
        }
        .result-table th { background-color: #f8f9fa; padding: 12px; border: 1px solid #ddd; }
        .result-table td { padding: 10px; border: 1px solid #ddd; vertical-align: middle; }
        
        /* 컬럼별 너비 강제 지정 (한 줄에 나오도록) */
        .col-name { width: 20%; }
        .col-link { width: 30%; }
        .col-status { width: 50%; white-space: nowrap; }
    </style>

    <div class="header-container">
        <div class="main-title">지자체 교섭요구공고 확인</div>
        <div class="sub-title">(돌봄사업장 지역 공고 모니터링)</div>
        <div class="status-text">왼쪽 상단 [ > ] 화살표 눌러 지역 선택!</div>
    </div>
""", unsafe_allow_html=True)

# 3. 데이터 및 함수 설정 (생략 없이 유지)
sort_order = ["서울특별시", "부산광역시", "대구광역시", "울산광역시", "강원도", "전라북도", "경상북도", "경상남도", "충청남도", "충청북도"]
raw_target_data = {
    "서울특별시": [
        ["서울특별시", "https://www.seoul.go.kr/news/news_notice.do?bbsNo=277&srchText=교섭"],
        ["서울_강남", "https://www.gangnam.go.kr/notice/list.do?mid=ID05_040201&keyfield=BNI_MAIN_TITLE&keyword=교섭"],
        ["서울_강동", "https://www.gangdong.go.kr/web/newportal/notice/01?sv=교섭"],
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
    "울산광역시": [],
    "강원도": [
        ["강원특별자치도", "https://state.gwd.go.kr/portal/bulletin/notification?searchCondition=TITLE&searchKeyword=%EA%B5%90%EC%84%AD"],
        ["강원_춘천", "https://www.chuncheon.go.kr/cityhall/administrative-info/notice-info/notice-announcement/?searchCnd=SJ&searchWrd=%EA%B5%90%EC%84%AD"]
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
        ["경남_김해", "
