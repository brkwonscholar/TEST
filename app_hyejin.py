import os
from openai import OpenAI
import streamlit as st

# Streamlit secrets에서 API 키 불러오기
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

def ai_generate(prompt: str) -> str:
    """프롬프트를 보내고 AI 응답을 받는 함수"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "너는 티 소믈리에이자 사용자 경험 전문가야."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=400,
    )
    return response.choices[0].message.content


def main():
    st.title("나에게 맞는 차 추천 프로그램🍵")

    # 세션 상태 기본값 설정
    if "main_part" not in st.session_state:
        st.session_state["main_part"] = ""
    if "similar_part" not in st.session_state:
        st.session_state["similar_part"] = ""
    if "show_similar" not in st.session_state:
        st.session_state["show_similar"] = False

    # ------------------------
    # Q1. 커피 마시는지 여부
    # ------------------------
    st.subheader("Q1. 평소에 커피를 즐겨 마시나요?")
    drink_coffee = st.radio("선택해 주세요.", ["예", "아니오"])

    coffee_type = ""
    taste_type = ""

    # ------------------------
    # Q1-1 / Q1-2 분기
    # ------------------------
    if drink_coffee == "예":
        st.subheader("Q1-1. 어떤 커피를 가장 자주 즐기시나요?")
        coffee_type = st.selectbox(
            "자주 마시는 커피를 선택해 주세요.",
            [
                "아메리카노",
                "아이스 아메리카노",
                "우유가 들어간 커피(라떼·카푸치노)",
                "달달한 커피(바닐라라떼·모카 등)",
                "디카페인 커피",
            ],
        )
    else:
        st.subheader("Q1-2. 평소에는 어떤 음료를 가장 자주 마시나요?")
        taste_type = st.selectbox(
            "가장 자주 마시는 음료를 선택해 주세요.",
            [
                "물·보리차 같은 담백한 음료",
                "과일주스·에이드 같은 상큼한 음료",
                "초코·딸기라떼 같은 달달한 우유 음료",
                "탄산음료·스파클링 같은 톡쏘는 음료",
                "허브티·전통차를 가끔 마신다",
            ],
        )

    # ------------------------
    # Q2. 주효과 선택
    # ------------------------
    st.subheader("Q2. 지금 차를 마시고 싶은 '가장 큰 이유'는 무엇인가요?")
    effect_options = [
        "수면 개선",
        "스트레스 완화",
        "체온 상승",
        "소화 개선",
        "갈증 해소",
        "집중력 증가",
        "잘 모르겠어요"
    ]
    effect = st.selectbox(
        "가장 우선순위가 높은 효과를 하나 골라주세요.",
        effect_options,
    )

    # ------------------------
    # Q2-1. 효과 상세 질문 (선택적으로)
    # ------------------------
    effect_detail = ""

    if effect == "수면 개선":
        st.subheader("Q2-1. 어떤 이유 때문에 잠이 잘 오지 않나요?")
        effect_detail = st.selectbox(
            "가장 가까운 이유를 골라주세요.",
            [
                "불안하거나 생각이 많아서 잠이 안 온다",
                "머리나 목, 어깨가 긴장되고 아파서 잠이 안 온다",
                "늦은 시간 카페인 섭취 때문에 잠이 안 온다",
                "몸은 피곤한데 신경이 예민해서 잠이 안 온다",
                "이유는 잘 모르지만 자꾸 뒤척이게 된다",
            ],
        )
    elif effect == "스트레스 완화":
        st.subheader("Q2-1. 요즘 가장 크게 느끼는 스트레스는 어떤가요?")
        effect_detail = st.selectbox(
            "가장 가까운 상황을 골라주세요.",
            [
                "공부·일 때문에 머리가 너무 복잡하다",
                "사람과의 관계 때문에 감정적으로 지친다",
                "몸이 너무 피곤하고 기운이 없어서 스트레스를 느낀다",
                "긴장·압박감이 심해서 마음이 편하지 않다",
            ],
        )
    elif effect == "소화 개선":
        st.subheader("Q2-1. 어떤 소화 불편이 가장 신경 쓰이나요?")
        effect_detail = st.selectbox(
            "가장 자주 느끼는 증상을 골라주세요.",
            [
                "식사 후에 속이 더부룩하고 답답하다",
                "속이 쓰리거나 위산이 올라오는 느낌이 난다",
                "배가 무겁고 소화가 잘 안 되는 느낌이다",
                "전체적으로 체한 것처럼 불편하다",
            ],
        )

    st.markdown("---")

    # ------------------------
    # 버튼 클릭 시 AI 추천
    # ------------------------
    if st.button("AI에게 추천받기"):
        # 상세 정보가 없을 수도 있으니 기본값 처리
        effect_detail_text = effect_detail if effect_detail else "추가 설명 없음"

        user_desc = f"""
        커피를 마시나요? → {drink_coffee}
        즐겨 마시는 커피 종류 → {coffee_type}
        커피를 마시지 않는다면 음료 취향 → {taste_type}
        가장 원하는 주효과 → {effect}
        효과에 대한 추가 설명 → {effect_detail_text}
        """

        prompt = f"""
        너는 티 소믈리에이자 사용자 경험 전문가야.

        아래 사용자 정보를 보고, 이 사람에게 어울리는 대표 차 1가지를 선택해서
        보기 편한 '카드형'으로 짧고 핵심만 소개해줘.
        그리고 마지막에 그 차와 비슷하게 즐길 수 있는 다른 차 1~2가지를
        "비슷한 차 추천" 목록으로 알려줘.

        반드시 아래 형식을 지켜서 한국어로 마크다운 형식으로 작성해.

        ### 🍵 대표 추천 차: [차 이름]

        **📌 추천 이유**  
        - 사용자가 선택한 주효과 '{effect}'과(와) 효과에 대한 추가 설명 '{effect_detail_text}'을(를) 참고해서 1~2문장으로 설명
        - 만약 효과에 대한 추가 설명이 '추가 설명 없음'이라면, 주효과만 자연스럽게 반영해서 설명

        **🌼 맛**  
        - 이 차를 처음 마셔보는 사람도 상상할 수 있도록 1문장으로 설명

        **🔥 따뜻하게 마시는 법**  
        - 물 온도 / 우리기 시간 / 마시기 좋은 상황을 1~2문장으로 설명

        **❄️ 아이스로 마시는 법**  
        - 어떻게 아이스로 만들면 좋은지, 어떤 상황에 어울리는지 1~2문장으로 설명

        **💡 초보자 팁**  
        - 차를 처음 마시는 사람을 위한 간단한 팁 1문장

        ## 비슷한 차 추천

        - 🍵 차 이름 1: 이 차의 맛과 향을 1문장으로만 설명 (효능 말하지 말기)
        - 🍵 차 이름 2: 이 차의 맛과 향을 1문장으로만 설명 (효능 말하지 말기)

        지켜야 할 조건:
        - 각 항목은 반드시 1~2문장 안으로만 작성해. 절대로 3문장 이상 쓰지 마.
        - 비슷한 차 부분에서는 효능·건강 효과를 설명하지 말고, 오직 맛과 향 느낌만 1문장으로 적어라.
        - 전체 글이 부담스럽지 않도록, 짧고 선명하게 표현해라.
        - 차를 잘 모르는 고등학생도 이해할 수 있을 만큼 쉽게 적어라.
        - 마크다운 제목(###, ##)과 굵은 글씨(**텍스트**)를 그대로 사용해라.

        사용자 정보:
        {user_desc}
        """

        # ✅ 단계별 로딩 표시: st.status 사용
        with st.status("🌿 당신에게 맞는 차를 고르는 중입니다...", expanded=True) as status:
            status.update(label="🌿 취향과 원하는 효과를 분석하는 중이에요...", state="running")
            result = ai_generate(prompt)

            status.update(label="🍵추천 결과를 정리하는 중입니다...", state="running")

            # 대표 차 / 비슷한 차 분리
            main_part = result
            similar_part = ""

            marker = "## 비슷한 차 추천"
            if marker in result:
                parts = result.split(marker, 1)
                main_part = parts[0].strip()
                similar_part = (marker + "\n" + parts[1].strip()).strip()

            # 세션에 저장
            st.session_state["main_part"] = main_part
            st.session_state["similar_part"] = similar_part
            st.session_state["show_similar"] = False

            status.update(label="✅ 추천이 완료되었습니다!", state="complete", expanded=False)

    # ------------------------
    # 2단계: 대표 차 출력 (세션에 값이 있을 때)
    # ------------------------
    if st.session_state["main_part"]:
        st.subheader("오늘의 대표 추천 차")
        st.markdown(st.session_state["main_part"])

    # ------------------------
    # 3단계: 비슷한 차 - 버튼 눌렀을 때만 펼치기
    # ------------------------
    if st.session_state["similar_part"]:
        # 비슷한 차 더 보기 버튼 (토글 기능)
        if st.button("비슷한 차 더 보기", key="show_similar_button"):
            st.session_state["show_similar"] = not st.session_state["show_similar"]

        # 버튼을 눌렀을 때만 내용 표시
        if st.session_state["show_similar"]:
            st.markdown(st.session_state["similar_part"])


if __name__ == "__main__":
    main()
