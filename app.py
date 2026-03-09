import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time

# 페이지 설정
st.set_page_config(page_title="교섭공고 알리미", page_icon="🔍")
st.title("🏛️ 전국 지자체 교섭요구공고 (안정 모드)")

# 자치구 리스트 (기존 리스트 그대로 사용)
target_sites = [
    ["서울특별시", "https://www.seoul.go.kr/news/news_notice.do?bbsNo=277&cntPerPage=10&curPage=1&srchText=%EA%B5%90%EC%84%AD"],
    ["강남구청", "https://www.gangnam.go.kr/notice/list.do?mid=ID05_040201&pgno=1&lists=10&gubunfield=&deptField=BNI_DEP_CODE&deptId=&keyfield=BNI_MAIN_TITLE&keyword=%EA%B5%90%EC%84%AD"],
    ["강동구청", "https://www.gangdong.go.kr/web/newportal/notice/01?pageSize=10&sc=&sv=%EA%B5%90%EC%84%AD"],
    ["강북구청", "https://www.gangbuk.go.kr/portal/bbs/B0000245/list.do?menuNo=200082&bbsId=&cl1Cd=&optn5=&pageIndex=1&searchCnd2=&searchCnd=&searchWrd=%EA%B5%90%EC%84%AD"],
    ["강서구청", "https://www.gangseo.seoul.kr/gs040301?srchPage=10&srchKey=sj&srchText=%EA%B5%90%EC%84%AD"],
    ["관악구청", "https://www.gwanak.go.kr/site/gwanak/ex/bbsNew/List.do?typeCode=1"],
    ["광진구청", "https://www.gwangjin.go.kr/portal/bbs/B0000378/list.do?pageIndex=1&menuNo=200192&noticeType=&searchCnd=&searchWrd=%EA%B5%90%EC%84%AD"],
    ["구로구청", "https://www.guro.go.kr/www/selectBbsNttList.do?key=1791&bbsNo=663&integrDeptCode=&searchCtgry=&searchCnd=SJ&searchKrwd=%EA%B5%90%EC%84%AD"],
    ["금천구청", "https://www.geumcheon.go.kr/portal/tblSeolGosiDetailList.do?key=294&rep=1&searchCnd=all&searchKrwd=%EA%B5%90%EC%84%AD"],
    ["노원구청", "https://www.nowon.kr/www/user/bbs/BD_selectBbsList.do?q_bbsCode=1003&q_bbscttSn=&q_estnColumn7=&q_estnColumn1=11&q_ntceSiteCode=11&q_clCode=0&q_rowPerPage=10&q_currPage=1&q_sortName=&q_sortOrder=&q_searchKeyTy=sj___1002&q_searchVal=%EA%B5%90%EC%84%AD"],
    ["도봉구청", "https://www.dobong.go.kr/WDB_DEV/gosigong_go/default.asp?sDEP_CODE=&strSearchType=1&strSearchKeyword=%EA%B5%90%EC%84%AD"],
    ["동대문구청", "https://www.ddm.go.kr/www/selectEminwonWebList.do?key=3291&searchNotAncmtSeCode=01%2C02%2C04%2C05%2C06%2C07&searchCnd=notAncmtSj&searchKrwd=%EA%B5%90%EC%84%AD"],
    ["동작구청", "https://www.dongjak.go.kr/portal/bbs/B0001297/list.do?menuNo=201317"],
    ["마포구청", "https://www.mapo.go.kr/site/main/nPortal/list?_sToken=1773057057300733_7fdc068a0a2e1c29d54c5dbbc2854934995e9895f3a41063e2d6ed98396173d3&sc=&sv=%EA%B5%90%EC%84%AD&pageSize=10"],
    ["서대문구청", "https://www.sdm.go.kr/news/notice/notice.do"],
    ["서초구청", "https://www.seocho.go.kr/site/seocho/05/10506020000002015070811.jsp"],
    ["성동구청", "https://www.sd.go.kr/main/selectBbsNttList.do?key=1473&bbsNo=184&integrDeptCode=&searchCtgry=&searchCnd=SJ&searchKrwd=%EA%B5%90%EC%84%AD"],
    ["성북구청", "https://www.sb.go.kr/main/selectBbsNttList.do?bbsNo=3&searchCnd=all&searchWrd=%EA%B5%90%EC%84%AD%EC%9A%94%EA%B5%AC"],
    ["송파구청", "https://www.songpa.go.kr/www/selectGosiList.do?key=2776&not_ancmt_se_code=&searchCnd=SJ&searchKrwd=%EA%B5%90%EC%84%AD"],
    ["양천구청", "https://www.yangcheon.go.kr/site/yangcheon/ex/bbs/List.do?cbIdx=262&searchTarget=title&searchKeyword=%EA%B5%90%EC%84%AD%EC%9A%94%EA%B5%AC"],
    ["영등포구청", "https://www.ydp.go.kr/www/selectEminwonList.do?key=2851&menuFlag=01&not_ancmt_se_code=&searchCnd=B_Subject&searchKrwd=%EA%B5%90%EC%84%AD"],
    ["용산구청", "https://www.yongsan.go.kr/portal/bbs/B0000095/list.do?menuNo=200233&optn1=&pageUnit=&sdate=&edate=&deptId=&searchCnd=1&searchWrd=%EA%B5%90%EC%84%AD"],
    ["은평구청", "https://www.ep.go.kr/www/selectEminwonList.do?key=754&notAncmtSeCode=01&pageUnit=10&searchCnd=notAncmtSj&searchKrwd=%EA%B5%90%EC%84%AD"],
    ["종로구청", "https://www.jongno.go.kr/portal/bbs/selectBoardList.do?bbsId=BBSMSTR_000000000271&menuNo=1756&menuId=1756"],
    ["중구청", "https://www.junggu.seoul.kr/content.do"],
    ["중랑구청", "https://www.jungnang.go.kr/portal/bbs/list/B0000117.do?menuNo=200475&viewType="],
    ["울산_중구", "https://www.junggu.ulsan.kr/index.ulsan?menuCd=DOM_000000102004001000"],
    ["울산_남구", "https://www.ulsannamgu.go.kr/cop/bbs/selectSaeolGosiList.do"],
    ["울산_동구", "https://www.donggu.ulsan.kr/donggu/contents/contents.do?mId=4040100"],
    ["울산_북구", "https://www.bukgu.ulsan.kr/lay1/S1T86C456/contents.do"],
    ["울산_울주군", "https://www.ulju.ulsan.kr/ulju/saeol/gosi/list.do?mId=0403010000"],
    ["충청북도", "https://www.chungbuk.go.kr/www/selectGosiPblancList.do?key=422^&se=^&searchCnd=all^&searchKrwd=%%EA%%B5%%90%%EC%%84%%AD"],
    ["충북_청주", "https://www.cheongju.go.kr/www/selectEminwonNoticeList.do?key=281^&notAncmtSeCd=^&nowDongGn=^&searchCnd=all^&searchKrwd=%%EA%%B5%%90%%EC%%84%%AD^&x=36^&y=0"],
    ["충북_충주", "https://www.chungju.go.kr/www/selectEminwonList.do?ancmt_sj=%%EA%%B5%%90%%EC%%84%%AD^&key=510"],
    ["충북_제천", "https://www.jecheon.go.kr/www/selectBbsNttList.do?key=5233^&bbsNo=18^&integrDeptCode=^&searchCtgry=^&searchCnd=SJ^&searchKrwd=%%EA%%B5%%90%%EC%%84%%AD"],
    ["충북_보은", "https://www.boeun.go.kr/www/selectBbsNttList.do?key=194^&bbsNo=66^&searchCtgry=^&integrDeptCode=^&searchCnd=SJ^&searchKrwd=%%EA%%B5%%90%%EC%%84%%AD"],
    ["충북_옥천", "https://www.oc.go.kr/www/selectBbsNttList.do?key=236^&bbsNo=40^&searchCtgry=^&integrDeptCode=^&searchCnd=SJ^&searchKrwd=%%EA%%B5%%90%%EC%%84%%AD"],
    ["충북_영동", "https://www.yd21.go.kr/kr/html/sub02/020103.html?mode=L"],
    ["충북_증평", "http://www.jp.go.kr/kor/sub03_01_03.do"],
    ["충북_진천", "https://www.jincheon.go.kr/home/sub.do?menukey=235"],
    ["충북_괴산", "https://eminwon.goesan.go.kr/emwp/gov/mogaha/ntis/web/ofr/action/OfrAction.do"],
    ["충북_음성", "https://www.eumseong.go.kr/www/selectEminwonList.do?pageUnit=10^&ofr_pageSize=10^&key=352^&searchCnd=B_Subject^&searchKrwd=%%EA%%B5%%90%%EC%%84%%AD"],
    ["충북_단양", "https://www.danyang.go.kr/dy21/976"],
    ["경기_평택", "https://www.pyeongtaek.go.kr/pyeongtaek/saeol/gosi/list.do?mid=0401020100"],
    ["경기_양평", "https://www.yp21.go.kr/www/selectBbsNttList.do?key=1119&bbsNo=5&integrDeptCode=&searchCtgry=&searchCnd=SJ&searchKrwd=%EA%B5%90%EC%84%AD"],
    ["경기_광주", "https://www.gjcity.go.kr/portal/saeol/gosi/list.do?mId=0202010000"],
    ["경기_양주", "https://www.yangju.go.kr/www/selectEminwonList.do?pageUnit=10&key=4075&ofr_pageSize=10&searchCnd=B_Subject&searchKrwd=%EA%B5%90%EC%84%AD"],
    ["전북_군산", "https://eminwon.gunsan.go.kr/emwp/gov/mogaha/ntis/web/ofr/action/OfrAction.do"],
    ["충남_보령", "https://www.brcn.go.kr/prog/eminwon/kor/BB/sub04_03_01/list.do"],
]
def get_recent_dates():
    return [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]

def check_site_stable(name, url, recent_dates):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        # 브라우저를 띄우지 않고 소스코드만 직접 요청
        response = requests.get(url, headers=headers, timeout=15, verify=False)
        content = response.text
        
        no_result = any(txt in content for txt in ["검색된 결과가 없습니다", "0건", "데이터가 없습니다"])
        has_keyword = "교섭" in content and not no_result
        has_date = any(date in content for date in recent_dates)
        
        if has_keyword and has_date: status = "🔴 신규 가능성 높음"
        elif has_keyword: status = "🟡 '교섭' 공고 존재"
        else: status = "⚪ 결과 없음"
        return [name, url, status]
    except Exception as e:
        return [name, url, f"⚠️ 확인 불가 (직접 확인 요망)"]

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
        time.sleep(0.1) # 서버 부하 방지

    df = pd.DataFrame(results, columns=["지자체명", "링크", "상태"])
    
    # 링크 클릭 가능하게 변환
    def make_link(url):
        return f'<a href="{url}" target="_blank">게시판 이동</a>'
    df['링크'] = df['링크'].apply(make_link)
    
    st.success("검사가 완료되었습니다!")
    st.write(df.to_html(escape=False), unsafe_allow_html=True)

    csv = df.to_csv(index=False).encode('utf-8-sig')

    st.download_button("📥 결과 CSV 다운로드", csv, "check_result.csv", "text/csv")






