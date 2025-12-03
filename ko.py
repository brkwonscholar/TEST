import os
from openai import OpenAI
import streamlit as st

# API 키 설정
os.environ["OPENAI_API_KEY"] = st.secrets['API_KEY']
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

# 앱 제목 및 설명
st.title("🌱 AI 감정 일기")
st.caption("오늘 있었던 일을 적으면 AI가 위로해주고 일기로 정리해줘요.")

# 사용자 입력
content = st.text_area("오늘 어떤 일이 있었나요?", height=150)

# 실행 버튼
if st.button("위로받기 및 일기 생성"):
    # 1. 위로 멘트 요청
    completion_comfort = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system", 
                "content": "너는 따뜻한 심리상담가야. 사용자의 말을 듣고 따뜻하게 공감해주고 위로해줘."
            },
            {
                "role": "user", 
                "content": content
            },
        ],
    )

    # 2. 일기 요약 요청
    completion_diary = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system", 
                "content": "사용자의 말을 듣고 '오늘의 일기' 형식으로 3줄 요약해줘."
            },
            {
                "role": "user", 
                "content": content
            },
        ],
    )

    # 결과 처리
    comfort_result = completion_comfort.choices[0].message.content
    diary_result = completion_diary.choices[0].message.content

    # 화면 출력
    st.divider()
    
    st.subheader("💌 AI의 위로")
    st.write(comfort_result)
    
    st.divider()
    
    st.subheader("📔 오늘의 일기장")
    st.write(diary_result)
