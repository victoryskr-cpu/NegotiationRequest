import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import re
from io import BytesIO

st.set_page_config(
    page_title="교섭공고 알리미", 
    page_icon="🔍", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
        .header-container {
            text-align: center;
            margin-bottom: 20px;
        }
        .main-title {
            font-size: 2.2rem;
            font-weight: bold;
            margin-bottom: 0px;
        }
        .sub-title {
            font-size: 24px; /* 기존 34px에서 약 2/3 수준인 24px로 조정 */
            font-weight: bold;
            color: #555;
            margin-top: 5px;
            margin-bottom: 30px;
        }
        .status-text {
            font-size: 18px;
            font-weight: bold;
            color: #ff4b4b;
            margin-bottom: 5px;
        }
        
        /* 버튼을 감싸는 div가 중앙에 오도록 하고, 버튼 자체를 중앙 정렬 */
        div.stButton {
            text-align: center;
            display: flex;
            justify-content: center;
        }
        
        div.stButton > button {
            width: 400px; /* 버튼 너비를 고정하여 중앙 배치를 명확히 함 */
            height: 3.5rem;
            font-size: 1.5rem !important;
            font-weight: bold !important;
            background-color: #007bff !important;
            color: white !important;
            border-radius: 12px;
            border: none;
            box-shadow: 0px 4px 10px rgba(0, 123, 255, 0.3);
            transition: all 0.3s;
        }
        div.stButton > button:hover {
            background-color: #0056b3 !important;
            transform: translateY(-2px);
        }
    </style>

    <div class="header-container">
        <div class="main-title">지자체 교섭요구공고 확인</div>
        <div class="sub-title">(돌봄사업장 지역 공고 모니터링)</div>
        <div class="status-text">왼쪽 상단 [ > ] 화살표 눌러 지역 선택!</div>
    </div>
""", unsafe_allow_html=True)

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
        ["충북_괴산", "https://www.goesan.go.kr/www/selectBbsNttList.do?key=604&searchCnd=SJ&searchKrwd=교섭"],
        ["충북_보은", "https://www.boeun.go.kr/www/selectBbsNttList.do?key=194&bbsNo=66&searchCnd=SJ&searchKrwd=교섭"],
        ["충북_옥천", "https://www.oc.go.kr/www/selectBbsNttList.do?key=236&bbsNo=40&searchCnd=SJ&searchKrwd=교섭"],
        ["충북_음성", "https://www.eumseong.go.kr/www/selectEminwonList.do?key=352&searchCnd=B_Subject&searchKrwd=교섭"],
        ["충북_제천", "https://www.jecheon.go.kr/www/selectBbsNttList.do?key=5233&bbsNo=18&searchCnd=SJ&searchKrwd=교섭"],
        ["충북_진천", "https://www.jincheon.go.kr/home/sub.do?menukey=235&searchCnd=sj&searchKrwd=교섭"]
    ]
}

manual_data = [
    ["보건복지부", "https://www.mohw.go.kr/board.es?mid=a10501010200&bid=0003"],
    ["서울_강북구", "https://www.gangbuk.go.kr/portal/bbs/B0000245/list.do?menuNo=200082"],
    ["서울_관악구", "https://www.gwanak.go.kr/site/gwanak/ex/bbsNew/List.do?typeCode=1&searchCondition=TITLE&searchKeyword=%EA%B5%90%EC%84%AD"],
    ["서울_서대문구", "https://www.sdm.go.kr/news/notice/notice.do?mode=list&srchTitle=%EA%B5%90%EC%84%AD"],
    ["서울_송파구", "https://www.songpa.go.kr/www/selectGosiList.do?key=2776&not_ancmt_se_code=&searchCnd=SJ&searchKrwd=교섭"],
    ["서울_양천구", "https://www.yangcheon.go.kr/site/yangcheon/ex/bbs/List.do?cbIdx=254#"],
    ["서울_종로구", "https://www.jongno.go.kr/portal/bbs/selectBoardList.do?bbsId=BBSMSTR_000000000271&menuNo=1756&menuId=1756"],
    ["서울_중구", "https://www.junggu.seoul.kr/content/boards/62/list?search_column=title&search_keyword=교섭"],
    ["부산_사상구", "https://www.sasang.go.kr/tour/board/list.sasang?boardId=BBS_0000001&menuIdx=75&searchCnd=0&searchWrd=%EA%B5%90%EC%84%AD"],
    ["대구광역시", "https://www.daegu.go.kr/index.do?menu_id=00000052&srchVal=%EA%B5%90%EC%84%AD&srchKey=sj"],
    ["대구_남구", "https://nam.daegu.kr/index.do?menu_id=00000851"],
    ["울산광역시", "https://www.ulsan.go.kr/u/rep/transfer/notice/list.ulsan?mId=001004002000000000"],
    ["울산_남구", "https://www.ulsannamgu.go.kr/cop/bbs/selectSaeolGosiList.do"],
    ["울산_동구", "https://www.donggu.ulsan.kr/donggu/contents/contents.do?mId=4040100"],
    ["울산_북구", "https://www.bukgu.ulsan.kr/lay1/S1T86C456/contents.do"],
    ["울산_울주군", "https://www.ulju.ulsan.kr/ulju/saeol/gosi/list.do?mId=0403010000"],
    ["울산_중구", "https://www.junggu.ulsan.kr/index.ulsan?menuCd=DOM_000000102004001000"],
    ["경기도", "https://www.gg.go.kr/bbs/board.do?bsIdx=469&menuId=1547"],
    ["경기_구리", "https://www.guri.go.kr/www/selectGosiNttList.do?key=387&searchCnd=ALL&searchKrwd=%EA%B5%90%EC%84%AD"],
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
    ["경상남도", "https://www.gyeongnam.go.kr/index.gyeong?menuCd=DOM_000000135003009001"],
    ["충남_공주", "https://www.gongju.go.kr/prog/saeolGosi/GOSI_01/sub04_03_01/list.do"],
    ["충남_당진", "https://www.dangjin.go.kr/kor/sub03_02_01_01.do"],
    ["충남_천안", "https://www.cheonan.go.kr/kor/sub02_02_01.do"],
    ["충청북도", "https://www.chungbuk.go.kr/www/selectGosiPblancList.do?key=422&searchKrwd=%EA%B5%90%EC%84%AD"],
    ["충북_단양", "https://www.danyang.go.kr/dy21/976"],
    ["충북_영동", "https://www.yd21.go.kr/kr/html/sub02/020103.html?mode=L"],
    ["충북_증평", "http://www.jp.go.kr/kor/sub03_01_03.do"],
    ["충북_청주", "https://www.cheongju.go.kr/www/selectEminwonNoticeList.do?key=281&searchKrwd=%EA%B5%90%EC%84%AD"],
    ["충북_충주", "https://www.chungju.go.kr/www/selectEminwonList.do?key=510&ancmt_sj=%EA%B5%90%EC%84%AD"]
]

target_data = {region: sorted(sites, key=lambda x: x[0]) for region, sites in raw_target_data.items()}
manual_sites = sorted(manual_data, key=lambda x: x[0])

def on_all_clicked():
    for region in sort_order:
        st.session_state[f"sidebar_{region}"] = st.session_state["all_regions"]

st.sidebar.header("📍 검색 지역 설정")
st.sidebar.checkbox("전체 지역 선택", value=False, key="all_regions", on_change=on_all_clicked)

selected_regions = []
for region in sort_order:
    count = len(target_data[region])
    # 개별 체크박스의 상태를 session_state로 직접 관리
    if f"sidebar_{region}" not in st.session_state:
        st.session_state[f"sidebar_{region}"] = False
        
    is_checked = st.sidebar.checkbox(f"{region} ({count})", key=f"sidebar_{region}")
    if is_checked and count > 0:
        selected_regions.append(region)

target_sites = []
for reg in selected_regions: target_sites.extend(target_data[reg])

def check_site_stable(name, url):
    headers = { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36" }
    try:
        response = requests.get(url, headers=headers, timeout=15, verify=False)
        response.encoding = response.apparent_encoding 
        clean_text = re.sub(r'<script.*?</script>|<style.*?</style>|<[^>]*>', '', response.text, flags=re.DOTALL)
        if "교섭" not in clean_text: return [name, url, "⚪ 결과 없음"]
        today = datetime.now()
        recent_days = []
        for i in range(8):
            dt = today - timedelta(days=i)
            d_str, d_dot = dt.strftime("%Y-%m-%d"), dt.strftime("%Y.%m.%d")
            recent_days.extend([d_str, d_dot, d_str[2:], d_dot[2:], dt.strftime("%m.%d")])
        for m in re.finditer(r"교섭", clean_text):
            start, end = max(0, m.start() - 50), min(len(clean_text), m.end() + 50)
            context = clean_text[start:end].replace(" ", "")
            if any(day.replace("-",".").replace(".","") in context.replace(".","") for day in recent_days):
                return [name, url, "🔴 신규 가능성 높음"]
        return [name, url, "🟡 기존 공고 존재"]
    except: return [name, url, "⚠️ 확인 요망"]

def to_excel(df):
    output = BytesIO()
    df_excel = df.copy()
    df_excel['링크'] = df_excel['링크'].apply(lambda x: re.search(r'href="(.*?)"', x).group(1) if 'href=' in str(x) else x)
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_excel.to_excel(writer, index=False, sheet_name='교섭공고결과')
    return output.getvalue()

col1, col2, col3 = st.columns([1, 2, 1]) # 비율을 조정하여 버튼 크기를 적절하게 설정
with col2:
    status_placeholder = st.empty()

    # 버튼 클릭 시에만 아래 블록이 실행됩니다.
if st.button("선택 지역 자동 확인 시작"):
    if not selected_regions: # 선택된 지역이 없을 때
        st.warning("먼저 왼쪽 사이드바에서 지역을 선택해주세요.")
    else:
        results = []
        bar = st.progress(0)
        
        # 실제 검사 시작
        for i, (name, url) in enumerate(target_sites):
            percent = int(((i + 1) / len(target_sites)) * 100)
            status_placeholder.markdown(f"<div style='text-align:center;' class='status-text'>⏳ [{percent}%] 확인 중: {name}</div>", unsafe_allow_html=True)
            
            results.append(check_site_stable(name, url))
            bar.progress((i + 1) / len(target_sites))
            time.sleep(0.1)
        
        status_placeholder.success(f"✅ 확인 완료! (총 {len(target_sites)}개)")
        
        # 결과 테이블 생성
        df = pd.DataFrame(results, columns=["지자체명", "링크", "상태"])
        df_display = df.copy()
        df_display['링크'] = df_display['링크'].apply(lambda x: f'<a href="{x}" target="_blank">게시판 이동</a>')
        
        # 엑셀 다운로드 버튼 (괄호 닫힘 확인!)
        st.download_button(
            label="📥 결과 엑셀 내려받기", 
            data=to_excel(df), 
            file_name=f"교섭결과_{datetime.now().strftime('%m%d_%H%M')}.xlsx", 
            mime="application/vnd.ms-excel"
        ) # <--- 이 괄호가 잘 닫혀있는지 꼭 확인하세요!
        
        # 테이블 출력
        st.write(df_display.to_html(escape=False, index=False), unsafe_allow_html=True)
