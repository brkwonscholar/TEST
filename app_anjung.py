import os
from openai import OpenAI
import streamlit as st

os.environ["OPENAI_API_KEY"] = st.secrets['API_KEY']
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"),)



# 앱 제목
st.title("얼굴상만 입력하세요! 당신의 이상형은 우리가 찾아드립니다.")

# 재료 입력 받기
face = st.text_input("이상형 찾기 - 취향의 시작")

# 재료 출력
if st.button("이상형 소환!"):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": face,
            },
            {
                "role": "system",
                "content": "위에서 입력받은 당신의 이상형 얼굴상을 간략하게 작성해줘",
            }
        ],
        model="gpt-4o",
    )
    response = client.images.generate(
    model="dall-e-3",
    prompt= f"{face}를 사람의 얼굴형을 참고해서 사람의 얼굴만 리얼하게 생성해줘. 동물 요소는 절대 포함하지마. 무조건 {face}를 입력하면 사람얼굴에 옷을 입고 있는 사진만 나와야해. 네이버에 ai사진이라 검색하면 여자 사진이랑 남자 사진 뜨는데 보면 고퀄리티에 진짜 사람같이 나와있어. 네이버에 ai사진 검색하면 몸매좋은 여자가 비키니 입고 있는 사진 뜨는데 보면 얼굴이 이쁘잖아. 위에서 정보 입력하면 얼굴이 이렇게 이쁘게 떠야한다는 말이야. 남자도 몸 좋고 잘생긴 얼굴로 떠야해. 그리고 뒤에 풍경사진도 같이 만들어줘. 집에서 찍은거 아니면 길에서 찍은거 또는 해변에서 찍은걸로 만들어줘. 풍경사진에 높은 건물이 있는 풍경도 좋아. 여자 사진이면 이쁘게 남자 사진이면 잘생긴 걸로 만들어줘. 위에서 정보 입력하면 {face}를 내가 전 문장에서 말한 정보로 만들어줘. 이런 특징을 가진 사람의 얼굴로 변한 사진을 만들어줘. 동물을 얼굴에 섞지 마. 얼굴에는 사람얼굴만 나와야해. 여자 - {face}를 입력하면 여성{face}에 옷을 입고 있고 뒤에 풍경사진이 있는 사진이 나와야해. 남자 - {face}를 남자{face}에 옷을 입고 있고 뒤에 풍경사진이 있는 사진이 나와야해. {face}는 동물의 얼굴이 아니라 사럼의 얼굴 분위기를 표현하는 단어야. 강아지나 고양이나 뱀이나 여우 같은 동물의 귀, 털, 수염 등 동물의 신체 특징을 절대로 포함하지마. 이 얼굴형 표현은 단지 사람의 분위기와 느낌을 묘사하는 단어일 뿐이야. 절대 동물과 사람을 섞지마. 오직 사람 얼굴만 표현해야해. 동물과는 아무 관련 없는 {face}의 분위기를 가진 사람 얼굴로 생성해줘. )",
    size="1024x1024",
    quality="standard",
    n=1,
    )




    result = chat_completion.choices[0].message.content
    image_url = response.data[0].url
    
    st.write(result)
    st.image(image_url)