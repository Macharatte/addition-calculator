import streamlit as st
import math
import statistics
import re

# --- ページ設定 ---
st.set_page_config(page_title="Python Calculator Premium", layout="centered")

# --- デザインCSS (レイアウトの崩れを徹底防止) ---
st.markdown("""
<style>
    :root { --bg-page: #FFFFFF; --text-display: #000000; --btn-bg: #000000; --btn-text: #FFFFFF; }
    @media (prefers-color-scheme: dark) { :root { --bg-page: #000000; --text-display: #FFFFFF; --btn-bg: #FFFFFF; --btn-text: #000000; } }
    
    .main .block-container { max-width: 95% !important; padding: 10px !important; }
    header {visibility: hidden;}
    
    .app-title { text-align: center; font-size: 26px; font-weight: 900; color: var(--text-display); border-bottom: 2px solid var(--text-display); margin-bottom: 10px; }
    
    .display-container {
        display: flex; align-items: center; justify-content: flex-end;
        font-size: 38px; font-weight: 900; margin-bottom: 15px; padding: 15px; 
        border-bottom: 5px solid var(--text-display); min-height: 90px; color: var(--text-display); word-break: break-all;
    }

    div.stButton > button {
        width: 100% !important; height: 50px !important; border-radius: 6px !important;
        background-color: var(--btn-bg) !important; color: var(--btn-text) !important;
        font-weight: 900; font-size: 14px; border: 1px solid var(--text-display) !important;
        margin-bottom: 5px !important;
    }
    
    .del-btn div.stButton > button { background-color: #FF4B4B !important; color: white !important; border: none !important; }
    .exe-btn div.stButton > button { background-color: #28a745 !important; color: white !important; border: none !important; }
</style>
""", unsafe_allow_html=True)

# --- 税金ロジック ---
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

def parse_val(formula):
    if not formula or formula == "Error": return 0.0
    clean_f = str(formula).split(':')[-1].strip().replace(',', '')
    f = clean_f.replace('×', '*').replace('÷', '/').replace('−', '-').replace('^^', '**')
    si = {'Q':1e30,'R':1e27,'Y':1e24,'Z':1e21,'E':1e18,'P':1e15,'T':1e12,'G':1e9,'M':1e6,'k':1e3,'h':1e2,'da':10,'d':0.1,'c':0.01,'m':0.001,'μ':1e-6,'n':1e-9,'p':1e-12,'f':1e-15,'a':1e-18,'z':1e-21,'y':1e-24,'r':1e-27,'q':1e-30}
    for k, v in si.items():
        if k in f: f = re.sub(f'(\\d+){k}', f'(\\1*{v})', f)
    try:
        safe_env = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
        safe_env.update({"平均": statistics.mean, "中央値": statistics.median, "最頻値": statistics.mode, "標準偏差": statistics.stdev, "最大値": max, "最小値": min})
        return float(eval(f, {"__builtins__": None}, safe_env))
    except: return 0.0

# --- 状態管理 ---
if 'formula_state' not in st.session_state: st.session_state.formula_state = ""
if 'tax_input_val' not in st.session_state: st.session_state.tax_input_val = ""
if 'mode_state' not in st.session_state: st.session_state.mode_state = "通常"
if 'tax_type' not in st.session_state: st.session_state.tax_type = "所得税"

# --- UI ---
st.markdown('<div class="app-title">Python Calculator Premium</div>', unsafe_allow_html=True)
st.markdown(f'<div class="display-container">{st.session_state.formula_state if st.session_state.formula_state else "0"}</div>', unsafe_allow_html=True)

# 電卓キーパッド
keys = ["7","8","9","π","√","+","4","5","6","e","^^","−","1","2","3","i","(-)","×","0","00",".","(",")","÷"]
cols = st.columns(6)
for i, k in enumerate(keys):
    if cols[i % 6].button(k, key=f"k_{k}_{i}"):
        st.session_state.formula_state += k; st.rerun()

# 電卓用＝とdelete
c_main = st.columns(2)
with c_main[0]:
    st.markdown('<div class="del-btn">', unsafe_allow_html=True)
    if st.button("delete", key="calc_del", use_container_width=True):
        st.session_state.formula_state = ""; st.rerun()
with c_main[1]:
    if st.button("＝", key="calc_eq", use_container_width=True):
        res = parse_val(st.session_state.formula_state)
        st.session_state.formula_state = format(res, '.10g'); st.rerun()

st.divider()

# モード選択
modes = ["通常", "科学計算", "拡縮", "値数", "有料機能"]
mc = st.columns(5)
for i, m in enumerate(modes):
    if mc[i].button(m, key=f"md_{m}"): st.session_state.mode_state = m; st.rerun()

# --- 有料機能（税金モード） ---
if st.session_state.mode_state == "有料機能":
    st.markdown("### 税金計算エリア")
    
    # 扶養人数と税金の種類を選択
    dep = st.selectbox("扶養人数 (38万円/人 控除)", options=list(range(11)), index=0)
    st.session_state.tax_type = st.selectbox("計算する税金を選択", ["所得税", "法人税", "住民税", "贈与税", "税込10%", "税込8%"])
    
    # 税金用入力欄
    tax_display_val = st.text_input("数値を入力 (空欄なら電卓の値を使用)", value=st.session_state.tax_input_val, key="tax_field")
    
    # 計算実行ボタンと削除ボタンを横並び
    tx_col1, tx_col2 = st.columns(2)
    with tx_col1:
        st.markdown('<div class="exe-btn">', unsafe_allow_html=True)
        if st.button("計算実行", key="tax_exec", use_container_width=True):
            source = tax_display_val if tax_display_val else st.session_state.formula_state
            base = parse_val(source)
            
            # 税計算
            tt = st.session_state.tax_type
            if tt == "所得税": r = calculate_income_tax(base, dep)
            elif tt == "法人税": r = (base * 0.15) if base <= 8000000 else (1200000 + (base - 8000000) * 0.232)
            elif tt == "住民税": r = base * 0.10
            elif tt == "贈与税": r = (base - 1100000) * 0.1
            elif tt == "税込10%": r = base * 1.1
            elif tt == "税込8%": r = base * 1.08
            
            st.session_state.tax_input_val = f"{tt}: {format(r, ',.0f')}"
            st.rerun()
            
    with tx_col2:
        st.markdown('<div class="del-btn">', unsafe_allow_html=True)
        if st.button("削除", key="tax_clear", use_container_width=True):
            st.session_state.tax_input_val = ""
            st.rerun()

# --- 他のモード ---
elif st.session_state.mode_state == "拡縮":
    units = ["Q","R","Y","Z","E","P","T","G","M","k","h","da","d","c","m","μ","n","p","f","a","z","y","r","q"]
    uc = st.columns(6)
    for i, u in enumerate(units):
        if uc[i % 6].button(u, key=f"u_{u}"): st.session_state.formula_state += u; st.rerun()

elif st.session_state.mode_state == "値数":
    stats = [("平均", "平均(["), ("中央値", "中央値(["), ("最頻値", "最頻値(["), ("標偏差", "標準偏差(["), ("最大", "最大値(["), ("最小", "最小値(["), ("])", "])"), (",", ",")]
    sc = st.columns(4)
    for i, (l, c) in enumerate(stats):
        if sc[i % 4].button(l, key=f"st_{l}"): st.session_state.formula_state += c; st.rerun()

elif st.session_state.mode_state == "科学計算":
    sci = ["sin(", "cos(", "tan(", "log(", "log10(", "abs(", "sqrt("]
    sc = st.columns(4)
    for i, s in enumerate(sci):
        if sc[i % 4].button(s, key=f"sc_{s}"): st.session_state.formula_state += s; st.rerun()
