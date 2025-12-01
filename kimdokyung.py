import os
import streamlit as st
from openai import OpenAI # 변경됨: OpenAI 클래스 임포트

# 환경 변수 및 클라이언트 설정
# st.secrets에 "API_KEY"가 설정되어 있어야 합니다.
if "API_KEY" in st.secrets:
    api_key = st.secrets["API_KEY"]
    client = OpenAI(api_key=api_key) # 변경됨: 클라이언트 객체 생성
else:
    st.error("Streamlit secrets에 API_KEY가 설정되지 않았습니다.")
    st.stop()

# 스트림릿 앱 설정: 밝은 배경 스타일 추가
st.set_page_config(page_title="트립AI", layout="wide")
st.markdown(
    """
    <style>
    body {
        background-color: #f0f8ff;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("트립AI ✈️")
st.write("여행지를 선택하고 예산, 여행일수, 동행 인원, 여행 테마 등을 입력하면 AI가 여행 계획을 제시해드립니다! 🧳🌍") 

# 사이드바 또는 폼을 사용하여 사용자 입력 받기
with st.form(key="trip_form"):
    destination = st.text_input("여행지 (예: 제주도, 서울 등)", placeholder="여행지를 입력하세요")
    budget = st.number_input("예산 (원)", min_value=0, step=10000, value=500000)
    num_days = st.number_input("여행 일수", min_value=1, step=1, value=3)
    num_people = st.number_input("동행 인원 수", min_value=1, step=1, value=2)
    theme = st.selectbox("여행 테마 선택", options=["휴양", "로맨틱", "음식", "역사", "자연", "모험", "가족"])
    
    submitted = st.form_submit_button("여행 계획 생성하기")

# 함수: OpenAI API를 호출하여 여행 계획 생성
def generate_travel_plan(destination, budget, num_days, num_people, theme):
    # 사실확인을 위한 간단한 정적 데이터 셋 (예시)
    verified_info = {
        "제주도": {
            "명소": "한라산, 성산일출봉, 우도",
            "맛집": "흑돼지 전문점, 해산물 식당",
            "숙소": "제주도 리조트, 펜션"
        },
        "서울": {
            "명소": "경복궁, N서울타워, 명동",
            "맛집": "한식, 분식 전문점",
            "숙소": "호텔, 게스트하우스"
        }
        # 필요에 따라 다른 여행지 추가
    }
    
    # 입력받은 여행지가 정적 데이터에 있는지 확인하여 데이터 삽입
    if destination in verified_info:
        info = verified_info[destination]
    else:
        # 기본 정보 값
        info = {
            "명소": "대표 명소 정보",
            "맛집": "유명 맛집 정보",
            "숙소": "추천 숙소 정보"
        }
    
    # OpenAI API 호출을 위한 프롬프트 작성
    system_prompt = (
        "당신은 각 여행지의 네이버 블로그에서 사실 확인된 정보를 바탕으로 "
        "자세하고 신뢰도 높은 여행 일정을 작성하는 전문가입니다. "
        "여행 계획에 포함되어야 하는 내용은 여행지 주변 명소, 맛집, 숙소, 등이며, "
        "각 일차별로 오전/오후 일정 및 이동시간, 식사 정보와 예상 소비 금액 등이 포함되어야 합니다. 😄\n"
        "여행 시작시간은 1일차 오후 12시입니다.\n"
        "특히, 여행 테마(휴양, 로맨틱, 음식, 역사, 자연, 모험, 가족)에 따라 맞춤 추천을 제공해주세요. "
        "예를 들어, 가족 여행의 경우 아이들도 즐길 수 있는 체험 장소를, 로맨틱 여행의 경우 연인과 함께한 리뷰가 높은 장소를 중점적으로 추천합니다.\n"
        "정보는 반드시  확인된 사실에 근거하고 모호한내용은 제외해주세요"
        "정보를 제시할때는 각 항목별로 이모티콘을 포함하여 작성해 주세요."
        "정보를 제시할때는 역사적인 명소일 경우 그 명소의 유래와 이야기도 간단히 포함해 주세요."
        "정보를 제시할때는 맛집일 경우 그 맛집의 대표 메뉴도 간단히 포함해 주세요."
        "맛집이나 식당을 추천할때는 반드시 영업시간도 포함해 주세요."
        "맛집이나 식당을 추천할때는 반드시 위치 정보도 포함해 주세요."
        "테마를 정할때 역사를 선택한 경우에는 반드시 그 여행지의 역사적인 명소를 포함해 주세요."
        "테마를 정할때 음식을 선택한 경우에는 반드시 그 여행지의 유명한 음식을 포함해 주세요."
        "테마를 정할때 자연을 선택한 경우에는 반드시 그 여행지의 자연 경관이 뛰어난 명소를 포함해 주세요."
        "테마를 정할때 모험을 선택한 경우에는 반드시 그 여행지의 액티비티 명소를 포함해 주세요."
        "테마를 정할때 가족을 선택한 경우에는 반드시 그 여행지의 가족 친화적인 명소를 포함해 주세요."
        "테마를 정할때 휴양을 선택한 경우에는 반드시 그 여행지의 휴양 명소를 포함해 주세요."
        "테마를 정할때 로맨틱을 선택한 경우에는 반드시 그 여행지의 로맨틱 명소를 포함해 주세요."
        "테마를 정할때는 반드시 그에 맞는 명소, 맛집, 숙소를 포함해 주세요."
        "모든 정보를 한국어로 작성해 주세요."
    )
    
    user_prompt = (
        f"여행지: {destination}\n"
        f"예산: 약 {budget} 원\n"
        f"여행 일수: {num_days}일\n"
        f"동행 인원: {num_people}명\n"
        f"여행 테마: {theme}\n\n"
        f"---\n"
        f"인근 명소: {info['명소']}\n"
        f"유명 맛집: {info['맛집']}\n"
        f"추천 숙소: {info['숙소']}\n"
        f"각 날짜별 상세 일정(1일차부터 {num_days}일차까지)과 예상 소비 금액, 이동시간, 식사 정보, 그리고 각 일정에 적합한 이모티콘을 포함하여 작성해 주십시오."
    )
    
    try:
        # 변경됨: 클라이언트 객체 사용 (client.chat.completions.create)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
        )
        # 변경됨: 객체 속성 접근 방식 사용 (.choices[0].message.content)
        travel_plan = response.choices[0].message.content
        return travel_plan
    except Exception as e:
        st.error(f"OpenAI API 에러가 발생했습니다: {e}")
        return None

# 사용자가 폼 제출 시 여행 계획 생성 및 출력
if submitted:
    st.write("여행 계획 생성중입니다... 잠시만 기다려주세요... 😊")
    plan = generate_travel_plan(destination, budget, num_days, num_people, theme)
    if plan:
        st.markdown("### 생성된 여행 일정 ✨")
        st.write(plan)
    else:
        st.error("여행 계획을 생성하는 과정에서 문제가 발생했습니다.")

    # 이용자 피드백 섹션
    st.markdown("### 이용자 만족도 및 개선점 피드백 📋")
    feedback = st.text_area("여행 계획에 대한 만족도와 개선점을 적어주세요 (자유롭게 작성)")
    if st.button("피드백 제출"):
        st.success("소중한 피드백 감사합니다! 더 나은 서비스를 위해 반영하도록 하겠습니다. 🙏")
