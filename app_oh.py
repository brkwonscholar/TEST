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





# 앱 제목
st.title("당신을 위로해 드립니다🙂")

# 재료 입력 받기
마음 = st.text_input("오늘은 어떤 기분이신가요?🙏")

# 재료 출력
if st.button("마음 상태 체크하고, 위로 받기"):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": 마음,
            },
            {
                "role" : "system",
                "content": "위 답변의 마음 상태를 체크하고, 힘들다고 하면 위로와 해결책을 주고, 기분이 좋은 상태이면 공감해줘"
            }
        ],
        model="gpt-4o",
    )

    result = chat_completion.choices[0].message.content
    st.write(result)
