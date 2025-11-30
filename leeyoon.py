import streamlit as st
from openai import OpenAI

# -----------------------------
# OpenAI API 키 설정
# -----------------------------
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# -----------------------------
# 페이지 설정
# -----------------------------
st.set_page_config(page_title="AI 루틴 추천 & 회고", layout="wide")
st.title("🧠 오늘의 AI 시간대별 루틴 추천 & 회고")

# -----------------------------
# 사용자 입력
# -----------------------------
st.header("1️⃣ 현재 상태 입력")
emotion = st.selectbox("현재 기분을 선택하세요", ["😃 기쁨", "😐 보통", "😢 슬픔", "😡 화남", "😴 피곤"])
energy = st.slider("현재 에너지 수준 (1-10)", 1, 10, 5)

# -----------------------------
# 시간대별 루틴 추천
# -----------------------------
st.header("2️⃣ 오늘의 시간대별 추천 루틴")

if st.button("추천 받기"):
    prompt = f"""
    사용자의 감정은 '{emotion}'이고 에너지 수준은 {energy}입니다.

    오늘 하루를 다음 4개 시간대로 나누어:
    - 아침(06~10)
    - 점심(11~14)
    - 오후(15~18)
    - 저녁(19~22)

    각 시간대에 적합한 활동 1~2개씩 추천하고
    짧은 이유도 설명해줘.
    bullet 형식으로 출력.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "당신은 루틴 추천 전문가입니다."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=500
        )

        # 최신 SDK: message["content"] 로 접근
        result = response.choices[0].message["content"]
        st.success(result)

    except Exception as e:
        st.error(f"추천 루틴 생성 중 오류 발생: {e}")

# -----------------------------
# 하루 회고
# -----------------------------
st.header("3️⃣ 하루 회고")
today_feedback = st.text_area("오늘 하루를 돌아보며 느낀 점과 성장을 입력하세요.")

if st.button("회고 저장"):
    if today_feedback.strip() == "":
        st.warning("회고 내용을 입력해주세요.")
    else:
        st.success("회고가 저장되었습니다!")

# -----------------------------
# AI 회고 분석
# -----------------------------
st.header("4️⃣ AI 피드백")

if today_feedback:
    feedback_prompt = f"""
    사용자가 작성한 회고: {today_feedback}

    1) 오늘 잘한 점
    2) 개선할 점
    3) 내일 적용 가능한 시간대별 루틴

    위 내용을 정리해서 출력하세요.
    """

    try:
        feedback_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": feedback_prompt}
            ],
            max_tokens=400
        )

        feedback_result = feedback_response.choices[0].message["content"]
        st.info(feedback_result)

    except Exception as e:
        st.error(f"AI 피드백 생성 중 오류 발생: {e}")


