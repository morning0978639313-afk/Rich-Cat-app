import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

st.set_page_config(page_title="RICH CAT 戰情室", layout="centered")

# 1. 精確對準你的四檔商品
SYMBOL_MAP = {
    "加權指數 (^TWII)": "^TWII",
    "微台 03 全 (WTXH26.TW)": "WTXH26.TW", # 2026年3月代號
    "台積電 (2330.TW)": "2330.TW",
    "台積電 ADR (TSM)": "TSM"
}

st.title("🐱 RICH CAT 戰情室 v6.1")
selected_label = st.selectbox("請選擇商品：", list(SYMBOL_MAP.keys()))
target_symbol = SYMBOL_MAP[selected_label]

tz_tw = pytz.timezone('Asia/Taipei')
st.write(f"🕒 台北實時：{datetime.now(tz_tw).strftime('%Y-%m-%d %H:%M:%S')}")

@st.cache_data(ttl=30)
def fetch_data(symbol):
    try:
        # 抓取 10 天確保跨過假日
        df = yf.download(symbol, period="10d", interval="1d", progress=False)
        
        # 如果微台 03 全沒資料，自動嘗試備用代號 WTX=F
        if (df is None or df.empty) and "WTXH26" in symbol:
            df = yf.download("WTX=F", period="10d", interval="1d", progress=False)
            
        return df
    except:
        return None

df = fetch_data(target_symbol)

if df is not None and not df.empty:
    try:
        # 【關鍵修復】解決導致 TypeError 的 MultiIndex 問題
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        last_row = df.iloc[-1]
        
        # 強制轉為標量數字，徹底消滅當機
        c_p = float(last_row['Close'])
        h_p = float(last_row['High'])
        l_p = float(last_row['Low'])
        
        diff = h_p - l_p
        r_0618 = l_p + (diff * 0.618)
        s_0382 = l_p + (diff * 0.382)

        st.success(f"📊 {selected_label} 連線成功")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("當前點數", f"{c_p:,.2f}")
        col2.metric("高點", f"{h_p:,.2f}")
        col3.metric("低點", f"{l_p:,.2f}")
        
        st.divider()
        st.subheader("🎯 0.618 關鍵位")
        st.info(f"📈 壓力 (0.618)： {r_0618:,.2f}")
        st.warning(f"📉 支撐 (0.382)： {s_0382:,.2f}")
        
    except Exception as e:
        st.error("⚠️ 數據解析失敗，請重新整理頁面。")
else:
    st.error(f"❌ 雅虎財經目前無法提供 {selected_label} 的報價，請切換其他商品。")

if st.button("🔄 刷新數據"):
    st.rerun()
