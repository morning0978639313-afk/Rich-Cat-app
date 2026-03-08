import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

# 1. 頁面設定
st.set_page_config(page_title="RICH CAT 精選戰情室", layout="centered")

# 2. 精簡商品清單
SYMBOL_MAP = {
    "加權指數 (^TWII)": "^TWII",
    "微台近全 (WTX=F)": "WTX=F",
    "台積電 (2330)": "2330.TW",
    "台積電 ADR (TSM)": "TSM"
}

st.title("🐱 RICH CAT 戰情室 v5.0")

# 3. 商品選擇選單 (僅限四檔)
selected_label = st.selectbox("請切換觀測商品：", list(SYMBOL_MAP.keys()))
target_symbol = SYMBOL_MAP[selected_label]

# 4. 顯示台北實時
tz_tw = pytz.timezone('Asia/Taipei')
st.write(f"🕒 台北實時：{datetime.now(tz_tw).strftime('%Y-%m-%d %H:%M:%S')}")

# 5. 數據抓取 (抓取 7 天確保有最後收盤價)
@st.cache_data(ttl=60)
def fetch_safe_data(symbol):
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="7d")
        return df if not df.empty else None
    except:
        return None

df = fetch_safe_data(target_symbol)

# 6. 計算與顯示
if df is not None:
    try:
        last_row = df.tail(1)
        c_p = float(last_row['Close'].iloc[0])
        h_p = float(last_row['High'].iloc[0])
        l_p = float(last_row['Low'].iloc[0])
        
        # 0.618 戰情點位計算
        diff = h_p - l_p
        r_0618 = l_p + (diff * 0.618)
        s_0382 = l_p + (diff * 0.382)

        st.success(f"📈 {selected_label} 數據連線成功")
        
        # 數據面板
        m1, m2, m3 = st.columns(3)
        m1.metric("當前點數/價格", f"{c_p:,.2f}")
        m2.metric("區間高點", f"{h_p:,.2f}")
        m3.metric("區間低點", f"{l_p:,.2f}")
        
        st.divider()
        
        # 戰情位
        st.subheader("🎯 關鍵戰情點位")
        st.info(f"🚀 壓力區 (0.618)：**{r_0618:,.2f}**")
        st.warning(f"🛡️ 支撐區 (0.382)：**{s_0382:,.2f}**")
        
        # 顯示計算公式
        st.latex(r"Resistance = Low + (High - Low) \times 0.618")

    except Exception as e:
        st.error(f"⚠️ 解析錯誤：{e}")
else:
    st.error("❌ 無法取得數據。目前非交易時段或數據源更新中。")

if st.button("🔄 重新整理"):
    st.rerun()
