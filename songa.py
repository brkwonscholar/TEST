import os
from openai import OpenAI

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

import streamlit as st


# 앱 제목
st.title("나만의 레시피를 소개합니다")

# 재료 입력 받기
food = st.text_input("어떤 재료를 가지고 계십니까?")

# 재료 출력 
if st.button("레시피 생성하기"):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": food,
            },
            { 
            "role": "user"
            "content": "입력받은 재료로 할 수 있는 맛있는 요리 레시피를 알려줘",
            }   
        ],
        model="gpt-4o",
    )

    result = chat_completion.choices[0].message.content
    st.write(title)