import streamlit as st
import streamlit.components.v1 as components
import json
import folium
from openai import OpenAI
from duckduckgo_search import DDGS

# --- [1. 페이지 설정] ---
st.set_page_config(
    page_title="SafeRoam: AI Travel Architect",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- [2. 사용자 제공 데이터베이스 (유지)] ---
INTERNAL_DB = [
  {"country": "Japan", "locals": "정중하고 질서 있는 문화.", "speech_style": "겸손한 표현, '이케즈'(돌려 말하기) 주의.", "religion_notes": "신사/절 참배 예절.", "legal_notes": "여권 상시 소지 필수(불심검문).", "meds_alerts": "코데인/슈도에페드린 등 감기약 성분 반입 엄격.", "local_issues": "지진, 태풍, 도심 소매치기."},
  {"country": "China", "locals": "체면 중시.", "speech_style": "완곡한 표현.", "legal_notes": "호텔 주숙등기 필수, VPN 사용 주의.", "meds_alerts": "처방전 필수.", "local_issues": "정치적 민감 이슈."},
  {"country": "Taiwan", "locals": "친절, 야시장.", "speech_style": "예의 바름.", "legal_notes": "지하철 취식 금지(물도 안됨).", "meds_alerts": "처방전 권장.", "local_issues": "양안 관계, 지진."},
  {"country": "Thailand", "locals": "미소의 나라.", "speech_style": "왕실 언급 금지.", "legal_notes": "왕실 모독죄, 전자담배 반입 금지.", "meds_alerts": "대마 성분 오남용 주의.", "local_issues": "교통사고, 관광지 사기."},
  {"country": "Vietnam", "locals": "근면, 가족 중심.", "speech_style": "직접적 표현도 흔함.", "legal_notes": "오토바이 소매치기 주의.", "meds_alerts": "약국 약품 성분 확인 필요.", "local_issues": "위생, 교통사고."},
  {"country": "Philippines", "locals": "낙천적.", "speech_style": "친근함.", "legal_notes": "공항 총알 심기 사기 주의.", "meds_alerts": "상비약 필수.", "local_issues": "치안(남부), 태풍."},
  {"country": "Indonesia", "locals": "온화함.", "religion_notes": "왼손 사용 금기.", "legal_notes": "마약 사형, 혼외 성관계 처벌법.", "meds_alerts": "처방전 필수.", "local_issues": "화산, 쓰나미."},
  {"country": "Malaysia", "locals": "다문화.", "religion_notes": "이슬람 규범.", "legal_notes": "동성애 불법, 마약 엄벌.", "meds_alerts": "향정신성 약물 주의.", "local_issues": "소매치기."},
  {"country": "Singapore", "locals": "규율, 질서.", "legal_notes": "껌 반입 금지, 태형 제도.", "meds_alerts": "진통제/수면제 엄격 규제.", "local_issues": "법규 위반 시 벌금."},
  {"country": "Cambodia", "locals": "느긋함, 불교.", "speech_style": "목소리 높이지 말 것.", "religion_notes": "머리 만지기 금지.", "legal_notes": "마약 엄격, 문화재 반출 금지.", "meds_alerts": "말라리아 예방약.", "local_issues": "취업 빙자 납치/감금 사기 경보."},
  {"country": "Laos", "locals": "온화.", "legal_notes": "미폭발탄(UXO) 위험.", "meds_alerts": "의료 시설 부족.", "local_issues": "교통사고."},
  {"country": "India", "locals": "다양성.", "religion_notes": "오른손 식사.", "legal_notes": "여성 안전 유의.", "meds_alerts": "물갈이 약 필수.", "local_issues": "위생, 사기."},
  {"country": "USA", "locals": "개인주의.", "legal_notes": "주별 법률 상이(대마), 경찰 지시 불복종 금지.", "meds_alerts": "의료비 고가.", "local_issues": "총기 사고, 팁 문화."},
  {"country": "UK", "locals": "줄서기, 매너.", "legal_notes": "칼 소지 엄격 처벌.", "meds_alerts": "NHS 비대상자 고비용.", "local_issues": "런던 소매치기."},
  {"country": "France", "locals": "자부심.", "speech_style": "Bonjour 필수.", "legal_notes": "복면 금지법.", "meds_alerts": "처방전 필수.", "local_issues": "파리 소매치기."},
  {"country": "Spain", "locals": "시에스타.", "daily_customs": "저녁 식사 21시 이후.", "legal_notes": "노상 음주 벌금.", "meds_alerts": "약물 규제.", "local_issues": "바르셀로나 소매치기."},
  {"country": "Italy", "locals": "음식 사랑.", "legal_notes": "유적지 훼손 엄벌.", "meds_alerts": "처방전 필수.", "local_issues": "관광지 소매치기."},
  {"country": "Switzerland", "locals": "정시성.", "legal_notes": "소음 규제 엄격.", "meds_alerts": "원포장 약물.", "local_issues": "고산병."},
  {"country": "Turkey", "locals": "환대.", "religion_notes": "모스크 복장.", "legal_notes": "국부 모독죄.", "meds_alerts": "처방전 소지.", "local_issues": "호객행위 사기."},
  {"country": "UAE", "locals": "보수적.", "legal_notes": "공공장소 애정행각 금지, 음주 제한.", "meds_alerts": "약물 반입 초강력 규제.", "local_issues": "폭염, 복장."},
  {"country": "Australia", "locals": "아웃도어.", "legal_notes": "검역(음식물) 엄격.", "meds_alerts": "반입 신고 철저.", "local_issues": "자외선, 해양 생물."},
  {"country": "Russia", "locals": "무뚝뚝해 보이나 정이 많음.", "legal_notes": "거주지 등록 필수.", "meds_alerts": "마약성 진통제 엄격.", "local_issues": "정세 불안, 스킨헤드."}
]

# --- [3. CSS 스타일 (SafeRoam 디자인 100% 유지)] ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&family=Noto+Sans+KR:wght@300;400;500;700;900&display=swap');
    
    /* Global Reset & Font */
    * { font-family: 'Noto Sans KR', 'Inter', sans-serif !important; }
    .stApp { background-color: #F8FAFC; }
    
    /* 상단 여백 조정 */
    .block-container {
        padding-top: 5rem !important;
        padding-bottom: 5rem;
    }
    
    /* Headers */
    h1, h2, h3 { letter-spacing: -0.5px; color: #0F172A; }
    
    /* Sidebar Customization */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E2E8F0;
    }
    [data-testid="stSidebar"] h1 { /* 브랜드 타이틀 스타일 */
        font-size: 2rem; /* 크기 키움 */
        font-weight: 900;
        background: -webkit-linear-gradient(45deg, #3B82F6, #8B5CF6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        font-family: 'Inter', sans-serif !important; /* 영문 폰트 유지 */
    }
    [data-testid="stSidebar"] h2 {
        font-size: 1.1rem;
        font-weight: 700;
        color: #334155;
        margin-bottom: 1rem;
        margin-top: 1.5rem;
    }
    
    /* Input Fields Styling */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        border-radius: 8px;
        border: 1px solid #CBD5E1;
        padding: 10px;
        font-size: 0.95rem;
        background-color: #F8FAFC;
        transition: all 0.2s;
    }
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: #3B82F6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }

    /* Buttons */
    div.stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
        color: white;
        font-weight: 700;
        padding: 14px 24px;
        border-radius: 12px;
        border: none;
        box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.2);
        transition: transform 0.1s ease, box-shadow 0.1s ease;
        font-size: 1.05rem;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.3);
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
        color: #fff;
    }

    /* Custom Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        border-bottom: 1px solid #E2E8F0;
        margin-bottom: 30px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        border: none;
        background-color: transparent;
        font-weight: 600;
        color: #64748B;
        font-size: 1rem;
        padding: 0 10px;
    }
    .stTabs [aria-selected="true"] {
        color: #3B82F6 !important;
        border-bottom: 3px solid #3B82F6;
    }

    /* --- Cards Design (Unified) --- */
    .pro-card {
        background: #FFFFFF;
        border-radius: 16px;
        padding: 32px;
        margin-bottom: 24px;
        border: 1px solid #F1F5F9;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .pro-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 20px -5px rgba(0, 0, 0, 0.08);
    }
    
    .card-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 20px;
        padding-bottom: 16px;
        border-bottom: 1px solid #F8FAFC;
    }
    .card-icon {
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 10px;
        font-size: 1.2rem;
    }
    .card-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #1E293B;
        margin: 0;
    }
    
    /* --- Timeline Design (Itinerary) --- */
    .itinerary-container {
        position: relative;
        padding-left: 20px;
    }
    .timeline-item {
        display: flex;
        gap: 20px;
        padding-bottom: 40px;
        position: relative;
    }
    .timeline-item:last-child { padding-bottom: 0; }
    .timeline-line {
        position: absolute;
        left: 7px;
        top: 10px;
        bottom: -10px;
        width: 2px;
        background-color: #E2E8F0;
        z-index: 0;
    }
    .timeline-item:last-child .timeline-line { display: none; }
    
    .time-dot {
        width: 16px;
        height: 16px;
        border-radius: 50%;
        background: #fff;
        border: 4px solid #3B82F6;
        z-index: 1;
        margin-top: 6px;
        flex-shrink: 0;
    }
    .time-badge {
        font-family: 'Inter', monospace;
        font-size: 0.85rem;
        font-weight: 600;
        color: #64748B;
        min-width: 60px;
        padding-top: 4px;
    }
    .content-box {
        flex-grow: 1;
        background: #F8FAFC;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
    }
    .place-name {
        font-size: 1rem;
        font-weight: 700;
        color: #0F172A;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .category-tag {
        font-size: 0.75rem;
        padding: 4px 10px;
        background: #DBEAFE;
        color: #1E40AF;
        border-radius: 20px;
        font-weight: 600;
    }
    .place-desc {
        font-size: 0.95rem; /* 글자 크기 약간 키움 */
        color: #334155;     /* 색상 더 진하게 */
        margin-top: 12px;
        line-height: 1.8;   /* 줄간격 넓힘 */
        word-break: keep-all; /* 단어 단위 줄바꿈 */
    }
    .transport-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        margin-top: 15px;
        font-size: 0.8rem;
        color: #64748B;
        background: #FFFFFF;
        padding: 6px 12px;
        border-radius: 8px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
    }

    /* --- Culture & Safety Specifics --- */
    .chip-container {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 10px;
    }
    .chip {
        padding: 6px 12px;
        background: #F1F5F9;
        border-radius: 20px;
        font-size: 0.85rem;
        color: #334155;
        font-weight: 600;
        border: 1px solid #E2E8F0;
    }
    .chip.purple { background: #F3E8FF; color: #6B21A8; border-color: #E9D5FF; }
    .chip.red { background: #FEE2E2; color: #B91C1C; border-color: #FECACA; }

    </style>
""", unsafe_allow_html=True)

# --- [4. API 키 (유지)] ---
try:
    api_key = st.secrets["API_KEY"]
    client = OpenAI(api_key=api_key)
except:
    st.error("API KEY 오류")
    st.stop()

# --- [5. 백엔드 로직 (기능 강화 + JSON 에러 수정)] ---

def find_db_info(dest):
    korean_map = {
        "일본": "Japan", "중국": "China", "대만": "Taiwan", "태국": "Thailand", "베트남": "Vietnam",
        "필리핀": "Philippines", "인도네시아": "Indonesia", "말레이시아": "Malaysia", "싱가포르": "Singapore",
        "캄보디아": "Cambodia", "라오스": "Laos", "인도": "India", "미국": "USA", "영국": "UK",
        "프랑스": "France", "스페인": "Spain", "이탈리아": "Italy", "스위스": "Switzerland",
        "터키": "Turkey", "튀르키예": "Turkey", "UAE": "UAE", "호주": "Australia", "러시아": "Russia"
    }
    target = None
    for k, v in korean_map.items():
        if k in dest: target = v
    for item in INTERNAL_DB:
        if (target and item['country'] == target) or (item['country'].lower() in dest.lower()):
            return item
    return None

def search_web_live(dest):
    try:
        with DDGS() as ddgs:
            q = f"site:0404.go.kr OR site:yna.co.kr OR site:bbc.com {dest} 여행 안전 사건 사고 법률"
            res = list(ddgs.text(q, max_results=4))
            return "\n".join([f"- {r['title']}: {r['body']}" for r in res])
    except: return "웹 검색 오류"

# --- [Agent 1] 일정 (꽉 채운 일정, 중복 제거, 이동 시간) ---
def agent_itinerary_chunk(dest, start_day, end_day, style, companion):
    prompt = f"""
    여행지: {dest}, 기간: {days}일, 스타일: {style}, 동행: {companion}
    **Day {start_day}~{end_day} 상세 일정 (JSON)**
    
    [필수 지시사항 - 엄격 준수]
    1. **일정 꽉 채우기**: 09:00부터 22:00까지, 하루 최소 **5~6곳 이상의 스팟**을 포함하세요. (아침, 점심, 오후1, 오후2, 저녁, 야간)
    2. **중복 금지**: 숙소를 제외하고 **동일한 장소를 절대 중복 방문하지 마세요.**
    3. **이동 시간 명시**: 'move' 필드에 이동 수단과 **'예상 소요 시간'**을 반드시 적으세요. (예: "택시 (20분)", "도보 (10분)")
    4. **상세 설명**: 각 장소마다 '론리플래닛' 스타일로 5문장 이상 상세히 서술하세요. (일기체 절대 금지)
    
    Format: {{ "days": [ {{ "day": {start_day}, "theme": "하루 테마 (명확한 컨셉)", "schedule": [ {{ "time": "09:00", "place": "장소명", "cat": "카테고리", "desc": "상세설명(5문장 이상, 정보 위주)", "move": "택시 (15분)", "lat": 0.0, "lon": 0.0 }} ] }} ] }}
    """
    response = client.chat.completions.create(
        model="gpt-4o", 
        messages=[
            {"role": "system", "content": "You are a professional guidebook editor. Write detailed, dense, and informative content in Korean. No diary style. Output valid JSON."}, 
            {"role": "user", "content": prompt}
        ],
        temperature=0.5, 
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)

# --- [Agent 2] 문화 ---
def agent_culture_boost(dest, db_data):
    db_txt = str(db_data) if db_data else "정보 없음"
    prompt = f"""
    여행지: {dest}
    [DB 데이터]: {db_txt}
    
    현지 문화를 **'심층 리포트' 수준으로 방대하게** 작성하세요. (모두 한국어로).
    
    1. **화법/소통**: 단순한 인사가 아니라, 현지인들의 대화 습관, 거절할 때의 돌려 말하기 방식, 비언어적 소통(제스처) 등을 **구체적 상황 예시**와 함께 5줄 이상 설명하세요.
    2. **종교/관습**: 국교가 생활에 미치는 영향, 식사 예절의 'Why', 현지인 집 방문 시 에티켓 등을 상세히 서술하세요.
    3. **금기사항**: 한국인이 가장 많이 실수하는 치명적인 행동 3가지를 **충격적인 예시**와 함께 경고하세요.
    4. **Pro Tip**: 검색해도 안 나오는 현지 거주자만의 팁 (택시 잡는 법, 흥정 멘트 등).

    Format:
    {{
        "title": "심층 문화 가이드",
        "speech_detail": "화법 및 대화 뉘앙스 (최소 200자 이상)",
        "religion_customs": "종교 및 생활 관습 (최소 200자 이상)",
        "taboos": [
            {{"action": "금기행동1", "reason": "이유 및 발생할 수 있는 문제"}}
        ],
        "language_tips": [
            {{"phrase": "단어(발음)", "meaning": "뜻 및 사용 상황"}}
        ],
        "pro_tip": "현지 거주자급 꿀팁 (상세)"
    }}
    """
    response = client.chat.completions.create(
        model="gpt-4o", 
        messages=[
            {"role": "system", "content": "You are a cultural anthropologist. Write comprehensive and long texts in Korean. Output valid JSON."},
            {"role": "user", "content": prompt}
        ], temperature=0.6,
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)

# --- [Agent 3] 안전 (수정: 현지 약국 주의 성분 포함) ---
def agent_safety_deep(dest, db_data, web_data):
    db_txt = str(db_data) if db_data else "정보 없음"
    prompt = f"""
    여행지: {dest}
    [DB]: {db_txt}
    [뉴스]: {web_data}
    
    안전/법률 보고서를 **'기업 보안 브리핑' 수준으로 상세하게** 작성하세요. (모두 한국어로).
    
    1. **치안 이슈**: "소매치기 조심" 금지. 소매치기범들이 **어떤 동선으로 움직이고, 어떤 역할을 분담해서 접근하는지** 시나리오(Step-by-step)로 묘사하세요. (5줄 이상)
    2. **법률(중요)**: 벌금 액수나 처벌 수위가 있다면 명시하고, 실제 한국인 적발 사례를 포함하세요.
    3. **의약품 & 현지 약국**: 
       - 반입 금지 성분뿐만 아니라, **현지 약국에서 판매하는 약 중 한국인이 무심코 샀다가 문제될 수 있는 성분(예: 마약성 진통제, 특정 흥분제 등)**을 구체적으로 경고하세요.
       - 현지 약국 이용 팁과 대체약품 정보를 포함하세요.

    Format:
    {{
        "warning_level": "Danger/Caution/Safe",
        "scam_alert": {{ "title": "주요 범죄/사기 유형", "detail": "범죄 메커니즘 및 상세 대처법 (최소 200자 이상)" }},
        "legal_local": "현지법 주의사항 (상세 리포트)",
        "legal_korea": "속인주의 주의사항 (상세 리포트)",
        "meds_ingredients": ["성분1", "성분2", "성분3"],
        "meds_detail": "반입 주의 약품 및 **현지 약국 구매 시 주의해야 할 특정 성분/제품** 가이드",
        "embassy": "대사관 정보"
    }}
    """
    response = client.chat.completions.create(
        model="gpt-4o", 
        messages=[{"role": "system", "content": "You are a senior security analyst. Provide a detailed risk assessment report in Korean. Output valid JSON."}, {"role": "user", "content": prompt}],
        temperature=0.4,
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)

# --- [6. UI 구현 (SafeRoam 브랜드)] ---

with st.sidebar:
    st.title("SafeRoam")
    st.markdown("<div style='color:#64748B; font-size:0.9rem; font-weight:500; margin-bottom:30px;'>AI가 설계하는 완벽한 여행</div>", unsafe_allow_html=True)
    
    st.subheader("여행 정보 입력")
    destination = st.text_input("여행지 (도시/국가)", placeholder="예: 도쿄, 파리")
    col1, col2 = st.columns(2)
    with col1: days = st.number_input("기간 (일)", 1, 14, 4)
    with col2: people = st.number_input("인원 (명)", 1, 10, 2)
    
    st.subheader("취향 설정")
    companion = st.selectbox("동행", ["친구", "연인", "가족", "혼자", "비즈니스"])
    style = st.selectbox("여행 스타일", ["로컬 탐방", "휴양 & 힐링", "미식 투어", "쇼핑 & 시티", "역사 & 문화"])
    
    st.markdown("---")
    run_btn = st.button("여행 계획 생성하기 ✨", type="primary", use_container_width=True)
    st.markdown("<div style='text-align:center; margin-top:20px; color:#94A3B8; font-size:0.75rem;'>Powered by OpenAI & Streamlit</div>", unsafe_allow_html=True)

if run_btn and destination:
    db_info = find_db_info(destination)
    web_info = search_web_live(destination)
    
    res_itinerary_list = []
    res_culture = None
    res_safety = None
    center_coords = [0, 0]

    with st.status("⚙️ 맞춤형 여행 여정을 설계하는 중...", expanded=True) as status:
        st.write("🎭 [Agent 1] 현지 문화와 예절 심층 분석 중...")
        res_culture = agent_culture_boost(destination, db_info)
        
        st.write("⚖️ [Agent 2] 안전 시나리오 및 법률 리포트 작성 중...")
        res_safety = agent_safety_deep(destination, db_info, web_info)
        
        chunk_size = 3
        for i in range(1, days + 1, chunk_size):
            end = min(i + chunk_size - 1, days)
            st.write(f"🗺️ [Agent 3] {i}~{end}일차 상세 동선 최적화 중...")
            chunk_res = agent_itinerary_chunk(destination, i, end, style, companion)
            if chunk_res and 'days' in chunk_res:
                res_itinerary_list.extend(chunk_res['days'])
                if i == 1 and chunk_res['days'][0]['schedule']:
                    first = chunk_res['days'][0]['schedule'][0]
                    center_coords = [first.get('lat', 0), first.get('lon', 0)]
        
        status.update(label="여정 설계 완료! 아래에서 확인하세요.", state="complete", expanded=False)

    if res_itinerary_list and res_culture and res_safety:
        tab1, tab2, tab3 = st.tabs(["🗺️ 상세 일정", "🎭 문화 & 에티켓", "🚨 안전 & 법률"])

        # --- Tab 1: Itinerary ---
        with tab1:
            try:
                m = folium.Map(location=center_coords, zoom_start=12, tiles="CartoDB positron")
                for day in res_itinerary_list:
                    color = ["#3B82F6", "#EF4444", "#10B981", "#F59E0B", "#8B5CF6"][day['day'] % 5]
                    for item in day.get('schedule', []):
                        lat, lon = item.get('lat'), item.get('lon')
                        if isinstance(lat, (int, float)):
                            folium.Marker(
                                [lat, lon], 
                                tooltip=item['place'], 
                                icon=folium.Icon(color="black", icon_color=color, prefix='fa', icon='circle')
                            ).add_to(m)
                
                st.markdown('<div style="border-radius:16px; overflow:hidden; box-shadow:0 4px 12px rgba(0,0,0,0.1); border:1px solid #E2E8F0; margin-bottom:30px;">', unsafe_allow_html=True)
                components.html(m._repr_html_(), height=450)
                st.markdown('</div>', unsafe_allow_html=True)
            except: st.error("지도 렌더링 실패")

            st.markdown("### 🗓️ 일자별 상세 스케줄")
            for day in res_itinerary_list:
                with st.expander(f"{day['day']}일차 — {day.get('theme', '자유 여행')}", expanded=True):
                    st.markdown('<div class="itinerary-container">', unsafe_allow_html=True)
                    for item in day.get('schedule', []):
                        # 이동 시간 표시
                        move_html = ""
                        if item.get('move'):
                             move_html = f'<div class="transport-badge">🚕 {item["move"]}</div>'
                             
                        st.markdown(f"""
                        <div class="timeline-item">
                            <div class="timeline-line"></div>
                            <div class="time-dot"></div>
                            <div class="time-badge">{item['time']}</div>
                            <div class="content-box">
                                <div class="place-name">
                                    {item['place']}
                                    <span class="category-tag">{item['cat']}</span>
                                </div>
                                <div class="place-desc">{item['desc']}</div>
                                {move_html}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

        # --- Tab 2: Culture ---
        with tab2:
            c1, c2 = st.columns([1, 1])
            
            with c1:
                st.markdown(f"""
                <div class="pro-card">
                    <div class="card-header">
                        <div class="card-icon" style="background:#EFF6FF; color:#3B82F6;">🗣️</div>
                        <h3 class="card-title">소통 및 화법</h3>
                    </div>
                    <div style="line-height:1.7; color:#475569; font-size:0.95rem;">
                        {res_culture.get('speech_detail')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="pro-card">
                    <div class="card-header">
                        <div class="card-icon" style="background:#F0FDF4; color:#16A34A;">🙏</div>
                        <h3 class="card-title">종교 및 생활 관습</h3>
                    </div>
                    <div style="line-height:1.7; color:#475569; font-size:0.95rem;">
                        {res_culture.get('religion_customs')}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with c2:
                st.markdown(f"""
                <div class="pro-card" style="border-color:#FECACA;">
                    <div class="card-header">
                        <div class="card-icon" style="background:#FEF2F2; color:#DC2626;">🚫</div>
                        <h3 class="card-title">주의해야 할 금기사항</h3>
                    </div>
                    <ul style="padding-left:20px; margin:0; color:#475569; line-height:1.8;">
                        {''.join([f'<li style="margin-bottom:8px;"><b>{t["action"]}</b><br><span style="font-size:0.9rem; color:#64748B;">{t["reason"]}</span></li>' for t in res_culture.get('taboos', [])])}
                    </ul>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="pro-card" style="background:#F8FAFC;">
                    <div class="card-header">
                        <div class="card-icon" style="background:#F3E8FF; color:#7C3AED;">💡</div>
                        <h3 class="card-title">생존 회화 & 꿀팁</h3>
                    </div>
                    <div style="margin-bottom:15px;">
                        <div style="font-size:0.85rem; font-weight:700; color:#64748B; margin-bottom:8px;">필수 문장</div>
                        <div class="chip-container">
                            {''.join([f'<span class="chip purple">{l["phrase"]} ({l["meaning"]})</span>' for l in res_culture.get('language_tips', [])])}
                        </div>
                    </div>
                    <div style="background:#FFFBEB; padding:12px; border-radius:8px; border:1px solid #FCD34D; color:#92400E; font-size:0.9rem;">
                        <strong>👑 현지인 Tip:</strong> {res_culture.get('pro_tip', '예의를 지키면 환영받습니다!')}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # --- Tab 3: Safety ---
        with tab3:
            is_danger = "Danger" in res_safety.get('warning_level', '')
            
            st.markdown(f"""
            <div class="pro-card" style="border-left: 6px solid {'#EF4444' if is_danger else '#10B981'};">
                <div style="display:flex; justify-content:space-between; align-items:start;">
                    <div>
                        <h3 style="margin:0; color:{'#EF4444' if is_danger else '#059669'}; font-size:1.3rem;">
                            {'🚨 긴급 안전 주의보' if is_danger else '✅ 안전 여행 가이드'}
                        </h3>
                        <p style="margin:10px 0 0 0; font-weight:600; color:#334155; font-size:1.05rem;">
                            {res_safety['scam_alert'].get('title')}
                        </p>
                        <p style="color:#64748B; margin-top:5px; line-height:1.6;">
                            {res_safety['scam_alert'].get('detail')}
                        </p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            col_l, col_r = st.columns(2)
            
            with col_l:
                st.markdown(f"""
                <div class="pro-card">
                    <div class="card-header">
                        <div class="card-icon" style="background:#FFEDD5; color:#EA580C;">⚖️</div>
                        <h3 class="card-title">현지 법률 (속지주의)</h3>
                    </div>
                    <div style="color:#475569; line-height:1.7; font-size:0.95rem;">
                        {res_safety.get('legal_local')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
            with col_r:
                 st.markdown(f"""
                <div class="pro-card">
                    <div class="card-header">
                        <div class="card-icon" style="background:#FEE2E2; color:#DC2626;">🇰🇷</div>
                        <h3 class="card-title">한국 법률 (속인주의)</h3>
                    </div>
                    <div style="color:#475569; line-height:1.7; font-size:0.95rem;">
                        {res_safety.get('legal_korea')}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="pro-card">
                <div class="card-header">
                    <div class="card-icon" style="background:#E0E7FF; color:#4338CA;">💊</div>
                    <h3 class="card-title">의료 및 응급 상황</h3>
                </div>
                <div style="margin-bottom:20px;">
                    <div style="font-size:0.85rem; font-weight:700; color:#64748B; margin-bottom:8px;">반입 주의 성분</div>
                    <div class="chip-container">
                        {''.join([f'<span class="chip red">🚫 {ing}</span>' for ing in res_safety.get('meds_ingredients', [])])}
                    </div>
                </div>
                <div style="background:#F1F5F9; padding:16px; border-radius:10px; color:#334155; line-height:1.6; font-size:0.95rem;">
                    {res_safety.get('meds_detail')}
                </div>
                <div style="margin-top:20px; border-top:1px solid #E2E8F0; padding-top:15px; color:#0F172A; font-weight:600;">
                    📞 대사관/영사관 연락처: <span style="color:#3B82F6;">{res_safety.get('embassy')}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

elif not destination:
    st.info("👈 사이드바에서 여행 정보를 입력하고 계획을 시작하세요.")
