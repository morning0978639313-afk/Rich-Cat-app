import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz
from streamlit_autorefresh import st_autorefresh

# 1. 基礎設定
st.set_page_config(page_title="RICH CAT 戰情室 v12.0", layout="centered")

# 2. 自動刷新：30 秒一次
st_autorefresh(interval=30 * 1000, key="datarefresh")

# 3. 指定商品
SYMBOL_MAP = {
    "加權指數": "^TWII",
    "微台近全": "WTX=F",
    "台積電": "2330.TW",
    "台積電 ADR": "TSM"
}

st.title("🐱 RICH CAT 戰情室 v12.0")
selected_label = st.selectbox("切換商品", list(SYMBOL_MAP.keys()))
target_symbol = SYMBOL_MAP[selected_label]

tz = pytz.timezone('Asia/Taipei')
st.write(f"🕒 台北實時：{datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')}")

# 4. 數據抓取
@st.cache_data(ttl=20)
def get_clean_data(symbol):
    try:
        df = yf.download(symbol, period="10d", interval="1d", progress=False)
        if df is None or df.empty: return None
        # 解決多層標籤導致的 TypeError
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except:
        return None

data = get_clean_data(target_symbol)

# 5. 戰情顯示
if data is not None:
    try:
        last = data.iloc[-1]
        # 強制轉型為單一數字，徹底消滅 Series 格式錯誤
        def to_f(v):
            if isinstance(v, pd.Series): v = v.iloc[0]
            return float(v)

        c = to_f(last['Close'])
        h = to_f(last['High'])
        l = to_f(last['Low'])

        r618 = l + (h - l) * 0.618
        s382 = l + (h - l) * 0.382

        st.success(f"📈 {selected_label} 連線成功")
        col1, col2, col3 = st.columns(3)
        col1.metric("價格", f"{c:,.2f}")
        col2.metric("高點", f"{h:,.2f}")
        col3.metric("低點", f"{l:,.2f}")
        
        st.divider()
        st.info(f"🚀 壓力區 (0.618)：**{r618:,.2f}**")
        st.warning(f"🛡️ 支撐區 (0.382)：**{s382:,.2f}**")
    except:
        st.error("數據解析中...")
else:
    st.error("❌ 目前抓不到數據，請稍後刷新。")
