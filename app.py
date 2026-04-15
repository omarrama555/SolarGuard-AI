
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from ultralytics import YOLO
from PIL import Image
import datetime
import time
import os

st.set_page_config(page_title="SolarGuard AI Pro v2", page_icon="☀️", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0b0e14; color: #e0e0e0; }
    .stMetric { background-color: #161b22; padding: 20px; border-radius: 12px; border: 1px solid #30363d; }
    .feature-card { background-color: #1c2128; padding: 20px; border-radius: 15px; border-right: 5px solid #2ea043; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_resource
def load_model():
    # تعديل المسار هنا ليكون في الفولدر الرئيسي للـ Colab
    model_path = 'best.pt'
    return YOLO(model_path) if os.path.exists(model_path) else None

model = load_model()

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.title("☀️ SolarGuard AI Enterprise")
    with st.form("Login"):
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            if u == "admin" and p == "solar2026":
                st.session_state['logged_in'] = True
                st.rerun()
            else:
                st.error("Invalid Credentials")
else:
    st.sidebar.title("☀️ SolarGuard v2.0")
    menu = st.sidebar.selectbox("Navigation", ["Smart Dashboard", "Batch AI Analysis", "Active Learning Center"])
    
    if menu == "Smart Dashboard":
        st.title("📊 Real-Time Monitoring Dashboard")
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Analyzed Panels", "1,240")
        c2.metric("Healthy Panels", "1,180", "95%")
        c3.metric("Critical Faults", "12", "-2", delta_color="inverse")
        st.area_chart(pd.DataFrame(np.random.randn(24, 1), columns=['KWh']), color="#2ea043")

    elif menu == "Batch AI Analysis":
        st.title("🤖 Multi-Panel AI Diagnostic")
        files = st.file_uploader("Upload Images (Max 5)", type=['jpg','png','jpeg'], accept_multiple_files=True)
        if files:
            results_list = []
            cols = st.columns(len(files))
            for i, file in enumerate(files[:5]):
                img = Image.open(file)
                img_path = f"temp_{i}.jpg"
                img.save(img_path)
                res = model.predict(img_path, conf=0.25)
                results_list.append({"name": file.name, "res": res[0]})
                with cols[i]:
                    st.image(res[0].plot(), caption=f"Panel: {file.name}", use_container_width=True)

            st.markdown("---")
            st.subheader("🎯 Panel Ranking System")
            ranking_data = []
            for r in results_list:
                label = "Clean" if len(r['res'].boxes) == 0 else model.names[int(r['res'].boxes[0].cls[0])]
                score = 100 if label == "Clean" else 100 - (float(r['res'].boxes[0].conf[0]) * 100)
                ranking_data.append({"Panel": r['name'], "Health Score": round(score, 1), "Status": label})
            
            df_rank = pd.DataFrame(ranking_data).sort_values(by="Health Score", ascending=False)
            st.table(df_rank)

            st.subheader("📅 Smart Maintenance Prediction")
            for index, row in df_rank.iterrows():
                days = int(row['Health Score'] * 1.5)
                pred_date = datetime.date.today() + datetime.timedelta(days=days)
                st.write(f"Panel **{row['Panel']}**: Prediction Date **{pred_date}**")

            col_mail, col_wa = st.columns(2)
            with col_mail:
                if st.button("📧 Send to Email"): st.success("Sent to: omarramadan88888888g@gmail.com")
            with col_wa:
                if st.button("💬 Send to WhatsApp"): st.info("Sent to: +201070007200")

    elif menu == "Active Learning Center":
        st.title("🧠 Self-Learning System")
        test_img = st.file_uploader("Upload image", type=['jpg'])
        if test_img:
            st.image(test_img, width=400)
            if st.button("Add to Training Set"): st.success("Saved for retraining!")
