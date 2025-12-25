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
    .app-title { text-align: center; font-size: 28px; font-weight: 900; color: var(--text-display); margin-bottom: 10px; border-bottom: 2px solid var(--text-display); padding-bottom: 5px; }
    .display-container {
        display: flex; align-items: center; justify-content: flex-end;
        font-size: 50px; font-weight: 900; margin-bottom: 10px; padding: 15px; 
        border-bottom: 5px solid var(--text-display); min-height: 100px; color: var(--text-display); word-break: break-all;
    }
    div.stButton > button {
        width: 100% !important; height: 50px !important; border-radius: 8px !important;
        background-color: var(--btn-bg) !important; color: var(--btn-text) !important;
        border: 2px solid var(--btn-border) !important; font-weight: 900; font-size: 14px;
    }
    .del-btn div.stButton > button { background-color: #FF4B4B !important; color: white !important; border-color: #FF4B4B !important; }
</style>
""", unsafe_allow_html=True)

# --- 税金計算ロジック ---
def calculate_income_tax(income, dependents):
    taxable_income = income - 480000 - (dependents * 380000)
    if taxable_income <= 0: return 0
    if taxable_income <= 1950000: return taxable_income * 0.05
    elif taxable_income <= 3300000: return taxable_income * 0.10 - 97500
    elif taxable_income <= 6950000: return taxable_income * 0.20 - 427500
    elif taxable_income <= 9000000: return taxable_income * 0.23 - 636000
    elif taxable_income <= 18000000: return taxable_income * 0.33 - 1536000
    elif taxable_income <= 40000000: return taxable_income * 0.40 - 2796000
    else: return taxable_income * 0.45 - 4796000

def calculate_corp_tax(val):
    if val <= 0: return 0
    if val <= 8000000: return val * 0.15
    else: return (8000000 * 0.15) + ((val - 8000000) * 0.232)

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

# --- 内部解析 ---
def parse_val(formula):
    if not formula or formula == "Error": return 0.0
    f = str(formula).replace('×', '*').replace('÷', '/').replace('−', '-').replace('^^', '**')
    # SI単位（巨数〜微数）の定義
    si_units = {
        'Q': 1e30, 'R': 1e27, 'Y': 1e24, 'Z': 1e21, 'E': 1e18, 'P': 1e15, 'T': 1e12, 'G': 1e9, 'M': 1e6, 'k': 1e3,
        'h': 1e2, 'da': 10, 'd': 0.1, 'c': 0.01, 'm': 0.001, 'μ': 1e-6, 'n': 1e-9, 'p': 1e-12, 'f': 1e-15, 'a': 1e-18,
        'z': 1e-21, 'y': 1e-24, 'r': 1e-27, 'q': 1e-30
    }
    for k, v in si_units.items():
        if k in f: f = re.sub(f'(\\d+){k}', f'(\\1*{v})', f)
    try:
        safe_env = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
        safe_env.update({
            "abs": abs, "平均": statistics.mean, "中央値": statistics.median, 
            "最頻値": statistics.mode, "標準偏差": statistics.stdev, "最大値": max, "最小値": min
        })
        # 日本語表記を関数名に置換
        f = f.replace("平均", "平均").replace("中央値", "中央値").replace("最頻値", "最頻値")
        return float(eval(f, {"__builtins__": None}, safe_env))
    except: return 0.0

# --- 状態管理 ---
if 'formula_state' not in st.session_state: st.session_state.formula_state = ""
if 'mode_state' not in st.session_state: st.session_state.mode_state = "通常"
if 'submode_state' not in st.session_state: st.session_state.submode_state = "なし"
if 'last_was_eq' not in st.session_state: st.session_state.last_was_eq = False

# --- UI表示 ---
st.markdown('<div class="app-title">Python Calculator Premium</div>', unsafe_allow_html=True)
st.markdown(f'<div class="display-container">{st.session_state.formula_state if st.session_state.formula_state else "0"}</div>', unsafe_allow_html=True)

# --- キーパッド ---
keys_layout = ["7","8","9","π","√","+","4","5","6","e","^^","−","1","2","3","i","(-)","×","0","00",".","(",")","÷"]
cols = st.columns(6)
for i, k in enumerate(keys_layout):
    if cols[i % 6].button(k, key=f"btn_{k}_{i}"):
        if st.session_state.last_was_eq: st.session_state.formula_state = ""; st.session_state.last_was_eq = False
        st.session_state.formula_state += k; st.rerun()

c1, c2 = st.columns(2)
with c1:
    st.markdown('<div class="del-btn">', unsafe_allow_html=True)
    if st.button("delete", key="main_del", use_container_width=True):
        st.session_state.formula_state = ""; st.rerun()
with c2:
    if st.button("＝", key="main_eq", use_container_width=True):
        st.session_state.formula_state = format(parse_val(st.session_state.formula_state), '.10g')
        st.session_state.last_was_eq = True; st.rerun()

st.divider()

# --- モード選択 ---
modes = ["通常", "科学計算", "単位", "値数", "有料機能"]
mc = st.columns(5)
for i, m in enumerate(modes):
    if mc[i].button(m, key=f"mode_{i}"): 
        st.session_state.mode_state = m; st.session_state.submode_state = "なし"; st.rerun()

# --- 各モード機能 ---
curr_m = st.session_state.mode_state
if curr_m == "有料機能":
    pc1, pc2 = st.columns(2)
    if pc1.button("税金計算モード", key="sub_tax"): st.session_state.submode_state = "税金"; st.rerun()
    if pc2.button("通貨変換モード", key="sub_conv"): st.session_state.submode_state = "通貨"; st.rerun()

    if st.session_state.submode_state == "税金":
        st.markdown("#### 扶養人数選択")
        dep_count = st.selectbox("扶養人数選択 (38万円/人 控除)", options=list(range(11)), index=0)
        input_val = st.text_input("所得・数値を直接入力 (空欄なら電卓の値を使用)", key="tax_field")
        st.divider()
        taxes = [("所得税計算", "inc"), ("法人税", "corp"), ("住民税", "res"), ("贈与税", "gift"), ("税込10%", 1.1), ("税込8%", 1.08)]
        tc = st.columns(3)
        for i, (label, val) in enumerate(taxes):
            if tc[i % 3].button(label, key=f"tx_run_{i}"):
                source = input_val if input_val else st.session_state.formula_state
                base = parse_val(source)
                if val == "inc": r = calculate_income_tax(base, dep_count)
                elif val == "corp": r = calculate_corp_tax(base)
                elif val == "gift": r = calculate_gift_tax(base)
                elif val == "res": r = base * 0.10
                else: r = base * val
                st.session_state.formula_state = format(r, '.10g'); st.session_state.last_was_eq = True; st.rerun()

elif curr_m == "単位":
    # 巨数〜微数まで24種類を表示
    units = ["Q","R","Y","Z","E","P","T","G","M","k","h","da","d","c","m","μ","n","p","f","a","z","y","r","q"]
    ec = st.columns(6)
    for i, u in enumerate(units):
        if ec[i % 6].button(u, key=f"unit_{i}"):
            st.session_state.formula_state += u; st.rerun()

elif curr_m == "値数":
    # 日本語化した統計ボタン
    stats = [("平均([", "平均(["), ("中央値([", "中央値(["), ("最頻値([", "最頻値(["), ("標偏差([", "標準偏差(["), ("最大([", "最大値(["), ("最小([", "最小値(["), ("])", "])"), (",", ",")]
    ec = st.columns(4)
    for i, (label, cmd) in enumerate(stats):
        if ec[i % 4].button(label, key=f"stat_{i}"):
            st.session_state.formula_state += cmd; st.rerun()

elif curr_m == "科学計算":
    sci = ["sin(", "cos(", "tan(", "log(", "log10(", "abs(", "sqrt("]
    ec = st.columns(4)
    for i, s in enumerate(sci):
        if ec[i % 4].button(s, key=f"sci_{i}"):
            st.session_state.formula_state += s; st.rerun()
