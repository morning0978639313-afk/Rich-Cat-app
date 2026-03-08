import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

# 1. 頁面設定
st.set_page_config(page_title="RICH CAT 終極戰情室", layout="centered")

# 2. 標題與商品清單
st.title("🐱 RICH CAT 戰情室 v4.0")

SYMBOL_MAP = {
    "台積電 ADR (TSM)": "TSM",
    "NVIDIA (NVDA)": "NVDA",
    "加權指數 (^TWII)": "^TWII",
    "台積電 (2330)": "2330.TW",
    "鴻海 (2317)": "2317.TW",
    "元大台灣50 (0050)": "0050.TW"
}

selected_label = st.selectbox("請切換觀測商品：", list(SYMBOL_MAP.keys()))
target_symbol = SYMBOL_MAP[selected_label]

# 3. 顯示台北實時
tz_tw = pytz.timezone('Asia/Taipei')
st.write(f"🕒 台北實時：{datetime.now(tz_tw).strftime('%Y-%m-%d %H:%M:%S')}")

# 4. 強化的數據抓取邏輯 (針對不同市場自動回溯)
@st.cache_data(ttl=60) # 增加緩存，防止頻繁抓取導致崩潰
def fetch_safe_data(symbol):
    try:
        # 抓取 7 天資料，確保週末或長假也有最後一筆收盤價
        df = yf.download(symbol, period="7d", interval="1d", progress=False)
        if df is None or df.empty:
            return None
        return df
    except:
        return None

df = fetch_safe_data(target_symbol)

# 5. 獨立點位計算與 UI
if df is not None and len(df) > 0:
    try:
        # 鎖定該商品最後一個交易日的數據
        last_row = df.iloc[-1]
        
        # 確保抓到的是純數字 (解決 TypeError)
        c_p = float(last_row['Close'])
        h_p = float(last_row['High'])
        l_p = float(last_row['Low'])
        
        # 計算 0.618 與 0.382 點位
        diff = h_p - l_p
        r_0618 = l_p + (diff * 0.618)
        s_0382 = l_p + (diff * 0.382)

        st.success(f"📈 {selected_label} 數據連線成功")
        
        # 顯示主要數據
        m1, m2, m3 = st.columns(3)
        m1.metric("當前點數", f"{c_p:,.2f}")
        m2.metric("高點", f"{h_p:,.2f}")
        m3.metric("低點", f"{l_p:,.2f}")
        
        st.divider()
        
        # 顯示戰情位
        st.subheader("🎯 關鍵戰情點位")
        st.info(f"🚀 壓力區 (0.618)：**{r_0618:,.2f}**")
        st.warning(f"🛡️ 支撐區 (0.382)：**{s_0382:,.2f}**")
        
        # 點位公式顯示
        st.latex(r"Price_{0.618} = Low + (High - Low) \times 0.618")

    except Exception as e:
        st.error(f"⚠️ 資料解析異常：{e}")
else:
    st.error("❌ 無法取得數據。可能是該商品目前無報價或網路延遲。")

# 增加手動重新讀取按鈕
if st.button("🔄 重新連線"):
    st.rerun()
