import streamlit as st
import math
import statistics
import re
import datetime
import urllib.request
import json

# --- 1. ページ構成 & 状態管理 ---
st.set_page_config(page_title="Ultimate Premium Calc 2025", layout="centered")

# 初期状態の定義
if 'lang' not in st.session_state:
    st.session_state.lang = "JP"
    st.session_state.f_state = ""
    st.session_state.m_idx = 0
    st.session_state.p_sub = "tax"
    st.session_state.tax_res = "---"
    st.session_state.theme = "Dark"
    st.session_state.rates = {"USD": 156.40, "BTC": 13972000, "ETH": 485500}
    st.session_state.last_update = "未更新"

# --- 2. リアルタイムデータ取得 (標準ライブラリのみ) ---
def fetch_realtime():
    try:
        with urllib.request.urlopen("https://open.er-api.com/v6/latest/USD") as response:
            data = json.loads(response.read().decode())
            st.session_state.rates["USD"] = data["rates"]["JPY"]
        cry_url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=jpy"
        with urllib.request.urlopen(cry_url) as response:
            c_data = json.loads(response.read().decode())
            st.session_state.rates["BTC"] = c_data["bitcoin"]["jpy"]
            st.session_state.rates["ETH"] = c_data["ethereum"]["jpy"]
        st.session_state.last_update = datetime.datetime.now().strftime("%H:%M:%S")
        st.toast("最新レートを同期しました")
    except:
        st.error("同期失敗。バックアップを使用します。")

# --- 3. デザイン定義 ---
is_dark = st.session_state.theme == "Dark"
bg, txt, dbg = ("#1A1A1A", "#FFFFFF", "#333333") if is_dark else ("#F0F2F6", "#000000", "#FFFFFF")

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg}; color: {txt}; }}
    .display {{
        display: flex; align-items: center; justify-content: flex-end; font-size: 38px; font-weight: 900; 
        margin: 5px 0; padding: 15px; border: 3px solid {txt}; border-radius: 12px; 
        min-height: 80px; background: {dbg}; color: {txt}; overflow-x: auto;
    }}
    div.stButton > button {{ width: 100% !important; background-color: {dbg} !important; color: {txt} !important; border: 1px solid {txt} !important; height: 45px !important; font-weight: 900 !important; }}
    button[key="update_btn"] {{ background-color: #007AFF !important; color: white !important; }}
    button[key="theme_btn"] {{ background-color: #FF9500 !important; color: white !important; }}
    .res-box {{ border: 2px solid {txt}; border-radius: 10px; padding: 15px; background: {dbg}; text-align: center; font-weight: 900; }}
</style>
""", unsafe_allow_html=True)

# --- 4. ヘッダー ---
c1, c2, c3 = st.columns([1,1,1])
with c1: st.session_state.lang = st.selectbox("", ["JP", "EN"], label_visibility="collapsed")
with c2: 
    if st.button("🔄 更新", key="update_btn"): fetch_realtime()
with c3:
    if st.button("☀️" if is_dark else "🌙", key="theme_btn"):
        st.session_state.theme = "Light" if is_dark else "Dark"
        st.rerun()

st.caption(f"最終更新: {st.session_state.last_update} | USD: {st.session_state.rates['USD']:.2f}")
st.markdown(f'<div class="display">{st.session_state.f_state if st.session_state.f_state else "0"}</div>', unsafe_allow_html=True)

# --- 5. 電卓キーパッド (常に表示) ---
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
            ex = st.session_state.f_state.replace('×','*').replace('÷','/').replace('−','-').replace('π','math.pi').replace('√','math.sqrt')
            st.session_state.f_state = format(eval(ex, {"math": math, "statistics": statistics}), '.10g')
        except: st.session_state.f_state = "Error"
        st.rerun()

st.divider()

# --- 6. モード切替 ---
mode_labels = ["通常", "科学計算", "統計", "拡縮", "有料"]
mc = st.columns(5)
for i, m in enumerate(mode_labels):
    if mc[i].button(m, key=f"m_{i}"): st.session_state.m_idx = i; st.rerun()

midx = st.session_state.m_idx

# --- 各モードの復元表示 ---
if midx == 1: # 科学計算
    sc = st.columns(4)
    labels = ["sin", "cos", "tan", "log", "exp", "√", "n!", "abs"]
    funcs = ["math.sin(", "math.cos(", "math.tan(", "math.log10(", "math.exp(", "math.sqrt(", "math.factorial(", "abs("]
    for i, l in enumerate(labels):
        if sc[i % 4].button(l, key=f"sci_{i}"): st.session_state.f_state += funcs[i]; st.rerun()

elif midx == 2: # 統計
    sc = st.columns(3)
    s_labels = ["平均", "中央値", "最大", "最小", "合計", "個数"]
    s_funcs = ["statistics.mean([", "statistics.median([", "max([", "min([", "sum([", "len(["]
    for i, l in enumerate(s_labels):
        if sc[i % 3].button(l, key=f"stat_{i}"): st.session_state.f_state += s_funcs[i]; st.rerun()
    if st.button("配列を閉じる: ])", key="cl_arr"): st.session_state.f_state += "])"; st.rerun()

elif midx == 3: # 拡縮 (SI接頭語)
    sc = st.columns(4)
    si_list = ["k", "M", "G", "T", "m", "μ", "n", "p"]
    for i, s in enumerate(si_list):
        if sc[i % 4].button(s, key=f"si_{i}"): st.session_state.f_state += s; st.rerun()

elif midx == 4: # 有料機能
    pc = st.columns(4)
    for i, l in enumerate(["燃料", "為替", "仮想", "税金"]):
        if pc[i].button(l, key=f"p_{i}"): st.session_state.p_sub = ["gas", "cur", "cry", "tax"][i]; st.rerun()
    
    sub = st.session_state.p_sub
    if sub == "gas":
        loc = st.selectbox("地点", ["青梅市河辺町(最高)", "立川市一番町(最低)", "東京平均"])
        p = 188 if "青梅" in loc else (169 if "立川" in loc else 176)
        v = st.number_input("給油量(L)", 1, 100, 50)
        st.session_state.tax_res = f"{loc}: {int(p*v):,} JPY"
    
    elif sub == "cur":
        usd = st.session_state.rates["USD"]
        v = st.number_input("米ドル(USD)", 0.0, 1000000.0, 100.0)
        st.session_state.tax_res = f"換算: {v * usd:,.2f} JPY"

    elif sub == "cry":
        coin = st.selectbox("銘柄", ["BTC", "ETH"])
        rate = st.session_state.rates[coin]
        v = st.number_input(f"保有量({coin})", 0.0, 1000.0, 0.1, format="%.4f")
        st.session_state.tax_res = f"時価: {int(v * rate):,} JPY"

    st.markdown(f'<div class="res-box">{st.session_state.tax_res}</div>', unsafe_allow_html=True)
