import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import re

# 페이지 설정
st.set_page_config(page_title="교섭공고 알리미", page_icon="🔍")

# 헤더 디자인
st.markdown("""
    <style>
    .header-container { text-align: center; margin-top: -20px; margin-bottom: 20px; }
    .main-title { font-size: 2.2rem; font-weight: bold; line-height: 1.2; margin-bottom: 5px; }
    .sub-title { font-size: 1.2rem; color: #666; font-weight: normal; line-height: 1.0; }
    </style>
    <div class="header-container">
        <h1 class="main-title">지자체 교섭요구공고 확인</h1>
        <h3 class="sub-title">(돌봄사업장 지역 공고 모니터링)</h3>
    </div>
""", unsafe_allow_html=True)

# 1. 자동 확인 가능 리스트 (검증 완료)
target_sites = [
#    ["서울특별시", "https://www.seoul.go.kr/news/news_notice.do?bbsNo=277&srchText=교섭"],
#    ["강남구청", "https://www.gangnam.go.kr/notice/list.do?mid=ID05_040201&keyfield=BNI_MAIN_TITLE&keyword=교섭"],
#    ["강동구청", "https://www.gangdong.go.kr/web/newportal/notice/01?sv=교섭"],
#    ["강서구청", "https://www.gangseo.seoul.kr/gs040301?srchKey=sj&srchText=교섭"],
#   ["구로구청", "https://www.guro.go.kr/www/selectBbsNttList.do?key=1791&bbsNo=663&searchCnd=SJ&searchKrwd=교섭"],
#    ["금천구청", "https://www.geumcheon.go.kr/portal/tblSeolGosiDetailList.do?key=294&rep=1&searchCnd=all&searchKrwd=%EA%B5%90%EC%84%AD"],
#    ["노원구청", "https://www.nowon.kr/www/user/bbs/BD_selectBbsList.do?q_bbsCode=1003&q_searchVal=%EA%B5%90%EC%84%AD"],
#    ["도봉구청", "https://www.dobong.go.kr/WDB_DEV/gosigong_go/default.asp?strSearchType=1&strSearchKeyword=%EA%B5%90%EC%84%AD"],
#    ["동대문구청", "https://www.ddm.go.kr/www/selectEminwonWebList.do?key=3291&searchCnd=notAncmtSj&searchKrwd=%EA%B5%90%EC%84%AD"],
#    ["동작구청", "https://www.dongjak.go.kr/portal/bbs/B0001297/list.do?menuNo=201317&searchCnd=1&searchWrd=%EA%B5%90%EC%84%AD"],
#    ["마포구청", "https://www.mapo.go.kr/site/main/nPortal/list?sv=%EA%B5%90%EC%84%AD"],
#    ["서초구청", "https://www.seocho.go.kr/site/seocho/05/10506020000002015070811.jsp"],
#    ["성동구청", "https://www.sd.go.kr/main/selectBbsNttList.do?key=1473&bbsNo=184&searchCnd=SJ&searchKrwd=%EA%B5%90%EC%84%AD"],
#    ["성북구청", "https://www.sb.go.kr/www/selectEminwonList.do?key=6977&searchCnd2=notAncmtSj&searchKrwd=%EA%B5%90%EC%84%AD"],
#    ["영등포구청", "https://www.ydp.go.kr/www/selectEminwonList.do?key=2851&searchCnd=B_Subject&searchKrwd=%EA%B5%90%EC%84%AD"],
#    ["용산구청", "https://www.yongsan.go.kr/portal/bbs/B0000095/list.do?menuNo=200233&searchCnd=1&searchWrd=%EA%B5%90%EC%84%AD"],
#    ["은평구청", "https://www.ep.go.kr/www/selectEminwonList.do?key=754&searchCnd=notAncmtSj&searchKrwd=%EA%B5%90%EC%84%AD"],
#    ["중랑구청", "https://www.jungnang.go.kr/portal/bbs/list/B0000117.do?menuNo=200475&searchWrd=%EA%B5%90%EC%84%AD"],
#    ["부산광역시", "https://www.busan.go.kr/nbgosi/list?schKeyType=A&srchText=%EA%B5%90%EC%84%AD"],
#    ["부산_남구", "https://www.bsnamgu.go.kr/index.namgu?menuCd=DOM_000000105001002000&search_key=title&search_val=%EA%B5%90%EC%84%AD"],
#    ["부산_동래구", "https://www.dongnae.go.kr/index.dongnae?menuCd=DOM_000000103001003000&search_key=title&search_val=%EA%B5%90%EC%84%AD"],
#    ["대구_동구", "https://www.dong.daegu.kr/portal/saeol/gosi/list.do?mid=0201020000&searchKrwd=%EA%B5%90%EC%84%AD"],
#    ["대구_달서구", "https://www.dalseo.daegu.kr/index.do?menu_id=10000104&searchKey=sj&searchKeyword=%EA%B5%90%EC%84%AD"],
#    ["대구_중구", "https://www.jung.daegu.kr/new/pages/administration/page.html?mc=0159&search_key=sj&search_keyword=%EA%B5%90%EC%84%AD"],
#    ["경기_양주", "https://www.yangju.go.kr/www/selectEminwonList.do?key=4075&searchCnd=B_Subject&searchKrwd=%EA%B5%90%EC%84%AD"],
#    ["경기_양평", "https://www.yp21.go.kr/www/selectBbsNttList.do?key=1119&bbsNo=5&searchCnd=SJ&searchKrwd=%EA%B5%90%EC%84%AD"],
#    ["경기_포천", "https://www.pocheon.go.kr/www/selectEminwonList.do?key=12563&searchCnd=notAncmtSj&searchKrwd=%EA%B5%90%EC%84%AD"],
#    ["충북_제천", "https://www.jecheon.go.kr/www/selectBbsNttList.do?key=5233&bbsNo=18&searchCnd=SJ&searchKrwd=%EA%B5%90%EC%84%AD"],
#    ["충북_보은", "https://www.boeun.go.kr/www/selectBbsNttList.do?key=194&bbsNo=66&searchCnd=SJ&searchKrwd=%EA%B5%90%EC%84%AD"],
#    ["충북_옥천", "https://www.oc.go.kr/www/selectBbsNttList.do?key=236&bbsNo=40&searchCnd=SJ&searchKrwd=%EA%B5%90%EC%84%AD"],
#    ["충북_진천", "https://www.jincheon.go.kr/home/sub.do?menukey=235&searchCnd=sj&searchKrwd=%EA%B5%90%EC%84%AD"],
#    ["충북_괴산", "https://www.goesan.go.kr/www/selectBbsNttList.do?key=604&searchCnd=SJ&searchKrwd=%EA%B5%90%EC%84%AD"],
#    ["충북_음성", "https://www.eumseong.go.kr/www/selectEminwonList.do?key=352&searchCnd=B_Subject&searchKrwd=%EA%B5%90%EC%84%AD"],
    ["강원특별자치도", "https://state.gwd.go.kr/portal/bulletin/notification?searchCondition=TITLE&searchKeyword=%EA%B5%90%EC%84%AD"],
    ["강원_춘천", "https://www.chuncheon.go.kr/cityhall/administrative-info/notice-info/notice-announcement/?searchCnd=SJ&searchWrd=%EA%B5%90%EC%84%AD"],
    ["전북특별자치도", "https://www.jeonbuk.go.kr/board/list.jeonbuk?boardId=BBS_0000129&menuCd=DOM_000000102002005000&searchType=DATA_TITLE&keyword=%EA%B5%90%EC%84%AD"],
    ["전북_군산", "https://www.gunsan.go.kr/main/m141"],
    ["전북_전주", "https://www.jeonju.go.kr/planweb/board/list.9is?boardUid=9be517a7914528ce01930aa3ddc26cf0&contentUid=ff8080818990c349018b041a879f395a&searchType=dataTitle&keyword=%EA%B5%90%EC%84%AD"],
    ["경상남도", "https://www.gyeongnam.go.kr/gosi/index.gyeong?amode=list&search_key=title&search_val=%EA%B5%90%EC%84%AD"],
    ["경남_김해", "https://www.gimhae.go.kr/03360/00023/00029.web?stype=title&sstring=%EA%B5%90%EC%84%AD"],
    ["경남_의령", "https://www.uiryeong.go.kr/board/list.uiryeong?boardId=BBS_0000070&menuCd=DOM_000000203003001001&searchType=DATA_TITLE&keyword=%EA%B5%90%EC%84%AD"],
    ["경남_창원", "https://www.changwon.go.kr/cwportal/10310/10438/10439.web?stype=title&sstring=%EA%B5%90%EC%84%AD"],
    ["경남_함안", "https://www.haman.go.kr/00960/00962.web?stype=title&sstring=%EA%B5%90%EC%84%AD"],#    ["경상북도", "https://www.gb.go.kr/Main/page.do?bdName=%EA%B3%A0%EC%8B%9C%EA%B3%B5%EA%B3%A0&mnu_uid=6789&CSRF_TOKEN=&p1=0&p2=0&dept_name=&dept_code=&BD_CODE=gosi_notice&B_START=2026-01-09&B_END=2026-03-09&key=2&word=%EA%B5%90%EC%84%AD"],
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

# 2. 직접 확인 필요 리스트 (분류 완료)
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
    ["충북_영동", "https://www.yd21.go.kr/kr/html/sub02/020103.html?mode=L"],
    ["충북_증평", "http://www.jp.go.kr/kor/sub03_01_03.do"],
    ["충청북도", "https://www.chungbuk.go.kr/www/selectGosiPblancList.do?key=422&searchKrwd=%EA%B5%90%EC%84%AD"],
    ["충북_청주", "https://www.cheongju.go.kr/www/selectEminwonNoticeList.do?key=281&searchKrwd=%EA%B5%90%EC%84%AD"],
    ["충북_충주", "https://www.chungju.go.kr/www/selectEminwonList.do?key=510&ancmt_sj=%EA%B5%90%EC%84%AD"],
    ["충북_단양", "https://www.danyang.go.kr/dy21/976"],
#    ["경상북도", "https://www.gb.go.kr/Main/page.do?bdName=%EA%B3%A0%EC%8B%9C%EA%B3%B5%EA%B3%A0&mnu_uid=6789"],
]

def get_recent_dates():
    return [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]

def get_recent_dates():
    return [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]

def check_site_stable(name, url, recent_dates):
    headers = { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36" }
    try:
        response = requests.get(url, headers=headers, timeout=25, verify=False)
        response.encoding = response.apparent_encoding 
        content = response.text
        
        # [교정] 노이즈 제거 범위를 더 넓힘 (사이드바, 네비게이션 단어 제외)
        clean_text = re.sub(r'<script.*?</script>|<style.*?</style>|<header.*?</header>|<footer.*?</footer>|<nav.*?</nav>', '', content, flags=re.DOTALL)
        
        # 1. [함안군 대응] 결과 없음 문구를 최우선으로 체크하여 오탐 방지
        fail_indicators = ['검색된 결과가 없습니다', '등록된 게시물이 없습니다', '조회된 내역이 없습니다', '데이터가 없습니다', '0건']
        if any(indicator in clean_text for indicator in fail_indicators):
            return [name, url, "⚪ 결과 없음"]

        # 2. 신규 공고 (날짜+교섭 조합)
        has_recent = any(date in clean_text for date in recent_dates)
        if "교섭" in clean_text and has_recent:
            return [name, url, "🔴 신규 가능성 높음"]

        # 3. 기존 공고 (날짜 양식 + 교섭)
        if "교섭" in clean_text and re.search(r'\d{2,4}[-.]\d{2}[-.]\d{2}', clean_text):
            return [name, url, "🟡 기존 공고 존재"]

        return [name, url, "⚪ 결과 없음"]
    except:
        return [name, url, "⚠️ 직접 확인 요망 (접속 지연)"]

# --- 화면 UI ---
if st.button("🚀 공고 확인 시작"):
    recent_dates = get_recent_dates()
    results = []
    progress_text = st.empty()
    bar = st.progress(0)
    
    for i, (name, url) in enumerate(target_sites):
        progress_text.text(f"현재 확인 중: {name} ({i+1}/{len(target_sites)})")
        results.append(check_site_stable(name, url, recent_dates))
        bar.progress((i + 1) / len(target_sites))
        time.sleep(0.1)

    df = pd.DataFrame(results, columns=["지자체명", "링크", "상태"])
    df['링크'] = df['링크'].apply(lambda x: f'<a href="{x}" target="_blank">게시판 이동</a>')
    
    st.success("자동 검사가 완료되었습니다!")
    st.write(df.to_html(escape=False), unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📢 게시판으로 이동해서 직접 검색하세요")
    m_df = pd.DataFrame(manual_sites, columns=["지자체명", "링크"])
    m_df['링크'] = m_df['링크'].apply(lambda x: f'<a href="{x}" target="_blank">게시판 이동</a>')
    st.write(m_df.to_html(escape=False), unsafe_allow_html=True)




















































