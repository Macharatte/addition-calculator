import streamlit as st
import math
import statistics
import re
import datetime
import urllib.request
import json

# --- 1. ページ構成 & 状態管理 ---
st.set_page_config(page_title="Premium Calc 2025", layout="centered")

if 'lang' not in st.session_state:
    st.session_state.lang = "JP"
    st.session_state.f_state = ""
    st.session_state.m_idx = 0
    st.session_state.p_sub = "tax"
    st.session_state.tax_res = "---"
    st.session_state.theme = "Dark"
    st.session_state.rates = {"USD": 156.40, "BTC": 13972000, "ETH": 485500}
    st.session_state.last_update = "未更新"

# --- 2. 外部ライブラリ不要のリアルタイム取得 ---
def fetch_realtime():
    try:
        # 為替取得
        with urllib.request.urlopen("https://open.er-api.com/v6/latest/USD") as response:
            data = json.loads(response.read().decode())
            st.session_state.rates["USD"] = data["rates"]["JPY"]
        # 仮想通貨取得
        cry_url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=jpy"
        with urllib.request.urlopen(cry_url) as response:
            c_data = json.loads(response.read().decode())
            st.session_state.rates["BTC"] = c_data["bitcoin"]["jpy"]
            st.session_state.rates["ETH"] = c_data["ethereum"]["jpy"]
        st.session_state.last_update = datetime.datetime.now().strftime("%H:%M:%S")
        st.toast("最新レートを同期しました")
    except:
        st.error("通信エラー。バックアップレートを使用します。")

# --- 3. デザイン定義 ---
is_dark = st.session_state.theme == "Dark"
bg, txt, dbg = ("#1A1A1A", "#FFFFFF", "#333333") if is_dark else ("#FFFFFF", "#000000", "#F8F9FA")

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg}; color: {txt}; }}
    .display {{
        display: flex; align-items: center; justify-content: flex-end; font-size: 38px; font-weight: 900; 
        margin: 5px 0; padding: 15px; border: 3px solid {txt}; border-radius: 12px; 
        min-height: 80px; background: {dbg}; color: {txt};
    }}
    div.stButton > button {{ width: 100% !important; background-color: {dbg} !important; color: {txt} !important; border: 1px solid {txt} !important; height: 45px !important; }}
    button[key="update_btn"] {{ background-color: #007AFF !important; color: white !important; }}
</style>
""", unsafe_allow_html=True)

# --- 4. ヘッダー & 電卓 ---
c1, c2, c3 = st.columns([1,1,1])
with c1: st.session_state.lang = st.selectbox("", ["JP", "EN"], label_visibility="collapsed")
with c2: 
    if st.button("🔄 更新", key="update_btn"): fetch_realtime()
with c3:
    if st.button("☀️" if is_dark else "🌙", key="theme_btn"):
        st.session_state.theme = "Light" if is_dark else "Dark"
        st.rerun()

st.caption(f"最終更新: {st.session_state.last_update}")
st.markdown(f'<div class="display">{st.session_state.f_state if st.session_state.f_state else "0"}</div>', unsafe_allow_html=True)

# キーパッド
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

# --- 5. モード選択 (燃料・税金) ---
mc = st.columns(5)
for i, m in enumerate(["通常", "科学", "統計", "拡縮", "有料"]):
    if mc[i].button(m, key=f"m_{i}"): st.session_state.m_idx = i; st.rerun()

if st.session_state.m_idx == 4:
    sc = st.columns(3)
    if sc[0].button("燃料"): st.session_state.p_sub = "gas"; st.rerun()
    if sc[1].button("為替"): st.session_state.p_sub = "cur"; st.rerun()
    if sc[2].button("仮想"): st.session_state.p_sub = "cry"; st.rerun()
    
    if st.session_state.p_sub == "gas":
        loc = st.selectbox("地点", ["青梅市河辺町(最高)", "立川市一番町(最低)", "東京平均"])
        p = 188 if "青梅" in loc else (169 if "立川" in loc else 176)
        v = st.number_input("給油量(L)", 1, 100, 50)
        st.info(f"合計金額: {int(p*v):,} JPY")
