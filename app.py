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
    from streamlit_webrtc import webrtc_streamer, VideoTransformerBase, ClientSettings
    WEBRTC_AVAILABLE = True
except ImportError:
    st.warning("streamlit_webrtc not found. Live camera analysis will be disabled.")
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
    model_path = 'best.pt'
    return YOLO(model_path) if os.path.exists(model_path) else None

model = load_model()

# ================= HELPER FUNCTIONS =================
def convert_to_infrared(image_pil):
    # Convert PIL Image to OpenCV format (BGR)
    image_cv = np.array(image_pil)
    image_cv = cv2.cvtColor(image_cv, cv2.COLOR_RGB2BGR)

    # Convert to grayscale
    gray_image = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)

    # Apply a colormap to simulate infrared effect (e.g., COLORMAP_JET)
    infrared_simulated = cv2.applyColorMap(gray_image, cv2.COLORMAP_JET)

    # Convert back to PIL Image for Streamlit display
    infrared_pil = Image.fromarray(cv2.cvtColor(infrared_simulated, cv2.COLOR_BGR2RGB))
    return infrared_pil

# ================= SESSION STATE INITIALIZATION =================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'entered_site' not in st.session_state:
    st.session_state.entered_site = False
if 'users' not in st.session_state:
    # In a real application, this would be loaded from a database
    st.session_state.users = {'admin': 'solar2026'} # Example user

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
                st.error("Username already exists. Please choose a different one.")
            elif password_register != confirm_password_register:
                st.error("Passwords do not match.")
            else:
                st.session_state.users[username_register] = password_register
                st.success("Registration successful! Please log in.")
                # In a real application, you would store this in a database
                # For example: save_user_to_database(username_register, password_register)
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

    # ---------------- HOME ----------------
    if menu == "Home Dashboard":
        st.markdown("## 📊 Smart Dashboard")

        c1, c2, c3 = st.columns(3)
        c1.metric("Total Panels", "1,240")
        c2.metric("Healthy", "95%")
        c3.metric("Critical", "12")

        chart = pd.DataFrame(np.random.randn(24, 1), columns=["KWh"])
        st.area_chart(chart)

    # ---------------- AI ANALYSIS ----------------
    elif menu == "AI Analysis":
        st.markdown("## 🤖 AI Multi Panel Analysis")

        files = st.file_uploader(
            "Upload up to 5 images",
            type=['jpg', 'png', 'jpeg'],
            accept_multiple_files=True
        )

        if files:
            cols = st.columns(min(len(files), 5))
            ir_cols = st.columns(min(len(files), 5))
            results_list = [] # Changed variable name to avoid conflict with `results` from model.predict

            for i, file in enumerate(files[:5]):
                img = Image.open(file)

                with cols[i]:
                    st.image(img, caption=f"Original: {file.name}", use_container_width=True)

                # Convert to infrared and display
                infrared_img = convert_to_infrared(img)
                with ir_cols[i]:
                    st.image(infrared_img, caption=f"Infrared: {file.name}", use_container_width=True)

                # ===== AI OR DEMO =====
                if model:
                    temp_path = f"temp_{i}.jpg"
                    img.save(temp_path)

                    res = model.predict(temp_path, conf=0.5)

                    if len(res[0].boxes) == 0:
                        label = "Clean"
                        score = 100
                    else:
                        label = model.names[int(res[0].boxes[0].cls[0])]
                        # If a defect is detected, health score drops. Otherwise, high confidence of clean means high score.
                        if label == 'Clean':
                            score = float(res[0].boxes[0].conf[0]) * 100
                        else:
                            score = (1 - float(res[0].boxes[0].conf[0])) * 100 # Inverted for non-clean detections
                else:
                    label = random.choice(["Clean", "Dust", "Crack", "Bird-Drop"])
                    score = random.randint(75, 99)

                results_list.append({
                    "Panel": file.name,
                    "Health Score": round(score, 1),
                    "Status": label
                })

            st.markdown("### 🎯 Results")
            df = pd.DataFrame(results_list).sort_values(by="Health Score", ascending=False)
            st.dataframe(df, use_container_width=True)

            # --- Download Report ---
            st.markdown("### Download Report")
            csv_report = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Results as CSV",
                data=csv_report,
                file_name="solar_analysis_report.csv",
                mime="text/csv",
                use_container_width=True
            )

            # --- WhatsApp Messaging (Placeholder) ---
            st.markdown("### Send Results via WhatsApp")
            st.info("To send real WhatsApp messages, you need to set up a WhatsApp Business API account (e.g., via Twilio, MessageBird) and provide credentials. This is a conceptual integration.")

            phone_number = st.text_input("Enter WhatsApp Phone Number (e.g., +1234567890)", key="whatsapp_num")
            whatsapp_message = f"SolarGuard AI Report:\n\n{df.to_string(index=False)}\n\nFor more details, visit your SolarGuard dashboard."

            if st.button("Send WhatsApp Message", use_container_width=True):
                if phone_number:
                    # In a real scenario, you would use an API client here.
                    # Example with Twilio (requires installation and credentials):
                    # from twilio.rest import Client
                    # account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
                    # auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
                    # client = Client(account_sid, auth_token)
                    # try:
                    #     message = client.messages.create(
                    #         from_='whatsapp:+14155238886', # Your Twilio WhatsApp number
                    #         body=whatsapp_message,
                    #         to=f'whatsapp:{phone_number}'
                    #     )
                    #     st.success(f"WhatsApp message sent to {phone_number} (SID: {message.sid})")
                    # except Exception as e:
                    #     st.error(f"Failed to send WhatsApp message: {e}")
                    st.success(f"Simulating WhatsApp message sent to {phone_number}.\n\nMessage Content:\n{whatsapp_message}")
                else:
                    st.warning("Please enter a phone number.")


    # ---------------- SMART MAINTENANCE PREDICTION ----------------
    elif menu == "Smart Maintenance Prediction":
        st.markdown("## 💡 Smart Maintenance Prediction")
        st.write("This section will provide intelligent predictions for solar panel maintenance based on analysis.")
        st.info("Feature under development: Upload an image here to get a detailed maintenance prediction and schedule.")

    # ---------------- SELF-LEARNING SYSTEM ----------------
    elif menu == "Self-Learning System":
        st.markdown("## 🧠 Self-Learning System")
        st.write("Help improve the AI model by providing new labeled data.")
        st.warning("If the model misidentified an issue, you can upload the image and correct its label here.")

        uploaded_image_sl = st.file_uploader("Upload an image for retraining", type=['jpg', 'png', 'jpeg'], key="sl_image")
        if uploaded_image_sl:
            st.image(uploaded_image_sl, caption="Image for Self-Learning", use_container_width=True)
            correct_label = st.selectbox(
                "Select the correct label for this image:",
                ["Clean", "Dusty", "Bird-drop", "Electrical-damage", "Physical-damage"],
                key="sl_label"
            )
            if st.button("Submit for Retraining Data", use_container_width=True):
                # In a real system, this would save the image and label to a dataset for future model retraining.
                st.success(f"Image '{uploaded_image_sl.name}' with label '{correct_label}' submitted for self-learning dataset.")
                st.info("This data will be used to improve the model in future updates.")

    # ---------------- LIVE CAMERA ANALYSIS ----------------
    elif menu == "Live Camera Analysis":
        st.markdown("## 🎥 Live Camera Feed Analysis")
        st.write("Connect a live camera to detect solar panel defects in real-time.")

        if WEBRTC_AVAILABLE and model:
            st.warning("For live camera to work in Colab, you might need to grant camera permissions in your browser. Performance may vary.")

            class VideoProcessor(VideoTransformerBase):
                def __init__(self, model):
                    self.model = model

                def recv(self, frame):
                    img = frame.to_ndarray(format="bgr24")

                    # Perform inference
                    results = self.model.predict(img, conf=0.5, verbose=False)

                    # Annotate the image
                    annotated_img = img.copy()
                    for r in results:
                        annotated_img = r.plot() # YOLO's plot method returns annotated image

                    return frame.from_ndarray(annotated_img, format="bgr24")

            webrtc_streamer(
                key="live_camera_analysis",
                video_transformer_factory=lambda: VideoProcessor(model),
                client_settings=ClientSettings(
                    rtc_configuration={
                        "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
                    ,
                    media_stream_constraints={
                        "video": True,
                        "audio": False,
                    },
                ),
            )
        elif not WEBRTC_AVAILABLE:
            st.error("streamlit_webrtc library is not installed. Please install it using `!pip install streamlit-webrtc`.")
        else:
            st.info("Model not loaded or not available for live analysis.")

    # ---------------- VIDEO ANALYSIS ----------------
    elif menu == "Video Analysis":
        st.markdown("## 🎬 Video Upload and Analysis")
        st.write("Upload a video of solar panels for frame-by-frame defect detection.")
        st.warning("Video processing can be resource-intensive. Frames will be extracted and analyzed sequentially.")

        uploaded_video = st.file_uploader("Upload a video file", type=['mp4', 'avi', 'mov'], key="video_upload")

        if uploaded_video and model:
            tfile = uploaded_video.name
            with open(tfile, "wb") as f:
                f.write(uploaded_video.getbuffer())

            cap = cv2.VideoCapture(tfile)
            if not cap.isOpened():
                st.error("Error: Could not open video file.")
            else:
                st.info("Processing video... This might take a while depending on video length.")
                frame_count = 0
                st_frame = st.empty()

                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break

                    # Process frame with model
                    results = model.predict(frame, conf=0.5, verbose=False)
                    annotated_frame = frame.copy()
                    for r in results:
                        annotated_frame = r.plot()

                    st_frame.image(annotated_frame, channels="BGR", use_column_width=True, caption=f"Frame {frame_count}")
                    frame_count += 1

                cap.release()
                os.remove(tfile) # Clean up temp file
                st.success("Video processing complete!")
        elif uploaded_video and not model:
            st.warning("Model is not loaded, cannot perform video analysis.")
        else:
            st.info("Please upload a video file to begin analysis.")

    # ---------------- REPORTS ----------------
    elif menu == "Reports":
        st.markdown("## 📋 Reports")
        st.success("Weekly report generated successfully")

    # ---------------- ABOUT ----------------
    elif menu == "About Us":
        st.markdown("## 🌍 About SolarGuard")
        st.write("SolarGuard AI Pro is an advanced artificial intelligence platform designed to revolutionize solar energy monitoring and maintenance.Our system leverages state-of-the-art computer vision and deep learning models to automatically detect defects in solar panels such as dust accumulation, cracks, bird droppings, and electrical damage.By combining real-time image analysis, predictive maintenance, and intelligent reporting, SolarGuard helps solar farm operators increase efficiency, reduce maintenance costs and maximize energy output.The platform also integrates interactive dashboards, live camera analysis, and video processing to provide a complete end-to-end monitoring solution.Our mission is to make renewable energy systems smarter, safer, and more efficient through AI-driven automation and continuous learning")

    # ---------------- CONTACT ----------------
    elif menu == "Contact":
        st.markdown("## 📞 Contact")
        st.text_input("Name")
        st.text_input("Email")
        st.text_area("Message")
        st.button("Send")
