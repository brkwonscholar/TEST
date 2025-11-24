import os
from openai import OpenAI
import streamlit as st

client = OpenAI(api_key = "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")



# 앱 제목
st.title("후회없는 여행 만들어드립니다✈️")

# 앱 나라 선택
import streamlit as st

option = st.selectbox(
    "어느 나라를 여행할 계획이신가요?",
    ("한국", "일본", "중국", "대만", "홍콩", "태국", "베트남", "싱가포르", "말레이시아",
"인도네시아", "필리핀", "캄보디아", "라오스", "몽골",
"미국", "캐나다", "멕시코", "영국", "프랑스", "독일", "이탈리아", "스페인", "스위스", "네덜란드", "체코", "오스트리아",
"호주", "뉴질랜드", "터키", "아랍에미리트", "사우디아라비아", "카타르",
"인도", "네팔", "스리랑카"),
)
 
 #여행 경비
expense = st.radio(
    "여행경비는 어느정도 예상하시나요?(항공값 제외)",
    ["50만원 이하 💸","50만원~100만원 💸", "100만원~150만원 💸", "150만원~200만원 💸", "200만원 이상 💸"]
)

 #동반자   
withwho = st.radio(
    "누구와 함께 여행 할 계획이신가요?",
    ["가족👪", "친구🤼‍♀️", "애인💏", "혼자🙍‍♂️", "지인🙇"]
)

#여행장소
options = st.multiselect(
    "추구하는 여행 장소는 어디이신가요?",
    ["도심🏙️", "야경이 예쁜 장소🌆", "웅장한 자연경관🏔️", "현지느낌 물씬나는 장소🏠", "어르신분들 취향저격 장소🦽", "애인에게 점수 딸만한 장소💏", "사람이 적은 장소🧘", "사람들이 북적이는 장소🚗", "돈을 최대한 아낄만한 장소💸", "기념품을 구매하기에 적합한 장소🎁"],
 default=["도심🏙️"],
)

#여행일정표
plan = st.select_slider(
    "여행일정을 어떤식으로 잡아드릴까요?",
    options=[
        "시간이 매우 널널하고 자유롭게",
        "오전, 오후로 나누어서",
        "아침, 점심, 저녁으로 나누어서",
        "완전 빡빡하게",
    ],
)
st.write("저는 이번 여행을", plan, "하고 싶어요!!")

#지피티
if st.button("✈️여행 추천 받기✈️"):

    # GPT 프롬프트 생성
    prompt = f"""
    다음 조건에 맞는 여행 루트를 만들어줘:
    - 나라: {option}
    - 여행 경비: {expense}
    - 동반자: {withwho}
    - 추구 장소: {', '.join(options)}
    - 일정 스타일: {plan}

    가능한 한 간단하게 3일~5일 기준 일정과 추천 장소를 작성해줘.
    """

    # GPT 텍스트 생성
    chat_completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    result = chat_completion.choices[0].message.content
    
    st.write(result)
 # 피드백 제출 버튼
feedback = st.text_area(
    "여행 추천은 어떠셨나요? 피드백을 남겨주세요!",
    placeholder="예: 일정이 마음에 들어요! / 너무 빡빡해요 등"
)


if st.button("피드백 제출"):
    if feedback.strip() == "":
        st.warning("피드백을 입력해주세요!!")
    else:
        st.success("이를 참고하여 더 나은 앱 개발에 열중하겠습니다😀")
