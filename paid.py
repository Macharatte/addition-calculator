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

# --- 解析ロジック ---
def parse_japanese_and_si(text):
    if not text: return 0.0
    s = str(text).replace(',', '').split(':')[0].strip()
    units = {"兆": 1e12, "億": 1e8, "万": 1e4, "千": 1e3}
    total = 0.0
    current_val = ""
    found_unit = False
    
    # 複合日本語（1億2000万など）の解析
    temp_s = s
    for unit, val in units.items():
        if unit in temp_s:
            parts = temp_s.split(unit)
            if parts[0]:
                try: total += float(parts[0]) * val
                except: pass
            temp_s = parts[1]
            found_unit = True
    if temp_s:
        try: total += float(temp_s)
        except: pass
    
    if not found_unit:
        si = {'Q':1e30,'R':1e27,'Y':1e24,'Z':1e21,'E':1e18,'P':1e15,'T':1e12,'G':1e9,'M':1e6,'k':1e3,'h':1e2,'da':10,'d':0.1,'c':0.01,'m':0.001,'μ':1e-6,'n':1e-9,'p':1e-12,'f':1e-15,'a':1e-18,'z':1e-21,'y':1e-24,'r':1e-27,'q':1e-30}
        for k, v in si.items():
            if s.endswith(k):
                try: return float(s[:-len(k)]) * v
                except: pass
        try: return float(s) if not total else total
        except: return total
    return total

# --- 税金計算ロジック ---
def calc_tax(base, t_type, dep, heirs=1):
    if t_type == "所得税":
        ti = base - 480000 - (dep * 380000)
        if ti <= 0: return 0
        if ti <= 1950000: return ti * 0.05
        elif ti <= 3300000: return ti * 0.10 - 97500
        elif ti <= 6950000: return ti * 0.20 - 427500
        elif ti <= 9000000: return ti * 0.23 - 636000
        elif ti <= 18000000: return ti * 0.33 - 1536000
        elif ti <= 40000000: return ti * 0.40 - 2796000
        else: return ti * 0.45 - 4796000
    elif t_type == "法人税":
        return (base * 0.15) if base <= 8000000 else (1200000 + (base - 8000000) * 0.232)
    elif t_type == "住民税":
        return base * 0.10
    elif t_type == "贈与税":
        ti = base - 1100000
        if ti <= 0: return 0
        # 簡易税率（一般）
        if ti <= 2000000: return ti * 0.10
        elif ti <= 3000000: return ti * 0.15 - 100000
        else: return ti * 0.20 - 250000
    elif t_type == "固定資産税":
        return base * 0.014
    elif t_type == "相続税":
        exemption = 30000000 + (6000000 * heirs)
        taxable = base - exemption
        if taxable <= 0: return 0
        # 簡易計算（法定相続人が1人の場合を想定した概算）
        if taxable <= 10000000: return taxable * 0.10
        elif taxable <= 30000000: return taxable * 0.15 - 500000
        elif taxable <= 50000000: return taxable * 0.20 - 2000000
        else: return taxable * 0.30 - 7000000
    elif t_type == "税込10%": return base * 1.1
    elif t_type == "税込8%": return base * 1.08
    return 0

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

if st.session_state.mode_state == "有料機能":
    sc1, sc2 = st.columns(2)
    if sc1.button("税金計算", key="go_tax"): st.session_state.sub_mode = "税金"; st.rerun()
    if sc2.button("通貨・貴金属", key="go_conv"): st.session_state.sub_mode = "通貨"; st.rerun()

    if st.session_state.sub_mode == "税金":
        tax_list = ["所得税", "法人税", "住民税", "固定資産税", "相続税", "贈与税", "税込10%", "税込8%"]
        t_type = st.selectbox("種類を選択", tax_list)
        
        # 動的入力
        dep, heirs = 0, 1
        if t_type == "所得税":
            dep = st.number_input("扶養人数", min_value=0, max_value=20, value=0)
        elif t_type == "相続税":
            heirs = st.number_input("法定相続人の数", min_value=1, max_value=20, value=1)
            
        tax_in = st.text_input("金額入力", placeholder="例: 1億2000万, 500k", key="t_input")
        
        st.markdown(f'<div class="tax-result-box">{st.session_state.tax_res}</div>', unsafe_allow_html=True)
        
        tx_col1, tx_col2 = st.columns(2)
        with tx_col1:
            st.markdown('<div class="exe-btn">', unsafe_allow_html=True)
            if st.button("計算実行"):
                source = tax_in if tax_in else st.session_state.formula_state
                base = parse_japanese_and_si(source)
                r = calc_tax(base, t_type, dep, heirs)
                st.session_state.tax_res = f"{t_type}: {format(r, ',.0f')} 円"; st.rerun()
        with tx_col2:
            st.markdown('<div class="del-btn">', unsafe_allow_html=True)
            if st.button("削除"): st.session_state.tax_res = "結果がここに表示されます"; st.rerun()

    elif st.session_state.sub_mode == "通貨":
        currency_list = ["JPY", "USD", "EUR", "GBP", "CNY", "AUD", "CAD", "CHF", "SGD", "HKD", "KRW", "THB", "TWD", "NZD", "INR", "XAU (金)", "XAG (銀)", "COPPER (銅)"]
        c_from = st.selectbox("変換元", currency_list)
        c_to = st.selectbox("変換先", currency_list)
        c_val = st.text_input("数量・金額入力", placeholder="例: 1000, 10万")
        if st.button("変換実行"):
            # 通貨レート処理（前回同様）...
            base_code = c_from.split(' ')[0]
            target_code = c_to.split(' ')[0]
            try:
                url = f"https://open.er-api.com/v6/latest/{base_code}"
                rate = requests.get(url).json()['rates'][target_code]
                if base_code in ["XAU", "XAG"]: rate /= 31.1035
                res = parse_japanese_and_si(c_val) * rate
                st.success(f"結果: {format(res, ',.2f')} {target_code}")
            except: st.error("取得失敗")

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
