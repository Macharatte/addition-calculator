import streamlit as st
import math
import statistics
import requests
import re

# --- ページ設定 ---
st.set_page_config(page_title="Python Calculator Premium", layout="centered")

# --- デザインCSS (黒を基調としたスタイル) ---
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
</style>
""", unsafe_allow_html=True)

# --- 税金計算ロジック ---
def calculate_income_tax(income, dependents):
    # 所得 － 基礎控除(48万) － 扶養控除(38万×人数)
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
    # 巨数単位の置換
    si = {'Q':1e30, 'R':1e27, 'Y':1e24, 'Z':1e21, 'E':1e18, 'P':1e15, 'T':1e12, 'G':1e9, 'M':1e6, 'k':1e3}
    for k, v in si.items():
        if k in f: f = re.sub(f'(\\d+){k}', f'(\\1*{v})', f)
    try:
        safe_env = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
        safe_env.update({"abs": abs, "mean": statistics.mean, "median": statistics.median, "mode": statistics.mode})
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
    if st.button("delete", key="widget_del", use_container_width=True):
        st.session_state.formula_state = ""; st.rerun()
with c2:
    if st.button("＝", key="widget_eq", use_container_width=True):
        st.session_state.formula_state = format(parse_val(st.session_state.formula_state), '.10g')
        st.session_state.last_was_eq = True; st.rerun()

st.divider()

# --- モード選択 ---
modes = ["通常", "科学計算", "巨数", "値数", "有料機能"]
mc = st.columns(5)
for i, m in enumerate(modes):
    if mc[i].button(m, key=f"mode_btn_{i}"): 
        st.session_state.mode_state = m; st.session_state.submode_state = "なし"; st.rerun()

# --- 各モード機能 ---
curr_m = st.session_state.mode_state
if curr_m == "有料機能":
    pc1, pc2 = st.columns(2)
    if pc1.button("税金計算モード", key="sub_tax"): st.session_state.submode_state = "税金"; st.rerun()
    if pc2.button("通貨変換モード", key="sub_conv"): st.session_state.submode_state = "通貨"; st.rerun()

    if st.session_state.submode_state == "税金":
        # 扶養人数選択
        dep_count = st.selectbox("扶養人数選択 (38万円/人 控除)", options=list(range(11)), index=0, key="dep_select")
        
        # 数値入力欄を追加
        input_val = st.text_input("所得・数値を入力 (電卓の結果を使う場合は空欄)", value="", key="tax_input_field")
        
        st.divider()
        taxes = [
            ("所得税計算", "inc"), ("法人税", "corp"), ("住民税", "resident"),
            ("贈与税", "gift"), ("税込10%", 1.1), ("税込8%", 1.08)
        ]
        tc = st.columns(3)
        for i, (label, val) in enumerate(taxes):
            if tc[i % 3].button(label, key=f"tx_btn_{i}"):
                # 入力欄に値があればそれを優先、なければ電卓の表示を使う
                source = input_val if input_val else st.session_state.formula_state
                base = parse_val(source)
                
                if val == "inc": r = calculate_income_tax(base, dep_count)
                elif val == "corp": r = calculate_corp_tax(base)
                elif val == "gift": r = calculate_gift_tax(base)
                elif val == "resident": r = base * 0.10
                else: r = base * val
                
                st.session_state.formula_state = format(r, '.10g')
                st.session_state.last_was_eq = True; st.rerun()

else:
    # 巨数などのボタンを復元
    items = []
    if curr_m == "巨数": items = ["Q","R","Y","Z","E","P","T","G","M","k"]
    elif curr_m == "科学計算": items = ["sin(", "cos(", "tan(", "log(", "log10(", "abs(", "sqrt("]
    elif curr_m == "値数": items = ["mean([", "median([", "mode([", "stdev([", "max([", "min([", "])", ","]
    
    ec = st.columns(5)
    for i, item in enumerate(items):
        if ec[i % 5].button(item, key=f"ex_btn_{curr_m}_{i}"):
            if st.session_state.last_was_eq: st.session_state.formula_state = ""; st.session_state.last_was_eq = False
            st.session_state.formula_state += item; st.rerun()
