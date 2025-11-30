import os
from openai import OpenAI
import streamlit as st 

# API 키 로드
os.environ["OPENAI_API_KEY"] = st.secrets['API_KEY']
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# 앱 제목
st.title("조선대 맛집 추천 :red[pick!]🍴")

# 음식 선택
options = st.multiselect(
    "지금 먹고싶은 음식을 골라주세요!!",
    ["중식", "양식", "한식", "일식", "아시아음식", "분식", "패스트푸드", "디저트/카페", "해산물", "기타"],
    default=["일식", "양식"],
)

# 선택 메뉴 보여주기
if options:
    st.write("👉 선택한 음식:", ", ".join(options))
    
# 버튼 클릭 시 맛집 추천
if st.button("맛집 추천 받기"):
    if not options:
        st.warning("음식 종류를 선택해주세요!")
    else:
        prompt = f"""
        조선대학교 주변에서 사용자가 선택한 [{', '.join(options)}] 음식 종류에 맞는 맛집 3곳을 아래 형식으로 출력해줘.

        ### 출력 형식 ###
        🍽️ ## 가게이름  
        📍 주소: 00로 00  
        ⭐ 추천 메뉴: 00, 00  
        💬 추천 이유: 한 줄 설명  

        절대 한 줄로 붙여 쓰지 말고, 줄바꿈 포함해서 예쁘게 작성해줘.
        가능한 실제 존재하는 식당 위주로 추천해줘.
        """

        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "너는 광주 지역 맛집 전문가야."},
                {"role": "user", "content": prompt},
            ],
            model="gpt-4o",  
        )

        result = chat_completion.choices[0].message.content

        st.markdown("## 📌 추천 맛집")
        st.markdown(result)

        st.markdown("---")  # 구분선

        # ============================
        # ⭐ 리뷰 별점 기능 추가
        # ============================
        st.markdown("# ⭐오늘 추천 맛집 별점 남겨주세요⭐")

    
        selected = st.radio("별점을 선택해주세요", [1, 2, 3, 4, 5])

        if selected is not None:
            st.markdown(f"🌟 선택한 별점: **{selected} 점**")






