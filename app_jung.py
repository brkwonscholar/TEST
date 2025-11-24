import streamlit as st
from openai import OpenAI
import os

# --- 페이지 설정 ---
st.set_page_config(page_title="GREEN DAILY", page_icon="🌿")

# --- API 키 처리 로직 (유연한 방식) ---
# 1. Streamlit Secrets에 저장된 키가 있는지 확인
if "OPENAI_API_KEY" in st.secrets:
    api_key = "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"
else:
    # 2. 없으면 사이드바에서 직접 입력받기 (테스트용)
    with st.sidebar:
        st.header("설정")
        api_key = st.text_input("OpenAI API Key를 입력하세요", type="password", help="sk-로 시작하는 키를 입력하세요.")

# --- 메인 앱 로직 ---
st.title("🌿🌲 GREEN DAILY 🗑️♻️")

# API 키가 없으면 경고 메시지 띄우고 중단
if not api_key:
    st.info("👈 왼쪽 사이드바에 API 키를 입력하거나, Secrets에 키를 설정해주세요.")
    st.stop()

# 클라이언트 초기화
try:
    client = OpenAI(api_key=api_key)
except Exception as e:
    st.error(f"API 키 설정 중 오류가 발생했습니다: {e}")
    st.stop()

# 날짜/상황 입력 받기
title = st.text_input("어떤 상황에서 환경보호 루틴을 실천하시려나요?", placeholder="예: 카페에서 음료를 마실 때")

# 버튼 클릭 시 실행
if st.button("오늘의 루틴 만들기"):
    if not title:
        st.warning("상황을 입력해주세요!")
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
                result_text = chat_completion.choices[0].message.content
                
                # 2. 이미지 생성 (DALL-E 3)
                # 주의: 텍스트 요청("3가지 짜줘")을 그대로 넣으면 글씨 그림이 나옵니다.
                # 상황(title)을 기반으로 감성적인 일러스트를 그리도록 프롬프트 수정
                image_response = client.images.generate(
                    model="dall-e-3",
                    prompt=f"환경 보호를 실천하는 따뜻하고 평화로운 일러스트. 상황: {title}. 지브리 스타일, 고해상도, 텍스트 없는 그림.",
                    size="1024x1024",
                    quality="standard",
                    n=1,
                )
                image_url = image_response.data[0].url

                # 3. 결과 출력
                st.subheader("실천 루틴 제안")
                st.write(result_text)
                
                st.subheader("이 순간의 이미지")
                st.image(image_url, caption="Green Daily Moment")
                
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
