import streamlit as st
import json
import os
import uuid
from datetime import datetime

# ==========================================
# 1. 페이지 및 스타일 설정
# ==========================================
st.set_page_config(
    page_title="교환독서 — 인덱스로 사람을 만나다",
    page_icon="📚",
    layout="centered"
)

# CSS 정리 (글자 겹침 방지를 위해 줄 간격 및 마진 조정)
st.markdown("""
<style>
    /* 폰트 설정 */
    @font-face {
        font-family: 'Pretendard';
        src: url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/woff2/Pretendard-Regular.subset.woff2') format('woff2');
        font-weight: 400;
    }
    
    /* 전체 폰트 적용 및 줄간격 확보 */
    html, body, [class*="css"], div, span, p, label, button, input, textarea {
        font-family: 'Pretendard', sans-serif !important;
        line-height: 1.6 !important; 
    }

    /* 카드 스타일 */
    .book-card {
        background-color: #f9f7f2;
        border-left: 5px solid #9c8f7a;
        padding: 16px 20px;
        margin-bottom: 16px; /* 카드 간 간격 확보 */
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    /* 감정 칩 스타일 */
    .emotion-chip {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 15px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 4px 4px 4px 0; /* 칩 간 간격 확보 */
        color: #333;
    }

    /* 헤더 스타일 */
    .app-header {
        background: #e9f2e3;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #cfdac9;
        margin-bottom: 25px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 데이터 및 상수 설정
# ==========================================
DATA_FILE = "bookmatch_data.json"

# 감정 데이터 (리스트 합치기)
EMOTION_GROUPS = {
    "따뜻한 감정": ["위로됨","따뜻함","편안함","공감됨","여운","잔잔함"],
    "무거운 감정": ["불안","외로움","슬픔","공허","답답함","두려움"],
    "강한 감정": ["분노","충격","씁쓸함","혼란","거부감","강렬"],
    "성장 감정": ["희망","다짐","용기","성장","영감","반짝임"],
    "이성적 감정": ["냉정함","객관적","거리감","사색적","비판적","분석적"],
}

# 모든 감정을 하나의 리스트로 변환 (선택박스용)
ALL_EMOTIONS = []
for emo_list in EMOTION_GROUPS.values():
    ALL_EMOTIONS.extend(emo_list)

# 감정별 색상 코드
EMOTION_COLORS = {
    "위로됨":"#d8f5c0", "따뜻함":"#c7f9d4", "편안함":"#b5efc2", "공감됨":"#a3e4b0", "여운":"#92d99e", "잔잔함":"#81ce8c",
    "불안":"#b8a6d9", "외로움":"#a996cc", "슬픔":"#9b87bf", "공허":"#8c78b2", "답답함":"#7e69a6", "두려움":"#6f5a99",
    "분노":"#d88c8c", "충격":"#d37979", "씁쓸함":"#cd6767", "혼란":"#c65454", "거부감":"#bf4141", "강렬":"#b92f2f",
    "희망":"#d8e8c9", "다짐":"#caddb7", "용기":"#bcd3a5", "성장":"#aec893", "영감":"#a0bd82", "반짝임":"#91b270",
    "냉정함":"#e8e8e3", "객관적":"#deded9", "거리감":"#d4d4cf", "사색적":"#c9c9c4", "비판적":"#bfbfba", "분석적":"#b5b5b0"
}

# ==========================================
# 3. 함수 정의
# ==========================================
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"books": []}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"books": []}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_user_id():
    if "user_id" not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())[:8]
    return st.session_state.user_id

def render_chips(emotion_list):
    html = ""
    for emo in emotion_list:
        color = EMOTION_COLORS.get(emo, "#eee")
        html += f"<span class='emotion-chip' style='background:{color}'>{emo}</span>"
    return html

def calculate_jaccard(set_a, set_b):
    if not set_a and not set_b: return 0.0
    union = len(set_a | set_b)
    if union == 0: return 0.0
    return len(set_a & set_b) / union

# ==========================================
# 4. 메인 UI 구성
# ==========================================

# 헤더
st.markdown("""
<div class='app-header'>
    <h2 style='margin:0'>📚🌱 교환독서</h2>
    <div style='color:#6b6b6b; margin-top:5px;'>인덱스로 취향이 통하는 사람을 만나보세요</div>
</div>
""", unsafe_allow_html=True)

# 사이드바 (사용자 설정)
with st.sidebar:
    st.header("내 정보")
    if "nickname" not in st.session_state:
        st.session_state.nickname = ""
    st.session_state.nickname = st.text_input("닉네임", value=st.session_state.nickname, placeholder="닉네임을 입력하세요")
    st.caption(f"User ID: {get_user_id()}")
    st.divider()
    st.info("데이터는 로컬 파일(json)에 저장됩니다.")

# 데이터 로드
data = load_data()
books = data.get("books", [])

# --- [섹션 1] 책 선택하기 ---
st.subheader("1. 책 선택하기")

col1, col2 = st.columns([2, 1])
with col1:
    # 기존 책 목록 생성
    book_map = {f"{b['title']} ({b.get('author','미상')})": b for b in books}
    selected_book_name = st.selectbox("기존에 등록된 책 선택", ["새로운 책 등록"] + list(book_map.keys()))

selected_book = None
if selected_book_name != "새로운 책 등록":
    selected_book = book_map[selected_book_name]
else:
    with st.expander("새로운 책 등록하기", expanded=True):
        new_title = st.text_input("책 제목")
        new_author = st.text_input("저자")
        if st.button("책 등록"):
            if new_title.strip():
                new_book_entry = {
                    "id": str(uuid.uuid4())[:8],
                    "title": new_title.strip(),
                    "author": new_author.strip(),
                    "created_at": datetime.utcnow().isoformat(),
                    "entries": []
                }
                books.append(new_book_entry)
                data["books"] = books
                save_data(data)
                st.success(f"'{new_title}' 등록 완료! 위 목록에서 선택해주세요.")
                st.rerun()
            else:
                st.error("책 제목을 입력해주세요.")

# --- [섹션 2] 기록하기 ---
if selected_book:
    st.divider()
    st.subheader(f"📖 {selected_book['title']} 기록하기")

    with st.form("entry_form"):
        col_page, col_empty = st.columns([1, 3])
        with col_page:
            page_num = st.text_input("페이지", placeholder="p.123")
        
        quote = st.text_area("인상 깊은 문장", height=100)
        
        # [수정됨] 체크박스 대신 멀티셀렉트로 변경 (글자 겹침 해결)
        selected_emotions = st.multiselect("이 문장의 감정은? (여러 개 선택 가능)", ALL_EMOTIONS)
        
        summary = st.text_input("한줄 요약 (선택)")
        private_note = st.text_area("나만 보는 메모 (선택)", height=80)
        
        submit_btn = st.form_submit_button("기록 저장하기")

    if submit_btn:
        if not quote.strip():
            st.warning("문장을 입력해야 저장할 수 있습니다.")
        else:
            new_entry = {
                "id": str(uuid.uuid4())[:8],
                "user_id": get_user_id(),
                "nickname": st.session_state.nickname or "익명",
                "page": page_num,
                "quote": quote,
                "emotions": selected_emotions,
                "summary": summary,
                "private_note": private_note,
                "created_at": datetime.utcnow().isoformat(),
            }
            # 해당 책에 엔트리 추가
            for b in books:
                if b["id"] == selected_book["id"]:
                    b["entries"].append(new_entry)
                    break
            save_data(data)
            st.success("성공적으로 기록되었습니다!")
            st.rerun()

    # --- [섹션 3] 기록 모아보기 & 매칭 ---
    st.divider()
    tab1, tab2 = st.tabs(["📝 전체 기록 보기", "🤝 취향 매칭 분석"])

    with tab1:
        entries = selected_book.get("entries", [])
        if not entries:
            st.info("아직 기록된 내용이 없습니다.")
        else:
            for e in reversed(entries):
                st.markdown(f"""
                <div class='book-card'>
                    <small style='color:#888'>{e['nickname']} | {e['page']}</small>
                    <div style='font-size:1.1em; margin: 8px 0;'>{e['quote']}</div>
                    <div>{render_chips(e.get('emotions', []))}</div>
                    {f"<div style='margin-top:8px; color:#555; font-size:0.9em'>Comment: {e['summary']}</div>" if e.get('summary') else ""}
                </div>
                """, unsafe_allow_html=True)

    with tab2:
        current_user_entries = [e for e in selected_book['entries'] if e['user_id'] == get_user_id()]
        
        if not current_user_entries:
            st.warning("먼저 '기록하기' 탭에서 나의 인덱스를 1개 이상 남겨주세요.")
        else:
            # 나의 데이터 집합
            my_text_set = set(e['quote'] for e in current_user_entries)
            my_emo_set = set(emo for e in current_user_entries for emo in e.get('emotions', []))
            my_full_set = my_text_set | my_emo_set

            # 타 유저 데이터 집합
            other_users = {}
            for e in selected_book['entries']:
                if e['user_id'] != get_user_id():
                    uid = e['user_id']
                    if uid not in other_users:
                        other_users[uid] = {'nickname': e['nickname'], 'set': set(), 'entries': []}
                    other_users[uid]['set'].add(e['quote'])
                    for emo in e.get('emotions', []):
                        other_users[uid]['set'].add(emo)
                    other_users[uid]['entries'].append(e)
            
            # 유사도 계산
            results = []
            for uid, info in other_users.items():
                score = calculate_jaccard(my_full_set, info['set'])
                results.append((score, info))
            
            # 결과 정렬
            results.sort(key=lambda x: x[0], reverse=True)

            col_sim, col_diff = st.columns(2)
            
            with col_sim:
                st.markdown("### 😊 나와 비슷한")
                if not results:
                    st.write("아직 비교할 대상이 없습니다.")
                else:
                    for score, info in results[:3]:
                        if score > 0:
                            st.info(f"**{info['nickname']}**님 (유사도 {int(score*100)}%)")

            with col_diff:
                st.markdown("### ⚡ 새로운 관점")
                if not results:
                    st.write("아직 비교할 대상이 없습니다.")
                else:
                    # 유사도가 낮은 순서로 뒤집기
                    for score, info in sorted(results, key=lambda x: x[0])[:3]:
                        if score < 0.3: # 유사도가 너무 높은 사람은 제외
                            st.success(f"**{info['nickname']}**님 (유사도 {int(score*100)}%)")

else:
    st.info("👆 위에서 책을 선택하거나 새로 등록해주세요.")
