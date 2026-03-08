import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz
from streamlit_autorefresh import st_autorefresh

# 1. 頁面設定
st.set_page_config(page_title="RICH CAT 戰情室 v9.0", layout="centered")

# 2. 自動刷新零件 (每 60 秒)
st_autorefresh(interval=60 * 1000, key="datarefresh")

# 3. 指定商品清單
SYMBOL_MAP = {
    "加權指數": "^TWII",
    "微台近全": "WTX=F",
    "台積電": "2330.TW",
    "台積電 ADR": "TSM"
}

st.title("🐱 RICH CAT 戰情室 v9.0")
selected_label = st.selectbox("選擇商品", list(SYMBOL_MAP.keys()))
target_symbol = SYMBOL_MAP[selected_label]

tz = pytz.timezone('Asia/Taipei')
st.write(f"🕒 台北實時：{datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')}")

# 4. 數據抓取 (終極安全氣囊)
def get_safe_data(symbol):
    try:
        df = yf.download(symbol, period="10d", interval="1d", progress=False)
        if df is None or df.empty: return None
        # 修正 MultiIndex 問題
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except:
        return None

df = get_safe_data(target_symbol)

# 5. 邏輯判斷與顯示
if df is not None:
    try:
        last = df.iloc[-1]
        # 徹底消滅 TypeError 的讀取方式
        def to_float(val):
            return float(val.iloc[0]) if isinstance(val, pd.Series) else float(val)

        c = to_float(last['Close'])
        h = to_float(last['High'])
        l = to_float(last['Low'])

        diff = h - l
        r618 = l + (diff * 0.618)
        s382 = l + (diff * 0.382)

        st.success(f"📈 {selected_label} 連線成功")
        col1, col2, col3 = st.columns(3)
        col1.metric("目前點數", f"{c:,.2f}")
        col2.metric("區間高點", f"{h:,.2f}")
        col3.metric("區間低點", f"{l:,.2f}")
        
        st.divider()
        st.subheader("🎯 0.618 關鍵位")
        st.info(f"🚀 壓力區 (0.618)：{r618:,.2f}")
        st.warning(f"🛡️ 支撐區 (0.382)：{s382:,.2f}")
    except Exception as e:
        st.error(f"解析中...請稍候 (Code: {e})")
else:
    st.error("❌ 抓取不到數據。請嘗試切換至『加權指數』確認連線。")
