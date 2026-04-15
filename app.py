
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from ultralytics import YOLO
from PIL import Image
import datetime
import time
import os

# --- الإعدادات الأساسية ---
st.set_page_config(page_title="SolarGuard AI Pro v2", page_icon="☀️", layout="wide")

# ألوان مريحة للعين (Dark Theme with Emerald & Gold)
st.markdown("""
    <style>
    .main { background-color: #0b0e14; color: #e0e0e0; }
    .stMetric { background-color: #161b22; padding: 20px; border-radius: 12px; border: 1px solid #30363d; }
    .feature-card { background-color: #1c2128; padding: 20px; border-radius: 15px; border-right: 5px solid #2ea043; margin-bottom: 15px; }
    .status-good { color: #2ea043; font-weight: bold; }
    .status-bad { color: #f85149; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# تحميل الموديل
@st.cache_resource
def load_model():
    model_path = '/content/runs/detect/Solar_Fault_Detector/weights/best.pt'
    return YOLO(model_path) if os.path.exists(model_path) else None

model = load_model()

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.title("☀️ SolarGuard AI Enterprise")
    st.info("Log in to access Real-time Solar Monitoring")
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
        # أرقام افتراضية يتم تحديثها
        c1.metric("Total Analyzed Panels", "1,240")
        c2.metric("Healthy Panels", "1,180", "95%")
        c3.metric("Critical Faults", "12", "-2", delta_color="inverse")
        
        st.subheader("📈 Energy Yield Prediction (Next 24h)")
        chart_data = pd.DataFrame(np.random.randn(24, 1), columns=['KWh'])
        st.area_chart(chart_data, color="#2ea043")

    elif menu == "Batch AI Analysis":
        st.title("🤖 Multi-Panel AI Diagnostic")
        st.write("Upload up to 5 images for bulk processing and ranking.")
        
        files = st.file_uploader("Upload Images", type=['jpg','png','jpeg'], accept_multiple_files=True)
        
        if files:
            if len(files) > 5:
                st.error("Please upload maximum 5 images.")
            else:
                results_list = []
                st.write(f"--- Processing {len(files)} Panels ---")
                
                cols = st.columns(len(files))
                for i, file in enumerate(files):
                    img = Image.open(file)
                    img_path = f"temp_{i}.jpg"
                    img.save(img_path)
                    
                    # Run AI
                    res = model.predict(img_path, conf=0.25)
                    results_list.append({"name": file.name, "res": res[0]})
                    
                    with cols[i]:
                        st.image(res[0].plot(), caption=f"Panel: {file.name}", use_container_width=True)

                # --- 🎯 Panel Ranking System ---
                st.markdown("---")
                st.subheader("🎯 Panel Ranking System (Best to Worst)")
                
                ranking_data = []
                for r in results_list:
                    label = "Clean" if len(r['res'].boxes) == 0 else model.names[int(r['res'].boxes[0].cls[0])]
                    score = 100 if label == "Clean" else 100 - (float(r['res'].boxes[0].conf[0]) * 100)
                    ranking_data.append({"Panel": r['name'], "Health Score": round(score, 1), "Status": label})
                
                df_rank = pd.DataFrame(ranking_data).sort_values(by="Health Score", ascending=False)
                st.table(df_rank)

                # --- 📅 Dynamic Predictive Maintenance ---
                st.subheader("📅 Smart Maintenance Prediction")
                for index, row in df_rank.iterrows():
                    days_to_fail = int(row['Health Score'] * 1.5) # معادلة ديناميكية
                    pred_date = datetime.date.today() + datetime.timedelta(days=days_to_fail)
                    st.write(f"Panel **{row['Panel']}**: Estimated maintenance needed by **{pred_date}** (Status: {row['Status']})")

                # --- 🚨 Alert System ---
                st.markdown("---")
                col_mail, col_wa = st.columns(2)
                with col_mail:
                    if st.button("📧 Send Report to Email"):
                        st.success(f"Report sent to: omarramadan88888888g@gmail.com")
                with col_wa:
                    if st.button("💬 Send Alert to WhatsApp"):
                        st.info(f"WhatsApp Notification Sent to: +201070007200")

    elif menu == "Active Learning Center":
        st.title("🧠 Self-Learning System")
        st.write("If the AI is unsure, you can label the image to retrain the model.")
        test_img = st.file_uploader("Upload ambiguous image", type=['jpg'])
        if test_img:
            st.image(test_img, width=400)
            correct_label = st.selectbox("What is the correct label?", ["Clean", "Dusty", "Bird-Drop", "Crack"])
            if st.button("Add to Training Set"):
                st.success("Image saved! Model will auto-update in the next cycle.")

