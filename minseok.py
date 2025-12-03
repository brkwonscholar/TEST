import os
import json
from datetime import datetime
from typing import Dict, Optional

import streamlit as st
from dotenv import load_dotenv
import openai
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import folium
from streamlit.components.v1 import html

# --- 환경변수 로드 ---
load_dotenv()
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

st.set_page_config(page_title="오늘 뭐할까?", layout="wide")
st.title("✈️오늘 뭐할까?")

with st.sidebar:
    st.header("여행 기본 정보")
    current_location = st.text_input("현재 위치 (예: 서울, 대한민국)", "서울, 대한민국")
    departure_time = st.time_input("출발 시간", datetime.now().time())
    destination = st.text_input("여행지 (도시/국가)", "서울, 대한민국")
    days = st.number_input("여행 일수", min_value=1, max_value=30, value=3)
    travel_keywords = st.text_area("여행 키워드 (콤마로 구분)", "음식, 문화, 자연")
    budget_level = st.selectbox("예산", ["저가", "보통", "여유로운"], index=1)
    travel_mode = st.selectbox("이동수단", ["대중교통", "도보", "렌트카"], index=0)
    pace = st.selectbox("여행 페이스", ["느긋하게", "보통", "빠르게"], index=1)
    generate = st.button("루트 생성하기")

# JSON 파싱 안전하게 처리
def safe_parse_json(content: str) -> Optional[Dict]:
    if content.startswith("```") and content.endswith("```"):
        content = content.strip("`\n")
    content = content.replace("'", '"')
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return None

# OpenAI 호출

def generate_itinerary(destination: str, days: int, travel_keywords: str, budget_level: str, travel_mode: str, pace: str, current_location: str, departure_time_str: str) -> Dict:
    if not OPENAI_API_KEY:
        raise RuntimeError("OpenAI API key not configured.")

    system_prompt = (
        "당신은 친절한 여행 계획 전문가입니다. 사용자가 제공한 여행 정보로 JSON 일정표를 생성하세요."
        "JSON 스키마: {title, destination, days, generated_at, day_plans: [{day, segments: [{time, title, description, address_optional, est_duration_minutes, transport, cost}]}]}"
        "모든 내용 한국어로 작성. 각 활동별 이동 수단과 예상 소요 시간, 비용(cost, 원)을 포함."
        "사용자의 현재 위치와 출발 시간을 고려하여 이동 순서와 시간을 계산하세요."
        "반드시 유효한 JSON만 반환하고 외부 설명은 포함하지 마세요."
    )

    user_prompt = (
        f"현재 위치: {current_location}\n출발 시간: {departure_time_str}\n목적지: {destination}\n일수: {days}\n여행 키워드: {travel_keywords}\n예산 수준: {budget_level}\n이동수단: {travel_mode}\n여행 페이스: {pace}\n"
        "각 일자별 3~6개의 활동과 시간, 간단한 설명, 주소, 이동수단, 예상 소요시간, 예상 비용 포함하여 작성하세요."
    )

    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
        max_tokens=2000,
    )

    content = resp['choices'][0]['message']['content'].strip()
    itin = safe_parse_json(content)
    if not itin:
        st.error("AI 응답을 JSON으로 파싱할 수 없습니다. 원본 내용:")
        st.code(content)
        return {}
    return itin

# 지오코딩 (캐시 제거, 함수 객체 전달 금지)
def geocode_itinerary(itin: Dict) -> Dict:
    geolocator = Nominatim(user_agent="ai-travel-planner")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

    for day in itin.get("day_plans", []):
        for seg in day.get("segments", []):
            addr = seg.get("address_optional") or seg.get("title")
            if addr and (not seg.get("lat") or not seg.get("lon")):
                try:
                    loc = geocode(addr)
                    if loc:
                        seg["lat"] = float(loc.latitude)
                        seg["lon"] = float(loc.longitude)
                except:
                    seg["lat"] = None
                    seg["lon"] = None
    return itin

# 지도 렌더링 (st_folium 대신 HTML로 안전하게 표시)
def render_map_safe(itin: Dict):
    points = [(seg.get("lat"), seg.get("lon"), str(seg.get("title", "")))
              for day in itin.get("day_plans", [])
              for seg in day.get("segments", [])
              if seg.get("lat") is not None and seg.get("lon") is not None]

    if not points:
        st.info("지도에 표시할 위치가 없습니다.")
        return

    center = points[0][:2]
    m = folium.Map(location=center, zoom_start=12)
    for lat, lon, title in points:
        folium.Marker([lat, lon], popup=str(title)).add_to(m)

    map_html = m._repr_html_()
    html(map_html, height=500, width=700)

# 일정표 UI 및 총 경비 계산

def display_itinerary(itin: Dict):
    total_cost = 0
    for day in itin.get('day_plans', []):
        with st.expander(f"Day {day.get('day')}", expanded=False):
            for seg in day.get('segments', []):
                st.markdown(f"**{seg.get('time','')} - {seg.get('title','')}**")
                st.write(seg.get('description',''))
                if seg.get('address_optional'):
                    st.caption(f"📍 주소: {seg.get('address_optional')}")
                if seg.get('est_duration_minutes'):
                    st.info(f"⏱ 예상 소요 시간: {seg.get('est_duration_minutes')}분")
                if seg.get('transport'):
                    st.info(f"🚗 이동 수단: {seg.get('transport')}")
                if seg.get('cost'):
                    st.info(f"💰 예상 비용: {seg.get('cost')}원")
                    total_cost += seg.get('cost',0)
                st.markdown("---")
    st.success(f"총 예상 경비: {total_cost}원")

# 메인
if generate:
    if not OPENAI_API_KEY:
        st.error(".env 파일이나 환경변수에 OPENAI_API_KEY를 설정하세요.")
    else:
        try:
            with st.spinner("AI가 일정과 예상 경비 생성 중입니다... 잠시만 기다려주세요"):
                departure_time_str = departure_time.strftime('%H:%M')
                itin = generate_itinerary(destination, int(days), travel_keywords, budget_level, travel_mode, pace, current_location, departure_time_str)
                if itin:
                    itin.setdefault('title', f"{destination} 여행 계획")
                    itin.setdefault('destination', destination)
                    itin.setdefault('days', days)
                    itin.setdefault('generated_at', datetime.utcnow().isoformat() + 'Z')

                    itin = geocode_itinerary(itin)

                    st.success("일정 및 경비 생성 완료!")

                    st.subheader("🗺 지도 보기")
                    render_map_safe(itin)

                    st.subheader("📖 대화형 일정 보기")
                    display_itinerary(itin)
        except Exception as e:
            st.error(f"오류 발생: {e}")
else:
    st.info("왼쪽 사이드바에서 정보를 입력하고 '루트 생성하기' 버튼을 누르세요.")
