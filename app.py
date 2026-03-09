import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import re

# 페이지 설정
st.set_page_config(page_title="교섭공고 알리미", page_icon="🔍")
st.markdown("""
    <style>
    .main-title {
        line-height: 1.2;
        margin-bottom: 0px;
        padding-bottom: 0px;
    }
    .sub-title {
        margin-top: -13px;
        color: #555;
        font-weight: normal;
    }
    </style>
    
    <h1 class="main-title">지자체 교섭요구공고 확인</h1>
    <h3 class="sub-title">(돌봄사업장 지역)</h3>
    <br>
""", unsafe_allow_html=True)

# 1. 자동 확인 가능 리스트 (#완 항목 활성화)
target_sites = [
    ["서울특별시", "https://www.seoul.go.kr/news/news_notice.do?bbsNo=277&srchText=교섭"],
    ["강남구청", "https://www.gangnam.go.kr/notice/list.do?mid=ID05_040201&keyfield=BNI_MAIN_TITLE&keyword=교섭"],
    ["강동구청", "https://www.gangdong.go.kr/web/newportal/notice/01?sv=교섭"],
    ["강서구청", "https://www.gangseo.seoul.kr/gs040301?srchKey=sj&srchText=교섭"],
    ["구로구청", "https://www.guro.go.kr/www/selectBbsNttList.do?key=1791&bbsNo=663&searchCnd=SJ&searchKrwd=교섭"],
    ["금천구청", "https://www.geumcheon.go.kr/portal/tblSeolGosiDetailList.do?key=294&rep=1&searchCnd=all&searchKrwd=%EA%B5%90%EC%84%AD"],
    ["노원구청", "https://www.nowon.kr/www/user/bbs/BD_selectBbsList.do?q_bbsCode=1003&q_bbscttSn=&q_estnColumn7=&q_estnColumn1=11&q_ntceSiteCode=11&q_clCode=0&q_rowPerPage=10&q_currPage=1&q_sortName=&q_sortOrder=&q_searchKeyTy=sj___1002&q_searchVal=%EA%B5%90%EC%84%AD"],
    ["도봉구청", "https://www.dobong.go.kr/WDB_DEV/gosigong_go/default.asp?sDEP_CODE=&strSearchType=1&strSearchKeyword=%EA%B5%90%EC%84%AD"],
    ["동대문구청", "https://www.ddm.go.kr/www/selectEminwonWebList.do?key=3291&searchNotAncmtSeCode=01%2C02%2C04%2C05%2C06%2C07&searchCnd=notAncmtSj&searchKrwd=%EA%B5%90%EC%84%AD"],
    ["동작구청", "https://www.dongjak.go.kr/portal/bbs/B0001297/list.do?menuNo=201317"],
    ["마포구청", "https://www.mapo.go.kr/site/main/nPortal/list?_sToken=1773057057300733_7fdc068a0a2e1c29d54c5dbbc2854934995e9895f3a41063e2d6ed98396173d3&sc=&sv=%EA%B5%90%EC%84%AD&pageSize=10"],
    ["서초구청", "https://www.seocho.go.kr/site/seocho/05/10506020000002015070811.jsp"],
    ["성동구청", "https://www.sd.go.kr/main/selectBbsNttList.do?key=1473&bbsNo=184&integrDeptCode=&searchCtgry=&searchCnd=SJ&searchKrwd=%EA%B5%90%EC%84%AD"],
    ["성북구청", "https://www.sb.go.kr/www/selectEminwonList.do?key=6977&searchCnd=all&depNm=&searchCnd2=notAncmtSj&pageUnit=10&bgnde=&endde=&searchKrwd=%EA%B5%90%EC%84%AD"],
    ["영등포구청", "https://www.ydp.go.kr/www/selectEminwonList.do?key=2851&menuFlag=01&not_ancmt_se_code=&searchCnd=B_Subject&searchKrwd=%EA%B5%90%EC%84%AD"],
    ["용산구청", "https://www.yongsan.go.kr/portal/bbs/B0000095/list.do?menuNo=200233&optn1=&pageUnit=&sdate=&edate=&deptId=&searchCnd=1&searchWrd=%EA%B5%90%EC%84%AD"],
    ["은평구청", "https://www.ep.go.kr/www/selectEminwonList.do?key=754&notAncmtSeCode=01&pageUnit=10&searchCnd=notAncmtSj&searchKrwd=%EA%B5%90%EC%84%AD"],
    ["중랑구청", "https://www.jungnang.go.kr/portal/bbs/list/B0000117.do?menuNo=200475&viewType="],
    ["부산광역시", "https://www.busan.go.kr/nbgosi/list?conIfmStdt=2025-09-10&conIfmEnddt=2026-03-10&conGosiGbn=&schKeyType=A&srchText=%EA%B5%90%EC%84%AD"],
    ["부산_남구", "https://www.bsnamgu.go.kr/index.namgu?menuCd=DOM_000000105001002000"],
    ["부산_동래구", "https://www.dongnae.go.kr/index.dongnae?menuCd=DOM_000000103001003000"],
    ["대구_동구", "https://www.dong.daegu.kr/portal/saeol/gosi/list.do?mid=0201020000"],
    ["대구_달서구", "https://www.dalseo.daegu.kr/index.do?menu_id=10000104"],
    ["대구_중구", "https://www.jung.daegu.kr/new/pages/administration/page.html?mc=0159"],
]

# 2. 직접 확인 필요 리스트 (#직 항목 분리)
manual_sites = [
    ["보건복지부", "https://www.mohw.go.kr/board.es?mid=a10501010200&bid=0003"],
    ["강북구청", "https://www.gangbuk.go.kr/portal/bbs/B0000245/list.do?menuNo=200082"],
    ["관악구청", "https://www.gwanak.go.kr/site/gwanak/ex/bbsNew/List.do?typeCode=1&searchCondition=TITLE&searchKeyword=%EA%B5%90%EC%84%AD"],
    ["서대문구청", "https://www.sdm.go.kr/news/notice/notice.do?mode=list&srchTitle=%EA%B5%90%EC%84%AD"],
    ["송파구청", "https://www.songpa.go.kr/www/selectGosiList.do?key=2776&not_ancmt_se_code=&searchCnd=SJ&searchKrwd=교섭"],
    ["양천구청", "https://www.yangcheon.go.kr/site/yangcheon/ex/bbs/List.do?cbIdx=254#"],
    ["종로구청", "https://www.jongno.go.kr/portal/bbs/selectBoardList.do?bbsId=BBSMSTR_000000000271&menuNo=1756&menuId=1756"],
    ["중구청", "https://www.junggu.seoul.kr/content/boards/62/list?search_column=title&search_keyword=교섭"],
    ["부산_사상구", "https://www.sasang.go.kr/tour/board/list.sasang?boardId=BBS_0000001&menuIdx=75&searchCnd=0&searchWrd=%EA%B5%90%EC%84%AD"],
    ["대구광역시", "https://www.daegu.go.kr/index.do?menu_id=00000052&srchVal=%EA%B5%90%EC%84%AD&srchKey=sj"],
    ["대구_남구", "https://nam.daegu.kr/index.do?menu_id=00000851"],
]

def get_recent_dates():
    return [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]

def check_site_stable(name, url, recent_dates):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    }
    session = requests.Session()
    
    try:
        response = session.get(url, headers=headers, timeout=20, verify=False)
        response.encoding = 'utf-8'
        content = response.text

        fail_indicators = [
            '검색된 결과가 없습니다', '등록된 게시물이 없습니다', '조회된 내역이 없습니다', 
            '데이터가 없습니다', '0건', '총 0건', '결과가 없습니다'
        ]
        if any(indicator in content for indicator in fail_indicators):
            return [name, url, "⚪ 결과 없음"]

        body_match = re.search(r'<tbody>(.*?)</tbody>', content, re.DOTALL)
        if body_match:
            search_area = body_match.group(1)
            clean_text = re.sub(r'<[^>]+>', '', search_area)
            if "교섭" in clean_text:
                has_recent_date = any(date in search_area for date in recent_dates)
                return [name, url, "🔴 신규 가능성 높음" if has_recent_date else "🟡 기존 공고 존재"]
        
        return [name, url, "⚪ 결과 없음"]

    except Exception:
        return [name, url, "⚠️ 직접 확인 요망 (접속 지연/에러)"]

# --- 화면 UI ---
st.warning("시스템 호환성을 위해 브라우저 엔진 없이 '직접 데이터 요청' 방식으로 작동합니다.")

if st.button("🚀 공고 확인 시작"):
    recent_dates = get_recent_dates()
    results = []
    
    progress_text = st.empty()
    bar = st.progress(0)
    
    for i, (name, url) in enumerate(target_sites):
        progress_text.text(f"현재 확인 중: {name} ({i+1}/{len(target_sites)})")
        res = check_site_stable(name, url, recent_dates)
        results.append(res)
        bar.progress((i + 1) / len(target_sites))
        time.sleep(0.1)

    df = pd.DataFrame(results, columns=["지자체명", "링크", "상태"])
    
    def make_link(url):
        return f'<a href="{url}" target="_blank">게시판 이동</a>'
    df['링크'] = df['링크'].apply(make_link)
    
    st.success("자동 검사가 완료되었습니다!")
    st.write(df.to_html(escape=False), unsafe_allow_html=True)

    # --- 직접 확인 리스트 섹션 ---
    st.markdown("---")
    st.subheader("📢 게시판으로 이동해서 직접 검색하세요")
    st.info("아래 사이트들은 구조적 특성상 자동 확인이 어려우므로 링크를 클릭해 직접 검색어(교섭)를 입력해 주세요.")
    
    m_df = pd.DataFrame(manual_sites, columns=["지자체명", "링크"])
    m_df['링크'] = m_df['링크'].apply(make_link)
    st.write(m_df.to_html(escape=False), unsafe_allow_html=True)

    # CSV 다운로드 (자동 결과 기준)
    csv = df.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 자동 확인 결과 CSV 다운로드", csv, "check_result.csv", "text/csv")


































