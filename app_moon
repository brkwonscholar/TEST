import os
from openai import OpenAI
import streamlit as st

os.environ["OPENAI_API_KEY"] = st.secrets['API_KEY']
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"),)

# 앱 제목
st.title("👨‍⚕️AI Hospital")

st.caption("몸이 아픈데 무엇을 해야할지 모르시겠나요?")
st.caption("증상을 입력하시면 그에 맞는 대처방법을 알려드려요.")

st.caption("⚠️대처방법은 증상을 완화시켜줄 뿐입니다 반드시 병원에 가서 진료를 받으시길 바랍니다.")

# 증상 입력 받기
symptoms = st.text_input("어떤 증상이 있으십니까?")

# 대처법 출력
if st.button("대처법 찾아보기"):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": symptoms,
            },
            {
                "role": "user",
                "content": "입력받은 증상의 대처방법과 증상에 맞는 약을 알려줘",
            }
        ],
        model="gpt-4o",
    )
    result = chat_completion.choices[0].message.content
    st.write(result)


st.caption("증상을 대처하는것도 중요하지만 사전에 예방하는 것도 중요합니다")
st.caption("예방방법이 궁금한 병을 입력하시고 사전에 예방해보세요")
    
# 병명 입력 받기
prevent = st.text_input("예방 방법을 알려드려요")

# 예방방법 출력
if st.button("예방방법 찾아보기"):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prevent,
            },
            {
                "role": "user",
                "content": "입력받은 병의 예방방법을 알려줘",
            }
        ],
        model="gpt-4o",
    )
    result = chat_completion.choices[0].message.content
    st.write(result)
    

