import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz
from streamlit_autorefresh import st_autorefresh # 使用你補上的第4個零件

# 頁面基礎設定
st.set_page_config(page_title="RICH CAT 戰情室", layout="centered")

# 自動刷新設定：每 60 秒自動更新一次
st_autorefresh(interval=60 * 1000, key="datarefresh")

# 1. 僅限這四檔商品
SYMBOL_MAP = {
    "加權指數 (^TWII)": "^TWII",
    "微台近全 (WTX=F)": "WTX=F",
    "台積電 (2330)": "2330.TW",
    "台積電 ADR (TSM)": "TSM"
}

st.title("🐱 RICH CAT 戰情室 v8.0")
selected_label = st.selectbox("切換觀測商品：", list(SYMBOL_MAP.keys()))
target_symbol = SYMBOL_MAP[selected_label]

# 2. 顯示台北實時
tz = pytz.timezone('Asia/Taipei')
st.write(f"🕒 台北實時：{datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')}")

# 3. 數據抓取邏輯 (針對 TypeError 進行終極防禦)
@st.cache_data(ttl=60)
def get_safe_data(symbol):
    try:
        df = yf.download(symbol, period="10d", interval="1d", progress=False)
        if df.empty: return None
        # 強制解決多層標籤導致當機的問題
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except:
        return None

data = get_safe_data(target_symbol)

# 4. 數據看板顯示
if data is not None:
    try:
        last = data.iloc[-1]
        c = float(last['Close'])
        h = float(last['High'])
        l = float(last['Low'])
        
        # 0.618 點位計算
        diff = h - l
        r618 = l + (diff * 0.618)
        s382 = l + (diff * 0.382)

        st.success(f"📈 {selected_label} 連線成功")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("當前價格", f"{c:,.2f}")
        col2.metric("區間高點", f"{h:,.2f}")
        col3.metric("區間低點", f"{l:,.2f}")
        
        st.divider()
        st.subheader("🎯 關鍵戰情位")
        st.info(f"🚀 壓力區 (0.618)：**{r618:,.2f}**")
        st.warning(f"🛡️ 支撐區 (0.382)：**{s382:,.2f}**")
    except:
        st.error("數據格式解析中，請稍候。")
else:
    st.error("❌ 無法取得數據。目前非交易時段或數據源忙碌中。")
