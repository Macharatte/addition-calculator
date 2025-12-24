import streamlit as st
import math
import statistics
import datetime
import requests

# --- ページ設定 ---
st.set_page_config(page_title="Python Calculator Pro", layout="centered")

# --- デザインCSS ---
st.markdown("""
<style>
    :root { --bg-page: #FFFFFF; --text-display: #000000; --btn-bg: #000000; --btn-text: #FFFFFF; --btn-border: #000000; }
    @media (prefers-color-scheme: dark) { :root { --bg-page: #000000; --text-display: #FFFFFF; --btn-bg: #FFFFFF; --btn-text: #000000; --btn-border: #FFFFFF; } }
    .main .block-container { max-width: 95% !important; padding: 5px 2px !important; background-color: var(--bg-page) !important; }
    header {visibility: hidden;}
    .display-container {
        display: flex; align-items: center; justify-content: flex-end;
        font-size: 55px; font-weight: 900; margin-bottom: 10px; padding: 10px; 
        border-bottom: 5px solid var(--text-display); min-height: 100px; color: var(--text-display);
    }
    div.stButton > button {
        width: 100% !important; height: 75px !important; border-radius: 8px !important;
        background-color: var(--btn-bg) !important; color: var(--btn-text) !important;
        border: 2px solid var(--btn-border) !important; transition: none !important;
    }
    div.stButton > button p { color: var(--btn-text) !important; white-space: nowrap !important; font-weight: 900; font-size: 16px; }
    
    .premium-btn div.stButton > button { background-color: #FFD700 !important; color: #000000 !important; border-color: #B8860B !important; }
    .premium-btn div.stButton > button p { color: #000000 !important; }
    
    .del-btn div.stButton > button { background-color: #FF4B4B !important; }
    .eq-btn div.stButton > button { background-color: #2e7d32 !important; }
</style>
""", unsafe_allow_html=True)

# --- 為替レート取得 ---
@st.cache_data(ttl=3600)
def get_rate(base_currency="JPY"):
    try:
        url = f"https://open.er-api.com/v6/latest/{base_currency}"
        return requests.get(url).json()["rates"]
    except:
        return {"USD": 0.0067, "EUR": 0.0061, "GBP": 0.0052, "CNY": 0.048}

# --- 状態管理 ---
ss = st.session_state
for key, val in [('formula', ""), ('mode', "通常"), ('last_was_equal', False), ('currency_select', False), ('tax_select', False)]:
    if key not in ss: ss[key] = val

st.markdown('<div style="text-align:center; font-weight:900; font-size:26px; color:var(--text-display);">PYTHON CALCULATOR 2 (PREMIUM)</div>', unsafe_allow_html=True)
st.markdown(f'<div class="display-container"><span>{ss.formula if ss.formula else "0"}</span></div>', unsafe_allow_html=True)

# --- ロジック ---
def on_click(char):
    try:
        if char == "＝":
            f = ss.formula.replace('×', '*').replace('÷', '/').replace('−', '-').replace('m', '-')
            ss.formula = format(eval(f, {"math": math, "statistics": statistics, "abs": abs}), '.10g')
            ss.last_was_equal = True
        elif char == "delete":
            ss.formula = ""
        elif "→JPY" in char:
            currency = char.split("→")[0]
            rates = get_rate("JPY")
            val = float(eval(ss.formula.replace('×', '*').replace('÷', '/').replace('−', '-')))
            ss.formula = format(val * (1 / rates[currency]), '.10g')
            ss.last_was_equal = True; ss.currency_select = False
        elif "tax_" in char:
            # 税金計算ロジック
            val = float(eval(ss.formula.replace('×', '*').replace('÷', '/').replace('−', '-')))
            rates = {"tax_10": 1.10, "tax_8": 1.08, "tax_income": 0.20, "tax_corp": 0.30, "tax_res": 0.10, "tax_fix": 0.014, "tax_gift": 0.15}
            if char in ["tax_10", "tax_8"]: ss.formula = format(val * rates[char], '.10g')
            else: ss.formula = format(val * rates[char], '.10g') # 各種税金額の算出
            ss.last_was_equal = True; ss.tax_select = False
        else:
            if ss.last_was_equal: ss.formula = ""; ss.last_was_equal = False
            ss.formula += str(char)
    except:
        ss.formula = "Error"

# --- キーパッド ---
main_btns = ["7","8","9","π","√","+","4","5","6","e","^^","−","1","2","3","i","(-)","×","0","00",".","(",")","÷"]
cols = st.columns(6)
for i, b in enumerate(main_btns):
    with cols[i % 6]:
        if st.button(b, key=f"k{i}"): on_click(b); st.rerun()

st.write("") 
bot_c1, bot_c2 = st.columns(2)
with bot_c1:
    st.markdown('<div class="del-btn">', unsafe_allow_html=True)
    if st.button("delete", use_container_width=True): on_click("delete"); st.rerun()
with bot_c2:
    st.markdown('<div class="eq-btn">', unsafe_allow_html=True)
    if st.button("＝", use_container_width=True): on_click("＝"); st.rerun()

st.markdown('<hr style="margin:15px 0; opacity:0.3;">', unsafe_allow_html=True)

# --- モード切替 ---
modes = ["通常", "科学計算", "巨数", "値数", "👑 有料機能"]
m_cols = st.columns(5)
for i, m in enumerate(modes):
    if m_cols[i].button(m, key=f"m{i}"): 
        ss.mode = m; ss.currency_select = False; ss.tax_select = False; st.rerun()

# --- 👑 有料機能モード ---
if ss.mode == "👑 有料機能":
    st.markdown('<div style="color:var(--text-display); font-weight:bold;">PREMIUM: 有料機能</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="premium-btn">', unsafe_allow_html=True)
        if st.button("税金計算"): ss.tax_select = not ss.tax_select; ss.currency_select = False; st.rerun()
    with c2:
        st.markdown('<div class="premium-btn">', unsafe_allow_html=True)
        if st.button("為替レート"): ss.currency_select = not ss.currency_select; ss.tax_select = False; st.rerun()

    # 税金計算メニュー
    if ss.tax_select:
        st.info("計算したい項目を選んでください（入力値に対して計算します）")
        t_cols = st.columns(4)
        taxes = [("税込(10%)", "tax_10"), ("税込(8%)", "tax_8"), ("所得税(20%目安)", "tax_income"), 
                 ("法人税(30%目安)", "tax_corp"), ("住民税(10%)", "tax_res"), ("固定資産税(1.4%)", "tax_fix"), ("贈与税(15%目安)", "tax_gift")]
        for i, (label, code) in enumerate(taxes):
            with t_cols[i % 4]:
                if st.button(label, key=f"taxbtn{i}"): on_click(code); st.rerun()

    # 為替レートメニュー
    if ss.currency_select:
        st.info("変換したい通貨を選んでください（日本円に換算します）")
        currencies = ["USD", "EUR", "GBP", "CNY", "KRW", "AUD", "CAD", "SGD"]
        c_cols = st.columns(4)
        for i, curr in enumerate(currencies):
            with c_cols[i % 4]:
                if st.button(f"{curr}→JPY", key=f"curr{i}"): on_click(f"{curr}→JPY"); st.rerun()
