import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz
from streamlit_autorefresh import st_autorefresh # 使用你補上的第四個零件

# 1. 頁面基礎設定
st.set_page_config(page_title="RICH CAT 戰情室 v8.0", layout="centered")

# 2. 自動刷新設定：每 60 秒自動更新一次網頁
st_autorefresh(interval=60 * 1000, key="datarefresh")

# 3. 指定四檔商品
SYMBOL_MAP = {
    "加權指數 (^TWII)": "^TWII",
    "微台近全 (WTX=F)": "WTX=F",
    "台積電 (2330)": "2330.TW",
    "台積電 ADR (TSM)": "TSM"
}

st.title("🐱 RICH CAT 戰情室 v8.0")
selected_label = st.selectbox("切換觀測商品：", list(SYMBOL_MAP.keys()))
target_symbol = SYMBOL_MAP[selected_label]

# 4. 顯示台北實時
tz = pytz.timezone('Asia/Taipei')
st.write(f"🕒 台北實時：{datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')}")

# 5. 超安全數據讀取邏輯
def get_safe_data(symbol):
    try:
        # 抓取 10 天確保跨過假日，並關閉進度條防止崩潰
        df = yf.download(symbol, period="10d", interval="1d", progress=False)
        
        if df.empty:
            return None
            
        # 【關鍵】解決 yfinance 最近造成 TypeError 的多層標籤問題
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        return df
    except:
        return None

data = get_safe_data(target_symbol)

# 6. 計算與顯示
if data is not None:
    try:
        last = data.iloc[-1]
        # 強制轉為純數字，確保不會因為格式問題跳出 Oh no
        c = float(last['Close'])
        h = float(last['High'])
        l = float(last['Low'])
        
        # 0.618 點位計算
        diff = h - l
        r618 = l + (diff * 0.618)
        s382 = l + (diff * 0.382)

        st.success(f"📈 {selected_label} 連線成功 (每分鐘自動刷新)")
        
        # 數據看板
        col1, col2, col3 = st.columns(3)
        col1.metric("當前價格", f"{c:,.2f}")
        col2.metric("高點", f"{h:,.2f}")
        col3.metric("低點", f"{l:,.2f}")
        
        st.divider()
        st.subheader("🎯 關鍵戰情點位")
        st.info(f"🚀 壓力區 (0.618)：**{r618:,.2f}**")
        st.warning(f"🛡️ 支撐區 (0.382)：**{s382:,.2f}**")

    except Exception as e:
        st.error("數據解析中，請稍候。")
else:
    st.error("❌ 無法取得數據。目前非交易時段或雅虎伺服器忙碌中。")
    st.info("提示：若微台無資料，請先切換至『加權指數』確認連線。")
