import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import re

# 페이지 설정
st.set_page_config(page_title="교섭공고 알리미", page_icon="🔍")

# CSS 및 HTML 수정: 가운데 정렬 및 줄간격 최적화
st.markdown("""
    <style>
    .header-container {
        text-align: center;      /* 전체 가운데 정렬 */
        margin-top: -20px;       /* 상단 여백 조절 */
        margin-bottom: 20px;
    }
    .main-title {
        font-size: 2.2rem;       /* 제목 크기 */
        font-weight: bold;
        line-height: 0.0;        /* 줄간격 최소화 */
        margin-bottom: 0px;      /* 아래 여백 제거 */
        padding-bottom: 3px;
    }
    .sub-title {
        font-size: 1.2rem;       /* 부제 크기 */
        color: #666;             /* 부제 색상 */
        margin-top: 0px;         /* 위쪽 여백 제거 */
        font-weight: normal;
        line-height: 1.0;
    }
    </style>
    
    <div class="header-container">
        <h1 class="main-title">지자체 교섭요구공고 확인</h1>
        <h3 class="sub-title">(돌봄사업장 지역)</h3>
    </div>
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
#    ["울산광역시", "https://www.ulsan.go.kr/u/rep/transfer/notice/list.ulsan?mId=001004002000000000"],
#    ["울산_중구", "https://www.junggu.ulsan.kr/index.ulsan?menuCd=DOM_000000102004001000"],
#    ["울산_남구", "https://www.ulsannamgu.go.kr/cop/bbs/selectSaeolGosiList.do"],
#    ["울산_동구", "https://www.donggu.ulsan.kr/donggu/contents/contents.do?mId=4040100"],
#    ["울산_북구", "https://www.bukgu.ulsan.kr/lay1/S1T86C456/contents.do"],
#    ["울산_울주군", "https://www.ulju.ulsan.kr/ulju/saeol/gosi/list.do?mId=0403010000"],
#    ["충청북도", "https://www.chungbuk.go.kr/www/selectGosiPblancList.do?key=422^&se=^&searchCnd=all^&searchKrwd=%%EA%%B5%%90%%EC%%84%%AD"],
#    ["충북_청주", "https://www.cheongju.go.kr/www/selectEminwonNoticeList.do?key=281^&notAncmtSeCd=^&nowDongGn=^&searchCnd=all^&searchKrwd=%%EA%%B5%%90%%EC%%84%%AD^&x=36^&y=0"],
#    ["충북_충주", "https://www.chungju.go.kr/www/selectEminwonList.do?ancmt_sj=%%EA%%B5%%90%%EC%%84%%AD^&key=510"],
#    ["충북_제천", "https://www.jecheon.go.kr/www/selectBbsNttList.do?key=5233^&bbsNo=18^&integrDeptCode=^&searchCtgry=^&searchCnd=SJ^&searchKrwd=%%EA%%B5%%90%%EC%%84%%AD"],
#    ["충북_보은", "https://www.boeun.go.kr/www/selectBbsNttList.do?key=194^&bbsNo=66^&searchCtgry=^&integrDeptCode=^&searchCnd=SJ^&searchKrwd=%%EA%%B5%%90%%EC%%84%%AD"],
#    ["충북_옥천", "https://www.oc.go.kr/www/selectBbsNttList.do?key=236^&bbsNo=40^&searchCtgry=^&integrDeptCode=^&searchCnd=SJ^&searchKrwd=%%EA%%B5%%90%%EC%%84%%AD"],
#    ["충북_영동", "https://www.yd21.go.kr/kr/html/sub02/020103.html?mode=L"],
#    ["충북_증평", "http://www.jp.go.kr/kor/sub03_01_03.do"],
#    ["충북_진천", "https://www.jincheon.go.kr/home/sub.do?menukey=235"],
#    ["충북_괴산", "https://eminwon.goesan.go.kr/emwp/gov/mogaha/ntis/web/ofr/action/OfrAction.do"],
#    ["충북_음성", "https://www.eumseong.go.kr/www/selectEminwonList.do?pageUnit=10^&ofr_pageSize=10^&key=352^&searchCnd=B_Subject^&searchKrwd=%%EA%%B5%%90%%EC%%84%%AD"],
#    ["충북_단양", "https://www.danyang.go.kr/dy21/976"],
#    ["경기도", "https://www.gg.go.kr/bbs/board.do?bsIdx=469&menuId=1547#page=1#keyfield=SUBJECTANDREMARK#keyword=%EA%B5%90%EC%84%AD"],
#    ["경기_고양", "https://www.goyang.go.kr/www/link/BD_notice.do?se=01"],
#    ["경기_광주", "https://www.gjcity.go.kr/portal/saeol/gosi/list.do?mId=0202010000"],
#    ["경기_구리", "https://www.guri.go.kr/www/selectGosiNttList.do?key=387&searchGosiSe=01%2C04%2C06&searchDeptNm=&searchCnd=ALL&searchKrwd=%EA%B5%90%EC%84%AD"],
#    ["경기_남양주", "https://www.nyj.go.kr/www/selectEminwonWebList.do?key=2492"],
#    ["경기_양주", "https://www.yangju.go.kr/www/selectEminwonList.do?pageUnit=10&key=4075&ofr_pageSize=10&searchCnd=B_Subject&searchKrwd=%EA%B5%90%EC%84%AD"],
#    ["경기_양평", "https://www.yp21.go.kr/www/selectBbsNttList.do?key=1119&bbsNo=5&integrDeptCode=&searchCtgry=&searchCnd=SJ&searchKrwd=%EA%B5%90%EC%84%AD"],
#    ["경기_평택", "https://www.pyeongtaek.go.kr/pyeongtaek/saeol/gosi/list.do?mid=0401020100"],
#    ["경기_포천", "https://www.pocheon.go.kr/www/selectEminwonList.do?key=12563&notAncmtSeCode=01&searchCnd=notAncmtSj&searchKrwd=%EA%B5%90%EC%84%AD&_csrfToken_pcg=9987888e-2dad-438c-8f9d-dc3ad5cfec63"],
#    ["강원특별자치도", "https://state.gwd.go.kr/portal/bulletin/notification?pageIndex=1&recordCountPerPage=15&mode=&firstYN=N&articleSeq=0&searchFromDate=2021-03-09&searchToDate=2026-03-09&searchCondition=TITLE&searchKeyword=%EA%B5%90%EC%84%AD"],
#    ["강원_춘천", "https://www.chuncheon.go.kr/cityhall/administrative-info/notice-info/notice-announcement/?pageIndex=1&searchCnd=SJ&searchWrd=%EA%B5%90%EC%84%AD"],
#    ["전북특별자치도", "https://www.jeonbuk.go.kr/board/list.jeonbuk?menuCd=DOM_000000102002005000&boardId=BBS_0000129&listCel=1&categoryCode1=&categoryCode2=&searchType=DATA_TITLE&listRow=10&keyword=%EA%B5%90%EC%84%AD"],
#    ["전북_군산", "https://eminwon.gunsan.go.kr/emwp/gov/mogaha/ntis/web/ofr/action/OfrAction.do"],
#    ["전북_전주", "https://www.jeonju.go.kr/planweb/board/list.9is?boardUid=9be517a7914528ce01930aa3ddc26cf0&contentUid=ff8080818990c349018b041a879f395a&rowCount=10&searchType=dataTitle&keyword=%EA%B5%90%EC%84%AD"],
#    ["경상남도", "https://www.gne.go.kr/user/bbs/BD_selectBbsList.do?csrfToken=84be7b4baea8a5da52e79f1b829dafd59cf7c68c304d971ad1d8676dbbc89021&q_rowPerPage=10&q_currPage=1&q_sortName=&q_sortOrder=&q_bbsSn=1238&q_bbsDocNo=&q_menu=&q_ctgryCd=&q_searchKeyTy=ttl___1002&q_searchVal=%EA%B5%90%EC%84%AD"],
#    ["경남_김해", "https://www.gimhae.go.kr/03360/00023/00029.web?cpage=1&deptCode=&stype=title&sstring=%EA%B5%90%EC%84%AD"],
#    ["경남_의령", "https://www.uiryeong.go.kr/board/list.uiryeong?orderBy=&boardId=BBS_0000070&searchStartDt=&searchEndDt=&startPage=1&menuCd=DOM_000000203003001001&contentsSid=201&searchType=DATA_TITLE&keyword=%EA%B5%90%EC%84%AD"],
#    ["경남_창원", "https://www.changwon.go.kr/cwportal/10310/10438/10439.web?cpage=1&pbsDivision=&stype=title&sstring=%EA%B5%90%EC%84%AD&upunit=10"],
#    ["경남_함안", "https://www.haman.go.kr/00960/00962.web?cpage=1&gubun=present&stype=title&sstring=%EA%B5%90%EC%84%AD"],
#    ["경상북도", "https://www.gb.go.kr/Main/page.do?bdName=%EA%B3%A0%EC%8B%9C%EA%B3%B5%EA%B3%A0&mnu_uid=6789&CSRF_TOKEN=&p1=0&p2=0&dept_name=&dept_code=&BD_CODE=gosi_notice&B_START=2026-01-09&B_END=2026-03-09&key=2&word=%EA%B5%90%EC%84%AD"],
#    ["경북_경산", "https://www.gbgs.go.kr/open_content/ko/page.do"],
#    ["경북_경주", "https://www.gyeongju.go.kr/open_content/ko/page.do"],
#    ["경북_구미", "https://www.gumi.go.kr/portal/saeol/gosi/list.do?seCode=01&mid=0401040000"],
#    ["경북_의성", "https://www.usc.go.kr/ko/page.do?mnu_uid=157&srchColumn=title&srchKwd=%EA%B5%90%EC%84%AD"],
#    ["충청남도", "http://www.cne.go.kr/boardCnts/list.do"],
#    ["충남_보령", "https://www.brcn.go.kr/prog/eminwon/kor/BB/sub04_03_01/list.do"],
#    ["충남_예산", "https://www.yesan.go.kr/prog/saeolGosi/GOSI/kor/sub04_03_01/list.do"],
#    ["충남_천안", "https://www.cheonan.go.kr/kor/sub02_02_01.do"],
#    ["충청북도", "https://www.chungbuk.go.kr/www/selectGosiPblancList.do?key=422&se=&searchCnd=all&searchKrwd=%EA%B5%90%EC%84%AD"],
#    ["충북_청주", "https://www.cheongju.go.kr/www/selectEminwonNoticeList.do?key=281&notAncmtSeCd=&nowDongGn=&searchCnd=all&searchKrwd=%EA%B5%90%EC%84%AD&x=36&y=8"],
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






































