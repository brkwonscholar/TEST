import streamlit as st
import json
import os
import uuid
from datetime import datetime

# ==========================================
# 1. 페이지 설정
# ==========================================
st.set_page_config(
    page_title="교환독서 — 인덱스로 사람을 만나다",
    page_icon="📚",
    layout="centered"
)

# ==========================================
# 2. 스타일 설정 (겹침 문제 해결됨)
# ==========================================
st.markdown("""
<style>
    @font-face {
        font-family: 'Pretendard';
        src: url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/woff2/Pretendard-Regular.subset.woff2') format('woff2');
        font-weight: 400;
    }
    
    /* 전체 폰트 적용 (입력창 충돌 방지를 위해 선택자 최소화) */
    html, body, p, div {
        font-family: 'Pretendard', sans-serif !important;
    }

    /* 카드 스타일 */
    .book-card {
        background-color: #f9f7f2;
        border-left: 5px solid #9c8f7a;
        padding: 16px 20px;
        margin: 16px 0;
        border-radius: 8px;
        line-height: 1.6; /* 카드 내 문장만 줄간격 적용 */
    }

    /* 사용자 정보 박스 스타일 */
    .user-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
        border: 1px solid #dce1e6;
    }

    /* 감정 칩 스타일 */
    .emotion-chip {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 13px;
        margin: 2px;
        color: #333;
    }

    /* 헤더 */
    .app-header {
        background: #e9f2e3;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #cfdac9;
        margin-bottom: 20px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. 데이터 및 함수
# ==========================================
DATA_FILE = "bookmatch_data.json"

EMOTION_GROUPS = {
    "1. 따뜻한 감정": ["위로됨","따뜻함","편안함","공감됨","여운","잔잔함"],
    "2. 무거운 감정": ["불안","외로움","슬픔","공허","답답함","두려움"],
    "3. 강한 감정": ["분노","충격","씁쓸함","혼란","거부감","강렬"],
    "4. 에너지/성장": ["희망","다짐","용기","성장","영감","반짝임"],
    "5. 분석/거리감": ["냉정함","객관적","거리감","사색적","비판적","분석적"],
}

ALL_EMOTIONS = []
for grp in EMOTION_GROUPS.values():
    ALL_EMOTIONS.extend(grp)

EMOTION_COLORS = {
    "위로됨":"#d8f5c0","따뜻함":"#c7f9d4","편안함":"#b5efc2","공감됨":"#a3e4b0","여운":"#92d99e","잔잔함":"#81ce8c",
    "불안":"#b8a6d9","외로움":"#a996cc","슬픔":"#9b87bf","공허":"#8c78b2","답답함":"#7e69a6","두려움":"#6f5a99",
    "분노":"#d88c8c","충격":"#d37979","씁쓸함":"#cd6767","혼란":"#c65454","거부감":"#bf4141","강렬":"#b92f2f",
    "희망":"#d8e8c9","다짐":"#caddb7","용기":"#bcd3a5","성장":"#aec893","영감":"#a0bd82","반짝임":"#91b270",
    "냉정함":"#e8e8e3","객관적":"#deded9","거리감":"#d4d4cf","사색적":"#c9c9c4","비판적":"#bfbfba","분석적":"#b5b5b0",
}

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

def new_user_id():
    if "user_id" not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())[:8]
    return st.session_state.user_id

def color_chip_html(text):
    color = EMOTION_COLORS.get(text, "#eee")
    return f"<span class='emotion-chip' style='background:{color}'>{text}</span>"

def jaccard(set_a, set_b):
    if not set_a and not set_b: return 0.0
    inter = len(set_a & set_b)
    uni = len(set_a | set_b)
    return inter/uni if uni else 0.0

# ==========================================
# 4. 메인 화면 로직
# ==========================================

# 헤더
st.markdown("""
<div class='app-header'>
    <h2 style='margin:0'>📚🌱 교환독서</h2>
    <div style='color:#6b6b6b; margin-top:5px;'>인덱스로 취향이 통하는 사람을 만나보세요</div>
</div>
""", unsafe_allow_html=True)

# [수정됨] 내 정보 입력창 (Expander 대신 깔끔한 박스로 변경하여 겹침 방지)
st.markdown("<div class='user-box'>", unsafe_allow_html=True)
col_u1, col_u2 = st.columns([3, 1])
with col_u1:
    if "nickname" not in st.session_state:
        st.session_state.nickname = ""
    st.session_state.nickname = st.text_input("닉네임", value=st.session_state.nickname, placeholder="닉네임을 입력하세요")
with col_u2:
    st.write("") # 간격 맞춤용
    st.write("") 
    st.caption(f"ID: {new_user_id()}")
st.markdown("</div>", unsafe_allow_html=True)


# 1) 책 선택 섹션
st.subheader("1. 책 선택하기")

# 데이터 로드
data = load_data()
books = data.get("books", [])

# 기존 책 제목 리스트
book_options = {f"{b['title']} ({b.get('author','미상')})": b for b in books}

col_sel1, col_sel2 = st.columns([2, 1])
with col_sel1:
    # 선택박스
    choice_key = st.selectbox("등록된 책 목록", ["새로운 책 직접 입력"] + list(book_options.keys()))

selected_book = None
if choice_key != "새로운 책 직접 입력":
    selected_book = book_options[choice_key]
else:
    # 새 책 입력
    with st.container():
        st.info("새로운 책을 등록합니다.")
        new_title = st.text_input("책 제목")
        new_author = st.text_input("저자")
        if st.button("이 책 등록하기"):
            if new_title.strip():
                new_book = {
                    "id": str(uuid.uuid4())[:8], 
                    "title": new_title.strip(), 
                    "author": new_author.strip(), 
                    "created_at": datetime.utcnow().isoformat(), 
                    "entries": []
                }
                books.append(new_book)
                data["books"] = books
                save_data(data)
                st.success(f"'{new_title}' 등록 완료! 목록에서 선택해주세요.")
                st.rerun() # 새로고침
            else:
                st.error("책 제목을 입력해주세요.")

# 2) 인덱스 기록 섹션
if selected_book:
    st.markdown("---")
    st.subheader(f"📖 '{selected_book['title']}' 기록하기")

    with st.form("entry_form"):
        col_p, _ = st.columns([1, 3])
        with col_p:
            page_num = st.text_input("페이지", placeholder="ex) p.123")
        
        quote = st.text_area("인상 깊은 문장", height=100)
        
        st.write("감정 태그 (다중 선택 가능)")
        selected_emotions = st.multiselect("이 문장에서 느껴지는 감정은?", ALL_EMOTIONS)
        
        summary = st.text_input("한줄 코멘트 (선택)")
        private_note = st.text_area("나만 보는 메모 (선택)", height=70)
        
        if st.form_submit_button("기록 저장"):
            if not quote.strip():
                st.error("문장을 입력해주세요!")
            else:
                entry = {
                    "id": str(uuid.uuid4())[:8],
                    "user_id": new_user_id(),
                    "nickname": st.session_state.nickname or "익명",
                    "page": page_num.strip(),
                    "quote": quote.strip(),
                    "emotions": selected_emotions,
                    "summary": summary.strip(),
                    "private_note": private_note.strip(),
                    "created_at": datetime.utcnow().isoformat(),
                }
                for b in books:
                    if b["id"] == selected_book["id"]:
                        b["entries"].append(entry)
                        break
                save_data(data)
                st.success("저장되었습니다!")
                st.rerun()

    # 3) 결과 탭 (기록 보기 & 매칭)
    st.markdown("---")
    tab1, tab2 = st.tabs(["📝 전체 기록 보기", "🤝 취향 매칭 분석"])

    with tab1:
        entries = selected_book.get("entries", [])
        if not entries:
            st.info("아직 기록된 내용이 없습니다.")
        else:
            for e in reversed(entries):
                st.markdown(f"""
                <div class='book-card'>
                    <div style='color:#888; font-size:0.9em; margin-bottom:5px;'>
                        {e.get('nickname','익명')} | {e.get('page','')}
                    </div>
                    <div style='font-weight:500; margin-bottom:10px;'>{e.get('quote')}</div>
                    <div>{ "".join([color_chip_html(emo) for emo in e.get('emotions', [])]) }</div>
                    {f"<div style='margin-top:10px; padding-top:10px; border-top:1px dashed #ddd; color:#555;'>💬 {e['summary']}</div>" if e.get('summary') else ""}
                </div>
                """, unsafe_allow_html=True)

    with tab2:
        current_uid = new_user_id()
        my_entries = [e for e in selected_book['entries'] if e['user_id'] == current_uid]
        
        if not my_entries:
            st.warning("나의 기록이 먼저 필요합니다. 위에서 인덱스를 1개 이상 남겨주세요.")
        else:
            # 나의 데이터 셋
            my_set = set(e['quote'] for e in my_entries) | set(emo for e in my_entries for emo in e.get('emotions', []))
            
            # 타인 데이터 분석
            others = {}
            for e in selected_book['entries']:
                if e['user_id'] != current_uid:
                    oid = e['user_id']
                    if oid not in others:
                        others[oid] = {'nickname': e.get('nickname','익명'), 'set': set(), 'entries': []}
                    others[oid]['set'].add(e['quote'])
                    others[oid]['set'].update(e.get('emotions', []))
                    others[oid]['entries'].append(e)
            
            # 유사도 계산
            results = []
            for oid, info in others.items():
                score = jaccard(my_set, info['set'])
                results.append((score, info))
            
            results.sort(key=lambda x: x[0], reverse=True)
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("#### 😊 나와 비슷한")
                if not results: st.caption("아직 데이터가 부족합니다.")
                for score, info in results[:3]:
                    if score > 0:
                        st.success(f"{info['nickname']} (일치도 {int(score*100)}%)")
            
            with c2:
                st.markdown("#### ⚡ 새로운 관점")
                if not results: st.caption("아직 데이터가 부족합니다.")
                # 유사도가 낮은 순으로 정렬 (0점 제외, 너무 낮은 점수 위주)
                diff_results = sorted([r for r in results if r[0] < 0.4], key=lambda x: x[0])
                for score, info in diff_results[:3]:
                    st.info(f"{info['nickname']} (일치도 {int(score*100)}%)")

else:
    st.info("👆 위에서 책을 선택하거나 등록해주세요.")
