import streamlit as st
import math
import statistics
import re
import datetime
import urllib.request
import json

# --- 1. ページ構成 & 状態管理 ---
APP_ID = "v2025_12_30_FINAL_STABLE"
if 'app_id' not in st.session_state or st.session_state.app_id != APP_ID:
    st.session_state.clear()
    st.session_state.app_id = APP_ID
    st.session_state.lang = "JP"
    st.session_state.f_state = ""
    st.session_state.m_idx = 0
    st.session_state.p_sub = "tax"
    st.session_state.tax_res = "---"
    st.session_state.theme = "Dark"
    # 初期レート
    st.session_state.rates = {"USD": 156.40, "BTC": 13972000, "ETH": 485500, "XAU": 13200}
    st.session_state.last_update = "未更新"

# --- 2. リアルタイムデータ取得 (yfinance不要版) ---
def fetch_realtime_data():
    try:
        # 為替レートをAPI経由で取得 (ExchangeRate-Host等のパブリックAPIを利用)
        # ※ここでは学習用として、信頼性の高いシミュレーションとFetchを統合
        url = "https://open.er-api.com/v6/latest/USD"
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            st.session_state.rates["USD"] = data["rates"]["JPY"]
        
        # 仮想通貨 (CoinGecko API)
        cry_url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=jpy"
        with urllib.request.urlopen(cry_url) as response:
            cry_data = json.loads(response.read().decode())
            st.session_state.rates["BTC"] = cry_data["bitcoin"]["jpy"]
            st.session_state.rates["ETH"] = cry_data["ethereum"]["jpy"]
            
        st.session_state.last_update = datetime.datetime.now().strftime("%H:%M:%S")
        st.toast("最新市場レートを同期しました！")
    except:
        st.warning("外部通信に失敗しました。以前のレートを使用します。")

# --- 3. デザイン定義 (テーマ切替) ---
is_dark = st.session_state.theme == "Dark"
bg_color = "#1A1A1A" if is_dark else "#FFFFFF"
text_color = "#FFFFFF" if is_dark else "#000000"
disp_bg = "#333333" if is_dark else "#F8F9FA"
btn_bg = "#333333" if is_dark else "#E9ECEF"

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg_color}; color: {text_color}; }}
    .display {{
        display: flex; align-items: center; justify-content: flex-end; font-size: 38px; font-weight: 900; 
        margin: 5px 0; padding: 15px; border: 3px solid {text_color}; border-radius: 12px; 
        min-height: 80px; background: {disp_bg}; color: {text_color};
    }}
    div.stButton > button {{ 
        width: 100% !important; background-color: {btn_bg} !important; color: {text_color} !important; 
        font-weight: 900 !important; border: 1px solid {text_color} !important; height: 45px !important;
    }}
    button[key="update_btn"] {{ background-color: #007AFF !important; color: white !important; border: none !important; }}
    button[key="theme_btn"] {{ background-color: #FF9500 !important; color: white !important; border: none !important; }}
    .res-box {{ border: 2px solid {text_color}; border-radius: 10px; padding: 10px; background: {disp_bg}; text-align: center; font-size: 20px; font-weight: 900; }}
</style>
""", unsafe_allow_html=True)

# --- 4. ヘッダー ---
c1, c2, c3 = st.columns([1, 1, 1])
with c1: st.session_state.lang = st.selectbox("", ["JP", "EN"], label_visibility="collapsed")
with c2: 
    if st.button("🔄 リアル更新", key="update_btn"): fetch_realtime_data()
with c3:
    if st.button("☀️" if is_dark else "🌙", key="theme_btn"):
        st.session_state.theme = "Light" if is_dark else "Dark"
        st.rerun()

st.caption(f"最終更新: {st.session_state.last_update} | USD: {st.session_state.rates['USD']:.2f}円")
st.markdown(f'<div class="display">{st.session_state.f_state if st.session_state.f_state else "0"}</div>', unsafe_allow_html=True)

# --- 5. 電卓本体 ---
keys = ["7","8","9","÷","4","5","6","×","1","2","3","−","0",".","π","+"]
cols = st.columns(4)
for i, k in enumerate(keys):
    if cols[i % 4].button(k, key=f"k_{i}"):
        st.session_state.f_state += k; st.rerun()

b1, b2 = st.columns(2)
with b1:
    if st.button("CLEAR", key="btn_del"): st.session_state.f_state = ""; st.rerun()
with b2:
    if st.button("＝", key="btn_exe"):
        try:
            ex = st.session_state.f_state.replace('×','*').replace('÷','/').replace('−','-')
            st.session_state.f_state = format(eval(ex), '.10g')
        except: st.session_state.f_state = "Error"
        st.rerun()

st.divider()

# --- 6. モード切替 ---
modes = ["通常", "科学", "統計", "拡縮", "有料"]
mc = st.columns(5)
for i, m in enumerate(modes):
    if mc[i].button(m, key=f"m_{i}"): st.session_state.m_idx = i; st.rerun()

if st.session_state.m_idx == 4:
    pc = st.columns(4)
    p_subs = ["tax", "cur", "gas", "cry"]
    for i, l in enumerate(["税金", "為替", "燃料", "仮想"]):
        if pc[i].button(l, key=f"p_{i}"): st.session_state.p_sub = p_subs[i]; st.rerun()
    
    sub = st.session_state.p_sub
    if sub == "gas":
        loc = st.selectbox("地点", ["青梅市河辺町 (最高額店)", "立川市一番町 (最低額店)", "東京平均"])
        p = 188 if "青梅" in loc else (169 if "立川" in loc else 176)
        st.info(f"現在の設定単価: {p}円/L")
        amt = st.text_input("給油量 (L)", "50")
        if st.button("計算"):
            st.session_state.tax_res = f"合計金額: {int(p * float(amt)):,} JPY"
            st.rerun()

    elif sub == "cur":
        usd = st.session_state.rates["USD"]
        v = st.text_input("金額 (USD)", "100")
        if st.button("換算"):
            st.session_state.tax_res = f"日本円: {float(v) * usd:,.2f} JPY"
            st.rerun()
            
    st.markdown(f'<div class="res-box">{st.session_state.tax_res}</div>', unsafe_allow_html=True)
