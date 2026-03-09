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
if "drop_num" not in st.session_state: st.session_state.drop_num = 30

def sync_ir_s2n(): st.session_state.ir_num = st.session_state.ir_slider
def sync_ir_n2s(): st.session_state.ir_slider = st.session_state.ir_num
def sync_drop_s2n(): st.session_state.drop_num = st.session_state.drop_slider
def sync_drop_n2s(): st.session_state.drop_slider = st.session_state.drop_num

# --- 3. 側邊欄配置 ---
st.sidebar.markdown("<h2 style='color:#BC944A; letter-spacing: 2px;'>ESTATE CONFIG</h2>", unsafe_allow_html=True)

# 【已修改】隱藏真實數據，換成乾淨的預設值 100 萬與 10 萬
loan = st.sidebar.number_input("總借款金額 (NT$)", value=1000000, step=10000)
cash = st.sidebar.number_input("預備救火現金 (NT$)", value=100000, step=10000)

st.sidebar.markdown("<div style='font-size: 14px; color: #FDFCF0; margin-bottom: 8px; margin-top: 20px; font-weight: bold; letter-spacing: 1px;'>質押利息 (%)</div>", unsafe_allow_html=True)
c1, c2 = st.sidebar.columns([6, 4])
with c1:
    st.slider("ir_s", min_value=1.0, max_value=10.0, step=0.1, key="ir_slider", on_change=sync_ir_s2n, label_visibility="collapsed")
with c2:
    st.number_input("ir_n", min_value=1.0, max_value=10.0, step=0.1, key="ir_num", on_change=sync_ir_n2s, label_visibility="collapsed")
interest_rate = st.session_state.ir_num

# 側邊欄大盤跌幅 (警示設計)
st.sidebar.markdown("""
    <div style="background: linear-gradient(90deg, rgba(158, 51, 26, 0.35) 0%, rgba(11, 48, 36, 0) 100%); 
                border-left: 4px solid #9E331A; padding: 12px 15px; margin-top: 40px; margin-bottom: 12px; border-radius: 0 4px 4px 0;">
        <div style="color: #BC944A; font-family: 'Arial', sans-serif; font-size: 0.75rem; font-weight: bold; letter-spacing: 2px; margin-bottom: 4px; text-transform: uppercase;">
            ⚡ Extreme Stress Test
        </div>
        <div style="color: #FDFCF0; font-size: 16px; font-weight: bold; letter-spacing: 1px;">
            假設大盤跌幅 (%)
        </div>
    </div>
""", unsafe_allow_html=True)

c3, c4 = st.sidebar.columns([6, 4])
with c3:
    st.slider("dr_s", min_value=0, max_value=50, step=1, key="drop_slider", on_change=sync_drop_s2n, label_visibility="collapsed")
with c4:
    st.number_input("dr_n", min_value=0, max_value=50, step=1, key="drop_num", on_change=sync_drop_n2s, label_visibility="collapsed")
drop_rate = st.session_state.drop_num / 100

st.sidebar.markdown("---")
st.sidebar.markdown('<a href="https://www.instagram.com/rolling_compound/" target="_blank" class="ig-button">FOLLOW OFFICIAL IG</a>', unsafe_allow_html=True)

# --- 4. 主畫面設計 ---
st.title("🛡️ 質押維持率・風控戰情室")
st.markdown("<h3 style='color:#9E331A; letter-spacing: 1px;'>揭開 6% 殖利率「安全放大」至 10% 的底層邏輯。</h3>", unsafe_allow_html=True)

st.markdown("""
    <div style="background-color: #FFFFFF; border-left: 5px solid #BC944A; padding: 20px 25px; margin-top: 20px; margin-bottom: 30px; border-radius: 0 8px 8px 0; box-shadow: 0 4px 15px rgba(11, 48, 36, 0.05);">
        <h4 style="color: #0B3024; margin-top: 0; margin-bottom: 12px; font-weight: bold; letter-spacing: 1px; font-size: 1.15rem;">
            📖 戰情室指南：掌控風險，放大格局
        </h4>
        <p style="color: #2D3436; font-size: 1.05rem; line-height: 1.6; margin-bottom: 15px;">
            <b>【系統簡介】</b><br>
            這是一套專為高階資產管理者打造的「質押風控儀表板」。透過串接即時市場報價，我們能為您的投資組合進行極端壓力測試，精算出崩跌時的維持率底線，並自動評估「預備現金」與「預備現股」的救援效率。讓您在擴張信用的同時，依然擁有 100% 的絕對掌控權。
        </p>
        <p style="color: #2D3436; font-size: 1.05rem; line-height: 1.6; margin-bottom: 0;">
            <b>【使用說明】</b><br>
            <span style="color: #9E331A; font-weight: bold;">Step 1. 左側設定參數：</span>輸入您的總借款、備用資金，並拖曳<span style="border-bottom: 2px solid #BC944A;">大盤跌幅滑桿</span>進行壓力測試。<br>
            <span style="color: #9E331A; font-weight: bold;">Step 2. 右側持股建檔：</span>於下方表格直接修改持股代碼，輸入您的「擔保品張數」、「未質押現股」與「預估殖利率」。<br>
            <span style="color: #9E331A; font-weight: bold;">Step 3. 啟動防禦試算：</span>點擊紅色按鈕，系統將瞬間為您展開風控矩陣與預期的被動現金流版圖。
        </p>
    </div>
""", unsafe_allow_html=True)

st.markdown("### 📋 PORTFOLIO CONFIG / 持股配置")

# 【已修改】隱藏真實庫存，給予一個乾淨的 5 行輸入範本
init_data = {
    "代碼": ["0050.TW", "", "", "", ""],
    "擔保品(張)": [10, 0, 0, 0, 0],
    "預備現股(張)": [2.0, 0.0, 0.0, 0.0, 0.0],
    "預估殖利率(%)": [3.5, 0.0, 0.0, 0.0, 0.0] 
}
df = pd.DataFrame(init_data)
edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

# --- 5. 執行分析 ---
if st.button("🚀 啟動即時風控試算"):
    with st.spinner("🚀 正在批量抓取市場數據，請稍候..."):
        tickers = [t for t in edited_df["代碼"].tolist() if t]
        
        try:
            data = yf.download(tickers, period="5d", progress=False)['Close']
            data = data.ffill().iloc[-1]
            price_dict = data.to_dict() if len(tickers) > 1 else {tickers[0]: data}
        except:
            price_dict = {}

        total_p_v = 0.0
        total_u_v = 0.0
        total_gross_dividend = 0.0 
        parsed_data = []
        
        for _, row in edited_df.iterrows():
            ticker = row["代碼"]
            if not ticker: continue
            
            price = price_dict.get(ticker, 0.0)
            if pd.isna(price): price = 0.0
            else: price = float(price)
                
            p_s = (float(row["擔保品(張)"]) if pd.notnull(row["擔保品(張)"]) else 0) * 1000
            u_s = (float(row["預備現股(張)"]) if pd.notnull(row["預備現股(張)"]) else 0) * 1000
            
            stock_p_v = p_s * price
            stock_u_v = u_s * price
            
            total_p_v += stock_p_v
            total_u_v += stock_u_v
            
            yield_rate = float(row["預估殖利率(%)"]) / 100 if pd.notnull(row["預估殖利率(%)"]) else 0.0
            total_gross_dividend += (stock_p_v + stock_u_v) * yield_rate
            
            parsed_data.append((ticker, price, p_s, u_s))

        margin_multiplier = (loan * 1.3) / total_p_v if total_p_v > 0 else 0
        details = []
        for ticker, price, p_s, u_s in parsed_data:
            portfolio_margin_price = price * margin_multiplier
            details.append({
                "代碼": ticker, 
                "現價": round(price, 2), 
                "擔保市值": f"{int(p_s * price):,}", 
                "預估斷頭價": round(portfolio_margin_price, 2)
            })

    sim_p = total_p_v * (1 - drop_rate)
    sim_u = total_u_v * (1 - drop_rate)
    
    curr_r = (total_p_v / loan) * 100 if loan > 0 else 0
    crash_r = (sim_p / loan) * 100 if loan > 0 else 0
    
    rescue_stock_r = ((sim_p + sim_u) / loan) * 100 if loan > 0 else 0
    rescue_cash_r = (sim_p / (loan - cash)) * 100 if (loan - cash) > 0 else 0
    rescue_both_r = ((sim_p + sim_u) / (loan - cash)) * 100 if (loan - cash) > 0 else 0

    st.markdown("---")
    st.markdown("### 🏛️ 風控關鍵指標")
    
    r1_c1, r1_c2 = st.columns(2)
    r1_c1.metric("當前維持率", f"{curr_r:.1f}%")
    r1_c2.metric(f"假設崩跌 {int(drop_rate*100)}% 後", f"{crash_r:.1f}%", f"{crash_r-curr_r:.1f}%", delta_color="inverse")

    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
    
    r2_c1, r2_c2, r2_c3 = st.columns(3)
    r2_c1.metric("🛡️ 投入「現股」後", f"{rescue_stock_r:.1f}%", f"+{rescue_stock_r-crash_r:.1f}% 恢復度", delta_color="normal")
    r2_c2.metric("🛡️ 投入「現金」後", f"{rescue_cash_r:.1f}%", f"+{rescue_cash_r-crash_r:.1f}% 恢復度", delta_color="normal")
    r2_c3.metric("🛡️ 兩者皆投入後", f"{rescue_both_r:.1f}%", f"+{rescue_both_r-crash_r:.1f}% 恢復度", delta_color="normal")

    st.write("### 🔍 市場即時明細")
    st.dataframe(pd.DataFrame(details), use_container_width=True)
    
    annual_interest = loan * (interest_rate / 100)
    net_dividend = total_gross_dividend - annual_interest
    monthly_dividend = net_dividend / 12  
    
    st.markdown(f"""<div style="background: linear-gradient(135deg, #0B3024 0%, #174233 100%); border: 3px solid #BC944A; padding: 40px 20px 30px 20px; border-radius: 12px; text-align: center; box-shadow: 0 15px 40px rgba(11, 48, 36, 0.4); margin-top: 40px; margin-bottom: 20px;"><div style="color: #BC944A; font-family: 'Georgia', serif; font-size: 1.3rem; font-weight: bold; letter-spacing: 3px; margin-bottom: 15px; text-transform: uppercase;">💰 預估年領淨配息金額</div><div style="color: #FDFCF0; font-family: 'Arial', sans-serif; font-size: 4.5rem; font-weight: 900; letter-spacing: 1px; line-height: 1; margin-bottom: 25px; text-shadow: 3px 3px 6px rgba(0,0,0,0.4);">NT$ {int(net_dividend):,}</div><div style="border-top: 1px solid rgba(188, 148, 74, 0.3); width: 60%; margin: 0 auto 25px auto;"></div><div style="color: #BC944A; font-family: 'Georgia', serif; font-size: 1.1rem; font-weight: bold; letter-spacing: 2px; margin-bottom: 10px;">✨ 相當於每月被動現金流</div><div style="color: #E8DCC5; font-family: 'Arial', sans-serif; font-size: 3.2rem; font-weight: 900; letter-spacing: 1px; line-height: 1; margin-bottom: 25px; text-shadow: 2px 2px 4px rgba(0,0,0,0.4);">NT$ {int(monthly_dividend):,}</div><div style="color: #E0D8C3; font-family: 'Georgia', serif; font-size: 1rem; opacity: 0.8; letter-spacing: 1px;">( 依各標的精算總配息 NT$ {int(total_gross_dividend):,} － 質押利息 NT$ {int(annual_interest):,} )</div></div>""", unsafe_allow_html=True)

# =====================================================================
# 【免責聲明與叮嚀】
# =====================================================================
st.markdown("""
    <div style="margin-top: 60px; padding-top: 25px; border-top: 1px solid rgba(188, 148, 74, 0.4); color: #555555; font-size: 0.9rem; line-height: 1.7;">
        <div style="font-weight: bold; color: #0B3024; margin-bottom: 10px; font-size: 1rem; letter-spacing: 1px;">
            【Rolling Compound 試算工具・免責聲明】
        </div>
        <ol style="margin-top: 0; padding-left: 20px; margin-bottom: 18px; color: #4A4A4A;">
            <li><b>非投資建議與盈虧自負：</b>本試算表內建公式僅供「壓力測試」參考，不保證 100% 精確，亦非任何買賣建議。各券商規定不同，借貸投資具高風險，使用本工具衍生之任何交易決策與虧損，皆由使用者完全承擔。</li>
        </ol>
        <div style="background-color: rgba(188, 148, 74, 0.08); border-left: 4px solid #BC944A; padding: 15px 20px; border-radius: 0 6px 6px 0; margin-bottom: 15px;">
            <span style="font-weight: bold; color: #9E331A; font-size: 1.05rem;">💡 Miles 的叮嚀：</span><br>
            <span style="color: #0B3024; font-style: italic;">「工具是用來計算風險的，不是用來壯膽的。請永遠把防禦底線，設在你最安心的位置。」</span>
        </div>
        <div style="text-align: right; font-style: italic; color: #888888; font-size: 0.85rem;">
            (繼續使用本表，即代表您同意上述聲明)
        </div>
    </div>
""", unsafe_allow_html=True)
