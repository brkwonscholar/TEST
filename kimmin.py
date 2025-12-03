import streamlit as st
import random
import time

# ======================================================
# Page Config
# ======================================================
st.set_page_config(page_title="GreenCycle 재활용 게임", page_icon="♻️")

# ======================================================
# Session State Initialization
# ======================================================
default_states = {
    "logged_in": False,
    "student_id": "",
    "student_name": "",
    "points": 0,
    "combo": 0,
    "stage": 1,
    "start_time": time.time(),
    "current_index": None,
    "wrong_answers": [],
    "game_active": False,
    "difficulty": "Easy",
    "total_co2_save": 0,
    "level": "새싹 🌱"
}
for key, val in default_states.items():
    if key not in st.session_state:
        st.session_state[key] = val

MAX_STAGE = 10

# ======================================================
# 쓰레기 데이터 확장 20개
# ======================================================
ITEMS = [
    ("생수병", "플라스틱", "라벨/뚜껑 분리 후 압착!", 25),
    ("우유팩", "종이", "헹구고 펼쳐서 종이팩 전용함!", 30),
    ("도시락 용기", "플라스틱", "음식물 제거 후 배출 필수!", 22),
    ("알루미늄 캔", "금속", "헹구고 찌그러뜨려요!", 40),
    ("유리병", "유리", "뚜껑은 분리 배출!", 35),
    ("종이 영수증", "일반쓰레기", "감열지 → 재활용 불가!", 5),
    ("플라스틱 빨대", "일반쓰레기", "작아서 재활용 불가!", 8),
    ("음식물", "음식물쓰레기", "이물질 제거 후!", 15),
    ("과자 봉지", "일반쓰레기", "복합재질 → 재활용 어려움!", 5),
    ("택배 박스", "종이", "테이프 제거 후 접어서!", 30),
    ("치킨 뼈", "일반쓰레기", "뼈는 음식물 아님!", 10),
    ("계란 껍질", "일반쓰레기", "음식물 아님!", 10),
    ("비닐봉지", "일반쓰레기", "오염이 많아 분리 어려움!", 7),
    ("샴푸통", "플라스틱", "내용물 제거 후 배출!", 25),
    ("캔 커피", "금속", "씻고 배출!", 35),
    ("종이컵", "일반쓰레기", "코팅되어 일반쓰레기!", 5),
    ("화장지", "일반쓰레기", "섬유 구조상 재활용 불가!", 3),
    ("유리 조각", "유리", "신문지에 싸서 배출!", 28),
    ("볼펜", "일반쓰레기", "재질 다양 → 일반쓰레기!", 6),
    ("피자박스", "일반쓰레기", "기름 오염 → 일반쓰레기!", 8),
]

BINS = ["플라스틱", "종이", "금속", "유리", "음식물쓰레기", "일반쓰레기"]

# ======================================================
# Functions
# ======================================================
def pick_question():
    st.session_state.current_index = random.randrange(len(ITEMS))
    st.session_state.start_time = time.time()

def start_game():
    st.session_state.points = 0
    st.session_state.combo = 0
    st.session_state.stage = 1
    st.session_state.wrong_answers = []
    st.session_state.total_co2_save = 0
    st.session_state.game_active = True
    pick_question()

def logout():
    for key, val in default_states.items():
        st.session_state[key] = val
    st.rerun()

def update_level():
    p = st.session_state.points
    if p >= 300:
        st.session_state.level = "지구 수호자 🌍"
    elif p >= 200:
        st.session_state.level = "환경 영웅 🌱"
    elif p >= 100:
        st.session_state.level = "초록 시민 🍀"
    else:
        st.session_state.level = "새싹 🌱"


# ======================================================
# Sidebar Navigation
# ======================================================
menu = st.sidebar.selectbox("메뉴 선택", ["홈", "게임하기", "오답 복습", "포인트 상점", "마이페이지"])

st.sidebar.title("👤 사용자 정보")
if st.session_state.logged_in:
    st.sidebar.write(f"학번: **{st.session_state.student_id}**")
    st.sidebar.write(f"이름: **{st.session_state.student_name}**")
    st.sidebar.write(f"등급: **{st.session_state.level}**")
    if st.sidebar.button("로그아웃"):
        logout()

# ======================================================
# 로그인 화면
# ======================================================
if not st.session_state.logged_in:
    st.title("🎓 GreenCycle 로그인")
    student_id = st.text_input("학번 (8자리)", max_chars=8)
    student_name = st.text_input("이름")
    if st.button("로그인"):
        if len(student_id) == 8 and student_name.strip():
            st.session_state.logged_in = True
            st.session_state.student_id = student_id
            st.session_state.student_name = student_name
            st.success("로그인 성공!🌱")
            st.rerun()
        else:
            st.error("학번과 이름을 정확히 입력해주세요!")
    st.stop()


# ======================================================
# 홈
# ======================================================
if menu == "홈":
    st.title("🌍 GreenCycle - 친환경 캠퍼스")
    st.write("게임으로 재활용을 배우고 보상을 받아가세요! 🎮♻️")
    st.stop()


# ======================================================
# 오답 복습
# ======================================================
if menu == "오답 복습":
    st.title("📚 오답 복습")
    if not st.session_state.wrong_answers:
        st.info("오답이 없습니다! 🎉")
    else:
        for i, (name, correct, tip) in enumerate(st.session_state.wrong_answers):
            with st.expander(f"❌ {i+1}. {name}"):
                st.write(f"정답: **{correct}**")
                st.write(f"💡 Tip: {tip}")
    st.stop()


# ======================================================
# 포인트 상점
# ======================================================
if menu == "포인트 상점":
    st.title("🏪 포인트 상점")
    st.write(f"현재 포인트: **{st.session_state.points}점**")

    shop_items = {
        "🥤 교내카페 1천원 할인": 100,
        "🍪 편의점 간식 쿠폰": 80,
        "🎁 친환경 굿즈 추첨권": 200
    }

    for item, cost in shop_items.items():
        if st.button(f"{item} - {cost}점"):
            if st.session_state.points >= cost:
                st.session_state.points -= cost
                st.success(f"{item} 교환 완료! 🎉")
            else:
                st.warning("포인트가 부족합니다 😥")
    st.stop()


# ======================================================
# 마이페이지
# ======================================================
if menu == "마이페이지":
    st.title("👤 마이페이지")
    update_level()
    st.write(f"🌱 등급: **{st.session_state.level}**")
    st.write(f"🌳 누적 탄소 절감: **{st.session_state.total_co2_save}g CO₂**")
    st.write(f"🎯 누적 포인트: **{st.session_state.points}점**")
    st.stop()


# ======================================================
# 게임하기
# ======================================================
st.title("♻️ GreenCycle 재활용 게임")

difficulty_choice = st.radio("난이도 선택", ["Easy", "Normal", "Hard"], index=["Easy","Normal","Hard"].index(st.session_state.difficulty))
if st.button("게임 시작 / 다시 시작 🎮"):
    st.session_state.difficulty = difficulty_choice
    start_game()
    st.rerun()

if not st.session_state.game_active:
    st.write("왼쪽에서 게임을 시작해주세요! 😊")
    st.stop()

difficulty = st.session_state.difficulty
stage = st.session_state.stage
name, correct_bin, tip, co2 = ITEMS[st.session_state.current_index]

st.subheader(f"🔥 Stage {min(stage, MAX_STAGE)}/{MAX_STAGE}")
st.progress(min(stage, MAX_STAGE) / MAX_STAGE)
st.write(f"🗑 쓰레기: **{name}**")


# -----------------------------
# 개선된 안전 카운트다운 타이머
# -----------------------------
if difficulty == "Easy":
    time_limit = None
elif difficulty == "Normal":
    time_limit = 12
else:  # Hard
    time_limit = 8

if time_limit is not None:
    elapsed = time.time() - st.session_state.start_time
    remain = int(time_limit - elapsed)

    if remain <= 0:
        penalty = 5 if difficulty == "Normal" else 10
        st.error(f"⏱ 시간 초과! 자동 오답 처리 (-{penalty}점)")
        st.session_state.combo = 0
        st.session_state.points -= penalty
        st.session_state.wrong_answers.append((name, correct_bin, tip))
        st.session_state.stage += 1

        if st.session_state.stage > MAX_STAGE:
            st.balloons()
            update_level()
            st.success("🎉 게임 종료!")
            st.session_state.game_active = False
        else:
            pick_question()
        st.rerun()

    # 색 변화로 긴장감
    if remain <= 3:
        st.markdown(f"<span style='color:red;font-size:24px;'>⏱ {remain}초</span>", unsafe_allow_html=True)
    elif remain <= 7:
        st.markdown(f"<span style='color:orange;font-size:22px;'>⏱ {remain}초</span>", unsafe_allow_html=True)
    else:
        st.markdown(f"<span style='color:green;font-size:20px;'>⏱ {remain}초</span>", unsafe_allow_html=True)


# -----------------------------
# 정답 선택
# -----------------------------
clicked = st.radio("어디에 버릴까요?", BINS)

if st.button("판정하기"):
    if difficulty == "Easy": base, penalty = 10, 0
    elif difficulty == "Normal": base, penalty = 15, 5
    else: base, penalty = 20, 10

    if clicked == correct_bin:
        st.session_state.combo += 1
        gained = base + 5 * (st.session_state.combo - 1)
        st.session_state.points += gained
        st.session_state.total_co2_save += co2
        st.success(f"🎯 정답! +{gained}점")
    else:
        st.session_state.combo = 0
        st.session_state.points -= penalty
        st.session_state.wrong_answers.append((name, correct_bin, tip))
        st.error(f"❌ 오답! 정답: **{correct_bin}** (-{penalty}점)")

    with st.expander("📘 학습하기"):
        st.write(f"💡 Tip: {tip}")
        st.write(f"🌳 나무 약 **{round(co2/50,2)}그루** 절감 효과!**")

    st.session_state.stage += 1
    if st.session_state.stage > MAX_STAGE:
        st.balloons()
        update_level()
        st.success("🎉 게임 종료!")
        st.session_state.game_active = False
    else:
        pick_question()

    st.rerun()
