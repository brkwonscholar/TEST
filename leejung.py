import os
from openai import OpenAI
import streamlit as st
import requests

# 🔥 API 키 가장 안정적인 방식 (환경 변수 제거)
client = OpenAI(api_key=st.secrets["API_KEY"])

# 앱 제목
st.title("🧣오늘 뭐 입지🧤")
st.write("코디가 어렵다면 참고해 보세요!")

# 정보 입력
gender = st.selectbox(
    "성별을 선택해 주세요",
    ("여자", "남자", "선택 안 함"),
)

age = st.selectbox(
    "연령대를 선택해 주세요",
    ("20대 초반", "20대 중반", "20대 후반", "30대 초반", "30대 중반", "30대 후반"),
)

season = st.selectbox(
    "계절을 선택해 주세요",
    ("봄", "여름", "가을", "겨울"),
)

# 선택 리스트
style_options = [
    "데이트룩", "하객룩", "여행", "꾸안꾸",
    "페미닌룩", "캐주얼", "오피스", "빈티지",
    "직접 입력하기"
]

# 멀티 선택 박스
style_selected = st.multiselect(
    "추구하는 스타일을 선택해 주세요",
    style_options
)

# 직접 입력 옵션 처리
custom_text = None
if "직접 입력하기" in style_selected:
    custom_text = st.text_input("원하는 스타일을 직접 입력해 주세요")

final_styles = [s for s in style_selected if s != "직접 입력하기"]
if custom_text:
    final_styles.append(custom_text)

# 버튼 클릭
if st.button("코디 추천받기"):

    st.info("✨ 코디 생성 중입니다. 잠시만 기다려 주세요...")

    # 1) GPT에게 코디 설명 + 검색 키워드만 생성하도록 요청
    prompt = f"""
너는 2024–2025 패션 트렌드를 모두 알고 있는 전문 스타일리스트 + 쇼핑 어시스턴트야.

[사용자 조건]
- 성별: {gender}
- 연령대: {age}
- 계절: {season}
- 스타일: {final_styles}

[코디 규칙]
1) 2024–2025 최신 트렌드 반영 (한국 패션 기준)
2) 상의 / 하의 / 아우터 / 신발 / 가방 / 악세서리까지 전신 코디를 구체적으로 구성
3) 컬러 조합 + 실루엣 + 소재 + 길이감까지 디테일하게 설명
4) 실제 착용 가능한 현실적 코디로 자연스럽게 구성
5) 전체 분위기 1줄 요약

[구매처 추천 규칙 — 반드시 포함]
각 아이템별로 아래 중 2~3곳에서만 추천해라:
- 무신사
- 지그재그
- 에이블리

출력 형식은 아래처럼 고정한다:

1) 📌 코디 설명  
   (디테일하게 작성)

2) ✨ 분위기 한 줄 요약

3) 🛍️ 구매처(쇼핑몰) 추천  
   - 상의: 브랜드/상품명 (무신사 검색 링크)  
   - 하의: 브랜드/상품명 (지그재그 검색 링크)  
   - 아우터: 브랜드/상품명 (에이블리 검색 링크)  
   - 신발: 브랜드/상품명 (무신사 검색 링크)  
   - 가방/악세서리: 적절한 쇼핑몰 검색 링크  
   “검색 링크는 실제 키워드 검색이 되는 URL로 생성”

검색 링크 예시:
- 무신사: https://www.musinsa.com/search/musinsa?q=니트+집업  
- 지그재그: https://www.zigzag.kr/search?keyword=와이드+슬랙스  
- 에이블리: https://www.a-bly.com/search?keyword=미니멀+코트  

위 예시처럼 ‘keyword=키워드’ 형태로 생성해서 클릭 시 실제 검색 결과가 나오도록 구성한다.
이미지 검색 키워드는 한국인 모델이 등장하는 트렌디한 스트릿/데일리 패션 중심으로 구성해라.
"""


    gpt = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )

    response_text = gpt.choices[0].message.content
    st.markdown(response_text)
