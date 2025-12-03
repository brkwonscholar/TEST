
import os
from openai import OpenAI
import streamlit as st
os.environ["OPENAI_API_KEY"] = st.secrets['API_KEY']

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"),)

import random

# 앱 제목
st.title("<🗓️통합 플래너🖊️✔️>")

# 날짜 입력하기
import datetime
import streamlit as st

d = st.date_input("오늘의 날짜를 입력하세요", value=None)

import streamlit as st
from dateutil import parser
import datetime

st.title("📌 일정 자동 분석")

# 세션 초기화
if "tasks" not in st.session_state:
    st.session_state.tasks = []

today = datetime.date.today()

# 일정 입력
input_text = st.text_input(
    "일정 입력",
    placeholder="예: 11월 5일 경통 과제 제출 마감 / 11월 3일 Egc 쪽지시험"
)

# 일정 추가 버튼
if st.button("일정 추가"):
    if input_text.strip():
        try:
            # 자연어 날짜 파싱
            parsed_date = parser.parse(
                input_text,
                fuzzy=True,
                default=datetime.datetime(today.year, today.month, today.day)
            ).date()

            st.session_state.tasks.append({
                "raw": input_text,
                "deadline": parsed_date
            })

        except Exception:
            st.error("날짜를 인식할 수 없습니다. 다시 입력해 주세요.")

# 입력된 일정 출력
#st.subheader("입력된 일정 목록")
for t in st.session_state.tasks:
    st.write(f"- {t['raw']} (마감일: {t['deadline']})")

# 우선순위 정렬 버튼
if st.button("우선순위 정렬"):
    if not st.session_state.tasks:
        st.warning("먼저 일정을 입력해 주세요.")
    else:
        st.session_state.sorted_tasks = sorted(
            st.session_state.tasks,
            key=lambda x: x["deadline"]
        )
        st.success("우선순위 정렬이 완료되었습니다.")

# 오늘 해야 할 일 자동 생성
if st.button("오늘 해야 할 일 생성"):
    if "sorted_tasks" not in st.session_state:
        st.warning("먼저 우선순위를 정렬하세요.")
    else:
        st.subheader("오늘 해야 할 일")

        today_list = []
        upcoming_list = []

        for task in st.session_state.sorted_tasks:
            deadline = task["deadline"]
            days_left = (deadline - today).days

            if days_left == 0:  # 오늘 마감
                today_list.append(
                    f"{task['raw']} (마감일이 오늘입니다.)"
                )
            elif 1 <= days_left <= 2:  # 급한 일정
                today_list.append(
                    f"{task['raw']} (마감까지 {days_left}일 남았습니다. 오늘 진행이 필요합니다.)"
                )
            else:  # 여유 있는 일정
                upcoming_list.append(
                    f"{task['raw']} (마감까지 {days_left}일 남았습니다.)"
                )

        if today_list:
            for t in today_list:
                st.write(t)
        else:
            st.info("오늘 반드시 해야 할 일은 없습니다.")

        st.subheader("여유 있는 일정")
        for u in upcoming_list:
            st.write(u)
            
            # to do list
import streamlit as st

# 리스트 초기화 (함수 이름과 충돌 방지)
if "task_items" not in st.session_state:
    st.session_state.task_items = []

# 항목 추가 버튼
if st.button("To Do List 생성"):
    st.session_state.task_items.append({"check": False, "text": ""})

# UI 표시
for i, item in enumerate(st.session_state.task_items):
    col1, col2 = st.columns([1, 6])

    with col1:
        st.session_state.task_items[i]["check"] = st.checkbox(
            "",
            value=item["check"],
            key=f"check_{i}"
        )

    with col2:
        st.session_state.task_items[i]["text"] = st.text_input(
            "",
            value=item["text"],
            placeholder="내용 입력",
            label_visibility="collapsed",
            key=f"text_{i}"
        )

import streamlit as st

st.title("⭐셀프 점검하기")

# 별점 선택 (1~5)
rating = st.radio(
    "계획을 얼마만큼 실행했나요?",
    options=[1, 2, 3, 4, 5],
    format_func=lambda x: "⭐" * x,  # 별 여러 개로 표시
    horizontal=True
)

# 별점별 피드백 문장
feedback_messages = {
    1: "오늘 완료하지 못했던 원인을 찾아 작성하고, 내일은 계획을 더 완료해보세요.",
    2: "아직 조금 부족하네요, 내일은 시간관리를 더 해서 계획을 완료해보세요.",
    3: "괜찮았어요! 그래도 더 좋아질 수 있도록 오늘의 잘했던 점, 부족했던 점을 작성해보세요.",
    4: "좋았어요! 오늘 효과 있었던 습관이나 선택을 작성해보고, 내 루틴으로 만들어보세요.",
    5: "최고네요! 오늘 완료할 수 있었던 이유를 기록하고, 습관으로 만들어보세요."
}

if rating:
    #st.write(f"### ⭐ {rating}점 선택!")
    st.write(feedback_messages[rating])
    
# 피드백 관련 내용 작성하기
st.title("🗒️✏️점검 관련 내용 작성하기")
st.text_input("피드백 내용을 점검하여 자신에게 필요한 내용을 작성하세요.", "")
st.write("꾸준히 작성하여 좋은 습관만 들여보세요!")
    
# 과제 입력 및 관련 자료 찾기
import streamlit as st
import requests
from urllib.parse import quote_plus  # ← 이거 추가하면 끝!
st.header("🧑‍💻📄과제(주제)의 관련 자료")

task = st.text_input("과제 또는 찾고 싶은 주제를 입력하세요. (예: '마케팅 리서치 방법론', '미분적분 복습')")

col1, col2 = st.columns([2,1])

with col1:
    if st.button("자료 찾기"):
        if not task.strip():
            st.write("과제(주제)를 입력해 주세요.")
        else:
            st.success(f"‘{task}’ 관련 자료를 찾아볼게요.")
            # 1) 먼저 위키피디아(한국어/영어) 요약 시도
            def fetch_wikipedia_summary(query, lang="ko"):
                """
                위키피디아 요약 시도. 실패하면 None 반환.
                """
                # 위키피디아의 REST summary API 사용
                url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{quote_plus(query)}"
                try:
                    r = requests.get(url, timeout=6)
                    if r.status_code == 200:
                        data = r.json()
                        # 페이지가 존재하고 extract가 있으면 반환
                        if "extract" in data and data["extract"].strip():
                            return {
                                "title": data.get("title"),
                                "extract": data.get("extract"),
                                "page_url": data.get("content_urls", {}).get("desktop", {}).get("page")
                            }
                    return None
                except Exception:
                    return None

            # 한글 위키피디아 시도 -> 실패하면 영어 시도
            wiki_result = fetch_wikipedia_summary(task, lang="ko")
            if wiki_result is None:
                wiki_result = fetch_wikipedia_summary(task, lang="en")

            if wiki_result:
                st.subheader("빠른 요약 (위키피디아 기준)")
                st.write(f"**{wiki_result['title']}**")
                st.write(wiki_result["extract"])
                if wiki_result.get("page_url"):
                    st.markdown(f"[원문(위키피디아) 보기]({wiki_result['page_url']})")
            else:
                st.info("위키피디아에서 직접적인 요약을 찾지 못했어요. 다음 검색 링크를 활용해 보세요.")

            # 2) 검색 링크들 제공 (네이버/구글/구글스칼라)
            encoded = quote_plus(task)
            search_links = {
                "구글 일반검색": f"https://www.google.com/search?q={encoded}",
                "구글 스칼라": f"https://scholar.google.com/scholar?q={encoded}",
                "네이버": f"https://search.naver.com/search.naver?query={encoded}",
                "다음(카카오)": f"https://search.daum.net/search?w=tot&q={encoded}"
            }

            st.subheader("추천 검색 링크")
            for name, link in search_links.items():
                st.markdown(f"- [{name}]({link})")
