import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

# 1. 基礎設定
st.set_page_config(page_title="RICH CAT 戰情室", layout="centered")

# 2. 精簡四檔商品
SYMBOL_MAP = {
    "加權指數 (^TWII)": "^TWII",
    "微台近全 (WTX=F)": "WTX=F",
    "台積電 (2330)": "2330.TW",
    "台積電 ADR (TSM)": "TSM"
}

st.title("🐱 RICH CAT 戰情室 v7.0")
selected_label = st.selectbox("切換商品：", list(SYMBOL_MAP.keys()))
target_symbol = SYMBOL_MAP[selected_label]

# 3. 顯示時間
tz = pytz.timezone('Asia/Taipei')
st.write(f"🕒 台北實時：{datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')}")

# 4. 終極防禦抓取邏輯
def safe_fetch(symbol):
    try:
        # 抓取比較長的時間範圍，增加成功率
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="10d")
        
        if df.empty:
            return None, "數據源暫時無資料"
            
        # 解決導致當機的多層標籤問題
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        return df, None
    except Exception as e:
        return None, str(e)

# 5. 執行抓取
data, error_msg = safe_fetch(target_symbol)

if data is not None:
    try:
        last = data.iloc[-1]
        # 強制轉為純數字，防止 TypeError
        c = float(last['Close'])
        h = float(last['High'])
        l = float(last['Low'])
        
        # 0.618 計算
        diff = h - l
        r618 = l + (diff * 0.618)
        s382 = l + (diff * 0.382)
        
        st.success(f"✅ {selected_label} 連線成功")
        
        # 數據面板
        col1, col2, col3 = st.columns(3)
        col1.metric("價格", f"{c:,.2f}")
        col2.metric("高點", f"{h:,.2f}")
        col3.metric("低點", f"{l:,.2f}")
        
        st.divider()
        st.subheader("🎯 關鍵點位")
        st.info(f"壓力區 (0.618)：**{r618:,.2f}**")
        st.warning(f"支撐區 (0.382)：**{s382:,.2f}**")
        
    except Exception as e:
        st.error(f"⚠️ 解析資料出錯：{e}")
else:
    st.error(f"❌ 抓取失敗：{error_msg}")
    st.info("提示：非交易時段（如凌晨）部分商品可能無報價，請切換至『加權指數』試試。")

if st.button("🔄 點此刷新"):
    st.rerun()
