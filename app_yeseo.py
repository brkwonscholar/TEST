import os
import streamlit as st
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


# -------------------------------
# 앱 제목
# -------------------------------
st.title("🛍️ AI 전통시장 플랫폼")

# -------------------------------
# 세션 초기화
# -------------------------------
if "products" not in st.session_state:
    st.session_state["products"] = []

if "reviews" not in st.session_state:
    st.session_state["reviews"] = {}

# -------------------------------
# 사용자 선택
# -------------------------------
role = st.radio("사용자 유형을 선택하세요👇", ["소비자", "판매자"])

# ===============================================================
# 🏪 판매자 화면
# ===============================================================
if role == "판매자":
    menu = st.sidebar.selectbox("📌 메뉴 선택", ["📦 상품 등록", "📊 등록 상품 관리"])

    # ---------------- 상품 등록 ----------------
    if menu == "📦 상품 등록":
        st.subheader("📦 상품 등록 및 AI 홍보 제작")
        name = st.text_input("상품명")
        desc = st.text_area("상품 설명")
        price = st.text_input("가격 (숫자만 입력)")
        market_name = st.text_input("시장명 입력 (예: 통인시장)")
        photo = st.file_uploader("상품 이미지 (선택)", type=["png","jpg","jpeg"])

        if st.button("✨ AI 홍보 생성 및 상품 등록"):
            if not name or not desc or not price or not market_name:
                st.warning("⚠ 상품명, 설명, 가격, 시장명은 필수입니다.")
            else:
                with st.spinner("AI 홍보 문구 생성 중..."):
                    prompt = f"""
                    아래 상품을 20~30대에게 매력적으로 홍보할 문구 작성:
                    상품명: {name}
                    설명: {desc}
                    가격: {price}원
                    형식: 제목, 2~3줄 소개, 해시태그 5개
                    """
                    res = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role":"user","content":prompt}]
                    )
                    ai_text = res.choices[0].message.content

                with st.spinner("AI 포스터 생성 중..."):
                    try:
                        img_res = client.images.generate(
                            model="dall-e-3",
                            prompt=f"{name}를 한국 전통시장 감성으로 표현한 포스터",
                            size="1024x1024"
                        )
                        poster_url = img_res.data[0].url
                    except Exception as e:
                        st.warning(f"이미지 생성 실패: {e}")
                        poster_url = None

                # 상품 저장
                st.session_state["products"].append({
                    "name": name,
                    "desc": desc,
                    "price": price,
                    "market": market_name,
                    "photo": photo,
                    "ai_text": ai_text,
                    "poster": poster_url
                })
                st.success("🎉 상품 등록 완료!")
                st.write(ai_text)
                if poster_url:
                    st.image(poster_url)

    # ---------------- 등록 상품 관리 ----------------
    elif menu == "📊 등록 상품 관리":
        st.subheader("📊 상품 관리 및 리뷰 답변/삭제")
        if not st.session_state["products"]:
            st.info("📭 등록된 상품이 없습니다.")
        else:
            for p in st.session_state["products"]:
                st.markdown("---")
                st.write(f"### {p['name']} — {p['price']}원")
                st.write(f"시장: {p.get('market','알수없음')}")
                st.write(p["ai_text"])
                if p.get("poster"):
                    st.image(p["poster"], width=300)

                reviews = st.session_state["reviews"].get(p["name"], [])
                if reviews:
                    st.write("⭐ 리뷰")
                    for idx, r in enumerate(reviews):
                        st.write(f"👤 {r['user']} | ⭐ {r['rating']}점")
                        st.write(f"💬 {r['text']}")
                        reply = st.text_input(f"답변 작성 ({r['user']})", value=r.get("reply",""), key=f"reply_{p['name']}_{idx}")
                        if st.button(f"답변 등록 ({r['user']})", key=f"btn_reply_{p['name']}_{idx}"):
                            reviews[idx]["reply"] = reply
                            st.success("✅ 답변 등록 완료")
                            st.experimental_rerun()
                        if st.button(f"리뷰 삭제 ({r['user']})", key=f"btn_del_{p['name']}_{idx}"):
                            reviews.pop(idx)
                            st.success("🗑️ 리뷰 삭제 완료")
                            st.experimental_rerun()
                else:
                    st.write("리뷰가 없습니다.")

                if st.button(f"상품 삭제 ({p['name']})", key=f"del_product_{p['name']}"):
                    st.session_state["products"].remove(p)
                    st.success("🗑️ 상품 삭제 완료")
                    st.experimental_rerun()

# ===============================================================
# 🛍 소비자 화면
# ===============================================================
elif role == "소비자":
    menu = st.sidebar.selectbox(
        "📌 메뉴 선택", ["🛒 상품 둘러보기", "🤖 AI 추천 받기", "📍 시장 안내"]
    )

    # ---------------- 상품 보기 + 리뷰 ----------------
    if menu == "🛒 상품 둘러보기":
        st.subheader("🛍 판매 중인 상품")
        market_filter = st.text_input("검색할 시장명을 입력하세요 (예: 통인시장)")

        filtered_products = [
            p for p in st.session_state["products"]
            if market_filter.lower() in p.get("market","").lower()
        ] if market_filter else st.session_state["products"]

        if not filtered_products:
            st.info("📭 해당 시장의 상품이 없습니다.")
        else:
            for product in filtered_products:
                st.markdown("---")
                st.write(f"### {product['name']} — 💰 {product['price']}원")
                if product.get("poster"):
                    st.image(product["poster"], width=300)
                st.write(product["ai_text"])

                # 리뷰 표시
                reviews = st.session_state["reviews"].setdefault(product["name"], [])
                if reviews:
                    st.write("⭐ 리뷰")
                    for r in reviews:
                        st.write(f"👤 {r['user']} | ⭐ {r['rating']}점")
                        st.write(f"💬 {r['text']}")
                        if r.get("reply"):
                            st.info(f"💬 판매자 답변: {r['reply']}")
                else:
                    st.write("리뷰가 없습니다.")

                # 리뷰 작성
                st.write("✏ 리뷰 작성")
                username = st.text_input(f"{product['name']} 리뷰 작성자", key=f"user_{product['name']}")
                rating = st.slider(f"{product['name']} 별점", 1, 5, key=f"rating_{product['name']}")
                review_text = st.text_area(f"{product['name']} 리뷰 내용", key=f"text_{product['name']}")

                if st.button(f"리뷰 등록 ({product['name']})"):
                    if username and review_text:
                        reviews.append({"user": username, "rating": rating, "text": review_text})
                        st.success("🎉 리뷰 등록 완료")
                        st.experimental_rerun()
                    else:
                        st.warning("⚠ 이름과 리뷰 내용을 입력해주세요.")

    # ---------------- AI 추천 ----------------
    elif menu == "🤖 AI 추천 받기":
        st.subheader("✨ AI 맞춤형 상품 추천")
        preference = st.text_input("당신의 취향 입력 (예: 단거 좋아함, 매운요리 찾는중)")

        if st.button("추천받기"):
            if not st.session_state["products"]:
                st.warning("⚠ 추천할 상품이 없습니다.")
            else:
                product_list = "\n".join([f"{p['name']} ({p.get('market','알수없음')}) : {p['desc']}" for p in st.session_state["products"]])
                prompt = f"""
                사용자 취향: {preference}
                아래 상품 중 추천하고 이유 설명:
                {product_list}
                """
                res = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role":"user","content":prompt}]
                )
                st.write(res.choices[0].message.content)

    # ---------------- 시장 안내 ----------------
    elif menu == "📍 시장 안내":
        st.subheader("📍 전통시장 안내 AI")
        market = st.text_input("시장 이름 입력 (예: 통인시장)")

        if st.button("검색"):
            prompt = f"""
            {market} 전통시장의 추천 코스, 인기 가게와 인기 상품, 위치 정보를 20~30대가 흥미롭게 읽을 수 있게 안내해줘.
            예: '통인시장: 엽전도시락 유명, 시장 내 기름떡볶이집 인기, 위치: 서울 종로구 ...'
            """
            res = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role":"user","content":prompt}]
            )
            st.write(res.choices[0].message.content)
