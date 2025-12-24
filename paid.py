import streamlit as st
import math
import statistics
import datetime
import requests

# --- ページ設定 ---
st.set_page_config(page_title="Python Calculator Pro 2", layout="centered")

# --- デザインCSS ---
st.markdown("""
<style>
    :root { --bg-page: #FFFFFF; --text-display: #000000; --btn-bg: #000000; --btn-text: #FFFFFF; --btn-border: #000000; }
    @media (prefers-color-scheme: dark) { :root { --bg-page: #000000; --text-display: #FFFFFF; --btn-bg: #FFFFFF; --btn-text: #000000; --btn-border: #FFFFFF; } }
    .main .block-container { max-width: 95% !important; padding: 5px 2px !important; background-color: var(--bg-page) !important; }
    header {visibility: hidden;}
    .display-container {
        display: flex; align-items: center; justify-content: flex-end;
        font-size: 50px; font-weight: 900; margin-bottom: 10px; padding: 10px; 
        border-bottom: 5px solid var(--text-display); min-height: 100px; color: var(--text-display); word-break: break-all;
    }
    div.stButton > button {
        width: 100% !important; height: 70px !important; border-radius: 8px !important;
        background-color: var(--btn-bg) !important; color: var(--btn-text) !important;
        border: 2px solid var(--btn-border) !important; transition: none !important;
    }
    div.stButton > button p { color: var(--btn-text) !important; white-space: nowrap !important; font-weight: 900; font-size: 15px; }
    .premium-btn div.stButton > button { background-color: #FFD700 !important; color: #000000 !important; border-color: #B8860B !important; }
    .premium-btn div.stButton > button p { color: #000000 !important; }
    .del-btn div.stButton > button { background-color: #FF4B4B !important; }
    .eq-btn div.stButton > button { background-color: #2e7d32 !important; }
</style>
""", unsafe_allow_html=True)

# --- 定数・ロジック ---
SI_PREFIXES = {
    'Q': 1e30, 'R': 1e27, 'Y': 1e24, 'Z': 1e21, 'E': 1e18, 'P': 1e15, 'T': 1e12, 'G': 1e9, 'M': 1e6, 'k': 1e3, 'h': 1e2, 'da': 1e1,
    'd': 1e-1, 'c': 1e-2, 'm': 1e-3, 'μ': 1e-6, 'n': 1e-9, 'p': 1e-12, 'f': 1e-15, 'a': 1e-18, 'z': 1e-21, 'y': 1e-24, 'r': 1e-27, 'q': 1e-30
}

@st.cache_data(ttl=3600)
def get_all_rates():
    try:
        url = "https://open.er-api.com/v6/latest/USD"
        return requests.get(url).json()["rates"]
    except:
        return {"JPY": 150.0, "USD": 1.0, "EUR": 0.9, "GBP": 0.8}

def parse_formula(formula):
    """巨数単位を含む数式を数値に変換して計算する"""
    f = formula.replace('×', '*').replace('÷', '/').replace('−', '-').replace('m', '-')
    for unit, val in SI_PREFIXES.items():
        if unit in f:
            f = f.replace(unit, f"*({val})")
    return eval(f, {"math": math, "statistics": statistics, "abs": abs})

def calculate_complex_tax(val, tax_type):
    if tax_type == "tax_income":
        if val <= 1950000: return val * 0.05
        elif val <= 3300000: return val * 0.10 - 97500
        elif val <= 6950000: return val * 0.20 - 427500
        elif val <= 9000000: return val * 0.23 - 636000
        elif val <= 18000000: return val * 0.33 - 1536000
        elif val <= 40000000: return val * 0.40 - 2796000
        else: return val * 0.45 - 4796000
    elif tax_type == "tax_gift":
        v = val - 1100000
        if v <= 0: return 0
        if v <= 2000000: return v * 0.10
        elif v <= 3000000: return v * 0.15 - 100000
        elif v <= 4000000: return v * 0.20 - 250000
        elif v <= 6000000: return v * 0.30 - 650000
        elif v <= 10000000: return v * 0.40 - 1250000
        else: return v * 0.55 - 4000000
    elif tax_type == "tax_corp": return val * 0.232
    elif tax_type == "tax_res": return val * 0.10
    elif tax_type == "tax_fix": return val * 0.014
    return val

# --- 状態管理 ---
ss = st.session_state
for key, val in [('formula', ""), ('mode', "通常"), ('last_was_equal', False), ('premium_sub', "なし")]:
    if key not in ss: ss[key] = val

st.markdown('<div style="text-align:center; font-weight:900; font-size:24px; color:var(--text-display);">PYTHON CALCULATOR 2 PREMIUM</div>', unsafe_allow_html=True)
st.markdown(f'<div class="display-container"><span>{ss.formula if ss.formula else "0"}</span></div>', unsafe_allow_html=True)

# --- 基本ロジック ---
def on_click(char):
    try:
        if char == "＝":
            ss.formula = format(parse_formula(ss.formula), '.10g')
            ss.last_was_equal = True
        elif char == "delete": ss.formula = ""
        else:
            if ss.last_was_equal: ss.formula = ""; ss.last_was_equal = False
            ss.formula += str(char)
    except: ss.formula = "Error"

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

st.markdown('<hr style="margin:10px 0; opacity:0.3;">', unsafe_allow_html=True)

# --- モード切替 ---
modes = ["通常", "科学計算", "巨数", "値数", "有料機能"]
m_cols = st.columns(5)
for i, m in enumerate(modes):
    if m_cols[i].button(m, key=f"m{i}"): ss.mode = m; ss.premium_sub = "なし"; st.rerun()

# --- 各モードの追加ボタン ---
if ss.mode == "有料機能":
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="premium-btn">', unsafe_allow_html=True)
        if st.button("税金計算モード"): ss.premium_sub = "税金"; st.rerun()
    with c2:
        st.markdown('<div class="premium-btn">', unsafe_allow_html=True)
        if st.button("通貨変換モード"): ss.premium_sub = "通貨"; st.rerun()

    if ss.premium_sub == "税金":
        st.markdown("---")
        taxes = [("税込(10%)", "tax_10"), ("税込(8%)", "tax_8"), ("所得税", "tax_income"), 
                 ("法人税", "tax_corp"), ("住民税", "tax_res"), ("固定資産税", "tax_fix"), ("贈与税", "tax_gift")]
        t_cols = st.columns(4)
        for i, (label, code) in enumerate(taxes):
            with t_cols[i % 4]:
                if st.button(label, key=f"tbtn{i}"):
                    try:
                        # 現在のディスプレイの値を数値化してから税金計算
                        base_val = parse_formula(ss.formula)
                        if "10" in code: res = base_val * 1.10
                        elif "8" in code: res = base_val * 1.08
                        else: res = calculate_complex_tax(base_val, code)
                        ss.formula = format(res, '.10g')
                        ss.last_was_equal = True; st.rerun()
                    except: ss.formula = "Error"; st.rerun()

    if ss.premium_sub == "通貨":
        st.markdown("---")
        rates = get_all_rates()
        cur_list = sorted(list(rates.keys()))
        c1, _, c2 = st.columns([4, 1, 4])
        from_c = c1.selectbox("元", cur_list, index=cur_list.index("USD"))
        to_c = c2.selectbox("先", cur_list, index=cur_list.index("JPY"))
        input_v = st.text_input("数値", value=ss.formula if ss.formula != "Error" else "0")
        st.markdown('<div class="premium-btn">', unsafe_allow_html=True)
        if st.button(f"変換実行"):
            try:
                val = parse_formula(input_v)
                ss.formula = format((val / rates[from_c]) * rates[to_c], '.10g')
                ss.last_was_equal = True; st.rerun()
            except: ss.formula = "Error"; st.rerun()

elif ss.mode != "通常":
    extra = []
    if ss.mode == "巨数": extra = list(SI_PREFIXES.keys())
    elif ss.mode == "科学計算": extra = ["sin(", "cos(", "tan(", "°", "abs(", "log("]
    elif ss.mode == "値数": extra = ["平均([", "中央値([", "最頻値([", "最大([", "最小([", "])", "偏差値(", "期待値(", ","]
    e_cols = st.columns(6)
    for i, b in enumerate(extra):
        if e_cols[i % 6].button(b, key=f"e{i}"): on_click(b); st.rerun()
