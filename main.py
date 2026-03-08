import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz
from streamlit_autorefresh import st_autorefresh
import requests # 對應你的第5個零件

# 頁面基礎設定
st.set_page_config(page_title="RICH CAT 戰情室 v10.0", layout="centered")

# 自動刷新：每 30 秒更新一次
st_autorefresh(interval=30 * 1000, key="datarefresh")

# 鎖定商品清單
SYMBOL_MAP = {
    "加權指數": "^TWII",
    "微台近全": "WTX=F",
    "台積電": "2330.TW",
    "台積電 ADR": "TSM"
}

st.title("🐱 RICH CAT 戰情室 v10.0")
selected_label = st.selectbox("選擇觀測商品", list(SYMBOL_MAP.keys()))
target_symbol = SYMBOL_MAP[selected_label]

tz = pytz.timezone('Asia/Taipei')
st.write(f"🕒 台北實時：{datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')}")

def get_data(symbol):
    try:
        df = yf.download(symbol, period="10d", interval="1d", progress=False)
        if df is None or df.empty: return None
        # 強制修正多層標籤問題，防止當機
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except:
        return None

df = get_data(target_symbol)

if df is not None:
    try:
        last = df.iloc[-1]
        # 顧慮周全的「三層數值轉化」，徹底消滅 TypeError
        def clean_val(v):
            if isinstance(v, pd.Series): v = v.iloc[0]
            return float(v)

        c = clean_val(last['Close'])
        h = clean_val(last['High'])
        l = clean_val(last['Low'])

        diff = h - l
        r618 = l + (diff * 0.618)
        s382 = l + (diff * 0.382)

        st.success(f"📈 {selected_label} 連線成功")
        
        # 數據看板
        col1, col2, col3 = st.columns(3)
        col1.metric("價格", f"{c:,.2f}")
        col2.metric("高點", f"{h:,.2f}")
        col3.metric("低點", f"{l:,.2f}")
        
        st.divider()
        st.info(f"🚀 壓力區 (0.618)：**{r618:,.2f}**")
        st.warning(f"🛡️ 支撐區 (0.382)：**{s382:,.2f}**")

    except Exception as e:
        st.error(f"數據格式解析中，請切換商品試試。 (Code: {e})")
else:
    st.error("❌ 抓不到數據。請確認商品或點擊重新整理。")
