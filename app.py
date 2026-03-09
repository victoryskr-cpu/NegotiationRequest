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
    ["서울특별시", "https://www.seoul.go.kr/news/news_notice.do?searchWrd=%EA%B5%90%EC%84%AD%EC%9A%94%EA%B5%AC"],
    ["강남구청", "https://www.gangnam.go.kr/office/gwanbo/bbs/getBbsList.do?searchCondition=0&searchKeyword=%EA%B5%90%EC%84%AD%EC%9A%94%EA%B5%AC"],
    ["강동구청", "https://www.gangdong.go.kr/web/portal/ko/bbs/list.do?bbsId=B0001&searchSj=%EA%B5%90%EC%84%AD%EC%9A%94%EA%B5%AC"],
    ["강북구청", "https://www.gangbuk.go.kr/www/boardList.do?boardId=B0006&searchCondition=nttSj&searchKeyword=%EA%B5%90%EC%84%AD%EC%9A%94%EA%B5%AC"],
    ["강서구청", "https://www.gangseo.seoul.kr/gs040101?curPage=1&searchType=title&searchText=%EA%B5%90%EC%84%AD%EC%9A%94%EA%B5%AC"],
    ["관악구청", "https://www.gwanak.go.kr/servlets/rnl/gwanak/board/action/BoardAction?p_menu_cd=000140&p_board_id=1&search_key=title&search_val=%EA%B5%90%EC%84%AD%EC%9A%94%EA%B5%AC"],
    ["광진구청", "https://www.gwangjin.go.kr/portal/bbs/B0000001/list.do?searchCnd=0&searchWrd=%EA%B5%90%EC%84%AD%EC%9A%94%EA%B5%AC"],
    ["구로구청", "https://www.guro.go.kr/www/selectBbsNttList.do?bbsNo=640&searchCnd=all&searchWrd=%EA%B5%90%EC%84%AD%EC%9A%94%EA%B5%AC"],
    ["금천구청", "https://www.geumcheon.go.kr/portal/selectBbsNttList.do?bbsNo=147&searchCnd=all&searchWrd=%EA%B5%90%EC%84%AD%EC%9A%94%EA%B5%AC"],
    ["노원구청", "https://www.nowon.kr/www/user/bbs/BD_selectBbsList.do?q_bbsCode=1001&q_searchKey=1001&q_searchVal=%EA%B5%90%EC%84%AD%EC%9A%94%EA%B5%AC"],
    ["도봉구청", "https://www.dobong.go.kr/bbs.asp?code=10004131&search_key=title&search_val=%EA%B5%90%EC%84%AD%EC%9A%94%EA%B5%AC"],
    ["동대문구청", "https://www.ddm.go.kr/www/selectBbsNttList.do?bbsNo=38&searchCnd=all&searchWrd=%EA%B5%90%EC%84%AD%EC%9A%94%EA%B5%AC"],
    ["동작구청", "https://www.dongjak.go.kr/portal/bbs/B0000022/list.do?searchCnd=0&searchWrd=%EA%B5%90%EC%84%AD%EC%9A%94%EA%B5%AC"],
    ["마포구청", "https://www.mapo.go.kr/site/main/board/notice/list?baCat=TITLE&baText=%EA%B5%90%EC%84%AD%EC%9A%94%EA%B5%AC"],
    ["서대문구청", "https://www.sdm.go.kr/news/notice/notice.do?searchCondition=1&searchKeyword=%EA%B5%90%EC%84%AD%EC%9A%94%EA%B5%AC"],
    ["서초구청", "https://www.seocho.go.kr/html/notice/notice.jsp?search_field=title&search_word=%EA%B5%90%EC%84%AD%EC%9A%94%EA%B5%AC"],
    ["성동구청", "https://www.sd.go.kr/main/selectBbsNttList.do?bbsNo=183&searchCnd=all&searchWrd=%EA%B5%90%EC%84%AD%EC%9A%94%EA%B5%AC"],
    ["성북구청", "https://www.sb.go.kr/main/selectBbsNttList.do?bbsNo=3&searchCnd=all&searchWrd=%EA%B5%90%EC%84%AD%EC%9A%94%EA%B5%AC"],
    ["송파구청", "https://www.songpa.go.kr/www/selectBbsNttList.do?bbsNo=78&searchCnd=all&searchWrd=%EA%B5%90%EC%84%AD%EC%9A%94%EA%B5%AC"],
    ["양천구청", "https://www.yangcheon.go.kr/site/yangcheon/ex/bbs/List.do?cbIdx=262&searchTarget=title&searchKeyword=%EA%B5%90%EC%84%AD%EC%9A%94%EA%B5%AC"],
    ["영등포구청", "https://www.ydp.go.kr/www/selectBbsNttList.do?bbsNo=40&searchCnd=all&searchWrd=%EA%B5%90%EC%84%AD%EC%9A%94%EA%B5%AC"],
    ["용산구청", "https://www.yongsan.go.kr/portal/bbs/B0000002/list.do?searchCnd=0&searchWrd=%EA%B5%90%EC%84%AD%EC%9A%94%EA%B5%AC"],
    ["은평구청", "https://www.ep.go.kr/www/selectBbsNttList.do?bbsNo=6&searchCnd=all&searchWrd=%EA%B5%90%EC%84%AD%EC%9A%94%EA%B5%AC"],
    ["종로구청", "https://www.jongno.go.kr/portal/bbs/B0000002/list.do?searchCnd=0&searchWrd=%EA%B5%90%EC%84%AD%EC%9A%94%EA%B5%AC"],
    ["중구청", "https://www.junggu.seoul.kr/board/list.do?boardId=BDS00001&searchCnd=all&searchWrd=%EA%B5%90%EC%84%AD%EC%9A%94%EA%B5%AC"],
    ["중랑구청", "https://www.jungnang.go.kr/portal/bbs/list.do?bbsId=B0000001&searchCnd=1&searchWrd=%EA%B5%90%EC%84%AD%EC%9A%94%EA%B5%AC"]
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
        elif has_keyword: status = "🟡 예전 공고 존재"
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