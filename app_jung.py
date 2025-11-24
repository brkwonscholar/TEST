import streamlit as st
from openai import OpenAI
import os

# --- 페이지 설정 및 UI ---
st.set_page_config(page_title="GREEN DAILY", page_icon="🌿")
st.title("🌿🌲 GREEN DAILY 🗑️♻️")

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

# 날짜/상황 입력 받기
title = st.text_input("어떤 상황에서 환경보호루틴을 실천하시려는건가요 ?", placeholder="예: 카페에서 음료를 마실 때")

# 운세 추천 버튼
if st.button("오늘의 루틴 만들기"):
    if not title:
        st.warning("내용을 입력해주세요!")
    else:
        with st.spinner("루틴을 짜고 그림을 그리는 중입니다..."):
            try:
                # 1. 텍스트 생성 (GPT-4o)
                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": title,
                        },
                        {
                            "role": "system",
                            "content": "환경보호하는 활동을 실천하려는데 입력받은 내용에서 최대한 실천할수있는 루틴을 간략하게 3가지정도 짜줘. 이모지를 적절히 사용해서 예쁘게 보여줘.",
                        }
                    ],
                    model="gpt-4o",
                )
                
                # 2. 이미지 생성 (DALL-E 3)
                response = client.images.generate(
                    model="dall-e-3",
                    prompt=f"환경 보호를 실천하는 따뜻하고 평화로운 일러스트. 상황: {title}. 지브리 스타일, 고해상도, 텍스트 없는 그림.",
                    size="1024x1024",
                    quality="standard",
                    n=1,
                )
                
                result = chat_completion.choices[0].message.content
                image_url = response.data[0].url
                
                st.write(result)
                st.image(image_url)
                
            except Exception as e:
                st.error(f"에러가 발생했습니다: {e}")
