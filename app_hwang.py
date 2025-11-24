import os
from openai import OpenAI
import streamlit as st

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

# 페이지 설정
st.set_page_config(page_title="마케팅 문구 생성기", layout="centered")

# CSS 스타일 정의
st.markdown("""
<style>

* {
    font-family: 'Pretendard', sans-serif !important;
}

/* 전체 배경 */
body {
    background-color: #E8F8F5; /* 파스텔 민트 배경 */
}

/* 메인 컨테이너 */
.block-container {
    padding-top: 2.5rem;
}

/* 제목 */
h1 {
    text-align: center;
    font-weight: 800;
    color: #2F5753;
}

/* 설명 문구 */
.sub-text {
    text-align: center;
    font-size: 1.05rem;
    color: #497D76;
    margin-bottom: 1.5rem;
}

/* 입력창 */
input[type="text"] {
    border-radius: 12px;
    border: 1px solid #C7E7E2;
    padding: 12px;
    background-color: #F6FFFD;
}

/* 버튼 */
div.stButton > button:first-child {
    background: linear-gradient(135deg, #A8EDE0, #7ED9C6);
    color: #043B35;
    border-radius: 12px;
    padding: 0.8rem 1.3rem;
    font-size: 1.1rem;
    font-weight: 600;
    border: none;
    transition: 0.25s ease;
    box-shadow: 0px 4px 10px rgba(126, 217, 198, 0.35);
}

div.stButton > button:hover {
    background: linear-gradient(135deg, #7ED9C6, #5AC4AE);
    transform: translateY(-2px);
}

/* 출력 박스 */
.output-box {
    background: #FFFFFF;
    padding: 24px;
    border-radius: 16px;
    border: 1px solid #D9F2ED;
    margin-top: 20px;
    font-size: 1.15rem;
    line-height: 1.6;
    color: #2F5753;
    box-shadow: 0px 6px 15px rgba(150, 225, 210, 0.25);
}

</style>
""", unsafe_allow_html=True)

# ---- UI 타이틀 ----
st.title(" 마케팅 문구 생성기 ")
st.markdown("<p class='sub-text'> 누구나 쉽게 만들 수 있어요 ✨</p>", unsafe_allow_html=True)

# ---- 기능 함수 ----
def generate_copy(product, tone, platform):
    prompt = f"""
다음 조건에 맞는 귀여우면서도 세련된 마케팅 카피를 작성해줘.

- 제품: {product}
- 말투: {tone}
- 플랫폼: {platform}

파스텔톤 감성에 맞춰서 부드럽고 따뜻한 어조로 작성해줘.
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

# ---- 입력 영역 ----
st.subheader("🧸 제품 정보 입력하기")

product = st.text_input("-- 제품 이름")
tone = st.text_input("-- 말투 (예: 귀여운, 감성적, 전문적, 유머 등)")
platform = st.text_input("-- 플랫폼 (예: 인스타그램, 블로그, 쇼핑몰 등)")

# ---- 실행 버튼 ----
if st.button("🎁 문구 생성하기"):
    if not product or not tone or not platform:
        st.warning("모든 항목을 입력해주세요 !")
    else:
        try:
            output = generate_copy(product, tone, platform)
            st.success("완성됐어요! ✨")

            st.markdown(f"""
            <div class="output-box">
            {output}
            </div>
            """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"오류 발생: {e}")





