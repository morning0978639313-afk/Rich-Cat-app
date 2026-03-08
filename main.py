import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

# 1. 頁面基礎設定
st.set_page_config(page_title="RICH CAT 戰情室", layout="centered")

# 2. 標題與時間 (確保每次執行都會更新)
st.title("🐱 RICH CAT 戰情室 v3.0")
tz = pytz.timezone('Asia/Taipei')
now = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
st.write(f"🕒 台北實時：{now}")

# 3. 穩定版數據抓取
def get_market_data():
    try:
        # 使用 Ticker 模式獲取數據，結構較 yf.download 穩定
        symbol = "^TWII" 
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="5d")
        if df.empty:
            return None
        return df
    except:
        return None

df = get_market_data()

# 4. 數據解析與防錯
if df is not None:
    try:
        # 強制抓取最後一列並轉換為純數字，解決 TypeError 問題
        last_val = df.tail(1)
        close_p = float(last_val['Close'].iloc[0])
        high_p = float(last_val['High'].iloc[0])
        low_p = float(last_val['Low'].iloc[0])

        # 5. 計算 0.618 戰情位
        diff = high_p - low_p
        r_0618 = low_p + (diff * 0.618)
        s_0382 = low_p + (diff * 0.382)

        st.success("✅ 數據連線成功")
        
        # 顯示數值
        c1, c2, c3 = st.columns(3)
        c1.metric("當前點數", f"{close_p:,.2f}")
        c2.metric("今日高點", f"{high_p:,.2f}")
        c3.metric("今日低點", f"{low_p:,.2f}")
        
        st.divider()
        st.subheader("🎯 關鍵 0.618 戰情位")
        st.info(f"📈 壓力區 (0.618)：**{r_0618:,.2f}**")
        st.warning(f"📉 支撐區 (0.382)：**{s_0382:,.2f}**")
        
    except Exception as e:
        st.error(f"⚠️ 數據解析中，請稍候再重新整理。")
        st.caption(f"系統訊息: {e}")
else:
    st.error("❌ 無法取得即時行情，請檢查網路。")

# 6. 增加手動刷新按鈕
if st.button("🔄 刷新數據"):
    st.rerun()
