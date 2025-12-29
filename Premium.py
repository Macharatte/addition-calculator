import streamlit as st
import math
import statistics
import urllib.request
import json
import datetime

# --- 1. ページ設定 ---
st.set_page_config(page_title="Professional Calculator 2025", layout="centered")

# --- 2. 状態管理 ---
if 'display' not in st.session_state:
    st.session_state.display = ""
if 'rates' not in st.session_state:
    st.session_state.rates = {"USD": 156.40, "BTC": 13972000, "ETH": 485500}
if 'theme' not in st.session_state:
    st.session_state.theme = "Dark"

# --- 3. 外部データ取得 ---
def update_rates():
    try:
        with urllib.request.urlopen("https://open.er-api.com/v6/latest/USD") as response:
            data = json.loads(response.read().decode())
            st.session_state.rates["USD"] = data["rates"]["JPY"]
        cry_url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=jpy"
        with urllib.request.urlopen(cry_url) as response:
            c_data = json.loads(response.read().decode())
            st.session_state.rates["BTC"] = c_data["bitcoin"]["jpy"]
            st.session_state.rates["ETH"] = c_data["ethereum"]["jpy"]
        st.toast("MARKET DATA UPDATED")
    except:
        st.error("CONNECTION ERROR")

# --- 4. CSS (枠囲みとボタンデザイン) ---
is_dark = st.session_state.theme == "Dark"
bg, txt, dbg = ("#121212", "#FFFFFF", "#252525") if is_dark else ("#F5F5F5", "#000000", "#FFFFFF")
border_color = "#444444" if is_dark else "#CCCCCC"

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg}; color: {txt}; }}
    /* ディスプレイ */
    .calc-display {{
        background-color: {dbg}; color: {txt};
        padding: 20px; border: 2px solid {txt}; border-radius: 4px;
        font-size: 40px; font-weight: 700; text-align: right;
        min-height: 90px; margin-bottom: 20px; font-family: 'Courier New', monospace;
    }}
    /* ボタン共通 */
    div.stButton > button {{
        width: 100% !important; height: 50px !important;
        font-weight: 700 !important; font-size: 16px !important;
        background-color: {dbg} !important; color: {txt} !important;
        border: 1px solid {border_color} !important; border-radius: 2px !important;
    }}
    /* 特殊ボタン */
    button[key="exe_btn"] {{ background-color: #28a745 !important; color: white !important; border: none !important; }}
    button[key="clr_btn"] {{ background-color: #dc3545 !important; color: white !important; border: none !important; }}
    button[key="update_btn"] {{ background-color: #007bff !important; color: white !important; border: none !important; }}
    
    /* 選択・入力エリアの枠囲み */
    .input-group {{
        border: 1px solid {border_color};
        padding: 20px;
        border-radius: 4px;
        background-color: {dbg};
        margin-bottom: 15px;
    }}
</style>
""", unsafe_allow_html=True)

# --- 5. ヘッダー ---
h1, h2 = st.columns([1, 1])
with h1:
    if st.button("UPDATE RATES", key="update_btn"): update_rates()
with h2:
    if st.button("SWITCH THEME"):
        st.session_state.theme = "Light" if is_dark else "Dark"
        st.rerun()

# --- 6. メインディスプレイ ---
st.markdown(f'<div class="calc-display">{st.session_state.display if st.session_state.display else "0"}</div>', unsafe_allow_html=True)

# --- 7. 数値・演算子キー (4x4) ---
rows = [
    ["7", "8", "9", "÷"],
    ["4", "5", "6", "×"],
    ["1", "2", "3", "−"],
    ["0", ".", "π", "+"]
]
mapping = {"÷": "/", "×": "*", "−": "-", "π": "math.pi"}

for row in rows:
    cols = st.columns(4)
    for i, label in enumerate(row):
        if cols[i].button(label):
            st.session_state.display += mapping.get(label, label)
            st.rerun()

b1, b2 = st.columns(2)
if b1.button("CLEAR", key="clr_btn"):
    st.session_state.display = ""
    st.rerun()
if b2.button("EXECUTE ( = )", key="exe_btn"):
    try:
        # 接頭語変換
        calc_str = st.session_state.display
        si = {"k":"*1e3", "M":"*1e6", "G":"*1e9", "T":"*1e12", "m":"*1e-3", "u":"*1e-6", "n":"*1e-9", "p":"*1e-12"}
        for k, v in si.items(): calc_str = calc_str.replace(k, v)
        res = eval(calc_str, {"math": math, "statistics": statistics})
        st.session_state.display = format(res, '.10g')
    except:
        st.session_state.display = "ERROR"
    st.rerun()

st.divider()

# --- 8. 追加機能エリア (タブ形式・ボタン配置) ---
tab_sci, tab_stat, tab_si, tab_paid = st.tabs(["SCIENTIFIC", "STATISTICS", "SI UNITS", "PAID FEATURES"])

with tab_sci:
    st.caption("SCIENTIFIC FUNCTIONS")
    s_rows = [["sin", "cos", "tan", "sqrt"], ["log10", "log", "abs", "("], [")", "^", "exp", "n!"]]
    s_map = {"sin":"math.sin(", "cos":"math.cos(", "tan":"math.tan(", "sqrt":"math.sqrt(", 
             "log10":"math.log10(", "log":"math.log(", "abs":"abs(", "^":"**", "exp":"math.exp(", "n!":"math.factorial("}
    for s_row in s_rows:
        cols = st.columns(4)
        for i, l in enumerate(s_row):
            if i < len(cols) and cols[i].button(l, key=f"s_{l}"):
                st.session_state.display += s_map.get(l, l)
                st.rerun()

with tab_stat:
    st.caption("STATISTICAL ANALYSIS")
    st_cols = st.columns(3)
    if st_cols[0].button("MEAN", key="st_mean"): st.session_state.display += "statistics.mean(["; st.rerun()
    if st_cols[1].button("MEDIAN", key="st_med"): st.session_state.display += "statistics.median(["; st.rerun()
    if st_cols[2].button("SUM", key="st_sum"): st.session_state.display += "sum(["; st.rerun()
    if st.button("CLOSE ARRAY ( ]) )", key="st_close"): st.session_state.display += "])"; st.rerun()

with tab_si:
    st.caption("SI PREFIXES")
    si_rows = [["k", "M", "G", "T"], ["m", "u", "n", "p"]]
    for si_row in si_rows:
        cols = st.columns(4)
        for i, l in enumerate(si_row):
            if cols[i].button(l, key=f"si_{l}"):
                st.session_state.display += l
                st.rerun()

with tab_paid:
    st.markdown('<div class="input-group">', unsafe_allow_html=True)
    mode = st.radio("SELECT FEATURE", ["FUEL PRICE", "CURRENCY", "CRYPTO"], horizontal=True)
    
    if mode == "FUEL PRICE":
        loc = st.selectbox("LOCATION", ["OME-KABE (MAX)", "TACHIKAWA-ICHIBAN (MIN)", "TOKYO AVERAGE"])
        price = 188 if "OME" in loc else (169 if "TACHIKAWA" in loc else 176)
        lit = st.number_input("VOLUME (L)", 1.0, 500.0, 50.0)
        st.info(f"UNIT PRICE: {price} JPY/L | TOTAL: {int(price*lit):,} JPY")
        
    elif mode == "CURRENCY":
        u_rate = st.session_state.rates["USD"]
        st.text(f"RATE: 1 USD = {u_rate:.2f} JPY")
        amt = st.number_input("AMOUNT (USD)", 0.0, 1000000.0, 100.0)
        st.info(f"CONVERSION: {amt * u_rate:,.0f} JPY")
        
    elif mode == "CRYPTO":
        coin = st.selectbox("ASSET", ["BTC", "ETH"])
        p = st.session_state.rates[coin]
        st.text(f"PRICE: 1 {coin} = {int(p):,} JPY")
        hold = st.number_input("HOLDING", 0.0, 1000.0, 0.1, format="%.4f")
        st.info(f"VALUE: {int(hold * p):,} JPY")
    st.markdown('</div>', unsafe_allow_html=True)
