import streamlit as st
from openai import OpenAI
from PIL import Image
import io
import os
from dotenv import load_dotenv
import base64

# .env 파일에서 환경 변수 로드 (API 키)
load_dotenv()

# --- 기본 설정 ---
st.set_page_config(page_title="냉장고 속 셰프", layout="wide")

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

# 사이드바 (사용자 설정)
with st.sidebar:
    st.header("사용자 설정 ⚙️")
    # 초기 유통기한 임박 재료 설정 (데모를 위해 수동 설정)
    urgent_ingredient = st.text_input(
        "긴급 소비 재료 (선택)",
        "양파, 두부"
    )
    # 개인 기호 설정
    preference = st.radio(
        "요리 스타일 선호도",
        ['기본', '한식', '건강식', '간단한 요리', '매운맛',]
    )
    
    st.markdown("---")
    st.info("💡 **사용법:** 냉장고 이미지를 업로드하고 '재료 인식 및 레시피 제안' 버튼을 누르세요.")
    st.subheader("프로젝트 정보")
    st.markdown(f"**분반:** 38분반")
    st.markdown(f"**학번/이름:** 20241481 윤한빛")
    st.markdown(f"**기술:** GPT-4 Vision, Streamlit")

# --- 메인 페이지 ---
st.title("🧊 냉장고 속 셰프 - AI 맞춤 레시피 제안")
st.markdown("남은 재료를 자동으로 인식하고 개인 선호도에 맞는 맞춤형 레시피를 제안합니다.")

# 세션 상태 초기화
if 'recognized_ingredients' not in st.session_state:
    st.session_state.recognized_ingredients = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# 이미지 파일 업로드
uploaded_file = st.file_uploader("냉장고 내부 사진을 업로드하세요.", type=["jpg", "jpeg", "png"])

col1, col2 = st.columns([1, 2])

with col1:
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="업로드된 냉장고 사진", use_column_width=True)

        # 이미지 파일을 Base64로 인코딩하여 API에 전달
        with io.BytesIO() as buffer:
            image.save(buffer, format="JPEG")
            base64_image = base64.b64encode(buffer.getvalue()).decode('utf-8')

        # GPT Vision API에 전달할 이미지 객체 생성
        image_content = {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
            }
        }
    else:
        # 이미지가 없을 때 메시지
        st.warning("사진을 업로드해주세요.")
        st.session_state.recognized_ingredients = None
        st.session_state.chat_history = []


# --- 핵심 로직: 재료 인식 및 레시피 제안 ---

with col2:
    if st.button("재료 인식 및 레시피 제안 시작 🚀", disabled=uploaded_file is None):
        with st.spinner("AI가 냉장고 속 재료를 분석 중입니다..."):
            
            # 1. Vision 모델을 사용하여 식재료 인식
            vision_prompt = """
            당신은 최고의 냉장고 재료 관리 셰프입니다. 
            업로드된 냉장고 사진을 보고 어떤 식재료들이 있는지 상세하게 리스트업해주세요. 
            재료 이름 외에 불필요한 서론/결론 없이 재료 리스트만 텍스트로 깔끔하게 정리해줍니다.
            """
            
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini", # 이미지 및 텍스트 처리가 가능한 모델 사용
                    messages=[
                        {"role": "user", "content": [
                            {"type": "text", "text": vision_prompt},
                            image_content
                        ]}
                    ]
                )
                
                recognized_ingredients_text = response.choices[0].message.content.strip()
                st.session_state.recognized_ingredients = recognized_ingredients_text
                
            except Exception as e:
                st.error(f"재료 인식 중 오류가 발생했습니다: {e}")
                st.stop()

            # 2. LLM을 사용하여 맞춤 레시피 생성 및 대화 시작
            ingredients = st.session_state.recognized_ingredients
            
            # 사용자 맞춤 프롬프트 생성
            llm_prompt = f"""
            방금 인식된 냉장고 재료는 다음과 같습니다: {ingredients}
            긴급 소비가 필요한 재료는 "{urgent_ingredient}"입니다.
            사용자의 선호도는 "{preference}"입니다.

            위 재료와 선호도를 바탕으로 가장 적합한 요리 1가지의 맞춤형 레시피를 단계별로 제안해주세요.
            제안된 요리 이름, 필요한 추가 재료, 단계별 조리법을 포함하여 친절하고 자세하게 설명해주세요.
            """
            
            try:
                recipe_response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "당신은 사용자 냉장고 재료를 활용하여 맞춤 레시피를 제안하는 친절하고 유능한 셰프입니다. 언제나 대화형으로 응답해주세요."},
                        {"role": "user", "content": llm_prompt}
                    ]
                )
                
                ai_initial_response = recipe_response.choices[0].message.content
                
                # 대화 내역 업데이트 및 표시
                st.session_state.chat_history = [
                    {"role": "assistant", "content": ai_initial_response}
                ]
                
                # 재료 인식 결과를 따로 표시
                st.success("✅ 재료 인식이 완료되었습니다. AI 셰프가 레시피를 제안합니다!")
                st.markdown(f"**👉 인식된 재료 목록:** {ingredients}")
                st.markdown("---")

            except Exception as e:
                st.error(f"레시피 제안 중 오류가 발생했습니다: {e}")
                st.stop()

# --- 대화형 레시피 제안 ---

st.subheader("AI 셰프와의 대화 💬")

if st.session_state.chat_history:
    # 기존 대화 표시
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 사용자 입력 처리
    user_input = st.chat_input("이 레시피에 대해 더 궁금한 점이 있나요? (예: '추가 재료 없이 만들 수 있나요?', '매운맛을 줄이는 방법은요?')")

    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.spinner("AI 셰프가 답변을 준비 중입니다..."):
            
            # 대화 기록을 바탕으로 API 호출
            messages_for_api = [
                {"role": "system", "content": "당신은 사용자 냉장고 재료를 활용하여 맞춤 레시피를 제안하는 친절하고 유능한 셰프입니다. 언제나 대화형으로 응답해주세요."},
                # 기존 대화 내역 추가
                *st.session_state.chat_history
            ]

            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages_for_api
                )
                ai_response = response.choices[0].message.content
                st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
                
                # 새로운 답변 표시
                with st.chat_message("assistant"):
                    st.markdown(ai_response)

            except Exception as e:
                st.error(f"대화 중 오류가 발생했습니다: {e}")

# --- 장보기 리스트 및 소비 기록 (데모용) ---

st.markdown("---")
st.subheader("관리 기능 🛒")
st.markdown("*향후 구현 목표: 재료 소비 기록 및 자동 장보기 리스트 생성*")

if st.button("장보기 리스트 생성"):
    with st.spinner("장보기 리스트를 생성합니다..."):
        # LLM을 활용하여 장보기 리스트 제안
        shopping_list_prompt = f"""
        현재 인식된 냉장고 재료 ({st.session_state.recognized_ingredients if st.session_state.recognized_ingredients else '없음'})와
        선호하는 요리 스타일 ({preference})을 고려하여, 다음 주 식사를 위한 필수 추가 재료 5가지를 리스트 형태로 제안해주세요.
        """
        try:
            shop_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": shopping_list_prompt}
                ]
            )
            st.success("✅ 장보기 리스트가 제안되었습니다.")
            st.markdown(shop_response.choices[0].message.content)
        except Exception as e:
            st.error(f"장보기 리스트 생성 중 오류: {e}")
