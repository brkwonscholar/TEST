import streamlit as st
from openai import OpenAI
import json

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

st.title("테마별 랜덤 미국 주식 추천")

themes = ["AI", "반도체", "자동차", "2차전지", "빅테크", "우량주", "배당주","SNS/소셜미디어","우주항공","의류","바이오"]

selected_theme = st.selectbox("테마 선택", themes)
btn = st.button("🎲 추천받기")

def get_stock(theme):
    prompt = f"""
다음 조건을 만족하는 미국 상장기업을 1개 랜덤으로 추천해줘.

- 테마: {theme}
- 미국 증시에 상장된 기업일 것 (NYSE 또는 NASDAQ 위주)
- 가능하면 한국 토스증권이나 국내 증권사 앱에서 자주 보이는 유명 종목일 것
- 회사 이름은 '국내 증권사에서 보이는 한글 이름 + 영문 이름' 형태로 써줘.
  예시: "엔비디아(NVIDIA)", "애플(Apple)", "마이크로소프트(Microsoft)"

반드시 아래 JSON 형식으로만 출력해줘. 다른 문장은 쓰지 마.

예시 형식:
{{
  "company": "NVIDIA",
  "display_name": "엔비디아(NVIDIA)",
  "ticker": "NVDA",
  "why": "AI용 GPU를 만들어서 AI 테마와 잘 맞는다.",
  "what": "이 회사가 어떤 사업을 하는지, 대학생 새내기가 이해할 수 있는 쉬운 말로 3~4문장.",
  "strengths": [
    "회사/비즈니스 모델의 장점 2~3개 bullet",
    "예: AI 성장과 함께 수요가 늘어날 가능성"
  ],
  "risks": [
    "투자 시 고려해야 할 리스크 2~3개 bullet",
    "예: 주가 변동성이 크고 밸류에이션이 높다"
  ],
  "risk_score": 3
}}

여기서 risk_score는 1~5 사이의 정수로,
- 1은 리스크 낮음
- 5는 리스크 매우 높음
을 의미하게 해줘.
"""

    res = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
    )

    content = res.choices[0].message.content.strip()
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        data = {
            "company": "파싱 오류",
            "display_name": "파싱 오류",
            "ticker": "",
            "why": "GPT 응답을 JSON으로 변환하는 데 실패했습니다.",
            "what": content,
            "strengths": [],
            "risks": [],
            "risk_score": 3,
        }
    return data

if btn:
    with st.spinner("추천 중..."):
        result = get_stock(selected_theme)

    company = result.get("company", "")
    display_name = result.get("display_name", company)
    ticker = result.get("ticker", "")

    raw_score = result.get("risk_score", 3)
    try:
        score_int = int(round(float(raw_score)))
    except Exception:
        score_int = 3
    score_int = max(1, min(5, score_int))  

    stars = "★" * score_int + "☆" * (5 - score_int)

    st.subheader(f"✨ 추천 종목: {display_name} ({ticker})")
    st.caption(f"선택한 테마: {selected_theme}")

    st.write(f"**투자 리스크:** {stars} ({score_int}/5)")

    st.write(f"**왜 이 테마에 맞나?**")
    st.write(result.get("why", ""))

    st.write("**이 회사는 어떤 회사인가요?**")
    st.write(result.get("what", ""))

    strengths = result.get("strengths", [])
    risks = result.get("risks", [])

    if strengths:
        st.write("**장점(Strengths):**")
        for s in strengths:
            st.markdown(f"- {s}")

    if risks:
        st.write("**리스크(Risks):**")
        for r in risks:
            st.markdown(f"- {r}")

    st.info("※ 이 정보는 공부용 참고용일 뿐, 실제 투자 판단은 반드시 본인이 직접 확인하고 결정해야 합니다.")
else:
    st.info("먼저 테마를 고르고, **🎲 추천받기** 버튼을 눌러보세요!")
