import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

# 1. 基礎頁面設定
st.set_page_config(page_title="RICH CAT 戰情室", layout="centered")

# 2. 標題與時間顯示
st.title("🐱 RICH CAT 戰情室 v3.0")
tz = pytz.timezone('Asia/Taipei')
now = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
st.write(f"🕒 台北實時：{now}")

# 3. 數據抓取函式 (強化非交易時段讀取)
def fetch_market_data():
    symbol = "^TWII"  # 以台股加權指數為例，可改為期指代碼
    try:
        # 抓取最近 5 天資料，確保在週末或凌晨也能抓到最後一個收盤日
        df = yf.download(symbol, period="5d", interval="1d")
        if df.empty:
            return None
        return df
    except:
        return None

# 4. 執行抓取與邏輯判斷
data = fetch_market_data()

if data is not None:
    # 取得最後一筆有效交易數據
    last_row = data.iloc[-1]
    
    close_price = float(last_row['Close'])
    high_price = float(last_row['High'])
    low_price = float(last_row['Low'])
    
    # 5. 0.618 戰情計算邏輯
    diff = high_price - low_price
    resistance_0618 = low_price + (diff * 0.618)
    support_0382 = low_price + (diff * 0.382)

    # 6. UI 顯示介面
    st.success("✅ 數據連線成功 (顯示最新交易日資訊)")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("當前點數", f"{close_price:,.2f}")
    col2.metric("今日高點", f"{high_price:,.2f}")
    col3.metric("今日低點", f"{low_price:,.2f}")
    
    st.divider()
    
    # 7. 0.618 戰情位
    st.subheader("🎯 關鍵 0.618 戰情位")
    st.info(f"📈 壓力區 (0.618)：**{resistance_0618:,.2f}**")
    st.warning(f"📉 支撐區 (0.382)：**{support_0382:,.2f}**")
    
    # 提示非交易時段狀態
    current_hour = datetime.now(tz).hour
    if current_hour >= 14 or current_hour < 9:
        st.caption("💡 目前為非正規交易時段，畫面顯示為最後一筆收盤結算資訊。")

else:
    st.error("❌ 數據連線中（夜盤或非交易時段可能略有延遲）...")
