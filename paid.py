import streamlit as st
import math
import statistics
import requests
import re

# --- ページ設定 ---
st.set_page_config(page_title="Python Calculator Premium", layout="centered")

# --- デザインCSS ---
st.markdown("""
<style>
    :root { --bg-page: #FFFFFF; --text-display: #000000; --btn-bg: #000000; --btn-text: #FFFFFF; --btn-border: #000000; }
    @media (prefers-color-scheme: dark) { :root { --bg-page: #000000; --text-display: #FFFFFF; --btn-bg: #FFFFFF; --btn-text: #000000; --btn-border: #FFFFFF; } }
    .main .block-container { max-width: 95% !important; padding: 5px 2px !important; }
    header {visibility: hidden;}
    .app-title { text-align: center; font-size: 28px; font-weight: 900; color: #000000; margin-bottom: 10px; border-bottom: 2px solid #000000; padding-bottom: 5px; }
    @media (prefers-color-scheme: dark) { .app-title { color: #FFFFFF; border-bottom: 2px solid #FFFFFF; } }
    .display-container {
        display: flex; align-items: center; justify-content: flex-end;
        font-size: 50px; font-weight: 900; margin-bottom: 10px; padding: 15px; 
        border-bottom: 5px solid #000000; min-height: 100px; color: var(--text-display); word-break: break-all;
    }
    @media (prefers-color-scheme: dark) { .display-container { border-bottom: 5px solid #FFFFFF; } }
    div.stButton > button {
        width: 100% !important; height: 60px !important; border-radius: 8px !important;
        background-color: var(--btn-bg) !important; color: var(--btn-text) !important;
        border: 2px solid var(--btn-border) !important; font-weight: 900;
    }
    .del-btn div.stButton > button { background-color: #FF4B4B !important; color: white !important; border-color: #FF4B4B !important; }
    .eq-btn div.stButton > button { background-color: #000000 !important; color: white !important; border-color: #000000 !important; }
    @media (prefers-color-scheme: dark) { .eq-btn div.stButton > button { background-color: #FFFFFF !important; color: #000000 !important; } }
    .result-box { background-color: rgba(0, 0, 0, 0.05); padding: 15px; border-radius: 8px; border: 2px solid #000000; margin-top: 10px; text-align: center; font-weight: 900; }
</style>
""", unsafe_allow_html=True)

# --- 税金計算ロジック ---
def calculate_income_tax(income, dependents):
    # 1. 控除額の計算
    basic_deduction = 480000  # 基礎控除 (所得2400万以下の標準額)
    dependent_deduction = dependents * 380000  # 扶養控除
    
    # 2. 課税所得の算出
    taxable_income = income - basic_deduction - dependent_deduction
    if taxable_income <= 0: return 0
    
    # 3. 税率と速算控除額の適用
    if taxable_income <= 1950000:
        return taxable_income * 0.05
    elif taxable_income <= 3300000:
        return taxable_income * 0.10 - 97500
    elif taxable_income <= 6950000:
        return taxable_income * 0.20 - 427500
    elif taxable_income <= 9000000:
        return taxable_income * 0.23 - 636000
    elif taxable_income <= 18000000:
        return taxable_income * 0.33 - 1536000
    elif taxable_income <= 40000000:
        return taxable_income * 0.40 - 2796000
    else:
        return taxable_income * 0.45 - 4796000

def calculate_corp_tax(val):
    if val <= 0: return 0
    if val <= 8000000:
        return val * 0.15
    else:
        return (8000000 * 0.15) + ((val - 8000000) * 0.232)

def calculate_gift_tax(val):
    v = val - 1100000
    if v <= 0: return 0
    if v <= 2000000: return v * 0.10
    elif v <= 3000000: return v * 0.15 - 100000
    elif v <= 4000000: return v * 0.20 - 250000
    elif v <= 6000000: return v * 0.30 - 650000
    elif v <= 10000000: return v * 0.40 - 1250000
    elif v <= 15000000: return v * 0.45 - 1750000
    elif v <= 30000000: return v * 0.50 - 2500000
    else: return v * 0.55 - 4000000

# --- 内部関数 ---
@st.cache_data(ttl=3600)
def fetch_rates():
    try: return requests.get("https://open.er-api.com/v6/latest/USD").json()["rates"]
    except: return {"JPY": 150.0, "USD": 1.0}

def parse_val(formula):
    if not formula or formula == "Error": return 0.0
    f = str(formula).replace('×', '*').replace('÷', '/').replace('−', '-').replace('^^', '**')
    try:
        safe_env = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
        safe_env.update({"abs": abs, "mean": statistics.mean, "median": statistics.median, "mode": statistics.mode})
        return float(eval(f, {"__builtins__": None}, safe_env))
    except: return 0.0

# --- アプリ状態 ---
if 'formula_state' not in st.session_state: st.session_state.formula_state = ""
if 'mode_state' not in st.session_state: st.session_state.mode_state = "通常"
if 'submode_state' not in st.session_state: st.session_state.submode_state = "なし"
if 'last_was_eq' not in st.session_state: st.session_state.last_was_eq = False

# --- UI ---
st.markdown('<div class="app-title">Python Calculator Premium</div>', unsafe_allow_html=True)
st.markdown(f'<div class="display-container">{st.session_state.formula_state if st.session_state.formula_state else "0"}</div>', unsafe_allow_html=True)

# キーパッド (省略なしで全て配置)
keys_layout = ["7","8","9","π","√","+","4","5","6","e","^^","−","1","2","3","i","(-)","×","0","00",".","(",")","÷"]
cols = st.columns(6)
for i, k in enumerate(keys_layout):
    if cols[i % 6].button(k, key=f"btn_{k}_{i}"):
        if st.session_state.last_was_eq: st.session_state.formula_state = ""; st.session_state.last_was_eq = False
        st.session_state.formula_state += k; st.rerun()

c1, c2 = st.columns(2)
with c1:
    st.markdown('<div class="del-btn">', unsafe_allow_html=True)
    if st.button("delete", key="widget_del", use_container_width=True):
        st.session_state.formula_state = ""; st.rerun()
with c2:
    st.markdown('<div class="eq-btn">', unsafe_allow_html=True)
    if st.button("＝", key="widget_eq", use_container_width=True):
        st.session_state.formula_state = format(parse_val(st.session_state.formula_state), '.10g')
        st.session_state.last_was_eq = True; st.rerun()

st.divider()

# モード切替
modes = ["通常", "科学計算", "巨数", "値数", "有料機能"]
mc = st.columns(5)
for i, m in enumerate(modes):
    if mc[i].button(m, key=f"mode_btn_{i}"): 
        st.session_state.mode_state = m; st.session_state.submode_state = "なし"; st.rerun()

# 有料機能 (税金・通貨)
if st.session_state.mode_state == "有料機能":
    pc1, pc2 = st.columns(2)
    if pc1.button("税金計算モード", key="sub_tax"): st.session_state.submode_state = "税金"; st.rerun()
    if pc2.button("通貨変換モード", key="sub_conv"): st.session_state.submode_state = "通貨"; st.rerun()

    if st.session_state.submode_state == "税金":
        st.write("### 所得税設定")
        dep_count = st.selectbox("扶養人数 (38万円/人 控除)", options=list(range(11)), index=0, key="dep_select")
        
        st.divider()
        taxes = [("所得税計算実行", "inc"), ("法人税", "corp"), ("贈与税", "gift"), ("税込10%", 1.1), ("税込8%", 1.08)]
        tc = st.columns(3)
        for i, (l, v) in enumerate(taxes):
            if tc[i % 3].button(l, key=f"tax_btn_{i}"):
                base = parse_val(st.session_state.formula_state)
                if v == "inc": r = calculate_income_tax(base, dep_count)
                elif v == "corp": r = calculate_corp_tax(base)
                elif v == "gift": r = calculate_gift_tax(base)
                else: r = base * v
                st.session_state.formula_state = format(r, '.10g'); st.session_state.last_was_eq = True; st.rerun()
# (以下、通常/巨数などのモード処理が続きます)
else:
    items = []
    if st.session_state.mode_state == "巨数": items = ["Q","R","Y","Z","E","P","T","G","M","k"]
    elif st.session_state.mode_state == "科学計算": items = ["sin(", "cos(", "tan(", "log(", "log10(", "abs(", "sqrt("]
    elif st.session_state.mode_state == "値数": items = ["mean([", "median([", "mode([", "stdev([", "max([", "min([", "])", ","]
    ec = st.columns(5)
    for i, item in enumerate(items):
        if ec[i % 5].button(item, key=f"extra_{st.session_state.mode_state}_{i}"):
            if st.session_state.last_was_eq: st.session_state.formula_state = ""; st.session_state.last_was_eq = False
            st.session_state.formula_state += item; st.rerun()
