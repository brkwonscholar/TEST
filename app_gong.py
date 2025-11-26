import os
from openai import OpenAI
import streamlit as st

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


st.title("당신만의 여행지를 만나보세요!!")


genre = st.radio(
    "여행을 할때 돈을 더 중시하나요? 만족감을 더 중시하나요?",
    ['가성비','가심비'],
    captions=[
    "적은 돈으로도 만족할 수 있는 여행을 하고싶어!!",
        "돈을 많이 쓰더라도 최고의 기분을 느끼면 상관없어!!"
        ],)
if genre == '가성비':
    trp ='가성비'
elif genre == '가심비':
    trp ='가심비'
st.write('당신은 여행을 할 때 무엇을 체험하고싶나요?')
cd= st.checkbox('자연 경관')
ce=st.checkbox('문화재 관람')
f= st.checkbox('축제(토마토 축제 등)')
cg= st.checkbox('전통 문화')
ch= st.checkbox('맛집 탐방')
cj= st.checkbox('스포츠(해양스포츠,스키 등)')
lis = []
if cd:
    lis.append('자연 경관')
if ce:
    lis.append('문화재 관람')
if f:
    lis.append('축제')
if cg:
    lis.append('전통 문화')
if ch:
    lis.append('맛집 탐방')
if cj:
    lis.append('스포츠')
        

if st.button("선택 완료"):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content":f"{trp}에 좋고 {lis}를 체험할수 있는 여행지나 도시를 각각 국내 해외 두개로 나눠서 선정해 "
            },
            {
                "role": "system",
                "content":f"위에서 선정한 도시들을 적고 {trp}에 왜 좋은지와 {lis}왜 체험하기 좋은지 알려줘"
            }
        ],
        model="gpt-4o",
    )
    city ='비행기'
    response = client.images.generate(
        model="dall-e-3",
        prompt=city,
        size="1024x1024",
        quality="standard",
        n=1,
    )




    result=(chat_completion.choices[0].message.content)
    image_url = response.data[0].url
    st.write(result)
    st.image(image_url)
