import streamlit as st
from openai import OpenAI
import os

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

st.set_page_config(page_title="AI 요리 레시피 생성기", layout="wide")
st.title("🍙재료 기반 요리 추천 & 레시피 생성기🍙")
st.markdown("원하는 재료를 입력하면, AI가 가능한 요리를 추천하고 레시피까지 만들어줍니다!")

ingredients = st.text_area(
    "사용 가능한 재료를 입력하세요 (예: 닭가슴살, 고추장, 양파, 마늘)", height=120
)

num_recipes = st.slider("몇 개의 요리를 추천할까요?", 1, 5, 3)

def generate_recipes(ingredients: str, n: int):
    prompt = f"""
아래 재료들만 사용해서 만들 수 있는 요리를 {n}가지 추천해줘.
응답은 서론 문장 없이, 아래 형식만 지켜서 바로 작성해줘:

1) 요리 이름
2) 요리 설명 (2~3문장)

3) 필요한 재료 목록

4) 단계별 레시피 (7단계 내외)

재료: {ingredients}
서론 문장이나 '물론입니다!' 같은 말은 절대 넣지 말 것.
각 항목 제목은 반복하지 말고, 단계별 레시피는 단계를 그대로 나열할 것.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500,
        temperature=0.8,
    )
    return response.choices[0].message.content

# 버튼 클릭 시 실행
if st.button("🍳 요리 생성하기", key="generate_recipe"):
    # 수정된 부분: 이미 위에서 api_key 검사를 했으므로 중복 검사 삭제
    if not ingredients.strip():
        st.warning("재료를 입력해주세요!")
    else:
        with st.spinner("AI가 레시피를 생성하는 중입니다..."):
            try:
                result = generate_recipes(ingredients, num_recipes)

                # 여러 요리별로 분리
                recipes = result.split('\n\n')
                clean_recipes = [r.strip() for r in recipes if r.strip()]

                st.markdown("## 🍽️ 생성된 요리들")

                for recipe in clean_recipes:
                    # 요리 제목 추출
                    lines = recipe.split('\n')
                    if not lines: continue
                    
                    first_line = lines[0]
                    title = first_line.replace("1)", "").replace("1.", "").strip()

                    # 제목 크게 표시 (하얀색 글자)
                    st.markdown(f"<h1 style='text-align: left; color: white;'>{title}</h1>", unsafe_allow_html=True)

                    # 나머지 내용 처리
                    content_lines = lines[1:]
                    for line in content_lines:
                        # 불필요한 기호 제거
                        clean_line = line.replace('####', '').replace('**', '').strip()
                        
                        # "요리 설명:", "필요한 재료 목록:" 같은 헤더 텍스트 처리
                        if "요리 설명" in clean_line or "필요한 재료" in clean_line or "단계별 레시피" in clean_line:
                            st.markdown(f"**{clean_line}**")
                        elif clean_line:
                            st.markdown(f"- {clean_line}")

                    st.markdown("---")
            except Exception as e:
                st.error(f"에러가 발생했습니다: {e}")

st.markdown("---")
