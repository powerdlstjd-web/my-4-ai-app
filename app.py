import streamlit as st
import google.generativeai as genai
from datetime import datetime
import pandas as pd

# 1. 페이지 설정 및 레이아웃
st.set_page_config(page_title="TeamSync Pro", page_icon="🛡️", layout="wide")

# CSS: React의 세련된 디자인 모방
st.markdown("""
    <style>
    .status-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 1rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .admin-badge {
        background-color: #e0e7ff;
        color: #4338ca;
        font-size: 10px;
        padding: 2px 6px;
        border-radius: 4px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. API 설정 및 Gemini 연결
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("설정에서 GOOGLE_API_KEY를 등록해주세요.")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# 3. 데이터 상태 관리 (React의 useState 역할)
if "team_data" not in st.session_state:
    st.session_state.team_data = [
        {"id": 1, "name": "김철수", "position": "팀장", "status": "사무실", "is_admin": True, "last_updated": "09:00"},
        {"id": 2, "name": "이영희", "position": "디자이너", "status": "회의 중", "is_admin": False, "last_updated": "10:30"},
        {"id": 3, "name": "박민수", "position": "개발자", "status": "외근", "is_admin": False, "last_updated": "11:00"},
    ]
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 사이드바: 로그인 및 내 상태 제어 ---
with st.sidebar:
    st.title("🛡️ TeamSync Pro")
    st.divider()
    
    user_names = [u["name"] for u in st.session_state.team_data]
    current_user_name = st.selectbox("사용자 로그인", user_names)
    
    st.subheader("내 상태 변경")
    status_options = ["사무실", "회의 중", "외근", "식사 중", "부재중"]
    new_status = st.radio("현재 상태 선택", status_options)
    
    if st.button("상태 업데이트"):
        now = datetime.now().strftime("%H:%M")
        for u in st.session_state.team_data:
            if u["name"] == current_user_name:
                u["status"] = new_status
                u["last_updated"] = now
        st.success(f"상태가 '{new_status}'로 변경되었습니다.")
        st.rerun()

# --- 메인 대시보드 ---
col_main, col_chat = st.columns([2, 1])

with col_main:
    # 상단 AI 요약 섹션
    st.subheader("🤖 AI 팀 상태 브리핑")
    if st.button("AI 분석 실행"):
        with st.spinner("분석 중..."):
            status_summary = str(st.session_state.team_data)
            prompt = f"다음 팀원들의 현황을 보고 협업을 위한 짧은 조언을 해줘: {status_summary}"
            response = model.generate_content(prompt)
            st.info(response.text)

    st.divider()

    # 팀원 카드 섹션 (React의 StatusCard 재현)
    st.subheader("실시간 팀원 현황")
    cols = st.columns(2)
    for i, user in enumerate(st.session_state.team_data):
        with cols[i % 2]:
            admin_tag = '<span class="admin-badge">ADMIN</span>' if user["is_admin"] else ""
            st.markdown(f"""
                <div class="status-card">
                    <div style="display: flex; justify-content: space-between;">
                        <b>{user['name']}</b> {admin_tag}
                    </div>
                    <div style="color: #64748b; font-size: 0.8rem;">{user['position']}</div>
                    <hr style="margin: 10px 0;">
                    <div style="font-size: 0.9rem;">
                        📍 현재 상태: <b>{user['status']}</b><br>
                        🕒 업데이트: {user['last_updated']}
                    </div>
                </div>
            """, unsafe_allow_html=True)
            if not user["is_admin"]:
                if st.button(f"{user['name']}에게 지원 요청", key=f"btn_{user['id']}"):
                    st.session_state.messages.append({"role": "system", "content": f"🚨 {current_user_name}님이 {user['name']}님께 지원을 요청했습니다."})

with col_chat:
    st.subheader("💬 상황 공유 채팅")
    
    # 채팅 내역 표시
    chat_container = st.container(height=500)
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

    # 채팅 입력
    if chat_input := st.chat_input("메시지를 입력하세요..."):
        st.session_state.messages.append({"role": "user", "content": f"[{current_user_name}] {chat_input}"})
        st.rerun()

# 사진 업로드 기능 (React의 handleFileUpload 대응)
st.sidebar.divider()
uploaded_file = st.sidebar.file_input("📸 현장 사진 공유", type=["jpg", "png", "jpeg"])
if uploaded_file:
    st.sidebar.image(uploaded_file, caption="업로드된 사진")
    if st.sidebar.button("채팅방에 사진 전송"):
        st.session_state.messages.append({"role": "user", "content": f"🖼️ {current_user_name}님이 사진을 공유했습니다."})
        st.rerun()
