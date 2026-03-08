import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

# 1. 頁面基礎設定
st.set_page_config(page_title="RICH CAT 戰情室", layout="centered")

# 2. 精確商品清單
SYMBOL_MAP = {
    "加權指數 (^TWII)": "^TWII",
    "微台近全 (WTX=F)": "WTX=F",
    "台積電 (2330)": "2330.TW",
    "台積電 ADR (TSM)": "TSM"
}

st.title("🐱 RICH CAT 戰情室 v5.1")
selected_label = st.selectbox("請選擇觀測商品：", list(SYMBOL_MAP.keys()))
target_symbol = SYMBOL_MAP[selected_label]

# 3. 台北實時顯示
tz_tw = pytz.timezone('Asia/Taipei')
st.write(f"🕒 台北實時：{datetime.now(tz_tw).strftime('%Y-%m-%d %H:%M:%S')}")

# 4. 強化的數據抓取
@st.cache_data(ttl=60)
def fetch_safe_data(symbol):
    try:
        # 抓取 7 天數據，強制關閉進度條
        df = yf.download(symbol, period="7d", interval="1d", progress=False)
        if df.empty:
            return None
        
        # 【關鍵修復】解決多層標籤問題：強制將標籤扁平化
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        return df
    except:
        return None

df = fetch_safe_data(target_symbol)

# 5. 安全解析數據
if df is not None:
    try:
        # 抓取最後一列並轉換為純數字
        last_row = df.iloc[-1]
        
        # 使用 values[0] 確保只抓到單一數字，避免 TypeError
        c_p = float(last_row['Close'])
        h_p = float(last_row['High'])
        l_p = float(last_row['Low'])
        
        # 6. 計算 0.618 戰情點位
        diff = h_p - l_p
        r_0618 = l_p + (diff * 0.618)
        s_0382 = l_p + (diff * 0.382)

        st.success(f"✅ {selected_label} 連線成功")
        
        # 數據看板
        m1, m2, m3 = st.columns(3)
        m1.metric("目前價格", f"{c_p:,.2f}")
        m2.metric("高點", f"{h_p:,.2f}")
        m3.metric("低點", f"{l_p:,.2f}")
        
        st.divider()
        st.subheader("🎯 關鍵戰情點位")
        st.info(f"🚀 壓力區 (0.618)：**{r_0618:,.2f}**")
        st.warning(f"🛡️ 支撐區 (0.382)：**{s_0382:,.2f}**")

    except Exception as e:
        st.error("⚠️ 數據解析中，請稍候重新整理。")
        st.caption(f"錯誤代碼: {e}")
else:
    st.error("❌ 抓取不到數據。微台期 (WTX=F) 在非交易時段可能無資料，請嘗試切換到加權指數或 ADR。")

if st.button("🔄 刷新頁面"):
    st.rerun()
