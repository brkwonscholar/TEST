import os
from openai import OpenAI
import streamlit as st

os.environ["OPENAI_API_KEY"] = st.secrets['API_KEY']
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

# 앱 제목
st.title("화장품 추천💅💄")

# 재료 입력 받기

tone = st.selectbox(
    "당신의 퍼스널 컬러는?",
    ("봄 웜톤🌸", "여름 쿨톤💧", "가을 웜톤🍁","겨울 쿨톤❄️"),
)


skin_type = st.radio(
    "당신의 피부 타입은?",
    ["건성", "지성", "복합성","민감성","중성"],
    captions=[
        "피지 분비량이 적고 건조한 타입.",
        "피지와 유분 분비량이 많은 타입.",
        "한 피부 권역에 건성 부위와 지성 부위가 동시에 존재하는 타입.",
        "정상인 피부보다 더 민감하게 반응하여 자극반응이나 피부염을잘 일으키는 타입",
        "유분과 수분이 적당히 균형을 이루는 피부타입"
    ],
)

option = st.selectbox(
    "당신이 추천받고 싶은 화장품 종류를 선택하세요",
    ("파운데이션(쿠션)", "섀도우", "블러셔","립"),
)

price = st.slider("원하는 가격대를 설정하세요(단위:원)", 1000, 100000, (10000, 50000))


if st.button("화장품 추천 받기"):
        chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": tone, 
            },
            {
                "role": "user",
                "content": skin_type,
            },
            {
                "role": "user",
                "content": option,
            },
            {
                "role": "user",
                "content": str(price), 
            },
            {
                "role": "system",
                "content": "넌 화장품, 퍼스널 컬러 전문가야 입력받은 정보를 기반으로 화장품 자세히 상호 명까지 3개 추천해주고 구매할 수 있는 링크도 줘",
            }
        ],
        model="gpt-4o",
    )

        st.write(chat_completion.choices[0].message.content)
