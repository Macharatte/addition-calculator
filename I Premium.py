import streamlit as st
import math
import statistics
import urllib.request
import json

# --- 1. 状態管理 ---
if 'display' not in st.session_state: st.session_state.display = ""
if 'lang' not in st.session_state: st.session_state.lang = "日本語"
if 'theme' not in st.session_state: st.session_state.theme = "Dark"
if 'rates' not in st.session_state:
    st.session_state.rates = {"USD": 156.4, "EUR": 168.2, "BTC": 14000000}

# --- 2. 日本の累進課税ロジック ---
def calc_complex_tax(amount, tax_type):
    if amount <= 0: return 0, 0
    if tax_type == "所得税 (自動累進)":
        # 令和6年時点 所得税速算表
        brackets = [
            (45_000_000, 0.45, 4_796_000), (18_000_000, 0.40, 2_796_000),
            (9_000_000, 0.33, 1_536_000), (6_950_000, 0.23, 636_000),
            (3_300_000, 0.20, 427_500), (1_950_000, 0.10, 97_500), (0, 0.05, 0)
        ]
        for limit, rate, deduction in brackets:
            if amount > limit: return amount * rate - deduction, rate
    elif tax_type == "法人税 (自動累進)":
        # 中小法人の例: 800万円以下15%、超 23.2%
        if amount <= 8_000_000: return amount * 0.15, 0.15
        else: return (8_000_000 * 0.15) + (amount - 8_000_000) * 0.232, 0.232
    elif tax_type == "相続税 (自動累進)":
        # 法定相続分に応じた取得金額に対する税率
        brackets = [
            (600_000_000, 0.55, 72_000_000), (300_000_000, 0.50, 42_000_000),
            (200_000_000, 0.45, 27_000_000), (100_000_000, 0.40, 17_000_000),
            (50_000_000, 0.30, 7_000_000), (30_000_000, 0.20, 2_000_000),
            (10_000_000, 0.15, 500_000), (0, 0.10, 0)
        ]
        for limit, rate, deduction in brackets:
            if amount > limit: return amount * rate - deduction, rate
    return 0, 0

# --- 3. UI/CSS ---
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
    /* セレクトボックスのテキスト入力（カーソル）を無効化 */
    div[data-baseweb="select"] input {{ cursor: pointer !important; caret-color: transparent !important; }}
    .result-card {{
        background-color: {text_color}11 !important; 
        padding: 20px; border-radius: 10px; border-left: 5px solid #1E88E5; margin-top: 15px;
    }}
</style>
""", unsafe_allow_html=True)

# --- 4. メインディスプレイ & キーパッド ---
c1, c2, c3 = st.columns([1, 1, 1])
if c3.button("表示切替"):
    st.session_state.theme = "Light" if is_dark else "Dark"; st.rerun()

st.markdown(f'<div class="disp">{st.session_state.display if st.session_state.display else "0"}</div>', unsafe_allow_html=True)

rows = [["7","8","9","÷"],["4","5","6","×"],["1","2","3","−"],["0",".","00","+"]]
for row in rows:
    cols = st.columns(4)
    for i, k in enumerate(row):
        if cols[i].button(k, key=f"btn_{k}"): st.session_state.display += k; st.rerun()

cl, ex = st.columns(2)
if cl.button("消去"): st.session_state.display = ""; st.rerun()
if ex.button("計算実行"):
    try:
        expr = st.session_state.display.replace("×", "*").replace("÷", "/").replace("−", "-").replace("π", str(math.pi))
        for k, v in {'Q':'*1e30','R':'*1e27','Y':'*1e24','Z':'*1e21','E':'*1e18','P':'*1e15','T':'*1e12','G':'*1e9','M':'*1e6','k':'*1e3','m':'*1e-3','μ':'*1e-6','n':'*1e-9','p':'*1e-12'}.items():
            expr = expr.replace(k, v)
        res = eval(expr, {"math": math})
        st.session_state.display = format(res, '.10g'); st.rerun()
    except: st.session_state.display = "Error"; st.rerun()

st.divider()

# --- 5. タブ機能 (プロ機能) ---
t_si, t_sci, t_paid = st.tabs(["接頭語", "科学計算", "プロ設定"])

with t_si:
    for k in ['k','M','G','T','m','μ','n','p']:
        if st.button(k, key=f"si_{k}"): st.session_state.display += k; st.rerun()

with t_paid:
    mode = st.radio("機能選択", ["燃料", "通貨", "税金"], horizontal=True)
    
    # 共通処理: メインディスプレイの数値を取得するロジック
    current_val = 0.0
    try:
        # ディスプレイの中身を評価して数値化
        eval_expr = st.session_state.display.replace("×", "*").replace("÷", "/").replace("−", "-")
        for k, v in {'k':'*1e3','M':'*1e6','G':'*1e9','T':'*1e12'}.items(): eval_expr = eval_expr.replace(k, v)
        current_val = float(eval(eval_expr)) if st.session_state.display else 0.0
    except: pass

    if mode == "燃料":
        f_col1, f_col2 = st.columns(2)
        oil = f_col1.selectbox("油種", ["レギュラー", "ハイオク", "軽油", "灯油"], key="oil_s")
        reg = f_col2.selectbox("地方", ["全国平均", "東京", "大阪", "福岡"], key="reg_s")
        
        c_val1, c_val2 = st.columns([3, 1])
        lit = c_val1.number_input("数量 (L)", value=50.0, step=1.0)
        if c_val2.button("表示値反映", key="f_sync"): 
             st.toast(f"{current_val}L を反映しました"); lit = current_val # 簡易反映
        
        price = {"レギュラー":170, "ハイオク":181, "軽油":149, "灯油":115}[oil]
        st.markdown(f'<div class="result-card"><h3>合計: {int(lit * price):,} JPY</h3></div>', unsafe_allow_html=True)

    elif mode == "税金":
        tax_target = st.selectbox("税目 (累進課税は自動計算)", 
                                 ["所得税 (自動累進)", "法人税 (自動累進)", "相続税 (自動累進)", "消費税 (10%)", "消費税 (8%)"], key="tax_s")
        
        c_val1, c_val2 = st.columns([3, 1])
        base_amt = c_val1.number_input("課税対象額 (JPY)", value=0.0, step=1000.0, format="%.f")
        if c_val2.button("表示値反映", key="t_sync"):
            st.session_state.tax_input = current_val # Stateに保存
            st.rerun()
            
        # 反映された値がある場合はそれを使用
        final_base = st.session_state.get('tax_input', base_amt)
        
        if "自動累進" in tax_target:
            tax_val, rate = calc_complex_tax(final_base, tax_target)
            st.markdown(f"""
            <div class="result-card">
                <h3>推定税額: {int(tax_val):,} JPY</h3>
                <p>適用税率(最大分): {rate*100:.1f}% / 課税対象: {final_base:,.0f}円</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            rate = 0.10 if "10%" in tax_target else 0.08
            st.markdown(f'<div class="result-card"><h3>税込合計: {int(final_base*(1+rate)):,} JPY</h3><p>税額: {int(final_base*rate):,} JPY</p></div>', unsafe_allow_html=True)
