import streamlit as st
import math
import statistics
import re
import requests

# --- ページ設定 ---
st.set_page_config(page_title="Python Calculator Premium", layout="centered")

# --- デザインCSS ---
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
    .tax-result-box {
        background-color: #f0f2f6; border-radius: 8px; padding: 15px; margin-bottom: 10px;
        text-align: center; font-size: 24px; font-weight: 900; color: #000000; border: 2px solid #000000;
    }
    @media (prefers-color-scheme: dark) { .tax-result-box { background-color: #1e1e1e; color: #ffffff; border: 2px solid #ffffff; } }
    div.stButton > button {
        width: 100% !important; height: 50px !important; border-radius: 6px !important;
        background-color: var(--btn-bg) !important; color: var(--btn-text) !important;
        font-weight: 900; font-size: 14px; border: 1px solid var(--text-display) !important;
    }
    .del-btn div.stButton > button { background-color: #FF4B4B !important; color: white !important; border: none !important; }
    .exe-btn div.stButton > button { background-color: #28a745 !important; color: white !important; border: none !important; }
</style>
""", unsafe_allow_html=True)

# --- 単位解析ロジック ---
def parse_japanese_and_si(text):
    if not text: return 0.0
    # カンマ削除
    s = str(text).replace(',', '')
    
    # 日本語単位の変換
    units = {"兆": 1e12, "億": 1e8, "万": 1e4, "千": 1e3}
    for unit, val in units.items():
        if unit in s:
            parts = s.split(unit)
            try:
                # 「1億2000万」のような形式に対応
                num_part = float(parts[0]) if parts[0] else 0.0
                remaining = parse_japanese_and_si(parts[1]) if parts[1] else 0.0
                return num_part * val + remaining
            except: pass

    # SI接頭語の変換
    si = {'Q':1e30,'R':1e27,'Y':1e24,'Z':1e21,'E':1e18,'P':1e15,'T':1e12,'G':1e9,'M':1e6,'k':1e3,'h':1e2,'da':10,'d':0.1,'c':0.01,'m':0.001,'μ':1e-6,'n':1e-9,'p':1e-12,'f':1e-15,'a':1e-18,'z':1e-21,'y':1e-24,'r':1e-27,'q':1e-30}
    for k, v in si.items():
        if s.endswith(k):
            try: return float(s[:-len(k)]) * v
            except: pass
            
    # 数値のみの場合
    try: return float(s)
    except:
        # 電卓の計算式として評価
        try:
            f = s.replace('×', '*').replace('÷', '/').replace('−', '-').replace('^^', '**')
            safe_env = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
            return float(eval(f, {"__builtins__": None}, safe_env))
        except: return 0.0

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

# --- 為替API ---
def get_exchange_rate(base, target):
    try:
        url = f"https://open.er-api.com/v6/latest/{base}"
        data = requests.get(url).json()
        return data['rates'][target]
    except: return None

# --- 状態管理 ---
if 'formula_state' not in st.session_state: st.session_state.formula_state = ""
if 'tax_res' not in st.session_state: st.session_state.tax_res = "結果がここに表示されます"
if 'mode_state' not in st.session_state: st.session_state.mode_state = "通常"
if 'sub_mode' not in st.session_state: st.session_state.sub_mode = "税金"

# --- UI ---
st.markdown('<div class="app-title">Python Calculator Premium</div>', unsafe_allow_html=True)
st.markdown(f'<div class="display-container">{st.session_state.formula_state if st.session_state.formula_state else "0"}</div>', unsafe_allow_html=True)

# 電卓
keys = ["7","8","9","π","√","+","4","5","6","e","^^","−","1","2","3","i","(-)","×","0","00",".","(",")","÷"]
cols = st.columns(6)
for i, k in enumerate(keys):
    if cols[i % 6].button(k, key=f"k_{i}"): st.session_state.formula_state += k; st.rerun()

c_main = st.columns(2)
with c_main[0]:
    st.markdown('<div class="del-btn">', unsafe_allow_html=True)
    if st.button("delete", key="c_del"): st.session_state.formula_state = ""; st.rerun()
with c_main[1]:
    if st.button("＝", key="c_eq"):
        val = parse_japanese_and_si(st.session_state.formula_state)
        st.session_state.formula_state = format(val, '.10g'); st.rerun()

st.divider()

# モード選択
modes = ["通常", "科学計算", "拡縮", "値数", "有料機能"]
mc = st.columns(5)
for i, m in enumerate(modes):
    if mc[i].button(m, key=f"m_{i}"): st.session_state.mode_state = m; st.rerun()

# --- 有料機能エリア ---
if st.session_state.mode_state == "有料機能":
    sc1, sc2 = st.columns(2)
    if sc1.button("税金計算", key="go_tax"): st.session_state.sub_mode = "税金"; st.rerun()
    if sc2.button("通貨変換", key="go_conv"): st.session_state.sub_mode = "通貨"; st.rerun()

    if st.session_state.sub_mode == "税金":
        dep = st.selectbox("扶養人数", options=list(range(11)))
        t_type = st.selectbox("種類", ["所得税", "法人税", "住民税", "贈与税", "税込10%", "税込8%"])
        tax_in = st.text_input("金額入力", placeholder="例: 500万, 1.2億, 10k (課税対象額)", key="t_input")
        
        # 結果表示エリア（ボタンの上）
        st.markdown(f'<div class="tax-result-box">{st.session_state.tax_res}</div>', unsafe_allow_html=True)
        
        tx_col1, tx_col2 = st.columns(2)
        with tx_col1:
            st.markdown('<div class="exe-btn">', unsafe_allow_html=True)
            if st.button("計算実行", key="t_exe"):
                # 入力がない場合は電卓のディスプレイを使用
                source = tax_in if tax_in else st.session_state.formula_state
                base = parse_japanese_and_si(source)
                
                if t_type == "所得税": r = calculate_income_tax(base, dep)
                elif t_type == "法人税": r = (base * 0.15) if base <= 8000000 else (1200000 + (base - 8000000) * 0.232)
                elif t_type == "住民税": r = base * 0.10
                elif t_type == "贈与税": r = max(0, (base - 1100000) * 0.1)
                elif t_type == "税込10%": r = base * 1.1
                elif t_type == "税込8%": r = base * 1.08
                
                st.session_state.tax_res = f"{t_type}: {format(r, ',.0f')} 円"; st.rerun()
        with tx_col2:
            st.markdown('<div class="del-btn">', unsafe_allow_html=True)
            if st.button("削除", key="t_del"): st.session_state.tax_res = "結果がここに表示されます"; st.rerun()

    elif st.session_state.sub_mode == "通貨":
        c_from = st.selectbox("元通貨", ["JPY", "USD", "EUR", "GBP", "CNY"])
        c_to = st.selectbox("先通貨", ["USD", "JPY", "EUR", "GBP", "CNY"])
        c_val = st.text_input("変換する金額を入力", placeholder="例: 1000, 10k")
        if st.button("変換実行"):
            rate = get_exchange_rate(c_from, c_to)
            if rate:
                res = parse_japanese_and_si(c_val) * rate
                st.success(f"{format(res, ',.2f')} {c_to} (レート: {rate})")
            else: st.error("レート取得失敗")

# --- 他モード ---
elif st.session_state.mode_state == "拡縮":
    units = ["Q","R","Y","Z","E","P","T","G","M","k","h","da","d","c","m","μ","n","p","f","a","z","y","r","q"]
    uc = st.columns(6)
    for i, u in enumerate(units):
        if uc[i % 6].button(u, key=f"u_{i}"): st.session_state.formula_state += u; st.rerun()

elif st.session_state.mode_state == "値数":
    stats = [("平均", "平均(["), ("中央値", "中央値(["), ("最頻値", "最頻値(["), ("標偏差", "標準偏差(["), ("最大", "最大値(["), ("最小", "最小値(["), ("])", "])"), (",", ",")]
    sc = st.columns(4)
    for i, (l, c) in enumerate(stats):
        if sc[i % 4].button(l, key=f"st_{i}"): st.session_state.formula_state += c; st.rerun()

elif st.session_state.mode_state == "科学計算":
    sci = ["sin(", "cos(", "tan(", "log(", "log10(", "abs(", "sqrt("]
    sc = st.columns(4)
    for i, s in enumerate(sci):
        if sc[i % 4].button(s, key=f"sc_{i}"): st.session_state.formula_state += s; st.rerun()
