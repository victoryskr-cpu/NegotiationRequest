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

# 2. CSS 스타일 설정 (버튼 정중앙, 테이블 정렬)
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
            width: 95%;
            text-align: center;
        }
        .result-table th { background-color: #f8f9fa; padding: 12px; border: 1px solid #ddd; text-align: center !important; }
        .result-table td { padding: 10px; border: 1px solid #ddd; vertical-align: middle; text-align: center !important; }
        
        .col-name { width: 20%; }
        .col-link { width: 25%; }
        .col-status { width: 55%; white-space: nowrap; }
    </style>

    <div class="header-container">
        <div class="main-title">지자체 교섭요구공고 확인</div>
        <div class="sub-title">(돌봄사업장 지역 공고 모니터링)</div>
        <div class="status-text">왼쪽 상단 [ > ] 화살표 눌러 지역 선택!</div>
    </div>
""", unsafe_allow_html=True)

# 3. 데이터 설정 (따옴표 오류 완벽 수정)
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
        ["서울_은평", "
