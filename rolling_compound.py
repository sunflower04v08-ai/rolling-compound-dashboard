import streamlit as st
import yfinance as yf
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import os
import requests

# --- 0. 自動下載中文字體 (PDF 必備) ---
FONT_FILENAME = "NotoSansTC-Regular.ttf"
FONT_URL = "https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTC/NotoSansCJKtc-Regular.ttf"

if not os.path.exists(FONT_FILENAME):
    with st.spinner("正在初始化中文字體..."):
        r = requests.get(FONT_URL)
        with open(FONT_FILENAME, "wb") as f:
            f.write(r.content)

# --- 1. 網頁配置 ---
st.set_page_config(page_title="台股質押風控戰情室", layout="wide")

# --- 2. 側邊欄：帳戶數據 ---
st.sidebar.header("⚙️ 帳戶數據設定")
loan = st.sidebar.number_input("總借款金額 (NT$)", value=1000000, step=10000)
cash = st.sidebar.number_input("預備救火現金 (NT$)", value=550000, step=10000)
drop_val = st.sidebar.slider("模擬無差別跌幅 (%)", 0, 50, 30) / 100

# --- 3. 主畫面 ---
st.title("📊 台股質押維持率監控系統")
st.info("📢 [贊助廣告] 您的質押利息太高嗎？點此查看 2026 最新券商優惠利率專案")

# --- 4. 持股編輯區 (支援使用者自行新增標的) ---
st.subheader("📋 您的持股配置")
st.caption("💡 您可以在表格下方自行新增標的，請記得代號後加上 .TW (上市) 或 .TWO (上櫃)")

# 預設數據
init_data = {
    "代碼": ["0056.TW", "00713.TW", "00878.TW", "00929.TW", "00919.TW", "00939.TW", "00940.TW", "00937B.TW"],
    "擔保品(張)": [54, 39, 79, 34, 124, 29, 10, 5],
    "預備現股(張)": [15, 2, 18, 3, 8, 0, 0, 0]
}
df = pd.DataFrame(init_data)

# 關鍵：num_rows="dynamic" 允許使用者自行新增或刪除標的
edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

# --- 5. 執行計算與顯示結果 ---
if st.button("🚀 執行即時查價與壓力測試"):
    with st.spinner('連線抓取即時報價中...'):
        total_p_v = 0
        total_u_v = 0
        display_details = []
        
        for _, row in edited_df.iterrows():
            ticker = row["代碼"]
            if not ticker: continue # 跳過空白行
            
            # 抓取即時股價
            try:
                stock = yf.Ticker(ticker)
                now_price = stock.fast_info['last_price']
            except:
                now_price = 0
            
            p_shares = row["擔保品(張)"] * 1000
            u_shares = row["預備現股(張)"] * 1000
            p_val = p_shares * now_price
            u_val = u_shares * now_price
            
            total_p_v += p_val
            total_u_v += u_val
            
            # 存入明細表 (新增現在股價欄位)
            display_details.append({
                "代碼": ticker,
                "現在股價": round(now_price, 2),
                "擔保品市值": round(p_val, 0),
                "現股市值": round(u_val, 0),
                "總持倉市值": round(p_val + u_val, 0)
            })

        # 模擬計算
        sim_p = total_p_v * (1 - drop_val)
        sim_u = total_u_v * (1 - drop_val)
        
        curr_r = (total_p_v / loan) * 100 if loan > 0 else 0
        crash_r = (sim_p / loan) * 100 if loan > 0 else 0
        res_2 = ((sim_p + sim_u) / (loan - cash)) * 100 if (loan - cash) > 0 else 0

        # --- 6. 顯示即時持股明細表 (包含現在股價) ---
        st.write("### 🔍 即時持股明細")
        st.table(pd.DataFrame(display_details)) # 這裡會顯示現在股價欄位

        # --- 7. 維持率儀表板 ---
        st.write("### 📊 壓力測試結果")
        c1, c2, c3 = st.columns(3)
        c1.metric("當前維持率", f"{curr_r:.2f}%")
        c2.metric(f"崩跌 {drop_val*100:.0f}% 後", f"{crash_r:.2f}%", f"{crash_r-curr_r:.1f}%", delta_color="inverse")
        c3.metric("救援後預期維持率", f"{res_2:.2f}%", "🛡️ 終極防禦")

        if crash_r < 135:
            st.error("🚨 警告：模擬崩跌後維持率低於 135% 警戒線！")
        else:
            st.success("✅ 配置安全：您的預備現股與現金足以抵擋模擬跌幅。")

        st.markdown("---")
        st.warning("💼 **專業功能**：如需下載包含上述所有數據的 PDF 報告，請聯繫系統管理員。")