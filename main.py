import os, subprocess, sys

# 強制檢查零件，如果沒裝就現場裝
def check_and_install(pkg):
    try:
        __import__(pkg)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

for p in ["yfinance", "pandas", "pytz", "streamlit_autorefresh"]:
    check_and_install(p)

import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="RICH CAT 戰情室 v13.0", layout="centered")
st_autorefresh(interval=30 * 1000, key="datarefresh")

SYMBOL_MAP = {"加權指數": "^TWII", "微台近全": "WTX=F", "台積電": "2330.TW", "台積電 ADR": "TSM"}
st.title("🐱 RICH CAT 終極戰情室")
selected_label = st.selectbox("切換商品", list(SYMBOL_MAP.keys()))

@st.cache_data(ttl=20)
def get_data(symbol):
    df = yf.download(symbol, period="10d", progress=False)
    if df is not None and isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

df = get_data(SYMBOL_MAP[selected_label])
tz = pytz.timezone('Asia/Taipei')
st.write(f"🕒 台北：{datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')}")

if df is not None and not df.empty:
    last = df.iloc[-1]
    def to_f(v): return float(v.iloc[0]) if isinstance(v, pd.Series) else float(v)
    c, h, l = to_f(last['Close']), to_f(last['High']), to_f(last['Low'])
    diff = h - l
    
    st.success(f"📈 {selected_label} 連線成功")
    col1, col2, col3 = st.columns(3)
    col1.metric("價格", f"{c:,.2f}")
    col2.metric("高點", f"{h:,.2f}")
    col3.metric("低點", f"{l:,.2f}")
    
    st.divider()
    st.info(f"🚀 壓力區 (0.618)：**{l + diff * 0.618:,.2f}**")
    st.warning(f"🛡️ 支撐區 (0.382)：**{l + diff * 0.382:,.2f}**")
