import os
from openai import OpenAI
import streamlit as st

os.environ["OPENAI_API_KEY"] = st.secrets['API_KEY']
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"),)

st.title("🌈배경화면 제작🌈")

a = st.text_input("색상을 입력해주세요")
b = st.text_input("배경화면에 넣을 요소를 입력해주세요")

if st.button("배경화면 생성하기"):
    response = client.images.generate(
    model="dall-e-3",
    prompt= f"{a, b}를 감성적인 휴대폰 배경화면으로 쓸 수 있는 사진으로 제작해줘",
    size="1024x1024",
    quality="standard",
    n=1,
)
    image_url = response.data[0].url
    
    st.image(image_url)
