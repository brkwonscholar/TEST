import os
import streamlit as st
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



# 앱 제목
st.title("🛡️ AI 거르미 – 허위 정보/가짜 논문 탐지기")

st.write("AI 생성 허위 정보, 논문 사기, 가짜 출처를 자동으로 점검해줍니다.")

# 사용자 입력
user_text = st.text_area("🔍 검사할 문장·정보·논문 제목 등을 입력하세요:")

# 버튼
if st.button("검사하기"):

    with st.spinner("AI가 정보를 분석 중입니다..."):

        prompt = f"""
너는 'AI 거르미'라는 허위 정보 검증 AI다.

사용자가 제공한 문장/정보/논문 제목이 다음 기준에서 어떤지 분석해라:

1. **사실 가능성 평가 (0~100%)**
2. **허위 정보 여부 (패턴·과장·AI 특유 표현 등)**
3. **논문 제목/저자/저널이 실제 존재하는지 확인**
4. **틀린 정보가 있다면 어떤 부분인지 구체적으로 설명**
5. **유사한 실제 존재하는 논문 1~3개 추천**
6. **정보의 신뢰도를 높이기 위한 조언 제공**

분석할 내용:
{user_text}
"""

        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": prompt}]
        )

        result = completion.choices[0].message.content

        st.subheader("🔎 분석 결과")
        st.write(result)

        # 추가: 검증 결과에 대한 이미지 생성 (재미 요소)
        img_prompt = f"AI 허위 정보 필터링을 시각적으로 보여주는 간단한 일러스트. 키워드: {user_text}"

        img_res = client.images.generate(
            model="dall-e-3",
            prompt=img_prompt,
            size="1024x1024",
            n=1
        )

        st.subheader("🖼️ 시각화 이미지 (AI 자동 생성)")
        st.image(img_res.data[0].url)

