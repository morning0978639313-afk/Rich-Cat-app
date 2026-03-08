import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

# 1. 頁面基礎設定
st.set_page_config(page_title="RICH CAT 戰情室", layout="centered")

# 2. 只有這四檔商品
SYMBOL_MAP = {
    "加權指數 (^TWII)": "^TWII",
    "微台近全 (WTX=F)": "WTX=F",
    "台積電 (2330)": "2330.TW",
    "台積電 ADR (TSM)": "TSM"
}

st.title("🐱 RICH CAT 戰情室 v6.0")
selected_label = st.selectbox("請選擇商品：", list(SYMBOL_MAP.keys()))
target_symbol = SYMBOL_MAP[selected_label]

# 3. 顯示目前時間
tz_tw = pytz.timezone('Asia/Taipei')
st.write(f"🕒 台北實時：{datetime.now(tz_tw).strftime('%Y-%m-%d %H:%M:%S')}")

# 4. 資料抓取 (包在 try 裡面，保證不當機)
try:
    df = yf.download(target_symbol, period="10d", interval="1d", progress=False)
    
    if not df.empty:
        # 強制修復 yfinance 可能出現的多層標籤 (解決 TypeError)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        last_row = df.iloc[-1]
        
        # 抓取數值並轉為純數字
        c_p = float(last_row['Close'])
        h_p = float(last_row['High'])
        l_p = float(last_row['Low'])
        
        # 計算點位
        diff = h_p - l_p
        r_0618 = l_p + (diff * 0.618)
        s_0382 = l_p + (diff * 0.382)

        st.success(f"📊 {selected_label} 連線成功")
        
        # 顯示看板
        c1, c2, c3 = st.columns(3)
        c1.metric("目前價格", f"{c_p:,.2f}")
        c2.metric("區間高點", f"{h_p:,.2f}")
        c3.metric("區間低點", f"{l_p:,.2f}")
        
        st.divider()
        st.subheader("🎯 關鍵戰情位")
        st.info(f"📈 壓力區 (0.618)： {r_0618:,.2f}")
        st.warning(f"📉 支撐區 (0.382)： {s_0382:,.2f}")
        
    else:
        st.error("❌ 抓不到數據，請嘗試切換其他商品（微台在非交易時段可能無資料）。")

except Exception as e:
    st.error("⚠️ 系統數據對接中，請點擊下方按鈕刷新。")
    st.caption(f"診斷訊息：{e}")

if st.button("🔄 手動刷新"):
    st.rerun()
