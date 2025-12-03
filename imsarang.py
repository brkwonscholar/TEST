import streamlit as st
import json
import os
import uuid
from datetime import datetime

# 페이지 세팅
st.set_page_config(
    page_title="교환독서 — 인덱스로 사람을 만나다",
    page_icon="📚",
    layout="centered"
)

# ===== 감성 스타일 CSS (기존 CSS 완전삭제 후 이것만 사용) =====
st.markdown("""
<style>
@font-face {
    font-family: 'Pretendard';
    src: url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/woff2/Pretendard-Regular.subset.woff2')
         format('woff2');
    font-weight: 400;
}

html, body, [class*="css"], div, span, p, label, button, input, textarea {
    font-family: 'Pretendard', sans-serif !important;
    border-radius: 6px !important;
}

/* 카드 스타일 */
.book-card {
    background: #f7f5ef;
    border-left: 6px solid #9c8f7a;
    padding: 14px 18px;
    margin: 14px 0;
    border-radius: 10px;
}

/* 감정칩 */
.emotion-chip {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 10px;
    font-size: 13px;
    margin: 3px;
}

/* 헤더 */
.app-header {
    background: #e9f2e3;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #cfdac9;
}
</style>
""", unsafe_allow_html=True)

# ===== 데이터 파일 =====
DATA_FILE = "bookmatch_data.json"

EMOTION_GROUPS = {
    "1. 따뜻한 감정": ["위로됨","따뜻함","편안함","공감됨","여운","잔잔함"],
    "2. 무거운 감정": ["불안","외로움","슬픔","공허","답답함","두려움"],
    "3. 강한 감정": ["분노","충격","씁쓸함","혼란","거부감","강렬"],
    "4. 에너지/성장 감정": ["희망","다짐","용기","성장","영감","반짝임"],
    "5. 분석/거리감": ["냉정함","객관적","거리감","사색적","비판적","분석적"],
}

# 감정 색상 (자연색 계열)
EMOTION_COLORS = {
    # 따뜻
    "위로됨":"#d8f5c0","따뜻함":"#c7f9d4","편안함":"#b5efc2","공감됨":"#a3e4b0","여운":"#92d99e","잔잔함":"#81ce8c",
    # 무거움
    "불안":"#b8a6d9","외로움":"#a996cc","슬픔":"#9b87bf","공허":"#8c78b2","답답함":"#7e69a6","두려움":"#6f5a99",
    # 강렬
    "분노":"#d88c8c","충격":"#d37979","씁쓸함":"#cd6767","혼란":"#c65454","거부감":"#bf4141","강렬":"#b92f2f",
    # 성장
    "희망":"#d8e8c9","다짐":"#caddb7","용기":"#bcd3a5","성장":"#aec893","영감":"#a0bd82","반짝임":"#91b270",
    # 분석
    "냉정함":"#e8e8e3","객관적":"#deded9","거리감":"#d4d4cf","사색적":"#c9c9c4","비판적":"#bfbfba","분석적":"#b5b5b0",
}

# JSON 파일 없으면 생성
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({"books": []}, f, ensure_ascii=False, indent=2)

def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

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

# 앱 헤더 (📚🌱 추가)
st.markdown("<div class='app-header'><h2 style='margin:0'>📚🌱 교환독서 — 인덱스로 사람을 만나다</h2><div style='color:#6b6b6b'>책의 문장과 감정을 기록하고 비교해보세요.</div></div>", unsafe_allow_html=True)
st.write("")

# 닉네임
if "nickname" not in st.session_state:
    st.session_state.nickname = ""
with st.expander("내 정보 (닉네임 입력)"):
    st.session_state.nickname = st.text_input("닉네임", value=st.session_state.nickname)
    st.write("사용자 ID:", new_user_id())

# 1) 책 입력
st.header("1. 책 정보 입력")
book_title = st.text_input("책 제목")
book_author = st.text_input("저자 (선택)")

col1, col2 = st.columns([1,3])
with col1:
    add_book_btn = st.button("이 책 추가/선택")
with col2:
    st.caption("동일 제목 존재 시 기존 데이터 사용")

data = load_data()
books = data.get("books", [])
selected_book = None

if add_book_btn and book_title.strip():
    matched = None
    for b in books:
        if b["title"].strip() == book_title.strip() and (not book_author.strip() or b.get("author","") == book_author.strip()):
            matched = b; break
    if matched:
        selected_book = matched
        st.success(f"기존 책 선택: {matched['title']}")
    else:
        new_book = {"id": str(uuid.uuid4())[:8], "title": book_title.strip(), "author": book_author.strip(), "created_at": datetime.utcnow().isoformat(), "entries": []}
        books.append(new_book); data["books"]=books; save_data(data)
        selected_book = new_book; st.success("새 책 추가 완료")

book_options = {f"{b['title']} — {b.get('author','')}": b for b in books}
choice = st.selectbox("기존 책 선택", options=["선택없음"] + list(book_options.keys()))
if choice != "선택없음":
    selected_book = book_options[choice]
if selected_book:
    st.markdown(f"**선택된 책:** {selected_book['title']} {selected_book.get('author','')}")

# 2) 인덱스 기록
if selected_book:
    st.header("2. 인덱스 문장 기록")

    with st.form("add_entry_form"):
        page_num = st.text_input("페이지/위치")
        quote = st.text_area("인상 깊었던 문장")
        st.write("감정 선택:")
        
        cols = st.columns(5)
        selected_emotions = []
        all_emotions_flat = []
        for grp in EMOTION_GROUPS.values():
            all_emotions_flat += grp
        for idx, emo in enumerate(all_emotions_flat):
            with cols[idx % 5]:
                if st.checkbox(emo, key=f"emo_{emo}"):
                    selected_emotions.append(emo)
        
        summary = st.text_input("요약 (선택)")
        private_note = st.text_area("나만 보는 메모 (선택)")
        submitted = st.form_submit_button("저장")

    if submitted:
        if not quote.strip():
            st.error("문장을 반드시 입력하세요.")
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
                    b["entries"].append(entry); selected_book = b; break
            data["books"] = books; save_data(data)
            st.success("저장되었습니다")

    # 저장된 인덱스 표시
    st.subheader("이 책에 저장된 인덱스들")
    for e in selected_book.get("entries", [])[::-1]:
        st.markdown("<div class='book-card'>", unsafe_allow_html=True)
        st.write(f"**{e.get('nickname','익명')}** — {e.get('page','')}")
        st.write(e.get("quote"))
        chips = "".join([color_chip_html(em) for em in e.get("emotions", [])])
        st.markdown(chips, unsafe_allow_html=True)
        if e.get("summary"): st.caption("요약: " + e.get("summary"))
        st.markdown("</div>", unsafe_allow_html=True)

    # 3) 매칭
    st.header("3. 비슷한/다른 관점 찾기")
    my_entries = [e for e in selected_book.get("entries", []) if e["user_id"] == new_user_id()]
    others = [e for e in selected_book.get("entries", []) if e["user_id"] != new_user_id()]
    
    if not my_entries:
        st.info("먼저 인덱스를 기록해주세요!")
    else:
        my_quotes = set([e['quote'] for e in my_entries])
        my_emotions = set(sum([e['emotions'] for e in my_entries], []))
        my_set = my_quotes | my_emotions

        others_by_user = {}
        for e in others:
            uid = e["user_id"]
            others_by_user.setdefault(uid, {"nickname": e.get("nickname","익명"), "quotes": set(), "emotions": set(), "entries": []})
            others_by_user[uid]["quotes"].add(e["quote"])
            others_by_user[uid]["emotions"].update(e.get("emotions", []))
            others_by_user[uid]["entries"].append(e)

        scores = []
        for uid, info in others_by_user.items():
            other_set = info["quotes"] | info["emotions"]
            sim = jaccard(my_set, other_set)
            scores.append((sim, uid, info))

        scores.sort(reverse=True, key=lambda x: x[0])

        top_similar = [s for s in scores if s[0] > 0][:3]
        top_different = [s for s in sorted(scores, key=lambda x: x[0]) if s[0] < 0.5][:3]

        st.subheader("비슷한 관점 (최대 3명)")
        if not top_similar:
            st.write("아직 비슷한 관점의 사용자가 없습니다.")
        else:
            for sim, uid, info in top_similar:
                st.markdown(f"**{info['nickname']}** — 유사도: {sim:.2f}")
                sample = info['entries'][-1]
                st.write(sample['quote'])
                chips = "".join([color_chip_html(em) for em in info['emotions']])
                st.markdown(chips, unsafe_allow_html=True)
                if sample.get("summary"):
                    st.caption("요약: " + sample["summary"])
                st.write("---")

        st.subheader("다른 관점 (최대 3명)")
        if not top_different:
            st.write("충분한 비교 대상이 없습니다.")
        else:
            for sim, uid, info in top_different:
                st.markdown(f"**{info['nickname']}** — 유사도: {sim:.2f}")
                sample = info['entries'][-1]
                st.write(sample['quote'])
                chips = "".join([color_chip_html(em) for em in info['emotions']])
                st.markdown(chips, unsafe_allow_html=True)
                if sample.get("summary"):
                    st.caption("요약: " + sample["summary"])
                st.write("---")

st.markdown("---")
st.caption("데이터는 로컬 파일(bookmatch_data.json)에 저장됩니다.")
