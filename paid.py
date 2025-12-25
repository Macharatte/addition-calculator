import streamlit as st
import math
import statistics
import requests
import re

# --- ページ設定 ---
st.set_page_config(page_title="Python Calculator Premium", layout="centered")

# --- デザインCSS (レイアウト固定) ---
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
    /* ボタンのサイズを完全に固定 */
    div.stButton > button {
        width: 100% !important; height: 55px !important; border-radius: 8px !important;
        background-color: var(--btn-bg) !important; color: var(--btn-text) !important;
        border: 2px solid var(--btn-border) !important; font-weight: 900; font-size: 16px;
        display: block;
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

# --- 内部解析 ---
def parse_val(formula):
    if not formula or formula == "Error": return 0.0
    f = str(formula).replace('×', '*').replace('÷', '/').replace('−', '-').replace('^^', '**')
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
            "平均": statistics.mean, "中央値": statistics.median, "最頻値": statistics.mode,
            "標準偏差": statistics.stdev, "最大値": max, "最小値": min
        })
        return float(eval(f, {"__builtins__": None}, safe_env))
    except: return 0.0

# --- 状態管理 ---
if 'formula_state' not in st.session_state: st.session_state.formula_state = ""
if 'mode_state' not in st.session_state: st.session_state.mode_state = "通常"
if 'unit_submode' not in st.session_state: st.session_state.unit_submode = "拡"
if 'last_was_eq' not in st.session_state: st.session_state.last_was_eq = False

# --- メインディスプレイ ---
st.markdown('<div class="app-title">Python Calculator Premium</div>', unsafe_allow_html=True)
st.markdown(f'<div class="display-container">{st.session_state.formula_state if st.session_state.formula_state else "0"}</div>', unsafe_allow_html=True)

# --- 基本キーパッド ---
keys = ["7","8","9","π","√","+","4","5","6","e","^^","−","1","2","3","i","(-)","×","0","00",".","(",")","÷"]
cols = st.columns(6)
for i, k in enumerate(keys):
    if cols[i % 6].button(k, key=f"k_{i}"):
        if st.session_state.last_was_eq: st.session_state.formula_state = ""; st.session_state.last_was_eq = False
        st.session_state.formula_state += k; st.rerun()

# ＝ と delete の横並び
c1, c2 = st.columns(2)
with c1:
    st.markdown('<div class="del-btn">', unsafe_allow_html=True)
    if st.button("delete", key="m_del", use_container_width=True):
        st.session_state.formula_state = ""; st.rerun()
with c2:
    if st.button("＝", key="m_eq", use_container_width=True):
        st.session_state.formula_state = format(parse_val(st.session_state.formula_state), '.10g')
        st.session_state.last_was_eq = True; st.rerun()

st.divider()

# --- モード選択 ---
modes = ["通常", "科学計算", "単位", "値数", "有料機能"]
mc = st.columns(5)
for i, m in enumerate(modes):
    if mc[i].button(m, key=f"md_{i}"): 
        st.session_state.mode_state = m; st.rerun()

# --- 各モード詳細 ---
curr_m = st.session_state.mode_state

if curr_m == "単位":
    sc1, sc2 = st.columns(2)
    if sc1.button("拡 (巨数: Q ~ k)", key="u_big"): st.session_state.unit_submode = "拡"; st.rerun()
    if sc2.button("縮 (微数: d ~ q)", key="u_small"): st.session_state.unit_submode = "縮"; st.rerun()
    
    units = ["Q","R","Y","Z","E","P","T","G","M","k"] if st.session_state.unit_submode == "拡" else ["h","da","d","c","m","μ","n","p","f","a","z","y","r","q"]
    uc = st.columns(5)
    for i, u in enumerate(units):
        if uc[i % 5].button(u, key=f"ut_{i}"):
            st.session_state.formula_state += u; st.rerun()

elif curr_m == "値数":
    stats = [("平均", "平均(["), ("中央値", "中央値(["), ("最頻値", "最頻値(["), ("標偏差", "標準偏差(["), ("最大", "最大値(["), ("最小", "最小値(["), ("])", "])"), (",", ",")]
    sc = st.columns(4)
    for i, (label, cmd) in enumerate(stats):
        if sc[i % 4].button(label, key=f"st_{i}"):
            st.session_state.formula_state += cmd; st.rerun()

elif curr_m == "有料機能":
    st.markdown("#### 扶養人数選択")
    dep_count = st.selectbox("人数に応じて所得税の控除が変わります", options=list(range(11)), index=0)
    input_val = st.text_input("数値を入力 (空欄なら電卓の値を使用)", key="tax_in")
    
    st.divider()
    taxes = [("所得税", "inc"), ("法人税", "corp"), ("住民税", 0.1), ("贈与税", "gift"), ("税込10%", 1.1), ("税込8%", 1.08)]
    tc = st.columns(3)
    for i, (label, val) in enumerate(taxes):
        if tc[i % 3].button(label, key=f"tx_{i}"):
            source = input_val if input_val else st.session_state.formula_state
            base = parse_val(source)
            if val == "inc": r = calculate_income_tax(base, dep_count)
            elif val == "corp": 
                r = (base * 0.15) if base <= 8000000 else (1200000 + (base - 8000000) * 0.232)
            elif val == "gift":
                v = base - 1100000
                r = (v * 0.1) if v <= 2000000 else (v * 0.15 - 100000) # (略式)
            else: r = base * val
            st.session_state.formula_state = format(r, '.10g'); st.session_state.last_was_eq = True; st.rerun()

elif curr_m == "科学計算":
    sci = ["sin(", "cos(", "tan(", "log(", "log10(", "abs(", "sqrt("]
    sc = st.columns(4)
    for i, s in enumerate(sci):
        if sc[i % 4].button(s, key=f"sc_{i}"):
            st.session_state.formula_state += s; st.rerun()
