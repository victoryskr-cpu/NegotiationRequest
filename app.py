import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import re
from io import BytesIO

# -------------------------------------------------
# 기본 설정
# -------------------------------------------------

st.set_page_config(
    page_title="교섭공고 알리미",
    page_icon="🔍",
    layout="wide"
)

# -------------------------------------------------
# 스타일
# -------------------------------------------------

st.markdown("""
<style>

.header-container {
    text-align:center;
    margin-top:-20px;
}

.main-title{
    font-size:2rem;
    font-weight:bold;
}

.sub-title{
    font-size:1.2rem;
    color:#555;
}

.status-text{
    font-weight:bold;
    color:#ff4b4b;
    text-align:center;
}

.stButton{
    display:flex;
    justify-content:center;
}

.stButton>button{
    background-color:#007BFF;
    color:white;
    font-size:1.1rem;
    font-weight:900;
    border-radius:10px;
    height:55px;
}

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
"서울특별시",
"부산광역시",
"대구광역시",
"울산광역시",
"강원도",
"경기도",
"전라북도",
"경상북도",
"경상남도",
"충청남도",
"충청북도"
]

raw_target_data = {

"서울특별시":[
["서울특별시","https://www.seoul.go.kr/news/news_notice.do?bbsNo=277&srchText=교섭"],
["서울_강남","https://www.gangnam.go.kr/notice/list.do?mid=ID05_040201&keyfield=BNI_MAIN_TITLE&keyword=교섭"],
["서울_강동","https://www.gangdong.go.kr/web/newportal/notice/01?sv=교섭"],
["서울_강서","https://www.gangseo.seoul.kr/gs040301?srchKey=sj&srchText=교섭"],
["서울_구로","https://www.guro.go.kr/www/selectBbsNttList.do?key=1791&bbsNo=663&searchCnd=SJ&searchKrwd=교섭"],
["서울_금천","https://www.geumcheon.go.kr/portal/tblSeolGosiDetailList.do?key=294&rep=1&searchCnd=all&searchKrwd=%EA%B5%90%EC%84%AD"],
["서울_노원","https://www.nowon.kr/www/user/bbs/BD_selectBbsList.do?q_bbsCode=1003&q_searchVal=%EA%B5%90%EC%84%AD"],
["서울_도봉","https://www.dobong.go.kr/WDB_DEV/gosigong_go/default.asp?strSearchType=1&strSearchKeyword=%EA%B5%90%EC%84%AD"],
["서울_동대문","https://www.ddm.go.kr/www/selectEminwonWebList.do?key=3291&searchCnd=notAncmtSj&searchKrwd=%EA%B5%90%EC%84%AD"],
["서울_동작","https://www.dongjak.go.kr/portal/bbs/B0001297/list.do?menuNo=201317&searchCnd=1&searchWrd=%EA%B5%90%EC%84%AD"],
["서울_마포","https://www.mapo.go.kr/site/main/nPortal/list?sv=%EA%B5%90%EC%84%AD"],
["서울_성동","https://www.sd.go.kr/main/selectBbsNttList.do?key=1473&bbsNo=184&searchCnd=SJ&searchKrwd=%EA%B5%90%EC%84%AD"],
["서울_성북","https://www.sb.go.kr/www/selectEminwonList.do?key=6977&searchCnd2=notAncmtSj&searchKrwd=교섭"],
["서울_영등포","https://www.ydp.go.kr/www/selectEminwonList.do?key=2851&searchCnd=B_Subject&searchKrwd=교섭"],
["서울_용산","https://www.yongsan.go.kr/portal/bbs/B0000095/list.do?menuNo=200233&searchCnd=1&searchWrd=교섭"],
["서울_은평","https://www.ep.go.kr/www/selectEminwonList.do?key=754&searchCnd=notAncmtSj&searchKrwd=교섭"],
["서울_중랑","https://www.jungnang.go.kr/portal/bbs/list/B0000117.do?menuNo=200475&searchWrd=교섭"]
],

"부산광역시":[
["부산광역시","https://www.busan.go.kr/nbgosi/list?schKeyType=A&srchText=%EA%B5%90%EC%84%AD"],
["부산_남구","https://www.bsnamgu.go.kr/index.namgu?menuCd=DOM_000000105001002000&search_key=title&search_val=%EA%B5%90%EC%84%AD"],
["부산_동래구","https://www.dongnae.go.kr/index.dongnae?menuCd=DOM_000000103001003000&search_key=title&search_val=%EA%B5%90%EC%84%AD"]
],

"대구광역시":[
["대구_동구","https://www.dong.daegu.kr/portal/saeol/gosi/list.do?mid=0201020000&searchKrwd=%EA%B5%90%EC%84%AD"],
["대구_달서구","https://www.dalseo.daegu.kr/index.do?menu_id=10000104&searchKey=sj&searchKeyword=%EA%B5%90%EC%84%AD"],
["대구_중구","https://www.jung.daegu.kr/new/pages/administration/page.html?mc=0159&search_key=sj&search_keyword=%EA%B5%90%EC%84%AD"]
],

"울산광역시":[],
"강원도":[
["강원특별자치도","https://state.gwd.go.kr/portal/bulletin/notification?searchCondition=TITLE&searchKeyword=%EA%B5%90%EC%84%AD"],
["강원_춘천","https://www.chuncheon.go.kr/cityhall/administrative-info/notice-info/notice-announcement/?searchCnd=SJ&searchWrd=%EA%B5%90%EC%84%AD"]
]
}

# -------------------------------------------------
# 크롤링 함수
# -------------------------------------------------

@st.cache_data(ttl=600)
def check_site(name,url):

    try:

        headers={"User-Agent":"Mozilla/5.0"}

        r=requests.get(url,headers=headers,timeout=15)
        r.raise_for_status()

        soup=BeautifulSoup(r.text,"html.parser")

        for s in soup(["script","style"]):
            s.extract()

        text=soup.get_text(" ",strip=True)

        if "교섭" not in text:
            return [name,url,"⚪ 결과 없음"]

        today=datetime.now()

        for i in range(7):

            d=(today-timedelta(days=i)).strftime("%Y.%m.%d")

            if d in text:

                return [name,url,"🔴 신규 가능성 높음"]

        return [name,url,"🟡 기존 공고 존재"]

    except:

        return [name,url,"⚠️ 확인 필요"]

# -------------------------------------------------
# 사이드바
# -------------------------------------------------

st.sidebar.header("검색 지역")

selected_regions=[]

for r in sort_order:

    if r in raw_target_data:

        if st.sidebar.checkbox(r):

            selected_regions.append(r)

# -------------------------------------------------
# 실행 버튼
# -------------------------------------------------

status_placeholder=st.empty()

col1,col2,col3=st.columns([1,2,1])

with col2:

    run=st.button("선택 지역 자동 확인 시작",use_container_width=True)

# -------------------------------------------------
# 실행
# -------------------------------------------------

if run:

    sites=[]

    for r in selected_regions:

        sites.extend(raw_target_data[r])

    if not sites:

        st.warning("지역을 선택해주세요")

    else:

        results=[]

        progress=st.progress(0)

        for i,(name,url) in enumerate(sites):

            percent=int((i+1)/len(sites)*100)

            status_placeholder.markdown(
            f"<div class='status-text'>⏳ {percent}% 확인중 : {name}</div>",
            unsafe_allow_html=True
            )

            results.append(check_site(name,url))

            progress.progress((i+1)/len(sites))

            time.sleep(0.05)

        status_placeholder.success(f"검사 완료 (총 {len(sites)}개)")

        df=pd.DataFrame(results,columns=["지자체","링크","상태"])

        df_display=df.copy()

        df_display["링크"]=df_display["링크"].apply(
        lambda x:f'<a href="{x}" target="_blank">이동</a>'
        )

        st.write(df_display.to_html(escape=False,index=False),unsafe_allow_html=True)

        # 엑셀 다운로드

        output=BytesIO()

        with pd.ExcelWriter(output,engine="xlsxwriter") as writer:

            df.to_excel(writer,index=False)

        st.download_button(
        "결과 엑셀 다운로드",
        data=output.getvalue(),
        file_name=f"교섭결과_{datetime.now().strftime('%m%d_%H%M')}.xlsx"
        )
