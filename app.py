import streamlit as st
import pandas as pd
import numpy as np
from ultralytics import YOLO
from PIL import Image
import datetime
import os
import random
import cv2

# Try to import streamlit_webrtc, but handle if it's not installed
try:
    from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
    WEBRTC_AVAILABLE = True
except ImportError:
    WEBRTC_AVAILABLE = False

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="SolarGuard AI Pro",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================= GLOBAL STYLE =================
st.markdown("""
<style>
[data-testid="stAppViewContainer"]{
    background-image: url("https://solar.com.ng/wp-content/uploads/2024/06/What-Factors-to-Consider-When-Choosing-Solar-Panels-in-Nigeria-750x375.webp");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

/* overlay lighter (background clearer) */
[data-testid="stAppViewContainer"]::before{
    content:"";
    position:fixed;
    inset:0;
    background:rgba(7,18,30,0.25);
}

.main *{position:relative; z-index:1;}

.hero-box,.glass-box,.feature-box{
    background: rgba(15,35,55,0.72);
    backdrop-filter: blur(14px);
    border:1px solid rgba(255,255,255,0.12);
    border-radius:24px;
    padding:30px;
    margin-bottom:20px;
    box-shadow:0 8px 30px rgba(0,0,0,0.25);
}

.project-title{
    text-align:center;
    font-size:60px;
    font-weight:900;
    color:white;
}

.subtitle{
    text-align:center;
    color:#f8d66d;
    font-size:22px;
    font-weight:700;
}

/* ================= SIDEBAR ORANGE ================= */
section[data-testid="stSidebar"]{
    background: linear-gradient(180deg, #ff8c00, #ffb347);
}

section[data-testid="stSidebar"] *{
    color:white !important;
    font-weight:600;
}

/* dropdown */
div[data-baseweb="select"] > div{
    background-color:#ff8c00 !important;
    border-radius:12px !important;
    color:white !important;
}

/* Styling for Streamlit alerts/messages */
div[data-testid="stAlert"] {
    background-color: #333333 !important; /* Dark gray background */
    color: #ff8c00 !important; /* Orange text */
    border-left: 6px solid #ff8c00 !important; /* Orange border */
}

div[data-testid="stAlert"] div[data-testid="stMarkdownContainer"] p {
    color: #ff8c00 !important;
}

/* Styling for titles outside of specific boxes */
.main h2, .main h3, .main h4 {
    background-color: rgba(255, 140, 0, 0.15); /* Light orange background */
    padding: 10px 15px;
    border-radius: 8px;
    color: white;
    margin-bottom: 20px;
    margin-top: 20px;
}

</style>
""", unsafe_allow_html=True)

# ================= MODEL =================
@st.cache_resource
def load_model():
    # Looking for best.pt in the same directory (as uploaded to GitHub)
    model_path = 'best.pt'
    if os.path.exists(model_path):
        try:
            return YOLO(model_path)
        except Exception as e:
            st.error(f"Error loading model: {e}")
            return None
    else:
        st.warning(f"Model file '{model_path}' not found. Please ensure it's in the same directory as app.py on GitHub.")
        return None

model = load_model()

# ================= HELPER FUNCTIONS =================
def convert_to_infrared(image_pil):
    image_cv = np.array(image_pil)
    image_cv = cv2.cvtColor(image_cv, cv2.COLOR_RGB2BGR)
    gray_image = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
    infrared_simulated = cv2.applyColorMap(gray_image, cv2.COLORMAP_JET)
    infrared_pil = Image.fromarray(cv2.cvtColor(infrared_simulated, cv2.COLOR_BGR2RGB))
    return infrared_pil

# ================= SESSION STATE INITIALIZATION =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'entered_site' not in st.session_state:
    st.session_state.entered_site = False
if 'users' not in st.session_state:
    st.session_state.users = {'admin': 'solar2026'}

# ================= LOGIN / REGISTRATION PAGE =================
if not st.session_state.logged_in:
    st.markdown('<div class="project-title">☀️ SolarGuard AI Pro</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Smart Solar AI Monitoring</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass-box">', unsafe_allow_html=True)
    st.subheader("Login or Register")
    tab1, tab2 = st.tabs(["Login", "Register"])
    with tab1:
        st.markdown("#### Existing User Login")
        username_login = st.text_input("Username", key="username_login")
        password_login = st.text_input("Password", type="password", key="password_login")
        if st.button("Login", use_container_width=True, key="login_button"):
            if username_login in st.session_state.users and st.session_state.users[username_login] == password_login:
                st.session_state.logged_in = True
                st.session_state.current_user = username_login
                st.success(f"Welcome, {username_login}!")
                st.rerun()
            else:
                st.error("Invalid username or password")
    with tab2:
        st.markdown("#### New User Registration")
        username_register = st.text_input("New Username", key="username_register")
        password_register = st.text_input("New Password", type="password", key="password_register")
        confirm_password_register = st.text_input("Confirm Password", type="password", key="confirm_password_register")
        if st.button("Register", use_container_width=True, key="register_button"):
            if not username_register or not password_register or not confirm_password_register:
                st.warning("All fields are required.")
            elif username_register in st.session_state.users:
                st.error("Username already exists.")
            elif password_register != confirm_password_register:
                st.error("Passwords do not match.")
            else:
                st.session_state.users[username_register] = password_register
                st.success("Registration successful! Please log in.")
    st.markdown('</div>', unsafe_allow_html=True)

# ================= LANDING =================
elif not st.session_state.entered_site:
    st.markdown('<div class="project-title">☀️ SolarGuard AI Pro</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">AI Renewable Energy Intelligence</div>', unsafe_allow_html=True)
    st.markdown("## Welcome to Solar Intelligence Platform")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Panels", "1240+")
    c2.metric("Accuracy", "97%")
    c3.metric("Alerts", "12")
    c4.metric("Energy Saved", "32%")
    if st.button("🚀 Enter Dashboard", use_container_width=True):
        st.session_state.entered_site = True
        st.rerun()

# ================= DASHBOARD =================
else:
    st.sidebar.title("☀️ SolarGuard AI Pro")
    menu = st.sidebar.selectbox(
        "Navigation",
        ["Home Dashboard", "AI Analysis", "Smart Maintenance Prediction", "Self-Learning System", "Live Camera Analysis", "Video Analysis", "Reports", "About Us", "Contact"]
    )

    if menu == "Home Dashboard":
        st.markdown("## 📊 Smart Dashboard")
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Panels", "1,240")
        c2.metric("Healthy", "95%")
        c3.metric("Critical", "12")
        chart = pd.DataFrame(np.random.randn(24, 1), columns=["KWh"])
        st.area_chart(chart)

    elif menu == "AI Analysis":
        st.markdown("## 🤖 AI Multi Panel Analysis")
        files = st.file_uploader("Upload up to 5 images", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True)
        if files:
            cols = st.columns(min(len(files), 5))
            ir_cols = st.columns(min(len(files), 5))
            results_list = []
            for i, file in enumerate(files[:5]):
                img = Image.open(file)
                with cols[i]:
                    st.image(img, caption=f"Original: {file.name}", use_container_width=True)
                infrared_img = convert_to_infrared(img)
                with ir_cols[i]:
                    st.image(infrared_img, caption=f"Infrared: {file.name}", use_container_width=True)
                if model:
                    temp_path = f"temp_{i}.jpg"
                    img.save(temp_path)
                    res = model.predict(temp_path, conf=0.5)
                    if len(res[0].boxes) == 0:
                        label = "Clean"
                        score = 100
                    else:
                        label = model.names[int(res[0].boxes[0].cls[0])]
                        if label == 'Clean':
                            score = float(res[0].boxes[0].conf[0]) * 100
                        else:
                            score = (1 - float(res[0].boxes[0].conf[0])) * 100
                    os.remove(temp_path)
                else:
                    label = random.choice(["Clean", "Dust", "Crack", "Bird-Drop"])
                    score = random.randint(75, 99)
                results_list.append({"Panel": file.name, "Health Score": round(score, 1), "Status": label})
            st.markdown("### 🎯 Results")
            df = pd.DataFrame(results_list).sort_values(by="Health Score", ascending=False)
            st.dataframe(df, use_container_width=True)
            st.markdown("### Download Report")
            csv_report = df.to_csv(index=False).encode('utf-8')
            st.download_button(label="Download Results as CSV", data=csv_report, file_name="solar_analysis_report.csv", mime="text/csv", use_container_width=True)

    elif menu == "Live Camera Analysis":
        st.markdown("## 🎥 Live Camera Feed Analysis")
        if WEBRTC_AVAILABLE and model:
            st.info("Live camera is active. Point it at a solar panel.")
            # Basic implementation for streamlit-webrtc
            webrtc_streamer(key="live_camera", video_processor_factory=None)
        else:
            st.warning("Live camera analysis requires model and webrtc support.")

    elif menu == "Video Analysis":
        st.markdown("## 🎬 Video Upload and Analysis")
        uploaded_video = st.file_uploader("Upload a video file", type=['mp4', 'avi', 'mov'])
        if uploaded_video and model:
            tfile = "temp_video.mp4"
            with open(tfile, "wb") as f:
                f.write(uploaded_video.getbuffer())
            cap = cv2.VideoCapture(tfile)
            st_frame = st.empty()
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret: break
                results = model.predict(frame, conf=0.5, verbose=False)
                annotated_frame = results[0].plot()
                st_frame.image(annotated_frame, channels="BGR", use_container_width=True)
            cap.release()
            os.remove(tfile)

    elif menu == "About Us":
        st.markdown("## 🌍 About SolarGuard")
        st.write("SolarGuard AI Pro is an advanced artificial intelligence platform designed to revolutionize solar energy monitoring and maintenance...")

    elif menu == "Contact":
        st.markdown("## 📞 Contact")
        st.text_input("Name")
        st.text_input("Email")
        st.text_area("Message")
        st.button("Send")
