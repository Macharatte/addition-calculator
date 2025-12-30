import streamlit as st
import math
import statistics
import urllib.request
import json

# --- 1. システム状態管理 ---
if 'display' not in st.session_state: st.session_state.display = ""
if 'theme' not in st.session_state: st.session_state.theme = "Dark"
if 'rates' not in st.session_state:
    # 初期レート (USD/JPY中心)
    st.session_state.rates = {
        "USD": 156.0, "EUR": 168.0, "GBP": 198.0, "AUD": 103.0, "CAD": 114.0,
        "CHF": 175.0, "CNH": 21.5, "HKD": 20.0, "SGD": 115.0, "NZD": 95.0,
        "BTC": 14000000, "ETH": 500000
    }

# --- 2. 日本の累進課税ロジック ---
def calc_complex_tax(amount, tax_type):
    if amount <= 0: return 0, 0
    if tax_type == "所得税 (自動累進)":
        brackets = [
            (45_000_000, 0.45, 4_796_000), (18_000_000, 0.40, 2_796_000),
            (9_000_000, 0.33, 1_536_000), (6_950_000, 0.23, 636_000),
            (3_300_000, 0.20, 427_500), (1_950_000, 0.10, 97_500), (0, 0.05, 0)
        ]
        for limit, rate, deduction in brackets:
            if amount > limit: return amount * rate - deduction, rate
    elif tax_type == "法人税 (自動累進)":
        if amount <= 8_000_000: return amount * 0.15, 0.15
        else: return (8_000_000 * 0.15) + (amount - 8_000_000) * 0.232, 0.232
    elif tax_type == "相続税 (自動累進)":
        brackets = [(600e6, 0.55, 72e6), (300e6, 0.50, 42e6), (200e6, 0.45, 27e6), (100e6, 0.40, 17e6), (50e6, 0.30, 7e6), (30e6, 0.20, 2e6), (10e6, 0.15, 0.5e6), (0, 0.10, 0)]
        for limit, rate, deduction in brackets:
            if amount > limit: return amount * rate - deduction, rate
    return 0, 0

# --- 3. UI/デザイン ---
is_dark = st.session_state.theme == "Dark"
bg_color = "#000000" if is_dark else "#FFFFFF"
text_color = "#FFFFFF" if is_dark else "#000000"

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg_color} !important; color: {text_color} !important; }}
    .disp {{
        background-color: {bg_color} !important; color: {text_color} !important;
        padding: 25px; border: 4px solid {text_color} !important;
        border-radius: 12px; font-size: 42px; text-align: right; margin-bottom: 20px;
    }}
    div[data-baseweb="select"] input {{ cursor: pointer !important; caret-color: transparent !important; }}
    .result-card {{
        background-color: {text_color}11 !important; 
        padding: 20px; border-radius: 10px; border-left: 5px solid #1E88E5; margin-top: 15px;
    }}
</style>
""", unsafe_allow_html=True)

# --- 4. メイン操作 (言語/テーマ/更新) ---
c1, c2, c3 = st.columns([1, 1, 1])
with c2:
    if st.button("為替レート更新"):
        try:
            with urllib.request.urlopen("https://open.er-api.com/v6/latest/USD") as r:
                data = json.loads(r.read())
                for c in ["EUR", "GBP", "AUD", "CAD", "CHF", "HKD", "SGD", "NZD"]:
                    st.session_state.rates[c] = data["rates"]["JPY"] / data["rates"][c]
                st.session_state.rates["USD"] = data["rates"]["JPY"]
            st.toast("最新レートを取得しました")
        except: st.error("通信エラー")
with c3:
    if st.button("テーマ切替"):
        st.session_state.theme = "Light" if is_dark else "Dark"; st.rerun()

st.markdown(f'<div class="disp">{st.session_state.display if st.session_state.display else "0"}</div>', unsafe_allow_html=True)

# キーパッド
rows = [["7","8","9","÷"],["4","5","6","×"],["1","2","3","−"],["0",".","00","+"]]
for row in rows:
    cols = st.columns(4)
    for i, k in enumerate(row):
        if cols[i].button(k, key=f"btn_{k}"): st.session_state.display += k; st.rerun()

cl, ex = st.columns(2)
if cl.button("消去"): st.session_state.display = ""; st.rerun()
if ex.button("計算実行"):
    try:
        expr = st.session_state.display.replace("×", "*").replace("÷", "/").replace("−", "-")
        # 接頭語変換
        si_map = {'Q':'*1e30','R':'*1e27','Y':'*1e24','Z':'*1e21','E':'*1e18','P':'*1e15','T':'*1e12','G':'*1e9','M':'*1e6','k':'*1e3','m':'*1e-3','μ':'*1e-6','n':'*1e-9','p':'*1e-12'}
        for k, v in si_map.items(): expr = expr.replace(k, v)
        # 定数変換
        expr = expr.replace("π", str(math.pi)).replace("e", str(math.e)).replace("i", "1j")
        res = eval(expr, {"math": math, "statistics": statistics})
        st.session_state.display = format(res, '.10g'); st.rerun()
    except: st.session_state.display = "Error"; st.rerun()

st.divider()

# --- 5. 復元されたタブ機能 ---
t_si, t_sci, t_paid = st.tabs(["接頭語 (SI)", "科学計算 (SCI)", "プロ設定 (PRO)"])

with t_si:
    # 接頭語ボタンの復元
    si_list = ['k','M','G','T','P','m','μ','n','p','f']
    cols = st.columns(5)
    for i, s in enumerate(si_list):
        if cols[i%5].button(s, key=f"si_{s}"): st.session_state.display += s; st.rerun()

with t_sci:
    # 科学計算ボタンの復元
    sci_funcs = [("sin","math.sin("), ("cos","math.cos("), ("tan","math.tan("), ("√","math.sqrt("), 
                 ("log","math.log10("), ("ln","math.log("), ("π","π"), ("i","i"), ("(","("), (")",")")]
    cols = st.columns(5)
    for i, (name, val) in enumerate(sci_funcs):
        if cols[i%5].button(name, key=f"sci_{name}"): st.session_state.display += val; st.rerun()

with t_paid:
    mode = st.radio("機能", ["燃料", "通貨", "税金"], horizontal=True)
    
    # メインディスプレイの数値を評価して取得
    current_val = 0.0
    try:
        eval_expr = st.session_state.display.replace("×", "*").replace("÷", "/").replace("−", "-")
        for k, v in {'k':'*1e3','M':'*1e6','G':'*1e9','T':'*1e12'}.items(): eval_expr = eval_expr.replace(k, v)
        current_val = float(eval(eval_expr, {"math": math}))
    except: pass

    if mode == "燃料":
        f_col1, f_col2 = st.columns(2)
        oil = f_col1.selectbox("油種", ["レギュラー", "ハイオク", "軽油", "灯油"])
        reg = f_col2.selectbox("地方", ["全国平均", "東京", "大阪", "福岡"])
        lit = st.number_input("数量 (L)", value=50.0)
        if st.button("メイン表示値を数量(L)に反映"): st.session_state.f_lit = current_val; st.rerun()
        final_lit = st.session_state.get('f_lit', lit)
        price = {"レギュラー":170, "ハイオク":181, "軽油":149, "灯油":115}[oil]
        st.markdown(f'<div class="result-card"><h3>合計: {int(final_lit * price):,} JPY</h3></div>', unsafe_allow_html=True)

    elif mode == "通貨":
        cur_list = ["USD", "EUR", "GBP", "AUD", "CAD", "CHF", "CNH", "HKD", "SGD", "NZD", "BTC", "ETH"]
        target = st.selectbox("通貨選択", cur_list)
        amt = st.number_input("金額", value=1.0)
        if st.button("メイン表示値を金額に反映"): st.session_state.c_amt = current_val; st.rerun()
        final_amt = st.session_state.get('c_amt', amt)
        rate = st.session_state.rates.get(target, 1.0)
        st.markdown(f'<div class="result-card"><h3>結果: {final_amt * rate:,.2f} JPY</h3><p>1 {target} = {rate:,.2f}円</p></div>', unsafe_allow_html=True)

    elif mode == "税金":
        tax_target = st.selectbox("日本の税制 (自動累進対応)", 
                                 ["所得税 (自動累進)", "法人税 (自動累進)", "相続税 (自動累進)", "消費税 (10%)", "消費税 (8%)"])
        base = st.number_input("課税対象額", value=0.0)
        if st.button("メイン表示値を対象額に反映"): st.session_state.t_base = current_val; st.rerun()
        final_base = st.session_state.get('t_base', base)
        
        if "自動累進" in tax_target:
            tax_val, rate = calc_complex_tax(final_base, tax_target)
            st.markdown(f'<div class="result-card"><h3>推定税額: {int(tax_val):,} JPY</h3><p>適用税率目安: {rate*100:.1f}%</p></div>', unsafe_allow_html=True)
        else:
            r = 0.10 if "10%" in tax_target else 0.08
            st.markdown(f'<div class="result-card"><h3>税込合計: {int(final_base*(1+r)):,} JPY</h3></div>', unsafe_allow_html=True)
