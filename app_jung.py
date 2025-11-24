import os
from openai import OpenAI

import streamlit as st

os.environ["OPENAI_API_KEY"] = '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'
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"),)

# 앱 제목
st.title("🌿🌲 GREEN DAILY 🗑️♻️")

# 날짜 입력 받기
title = st.text_input("어떤 상황에서 환경보호루틴을 실천하시려는건가요 ?")

# 운세 추천 버튼
if st.button("오늘의 루틴 만들기"):
    
    chat_completion = client.chat.completions.create(
        messages=[
        {
            "role": "user",
            "content": title,
        },
        {
            "role": "system",
            "content": "환경보호하는 활동을 실천하려는데 입력받은 내용에서 최대한 실천할수있는 루틴을 간략하게 3가지정도 짜줘",
        }
    ],
        model="gpt-4o",
)

    response = client.images.generate(
        model="dall-e-3",
        prompt="환경보호하는 활동을 실천하려는데 입력받은 내용에서 최대한 실천할수있는 루틴을 간략하게 3가지정도 짜줘",
        size="1024x1024",
        quality="standard",
        n=1,
        )
    result = chat_completion.choices[0].message.content
    image_url = response.data[0].url
    st.write(result)
    st.image(image_url)
