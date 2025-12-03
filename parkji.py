import streamlit as st
from openai import OpenAI
from urllib.parse import quote  # ✅ 주소 인코딩용

# ✅ OpenAI 클라이언트 초기화
client = OpenAI(api_key=st.secrets["API_KEY"])

# 🌸 페이지 기본 설정
st.set_page_config(
    page_title="AI 약 추천 & 근처 약국 찾기 💊",
    page_icon="💊",
    layout="centered"
)

# 🎨 스타일 꾸미기
st.markdown("""
    <style>
    body {
        background-color: #f9fbfc;
        font-family: "Apple SD Gothic Neo", sans-serif;
    }
    .main-title {
        text-align: center;
        color: #2a4d69;
        font-size: 34px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .sub-text {
        text-align: center;
        color: #555;
        font-size: 16px;
        margin-bottom: 30px;
    }
    .stButton>button {
        background-color: #6fa8dc;
        color: white;
        border-radius: 10px;
        height: 3em;
        width: 100%;
        font-size: 17px;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #5b8ac4;
    }
    .stTextInput>div>div>input {
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# 🩺 제목
st.markdown('<div class="main-title">AI 약 추천 도우미 💊</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-text">증상을 입력하면 관련 약품과 복용 팁을 알려드리고,<br>근처 약국까지 바로 연결해드려요!</div>', unsafe_allow_html=True)

# ✍️ 입력 섹션
symptom = st.text_input("😷 증상을 입력해주세요 (예: 감기, 생리통, 소화불량 등)")
age_group = st.selectbox("👶 연령대를 선택해주세요", ["소아", "청소년", "성인", "노인"])
location = st.text_input("📍 위치를 입력해주세요 (예: 광주광역시 동구 서석동)")

# 🚀 버튼 클릭 시 실행
if st.button("💡 추천 받기"):
    if not symptom:
        st.warning("⚠️ 증상을 입력해주세요!")
    else:
        with st.spinner("AI가 약을 추천 중입니다... 💊"):
            prompt = f"""
            증상: {symptom}
            연령대: {age_group}

            위 정보를 바탕으로,
            1. 약국에서 쉽게 구할 수 있는 일반의약품 3가지를 추천하고
            2. 각 약의 효능, 복용법, 주의사항을 한국어로 예쁘게 정리해줘.
            """

            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}]
                )

                answer = response.choices[0].message.content
                st.success("💊 AI 약 추천 결과")
                st.markdown(answer)

                if location:
                    encoded_loc = quote(location + " 약국")  # ✅ 공백/한글 인코딩
                    st.markdown("---")
                    st.markdown("📍 **근처 약국 바로가기**")
                    st.markdown(f"[🗺️ {location} 주변 약국 보기 (네이버지도)](https://map.naver.com/v5/search/{encoded_loc})")

            except Exception as e:
                st.error(f"🚨 오류 발생: {e}")

# 🌷 푸터
st.markdown("""
    <br><br>
    <div style='text-align:center; color:#95A5A6; font-size:14px;'>
    © 2025 💊 AI 약 추천 도우미 | 제작: ChatGPT & 지효 🌷
    </div>
""", unsafe_allow_html=True)
