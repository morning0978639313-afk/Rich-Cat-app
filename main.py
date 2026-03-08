import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

# 1. 介面設定
st.set_page_config(page_title="RICH CAT 戰情室", page_icon="🐱")
st.markdown("<style>.stApp { background-color: #0E1117; color: white; }</style>", unsafe_allow_html=True)

# 2. 修正台灣時區
taiwan_now = datetime.utcnow() + timedelta(hours=8)

# 3. 抓取三萬點真實行情 (使用 FinMind API)
def get_data():
    try:
        url = "https://api.finmindtrade.com/api/v4/data?dataset=TaiwanFuturesTick&data_id=TXF&date=" + taiwan_now.strftime('%Y-%m-%d')
        res = requests.get(url).json().get('data', [])
        if res:
            df = pd.DataFrame(res)
            return {"current": df['price'].iloc[-1], "open": df['price'].iloc[0], "high": df['price'].max(), "low": df['price'].min()}
    except: return None

market = get_data()

st.title("🐱 RICH CAT 戰情室 v3.0")
st.write(f"🕒 台北實時：{taiwan_now.strftime('%H:%M:%S')}")

if market:
    # 核心 0.618 邏輯
    target = ((market['current'] - market['open']) / 0.618) + market['open']
    defense = market['high'] - (market['high'] - market['low']) * 0.618
    
    st.metric("目前成交", f"{market['current']}", delta_color="inverse")
    st.success(f"🎯 一階目標價：{round(target, 1)}")
    st.error(f"🛡️ 0.618 防守位：{round(defense, 1)}")
else:
    st.warning("📊 數據連線中（夜盤或非交易時段可能略有延遲）...")
