import streamlit as st
import math
import statistics
import requests
import re

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
    .result-box { background-color: rgba(255, 215, 0, 0.1); padding: 15px; border-radius: 8px; border: 2px solid #FFD700; margin-top: 10px; text-align: center; }
</style>
""", unsafe_allow_html=True)

# --- 通貨名称辞書 ---
CURRENCY_NAMES = {
    "JPY": "日本円", "USD": "アメリカドル", "EUR": "ユーロ", "GBP": "イギリス・ポンド",
    "AUD": "オーストラリアドル", "CAD": "カナダドル", "CHF": "スイスフラン", "CNY": "中国人民元",
    "HKD": "香港ドル", "KRW": "韓国ウォン", "SGD": "シンガポールドル", "TWD": "台湾ドル"
}

# --- 定数・ロジック ---
SI_PREFIXES = [('Q', 1e30), ('R', 1e27), ('Y', 1e24), ('Z', 1e21), ('E', 1e18), ('P', 1e15), ('T', 1e12), ('G', 1e9), ('M', 1e6), ('k', 1e3)]

@st.cache_data(ttl=3600)
def get_all_rates():
    try:
        url = "https://open.er-api.com/v6/latest/USD"
        data = requests.get(url).json()["rates"]
        return data
    except:
        return {"JPY": 150.0, "USD": 1.0, "EUR": 0.9}

def parse_formula(formula):
    if not formula or formula == "Error": return 0.0
    f = formula.replace('×', '*').replace('÷', '/').replace('−', '-').replace('m', '-')
    for unit, val in SI_PREFIXES:
        if unit in f:
            f = re.sub(f'(\\d+){unit}', f'(\\1*{val})', f)
            f = f.replace(unit, str(val))
    try:
        return float(eval(f, {"__builtins__": None}, {"math": math, "statistics": statistics, "abs": abs}))
    except: return 0.0

def calculate_precise_tax(val, tax_type):
    """正確な税金計算ロジック"""
    if tax_type == "tax_income":  # 所得税
        if val <= 1950000: return val * 0.05
        elif val <= 3300000: return val * 0.10 - 97500
        elif val <= 6950000: return val * 0.20 - 427500
        elif val <= 9000000: return val * 0.23 - 636000
        elif val <= 18000000: return val * 0.33 - 1536000
        elif val <= 40000000: return val * 0.40 - 2796000
        else: return val * 0.45 - 4796000
    
    elif tax_type == "tax_gift":  # 贈与税（一般贈与財産）
        # 基礎控除 110万円
        taxable_val = val - 1100000
        if taxable_val <= 0: return 0
        
        # 課税価格に応じた税率と控除額
        if taxable_val <= 2000000: return taxable_val * 0.10
        elif taxable_val <= 3000000: return taxable_val * 0.15 - 100000
        elif taxable_val <= 4000000: return taxable_val * 0.20 - 250000
        elif taxable_val <= 6000000: return taxable_val * 0.30 - 650000
        elif taxable_val <= 10000000: return taxable_val * 0.40 - 1250000
        elif taxable_val <= 15000000: return taxable_val * 0.45 - 1750000
        elif taxable_val <= 30000000: return taxable_val * 0.50 - 2500000
        else: return taxable_val * 0.55 - 4000000
        
    elif tax_type == "tax_corp": return val * 0.232
    elif tax_type == "tax_res": return val * 0.10
    return val

# --- 状態管理 ---
ss = st.session_state
for k, v in [('formula', ""), ('mode', "通常"), ('last_was_equal', False), ('premium_sub', "なし"), ('conv_result', "")]:
    if k not in ss: ss[k] = v

st.markdown('<div style="text-align:center; font-weight:900; font-size:24px; color:var(--text-display);">PYTHON CALCULATOR 2 PREMIUM</div>', unsafe_allow_html=True)
st.markdown(f'<div class="display-container"><span>{ss.formula if ss.formula else "0"}</span></div>', unsafe_allow_html=True)

# --- 電卓ボタン ---
main_btns = ["7","8","9","π","√","+","4","5","6","e","^^","−","1","2","3","i","(-)","×","0","00",".","(",")","÷"]
cols = st.columns(6)
for i, b in enumerate(main_btns):
    with cols[i % 6]:
        if st.button(b, key=f"k{i}"):
            if ss.last_was_equal: ss.formula = ""; ss.last_was_equal = False
            ss.formula += b; st.rerun()

bot_c1, bot_c2 = st.columns(2)
with bot_c1:
    st.markdown('<div class="del-btn">', unsafe_allow_html=True)
    if st.button("delete", use_container_width=True): ss.formula = ""; ss.conv_result = ""; st.rerun()
with bot_c2:
    st.markdown('<div class="eq-btn">', unsafe_allow_html=True)
    if st.button("＝", use_container_width=True):
        try: ss.formula = format(parse_formula(ss.formula), '.10g'); ss.last_was_equal = True
        except: ss.formula = "Error"
        st.rerun()

st.markdown('<hr style="margin:10px 0; opacity:0.3;">', unsafe_allow_html=True)

# --- モード選択 ---
m_cols = st.columns(5)
for i, m in enumerate(["通常", "科学計算", "巨数", "値数", "有料機能"]):
    if m_cols[i].button(m, key=f"m{i}"): ss.mode = m; ss.premium_sub = "なし"; st.rerun()

# --- 有料機能 ---
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
        taxes = [("税込(10%)", "tax_10"), ("税込(8%)", "tax_8"), ("所得税", "tax_income"), ("贈与税", "tax_gift"), ("法人税", "tax_corp"), ("住民税", "tax_res")]
        t_cols = st.columns(3)
        for i, (label, code) in enumerate(taxes):
            with t_cols[i % 3]:
                if st.button(label, key=f"tbtn{i}"):
                    val = parse_formula(ss.formula)
                    if "10" in code: res = val * 1.10
                    elif "8" in code: res = val * 1.08
                    else: res = calculate_precise_tax(val, code)
                    ss.formula = format(res, '.10g'); ss.last_was_equal = True; st.rerun()

    if ss.premium_sub == "通貨":
        st.markdown("---")
        rates = get_all_rates()
        # 通貨コードに名前を付けてリスト化
        cur_options = [f"{c} ({CURRENCY_NAMES.get(c, 'その他')})" for c in sorted(rates.keys())]
        
        c1, _, c2 = st.columns([4, 1, 4])
        from_sel = c1.selectbox("変換元", cur_options, index=next(i for i, x in enumerate(cur_options) if "USD" in x))
        to_sel = c2.selectbox("変換先", cur_options, index=next(i for i, x in enumerate(cur_options) if "JPY" in x))
        
        from_code = from_sel.split(" ")[0]
        to_code = to_sel.split(" ")[0]
        
        input_v = st.text_input("数値入力", value=ss.formula if ss.formula != "Error" else "0")
        
        st.markdown('<div class="premium-btn">', unsafe_allow_html=True)
        if st.button("通貨変換を実行"):
            v = parse_formula(input_v)
            res = (v / rates[from_code]) * rates[to_code]
            ss.conv_result = f"{format(res, ',.2f')} {to_code} ({CURRENCY_NAMES.get(to_code, '')})"
            st.rerun()
        
        if ss.conv_result:
            st.markdown(f'<div class="result-box"><p style="color:gray;font-size:12px;">結果</p><h3>{ss.conv_result}</h3></div>', unsafe_allow_html=True)

elif ss.mode != "通常":
    # 各モードのボタン
    items = []
    if ss.mode == "巨数": items = [p[0] for p in SI_PREFIXES]
    elif ss.mode == "科学計算": items = ["sin(", "cos(", "tan(", "log("]
    elif ss.mode == "値数": items = ["平均([", "最大([", "最小([", ","]
    e_cols = st.columns(6)
    for i, b in enumerate(items):
        if e_cols[i % 6].button(b): ss.formula += b; st.rerun()
