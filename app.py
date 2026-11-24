import sqlite3
import streamlit as st

# DB 연결 및 테이블 생성 (SQLite 사용)
conn = sqlite3.connect("travel_country_board.db", check_same_thread=False)
c = conn.cursor()
c.execute("""
    CREATE TABLE IF NOT EXISTS country_places (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        country TEXT,
        nickname TEXT,
        place_name TEXT,
        crowd_time TEXT,
        day_safety TEXT,
        night_safety TEXT,
        safety_memo TEXT,
        cookie_comment TEXT
    )
""")
conn.commit()

# 국가(게시판) 목록 정의
COUNTRIES = ["🇯🇵 일본", "🇰🇷 대한민국", "🇪🇺 유럽", "🌴 동남아", "🇺🇸 미주/기타"]

# UI 구성
st.title("🌍 국가별 여행지 안전 & 쿠키 스토리 맵")
st.write(
    "나라별 게시판을 선택해 현지 혼잡도·치안 정보와 장소에 얽힌 짧은 역사"
    " 이야기를 확인해보세요!"
)

# 1. 유저 등록 폼
with st.expander("✍️ 새로운 여행지 정보 & 쿠키 코멘트 등록하기", expanded=True):
  with st.form("community_form", clear_on_submit=True):
    col_c, col_u, col_p = st.columns([1.2, 1.2, 2])
    with col_c:
      selected_country = st.selectbox("국가 게시판 선택", COUNTRIES)
    with col_u:
      nickname = st.text_input("작성자 닉네임", placeholder="예: 부산여행러")
    with col_p:
      place_name = st.text_input(
          "장소 이름", placeholder="예: 후쿠오카 구시다 신사"
      )

    crowd_time = st.text_input(
        "🕒 언제 한적하고 언제 붐비나요?",
        placeholder=(
            "예: 오전 9시 이전엔 한적하고, 오후 2시쯤 단체 관광객으로 붐빔"
        ),
    )

    col1, col2 = st.columns(2)
    with col1:
      day_safety = st.selectbox(
          "☀️ 낮 안전도", ["매우 안전", "안전", "보통", "주의 필요"]
      )
    with col2:
      night_safety = st.selectbox(
          "🌙 밤 안전도", ["안전", "보통", "주의 필요", "위험 (야간 외출 자제)"]
      )

    safety_memo = st.text_input(
        "🚨 치안 및 사건·특이사항 메모",
        placeholder=(
            "예: 밤에는 주변 골목 조명이 어두워 큰길로 이동 추천 / 소매치기 주의"
        ),
    )
    cookie_comment = st.text_area(
        "🍪 쿠키 코멘트 (왜 유명하고, 어떤 역사가 있는 곳인가요?)",
        placeholder=(
            "예: 757년에 창건된 하카타의 총진수 신사로, 매년 7월 열리는 기온"
            " 야마카사 축제의 중심지예요!"
        ),
    )

    submitted = st.form_submit_button("게시판에 등록하기")

    if submitted and place_name:
      author = nickname if nickname.strip() else "익명의 여행자"
      c.execute(
          """
                INSERT INTO country_places (country, nickname, place_name, crowd_time, day_safety, night_safety, safety_memo, cookie_comment) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
          (
              selected_country,
              author,
              place_name,
              crowd_time,
              day_safety,
              night_safety,
              safety_memo,
              cookie_comment,
          ),
      )
      conn.commit()
      st.success(
          f"[{selected_country}] 게시판에 '{place_name}' 정보가"
          " 등록되었습니다!"
      )

st.divider()

# 2. 첫 화면 국가별 게시판 (탭 구성)
st.subheader("📌 국가별 여행지 게시판")
tabs = st.tabs(COUNTRIES)

for idx, country_name in enumerate(COUNTRIES):
  with tabs[idx]:
    cursor = c.execute(
        "SELECT id, nickname, place_name, crowd_time, day_safety, night_safety,"
        " safety_memo, cookie_comment FROM country_places WHERE country = ?"
        " ORDER BY id DESC",
        (country_name,),
    )
    rows = cursor.fetchall()

    if rows:
      st.caption(f"총 {len(rows)}개의 여행지 정보가 등록되어 있습니다.")
      for row in rows:
        (
            p_id,
            nickname,
            place_name,
            crowd_time,
            day_safety,
            night_safety,
            safety_memo,
            cookie_comment,
        ) = row

        with st.container(border=True):
          col_a, col_b = st.columns([5, 1])
          with col_a:
            st.markdown(f"### 📍 {place_name}")
            st.caption(f"작성자: **{nickname}**")
          with col_b:
            if st.button("삭제", key=f"del_{p_id}"):
              c.execute("DELETE FROM country_places WHERE id = ?", (p_id,))
              conn.commit()
              st.rerun()

          st.write(f"- **🕒 혼잡/한적 시간:** {crowd_time}")
          st.write(
              f"- **☀️ 낮 안전도:** {day_safety}  |  **🌙 밤 안전도:**"
              f" {night_safety}"
          )

          if safety_memo:
            st.warning(f"🚨 **치안/사건 기록:** {safety_memo}")
          if cookie_comment:
            st.info(f"🍪 **쿠키 코멘트 (역사 & 특징):** {cookie_comment}")
    else:
      st.info(
          f"아직 {country_name} 게시판에 등록된 글이 없습니다. 첫 번째 여행자가"
          " 되어 정보를 공유해보세요!"
      )
