import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz
from streamlit_autorefresh import st_autorefresh

# 1. 頁面設定
st.set_page_config(page_title="RICH CAT 戰情室 v4.1", layout="centered")

# 2. 設定 1 秒自動刷新 (1000毫秒)
st_autorefresh(interval=1000, limit=None, key="fivedatarefresh")

# 3. 更新後的商品清單
SYMBOL_MAP = {
    "加權指數 (TAIEX)": "^TWII",
    "微台近全 (Micro Futures)": "MXF=F",
    "台積電 ADR (TSM)": "TSM",
    "台積電 (2330)": "2330.TW"
}

st.title("🐱 RICH CAT 戰情室 v4.1")

# 4. 商品選擇選單
selected_label = st.selectbox("請選擇觀測商品：", list(SYMBOL_MAP.keys()))
target_symbol = SYMBOL_MAP[selected_label]

# 5. 台北時間顯示
tz = pytz.timezone('Asia/Taipei')
now_time = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
st.write(f"🕒 台北實時：{now_time} (1秒自動更新中)")

# 6. 抓取數據 (針對個別商品市場)
@st.cache_data(ttl=1)
def get_live_data(symbol):
    try:
        ticker = yf.Ticker(symbol)
        # 抓取最近 5 天以涵蓋不同市場的交易時段
        df = ticker.history(period="5d")
        return df if not df.empty else None
    except:
        return None

df = get_live_data(target_symbol)

if df is not None:
    try:
        # 使用 iloc 確保抓到單一數值，修正先前遇到的 TypeError
        last_val = df.tail(1)
        curr_p = float(last_val['Close'].iloc[0])
        high_p = float(last_val['High'].iloc[0])
        low_p = float(last_val['Low'].iloc[0])

        # 7. 0.618 戰情位計算
        diff = high_p - low_p
        r_0618 = low_p + (diff * 0.618)
        s_0382 = low_p + (diff * 0.382)

        st.success(f"✅ {selected_label} 連線成功")
        
        # 儀表板顯示數值
        c1, c2, c3 = st.columns(3)
        c1.metric("當前價格", f"{curr_p:,.2f}")
        c2.metric("區間高點", f"{high_p:,.2f}")
        c3.metric("區間低點", f"{low_p:,.2f}")
        
        st.divider()
        
        # 8. 關鍵點位顯示
        st.subheader(f"🎯 {selected_label} 關鍵點位")
        st.info(f"📈 壓力區 (0.618)：**{r_0618:,.2f}**")
        st.warning(f"📉 支撐區 (0.382)：**{s_0382:,.2f}**")

    except Exception as e:
        st.error("數據解析中，請稍候...")
else:
    st.error(f"無法取得 {selected_label} 行情，請確認市場是否開放或代碼是否正確。")

st.caption("💡 提醒：不同商品的交易時段不同，非交易時段將顯示最後收盤資訊。")
