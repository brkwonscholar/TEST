import os
from openai import OpenAI
import streamlit as st

# 🔧 페이지 기본 설정
st.set_page_config(
    page_title="AI 스포츠 자세 코치",
    page_icon="🏋️",
    layout="centered"
)

# 🔐 API 키
os.environ["OPENAI_API_KEY"] = st.secrets['API_KEY']
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# 🎨 간단한 CSS 커스터마이징
st.markdown(
    """
    <style>
    /* 전체 배경 톤 */
    .main {
        background-color: #f5f7fb;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    /* 히어로 카드 */
    .hero-box {
        background: linear-gradient(135deg, #1e90ff, #5ac8fa);
        padding: 1.6rem 1.8rem;
        border-radius: 18px;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 12px 25px rgba(0,0,0,0.12);
    }
    .hero-title {
        font-size: 1.9rem;
        font-weight: 800;
        margin-bottom: 0.3rem;
    }
    .hero-sub {
        font-size: 0.98rem;
        opacity: 0.96;
    }
    /* 입력 섹션 카드 */
    .section-card {
        background-color: white;
        border-radius: 16px;
        padding: 1.4rem 1.5rem;
        box-shadow: 0 6px 16px rgba(0,0,0,0.06);
        margin-bottom: 1.2rem;
    }
    .section-title {
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 0.6rem;
    }
    /* 버튼 스타일 */
    div.stButton > button {
        width: 100%;
        border-radius: 999px;
        font-weight: 600;
        padding-top: 0.6rem;
        padding-bottom: 0.6rem;
        border: none;
    }
    /* 결과 박스 */
    .result-card {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 1.2rem 1.4rem;
        box-shadow: 0 6px 18px rgba(0,0,0,0.08);
        margin-top: 0.8rem;
        margin-bottom: 1.2rem;
    }
    .result-title {
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .small-hint {
        font-size: 0.8rem;
        color: #6b7280;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 🧭 사이드바 – 사용 방법 & 안내
st.sidebar.header("🧾 사용 방법")
st.sidebar.markdown(
    """
1. **운동 종목**을 입력해요.  
   - 예: 런닝, 축구, 스쿼트 위주 헬스 등  
2. **실력 수준**을 선택해요.  
3. **자세가 궁금한 동작 이름**을 적어요.  
4. 👉 `자세 코칭 받기` 버튼을 누르면  
   - 텍스트 코칭 + 자세 이미지가 함께 나와요.
    """
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
⚠️ **주의사항**  
- 실제 통증·부상 시에는  
  **반드시 의료진 / 전문 트레이너와 상담**하세요.
    """
)

# 🧱 상단 히어로 영역
st.markdown(
    """
    <div class="hero-box">
        <div class="hero-title">🏋️ AI 스포츠 자세 코치</div>
        <div class="hero-sub">
            혼자 운동할 때, 내 자세가 맞는지 헷갈릴 때가 많죠?<br>
            종목과 동작만 입력하면, AI 코치가 <b>올바른 자세와 부상 예방법</b>을 안내해 줍니다.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
> ⚠️ 이 서비스는 **의료진·전문 트레이너의 지도를 완전히 대체하지 않습니다.**  
> 참고용 코칭 도구로만 사용해 주세요.
"""
)

# 🔹 입력 섹션
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">① 운동 정보 입력</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    sport = st.text_input("종목", placeholder="예: 런닝, 축구, 야구, 헬스 등")

with col2:
    level = st.selectbox(
        "현재 본인의 수준",
        ["초보", "중급", "상급"],
        index=0  # 기본값: 초보
    )

move = st.text_input(
    "자세가 궁금한 동작",
    placeholder="예: 스쿼트, 인사이드 킥, 투구폼, 런닝 착지 자세 등"
)

st.markdown(
    '<p class="small-hint">💡 구체적으로 적을수록 더 도움이 되는 코칭이 제공됩니다.</p>',
    unsafe_allow_html=True,
)

st.markdown("</div>", unsafe_allow_html=True)  # section-card 끝

# ▶ 버튼 & 결과
clicked = st.button("🏃‍♂️ 자세 코칭 받기")

if clicked:
    if not move.strip():
        st.warning("먼저 **어떤 동작**이 궁금한지 입력해 주세요! 🏃")
    elif not sport.strip():
        st.warning("**종목**도 함께 적어주면 더 정확한 코칭이 가능해요! 🏋️")
    else:
        # 1️⃣ 자세 설명 및 부상 예방법 생성
        chat_completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "너는 스포츠 종목(축구, 야구, 헬스/웨이트 등)을 지도하는 트레이너야. "
                        "사용자가 입력한 동작, 선택한 종목, 난이도 정보를 바탕으로 "
                        "해당 수준에 맞는 현실적인 코칭을 한국어로 제공해.\n\n"
                        "항상 다음 구조로 간단·명확하게 bullet 형식으로 작성해:\n\n"
                        "1. 🔹 동작 개요 (어떤 동작인지 한두 문장으로)\n"
                        "2. ✅ 올바른 기본 자세 (선수나 상급자가 아닌, 사용자의 수준에 맞춰 설명)\n"
                        "3. ⚠️ 자주 나오는 잘못된 자세와 그로 인한 위험성\n"
                        "4. 🛡 부상 예방 팁 (워밍업, 강도/무게 조절, 호흡 등)\n"
                        "5. 🧑‍🎓 현재 난이도 수준에 맞는 연습 방법 또는 쉬운/어려운 변형 동작\n"
                        "6. ❗주의 문장: 통증·부상이 있을 경우 즉시 운동을 중단하고 의료진이나 전문 트레이너에게 상담을 권장한다."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"종목: {sport}\n"
                        f"난이도: {level}\n"
                        f"동작: {move}\n\n"
                        "위 정보를 바탕으로 코칭해줘."
                    ),
                }
            ],
        )

        result = chat_completion.choices[0].message.content

        # 🧾 결과 카드
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.markdown('<div class="result-title">📝 자세 코칭 결과</div>', unsafe_allow_html=True)
        st.markdown(result)
        st.markdown("</div>", unsafe_allow_html=True)

        # 2️⃣ 이미지 생성 (DALL·E 3)
        img_prompt = (
            f"{sport} 종목에서 {move} 동작을 수행하는 사람의 올바른 자세를 보여주는 교육용 일러스트. "
            f"운동 자세 교정용 포스터 스타일, {level} 수준의 운동자를 대상으로 함. "
            "단순하고 선명한 구도, 깨끗한 배경, 고해상도."
        )

        response = client.images.generate(
            model="dall-e-3",
            prompt=img_prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )

        image_url = response.data[0].url

        # 3️⃣ 이미지 표시
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📸 자세 이미지 예시 (참고용)</div>', unsafe_allow_html=True)
        st.image(
            image_url,
            caption=f"[{sport} · {level}] '{move}' 올바른 자세 예시 (AI 생성 이미지, 참고용)",
            use_column_width=True
        )
        st.markdown("</div>", unsafe_allow_html=True)

