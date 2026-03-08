import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz
from streamlit_autorefresh import st_autorefresh

# 頁面基礎設定
st.set_page_config(page_title="RICH CAT 戰情室", layout="centered")

# 自動重新整理 (每 60 秒)
st_autorefresh(interval=60 * 1000, key="datarefresh")

# 四個項目清單
SYMBOL_MAP = {
    "加權指數": "^TWII",
    "微台近全": "WTX=F",
    "台積電": "2330.TW",
    "台積電 ADR": "TSM"
}

st.title("🐱 RICH CAT 戰情室 v8.0")
selected_label = st.selectbox("選擇商品", list(SYMBOL_MAP.keys()))
target_symbol = SYMBOL_MAP[selected_label]

tz = pytz.timezone('Asia/Taipei')
st.write(f"🕒 台北實時：{datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')}")

def get_data(symbol):
    try:
        # 下載最近 10 天資料
        df = yf.download(symbol, period="10d", interval="1d", progress=False)
        if df.empty: return None
        
        # 解決 yfinance 多層標籤問題
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except:
        return None

df = get_data(target_symbol)

if df is not None:
    try:
        last = df.iloc[-1]
        # 強制轉為單一數字，徹底消滅 TypeError
        c = float(last['Close'].iloc[0]) if isinstance(last['Close'], pd.Series) else float(last['Close'])
        h = float(last['High'].iloc[0]) if isinstance(last['High'], pd.Series) else float(last['High'])
        l = float(last['Low'].iloc[0]) if isinstance(last['Low'], pd.Series) else float(last['Low'])

        diff = h - l
        r618 = l + (diff * 0.618)
        s382 = l + (diff * 0.382)

        st.success(f"📈 {selected_label} 連線成功")
        col1, col2, col3 = st.columns(3)
        col1.metric("價格", f"{c:,.2f}")
        col2.metric("高點", f"{h:,.2f}")
        col3.metric("低點", f"{l:,.2f}")
        
        st.divider()
        st.info(f"🚀 壓力區 (0.618)：{r618:,.2f}")
        st.warning(f"🛡️ 支撐區 (0.382)：{s382:,.2f}")
    except:
        st.error("解析中，請切換商品或刷新。")
else:
    st.error("暫時抓不到數據，請嘗試切換商品。")
