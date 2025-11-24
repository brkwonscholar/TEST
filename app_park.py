import streamlit as st
from openai import OpenAI

# ------------------------------------------------
# Streamlit 상태 초기화
# ------------------------------------------------
if 'selected_mbti' not in st.session_state:
    st.session_state.selected_mbti = None
if 'ai_profile' not in st.session_state:
    st.session_state.ai_profile = None

# ------------------------------------------------
# 사용자 프로필 설정 및 UI
# ------------------------------------------------

st.title("TYPEN: MBTI 빅데이터 기반 맞춤형 도서 큐레이터") 
st.header("프로필 설정")

# --- API 키 설정 (Secrets 사용) ---
# 에러 방지를 위한 안전한 키 가져오기 로직
# 1. Secrets에 'OPENAI_API_KEY'가 있는지 확인
if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
    client = OpenAI(api_key=api_key)
# 2. 혹시 사용자가 'API_KEY'라고 저장했을 경우를 대비 (호환성)
elif "API_KEY" in st.secrets:
    api_key = st.secrets["API_KEY"]
    client = OpenAI(api_key=api_key)
else:
    # 키가 아예 없을 경우 에러 메시지
    st.error("🚨 API 키를 찾을 수 없습니다. Streamlit Secrets에 'OPENAI_API_KEY'를 등록해주세요.")
    st.stop()

# 사용자 이름 입력
title = st.text_input("**당신의 이름을 작성해주세요**", "") 

if title:
    st.write("네. 다음단계를 진행해주세요.", title, "님")
else:
    st.write("이름을 작성하고 엔터를 눌러주세요.")

# 성별 선택
gender = st.radio(
    "**당신의 성별을 선택하세요 👇**",
    ["여성", "남성", "기타"],
    horizontal=True
)
st.write("**선택한 성별:**", gender)

# 출생연도 선택
birth_year = st.selectbox(
    "**당신의 출생연도를 선택해주세요 👇**",
    options=list(range(1900, 2026)), 
    index=100 
)
st.write("선택한 출생연도:", birth_year)

# MBTI 목록 정의
mbti_types = [
    ["ENFJ", "ENFP", "INFJ", "INFP"],
    ["ESTJ", "ESFJ", "ISTJ", "ISFJ"],
    ["ENTJ", "ENTP", "INTJ", "INTP"],
    ["ESTP", "ESFP", "ISTP", "ISFP"]
]
st.markdown("---")

st.write("**당신의 MBTI 유형을 선택하세요**")

# MBTI 4x4 그리드 레이아웃 구현
for row in mbti_types:
    cols = st.columns(4) 
    
    for i, mbti in enumerate(row):
        with cols[i]:
            if st.button(mbti, key=f"mbti_btn_{mbti}", use_container_width=True):
                st.session_state.selected_mbti = mbti

st.info('**잠깐, MBTI 유형을 모르신다면?**\n\n원할한 검사를 위해 하단 버튼을 눌러 MBTI 검사를 진행해주세요', icon="ℹ️")
st.link_button("MBTI 유형 검사 링크", "https://www.16personalities.com/ko/%EB%AC%B4%EB%A3%8C-%EC%84%B1%EA%B2%A9-%EC%9C%A0%ED%98%95-%EA%B2%80%EC%82%AC") 

# 선택 결과 표시
if st.session_state.selected_mbti:
    st.success(f"✅ 선택된 MBTI: **{st.session_state.selected_mbti}**")


# (선택 사항) CSS 스타일링
st.markdown("""
<style>
/* MBTI 버튼 스타일링 */
div.stButton > button {
    border-radius: 10px; 
    border-width: 1px;
    font-weight: bold; 
    height: 60px; 
    transition: all 0.2s;
}
</style>
""", unsafe_allow_html=True)

st.markdown("---")

# 선호 독서 장르 입력
genre = st.text_input("**선호 독서 장르를 작성해주세요. (예: 판타지, 자기계발, 역사)**", "") 

if genre:
    st.write("선호장르가", genre, "인것을 확인했습니다.")
    
st.info('**AI기반 장르분석**\n\nAI가 사용자님의 선호 장르를 분석하여 맞춤형 독서 리포트를 제공합니다. 다양한 장르를 입력할수록 더욱 다양하고 정확한 추천을 받을 수 있습니다.', icon="ℹ️")
st.markdown("---")

# 독서 시간 선택
reading_time_options = [f"{i}시간" for i in range(1, 31)]
reading_time = st.select_slider( 
    "**일주일에 몇 시간 정도 독서할 수 있나요? (최대 30시간)**",
    options=reading_time_options,
    value="5시간" # 기본값 설정
)

if st.button("독서 시간 확정"):
    if title:
        st.write(f"**{title}**님의 일주일 중 독서 할애 가능 시간은 **{reading_time}**이군요!")
    else:
        st.warning("이름을 먼저 입력해주세요.")


# 선호 독서 시간대 선택
st.markdown("---")
st.write("**주로 독서하는 시간대는 언제인가요?**")

options = ["아침","점심","오후","저녁","밤","새벽"]
if hasattr(st, "pills"): 
    selection = st.pills("선호하는 독서 시간대", options, selection_mode="multi")
else:
    selection = st.multiselect("선호하는 독서 시간대(다중선택 가능)", options)

reading_period = ', '.join(selection) if selection else '정보 없음'
st.markdown(f"**선택한 시간대:** {reading_period}")

# -------------------------------
# 📚 AI 독서 프로필 생성 기능
# -------------------------------

st.markdown("---")
st.header("📚 나의 독서 프로필 생성하기")

if st.button("AI 독서 프로필 생성하기"):
    if not title or not st.session_state.selected_mbti or not genre:
        st.warning("⚠️ 이름, MBTI, 선호 장르를 모두 입력해야 프로필을 생성할 수 있습니다.")
    else:
        with st.spinner("AI가 당신의 독서 성향을 분석 중입니다... ⏳"):
            # 텍스트 포맷 오류 해결을 위해 HTML 스타일 및 일반 텍스트 강제
            prompt_profile = f"""
            당신은 MBTI, 독서 습관, 성격 분석 전문가입니다.
            아래 사용자의 데이터를 기반으로 개인 맞춤형 독서 프로필을 작성하세요.

            [사용자 정보]
            - 이름: {title}
            - 성별: {gender}
            - 출생연도: {birth_year}
            - MBTI: {st.session_state.selected_mbti}
            - 선호 장르: {genre}
            - 일주일 독서 시간: {reading_time}
            - 선호 독서 시간대: {reading_period}

            [작성 지침]
            1. 성격적 독서 스타일, 몰입 패턴, 추천 도서 유형을 분석하세요.
            2. **절대로 Markdown 문법 (볼드체, 헤더, 리스트 등)을 사용하지 마세요.** 오직 일반 텍스트와 이모지만 사용해야 합니다.
            3. 모든 내용은 얇고 작은 일반 텍스트로만 작성합니다.

            출력 형식 (이 형식만 사용하고 추가적인 설명이나 인사말은 제외):
            ---
            <h4 style='font-size: 20px;'>📖 {title}님의 독서 프로필 기반 분석 리포트</h4>
            
            <p style='font-weight: bold;'>💡 성격 기반 독서 스타일:</p> [여기에 분석 내용을 일반 텍스트로 작성]
            
            <p style='font-weight: bold;'>✨ 몰입 패턴 및 추천 포인트:</p> [여기에 분석 내용을 일반 텍스트로 작성]
            
            <p style='font-weight: bold;'>📚 추천 도서 유형:</p> [여기에 분석 내용을 일반 텍스트로 작성. 큰 글씨를 사용하지 마세요.]
            ---
            """
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "당신은 독서 성향 분석 전문가입니다. 출력 지침을 엄격히 따르세요. **Markdown 문법 사용을 금지하며**, HTML 태그를 사용하여 지정된 포맷으로 출력하세요."},
                        {"role": "user", "content": prompt_profile},
                    ],
                    temperature=0.8,
                    max_tokens=500
                )
                
                ai_profile_content = response.choices[0].message.content
                st.session_state.ai_profile = ai_profile_content
                st.success("✨ 맞춤형 독서 프로필이 생성되었습니다!")
                
            except Exception as e:
                st.error(f"프로필 생성 중 오류가 발생했습니다: {e}")

# -------------------------------
# 🎨 독서 프로필 출력
# -------------------------------
if st.session_state.ai_profile:
    st.markdown("---")
    st.markdown("### 생성된 독서 프로필")
    st.markdown(st.session_state.ai_profile, unsafe_allow_html=True) # HTML 렌더링을 위해 True 설정


# -------------------------------
# 📖 AI 기반 도서 추천 기능
# -------------------------------

st.markdown("---")
st.header("📖 AI 기반 개인 맞춤 도서 추천")

if st.button("📚 AI 도서 추천 받기"):
    if not st.session_state.ai_profile:
        st.warning("⚠️ 먼저 'AI 독서 프로필 생성하기' 버튼을 눌러 프로필을 생성해야 합니다.")
    else:
        with st.spinner("AI가 당신에게 맞는 책을 고르고 있어요... ⏳"):
            prompt_recommendation = f"""
            당신은 전문 북 큐레이터이자 성격 분석 전문가입니다.
            아래 사용자의 정보와 독서 프로필을 기반으로, 한국에서 구매 가능한 도서 3권을 추천하세요.

            [사용자 정보]
            - MBTI: {st.session_state.selected_mbti}
            - 선호 장르: {genre}

            [출력 형식 지침]
            - 추천 도서는 3권입니다.
            - 추천할 책의 제목을 정한 뒤, **해당 책의 실제 표지 이미지**를 반드시 찾으세요.
            - 각 책은 다음 Markdown 및 img 형식으로 출력해야 합니다.

            ### 1. [책 제목]
            <img src="[웹브라우저에서 검색해 찾은 해당 책의 실제 표지 이미지]" style="border-radius: 8px; width: 150px; height: 200px; display: block;">
            - 작가: [작가 이름]
            - 출판사: [출판사 이름]
            - 추천 이유: [사용자 MBTI와 독서 성향을 고려한 구체적인 추천 이유 설명]

            ### 2. [책 제목]
            <img src="[웹브라우저에서 검색해 찾은 해당 책의 실제 표지 이미지]]" style="border-radius: 8px; width: 150px; height: 200px; display: block;">
            - 작가: [작가 이름]
            - 출판사: [출판사 이름]
            - 추천 이유: [추천 이유 설명]

            ### 3. [책 제목]
            <img src="[웹브라우저에서 검색해 찾은 해당 책의 실제 표지 이미지]" style="border-radius: 8px; width: 150px; height: 200px; display: block;">
            - 작가: [작가 이름]
            - 출판사: [출판사 이름]
            - 추천 이유: [추천 이유 설명]

            - 오직 추천 결과만 출력하세요. 다른 인사말이나 설명은 절대 포함하지 마세요.
            """

            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "당신은 전문 도서 큐레이터입니다. 추천할 책의 실제 표지 이미지를 웹 검색을 통해 찾고 이후 그 이미지를 img 형태로 삽입하면서 사용자에게 3권을 추천해야 합니다."},
                        {"role": "user", "content": prompt_recommendation},
                    ],
                    temperature=0.9,
                    max_tokens=800,
                )

                st.success("✨ AI 도서 추천이 완료되었습니다!")
                st.markdown(response.choices[0].message.content, unsafe_allow_html=True) 
            except Exception as e:
                st.error(f"도서 추천 중 오류가 발생했습니다: {e}")
