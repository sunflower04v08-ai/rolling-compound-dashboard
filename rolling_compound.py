import streamlit as st
import yfinance as yf
import pandas as pd
import os
import requests

# --- 0. 品牌視覺與幽靈代碼全域封殺 ---
st.set_page_config(page_title="Rolling Compound | 戰情室", layout="wide")

st.markdown("""
    <style>
    /* 全局襯線體 */
    * { font-family: 'Georgia', 'Times New Roman', serif !important; }
    .stApp { background-color: #FDFCF0; }
    h1 { color: #0B3024 !important; font-weight: 800; border-bottom: 2px solid #BC944A; padding-bottom: 10px; }
    h2, h3 { color: #0B3024 !important; }
    p, span, label, th, td { color: #2D3436 !important; }

    /* 指標方框 (Metric) 絕對對齊與黃金留白 */
    [data-testid="stMetric"] {
        background-color: #FFFFFF !important;
        border: 2px solid #BC944A !important; 
        box-shadow: 0 6px 20px rgba(11, 48, 36, 0.06); 
        border-radius: 12px !important; 
        padding: 20px 24px !important; 
        height: 155px !important; 
        display: block !important;
    }
    [data-testid="stMetricLabel"] { 
        color: #0B3024 !important; 
        letter-spacing: 1.5px; 
        font-weight: bold; 
        margin-bottom: 8px !important; 
    }
    [data-testid="stMetricValue"] { 
        color: #9E331A !important; 
        font-weight: 900; 
        letter-spacing: 1px;
    }

    [data-testid="stDataFrame"], .stDataEditor {
        background-color: #FFFFFF !important;
        border: 2px solid #BC944A !important; 
        border-radius: 8px; 
    }

    /* 主按鈕：穩定淺色文字 */
    .stButton>button {
        background-color: #9E331A !important; color: #FDFCF0 !important; 
        border-radius: 0px; border: none; font-weight: bold; padding: 12px; width: 100%;
        font-size: 1.1rem !important; letter-spacing: 1px;
    }
    .stButton>button div p, .stButton>button span { color: #FDFCF0 !important; }
    .stButton>button:hover { background-color: #9E331A !important; color: #FDFCF0 !important; box-shadow: 0 4px 12px rgba(158, 51, 26, 0.3); }

    /* 物理性封殺收合按鈕 */
    [data-testid="stSidebarCollapseButton"], header[data-testid="stHeader"] { display: none !important; }
    .block-container { padding-top: 2rem !important; }

    /* 側邊欄設計 */
    section[data-testid="stSidebar"] { background-color: #0B3024; border-right: 4px solid #BC944A; }
    section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] p { color: #FDFCF0 !important; }

    /* IG 導流按鈕 */
    .ig-button {
        display: block; width: 100%; padding: 12px; text-align: center;
        background-color: transparent; border: 2px solid #BC944A; 
        color: #BC944A !important; text-decoration: none; font-weight: bold;
        margin-top: 30px; letter-spacing: 2px;
    }
    .ig-button:hover { background-color: #BC944A; color: #0B3024 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. 自動下載字體 ---
@st.cache_resource
def init_env():
    if not os.path.exists("NotoSansTC-Regular.ttf"):
        try:
            r = requests.get("https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTC/NotoSansCJKtc-Regular.ttf", timeout=5)
            with open("NotoSansTC-Regular.ttf", "wb") as f: f.write(r.content)
        except: pass

init_env()

# --- 2. 雙向連動系統 ---
if "ir_slider" not in st.session_state: st.session_state.ir_slider = 2.2
if "ir_num" not in st.session_state: st.session_state.ir_num = 2.2
if "drop_slider" not in st.session_state: st.session_state.drop_slider = 30
if "drop_num" not
