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

    /* 物理性封殺收合按鈕與徹底隱藏側邊欄 */
    [data-testid="stSidebar"], [data-testid="stSidebarCollapseButton"], header[data-testid="stHeader"] { display: none !important; }
    .block-container { padding-top: 2rem !important; }

    /* IG 導流按鈕 (移至底部) */
    .ig-button {
        display: block; width: 100%; padding: 15px; text-align: center;
        background-color: #0B3024; border: 2px solid #BC944A; border-radius: 8px;
        color: #BC944A !important; text-decoration: none; font-weight: bold;
        margin-top: 20px; letter-spacing: 2px; box-shadow: 0 4px 15px rgba(11, 48, 36, 0.2);
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


# --- 3. 主畫面設計 ---
st.title("🛡️ 質押維持率・風控戰情室")
st.markdown("<h3 style='color:#9E331A; letter-spacing: 1px; font-size: 1.3rem; margin-bottom: 25px;'>揭開 6% 殖利率「安全放大」至 10% 的底層邏輯。</h3>", unsafe_allow_html=True)

st.markdown("""
    <div style="background-color: #FFFFFF; border-left: 5px solid #BC944A; padding: 20px 25px; margin-bottom: 40px; border-radius: 0 8px 8px 0; box-shadow: 0 4px 15px rgba(11, 48, 36, 0.05);">
        <h4 style="color: #0B3024; margin-top: 0; margin-bottom: 12px; font-weight: bold; letter-spacing: 1px; font-size: 1.15rem;">
            📖 戰情室指南：掌控風險，放大格局
        </h4>
        <p style="color: #2D3436; font-size: 1.05rem; line-height: 1.6; margin-bottom: 15px;">
            <b>【系統簡介】</b><br>
            這是一套專為高階資產管理者打造的「質押風控儀表板」。透過串接即時市場報價，我們能為您的投資組合進行極端壓力測試，精算出崩跌時的維持率底線，並自動評估「預備現金」與「預備現股」的救援效率。讓您在擴張信用的同時，依然擁有 100% 的絕對掌控權。
        </p>
        <p style="color: #2D3436; font-size: 1.05rem; line-height: 1.6; margin-bottom: 0;">
            <b>【使用說明】</b><br>
            <span style="color: #9E331A; font-weight: bold;">Step 1. 資金配置：</span>在下方輸入您的總借款與備用資金，並設定防禦參數。<br>
            <span style="color: #9E331A; font-weight: bold;">Step 2. 壓力測試：</span>拖曳「大盤跌幅滑桿」，模擬極端市況。<br>
            <span style="color: #9E331A; font-weight: bold;">Step 3. 啟動防禦：</span>於表格填妥庫存後，點擊最下方紅色按鈕展開風控矩陣。
        </p>
    </div>
""", unsafe_allow_html=True)

# --- 4. 核心參數區 (對稱雙引擎設計) ---
st.markdown("### ⚙️ ESTATE CONFIG / 資金與風險設定")
st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)

c_left, c_right = st.columns(2)

with c_left:
    loan = st.number_input("總借款金額 (NT$)", value=1000000, step=10000)
    
    # 【新增】墨綠色專屬控制台標籤，創造左右對稱感
    st.markdown("""
        <div style="background: linear-gradient(90deg, rgba(11, 48, 36, 0.1) 0%, rgba(11, 48, 36, 0) 100%); 
                    border-left: 4px solid #0B3024; padding: 10px 15px; margin-top: 20px; margin-bottom: 15px; border-radius: 0 4px 4px 0;">
            <div style="color: #0B3024; font-family: 'Arial', sans-serif; font-size: 0.75rem; font-weight: bold; letter-spacing: 2px; margin-bottom: 4px; text-transform: uppercase;">
                🏦 Loan Interest
            </div>
            <div style="color: #0B3024; font-size: 15px; font-weight: bold; letter-spacing: 1px;">
                質押利息 (%)
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    ir1, ir2 = st.columns([6, 4])
    with ir1: st.slider("ir_s", min_value=1.0, max_value=10.0, step=0.1, key="ir_slider", on_change=sync_ir_s2n, label_visibility="collapsed")
    with ir2: st.number_input("ir_n", min_value=1.0, max_value=10.0, step=0.1, key="ir_num", on_change=sync_ir_n2s, label_visibility="collapsed")
    interest_rate = st.session_state.ir_num

with c_right:
    cash = st.number_input("預備救火現金 (NT$)", value=100000, step=10000)
    
    # 磚紅色壓力測試標籤 (調整間距與左側完全一致)
    st.markdown("""
        <div style="background: linear-gradient(90deg, rgba(158, 51, 26, 0.15) 0%, rgba(11, 48, 36, 0) 100%); 
                    border-left: 4px solid #9E331A; padding: 10px 15px; margin-top: 20px; margin-bottom: 15px; border-radius: 0 4px 4px 0;">
            <div style="color: #9E331A; font-family: 'Arial', sans-serif; font-size: 0.75rem; font-weight: bold; letter-spacing: 2px; margin-bottom: 4px; text-transform: uppercase;">
                ⚡ Extreme Stress Test
            </div>
            <div style="color: #0B3024; font-size: 15px; font-weight: bold; letter-spacing: 1px;">
                假設大盤跌幅 (%)
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    dr1, dr2 = st.columns([6, 4])
    with dr1: st.slider("dr_s", min_value=0, max_value=50, step=1, key="drop_slider", on_change=sync_drop_s2n, label_visibility="collapsed")
    with dr2: st.number_input("dr_n", min_value=0, max_value=50, step=1, key="drop_num", on_change=sync_drop_n2s, label_visibility="collapsed")
    drop_rate = st.session_state.drop_num / 100

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("### 📋 PORTFOLIO CONFIG / 持股配置")

init_data = {
    "代碼": ["0050.TW", "", "", "", ""],
    "擔保品(張)": [10, 0, 0, 0, 0],
    "預備現股(張)": [2.0, 0.0, 0.0, 0.0, 0.0],
    "預估殖利率(%)": [3.5, 0.0, 0.0, 0.0, 0.0] 
}
df = pd.DataFrame(init_data)
edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

# --- 5. 執行分析 ---
st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
if st.button("🚀 啟動即時風控試算"):
    with st.spinner("🚀 正在批量抓取市場數據，請稍候..."):
        tickers = [str(t).strip() for t in edited_df["代碼"].tolist() if str(t).strip()]
        
        price_dict = {}
        if tickers:
            try:
                data = yf.download(tickers, period="5d", progress=False)['Close']
                last_row = data.ffill().iloc[-1]
                if isinstance(last_row, pd.Series):
                    price_dict = last_row.to_dict()
                elif len(tickers) == 1:
                    price_dict = {tickers[0]: float(last_row)}
            except Exception as e:
                pass

        total_p_v = 0.0
        total_u_v = 0.0
        total_gross_dividend = 0.0 
        parsed_data = []
        
        for _, row in edited_df.iterrows():
            ticker = str(row["代碼"]).strip()
            if not ticker: continue
            
            try:
                raw_price = price_dict.get(ticker, 0.0)
                if isinstance(raw_price, (pd.Series, pd.DataFrame)):
                    raw_price = raw_price.iloc[0]
                price = float(raw_price)
                if pd.isna(price): price = 0.0
            except:
                price = 0.0
                
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
# 【免責聲明與 IG 導流區】
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
    </div>
""", unsafe_allow_html=True)

# 滿版的官方 IG 追蹤按鈕，放在最吸睛的結尾
st.markdown('<a href="https://www.instagram.com/rolling_compound/" target="_blank" class="ig-button">👉 FOLLOW OFFICIAL IG</a>', unsafe_allow_html=True)
st.markdown('<div style="text-align: center; font-style: italic; color: #888888; font-size: 0.85rem; margin-top: 10px;">(繼續使用本表，即代表您同意上述聲明)</div>', unsafe_allow_html=True)
