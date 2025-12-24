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
    .eq-btn div.stButton > button { background-color: #000000 !important; color: white !important; border-color: #000000 !important; }
    @media (prefers-color-scheme: dark) { .eq-btn div.stButton > button { background-color: #FFFFFF !important; color: #000000 !important; } }
    .result-box { background-color: rgba(0, 0, 0, 0.05); padding: 15px; border-radius: 8px; border: 2px solid #000000; margin-top: 10px; text-align: center; font-weight: 900; }
    @media (prefers-color-scheme: dark) { .result-box { background-color: rgba(255, 255, 255, 0.1); border: 2px solid #FFFFFF; } }
</style>
""", unsafe_allow_html=True)

# --- 税金計算ロジック ---
def calculate_income_tax(val):
    if val <= 0: return 0
    if val <= 1950000: return val * 0.05
    elif val <= 3300000: return val * 0.10 - 97500
    elif val <= 6950000: return val * 0.20 - 427500
    elif val <= 9000000: return val * 0.23 - 636000
    elif val <= 18000000: return val * 0.33 - 1536000
    elif val <= 40000000: return val * 0.40 - 2796000
    else: return val * 0.45 - 4796000

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

# --- データ定義 ---
CURRENCY_MAP = {
    "JPY": "日本円", "USD": "アメリカドル", "EUR": "ユーロ", "GBP": "イギリス・ポンド",
    "AUD": "豪ドル", "CAD": "カナダドル", "CHF": "スイスフラン", "CNY": "人民元",
    "KRW": "韓国ウォン", "HKD": "香港ドル", "SGD": "シンガポールドル", "TWD": "台湾ドル",
    "THB": "タイバーツ", "VND": "ベトナムドン", "PHP": "フィリピンペソ", "IDR": "ルピア",
    "MYR": "リンギット", "INR": "インドルピー", "TRY": "トルコリラ", "AED": "UAEディルハム"
}

SI_PREFIXES = [
    ('Q', 1e30), ('R', 1e27), ('Y', 1e24), ('Z', 1e21), ('E', 1e18), ('P', 1e15), ('T', 1e12), 
    ('G', 1e9), ('M', 1e6), ('k', 1e3), ('h', 1e2), ('da', 1e1), ('d', 1e-1), ('c', 1e-2), 
    ('m', 1e-3), ('μ', 1e-6), ('n', 1e-9), ('p', 1e-12), ('f', 1e-15), ('a', 1e-18), ('z', 1e-21), 
    ('y', 1e-24), ('r', 1e-27), ('q', 1e-30)
]

# --- 内部関数 ---
@st.cache_data(ttl=3600)
def fetch_rates():
    try: return requests.get("https://open.er-api.com/v6/latest/USD").json()["rates"]
    except: return {"JPY": 150.0, "USD": 1.0}

def parse_val(formula):
    if not formula or formula == "Error": return 0.0
    f = str(formula).replace('×', '*').replace('÷', '/').replace('−', '-').replace('^^', '**')
    for unit, val in SI_PREFIXES:
        if unit in f:
            f = re.sub(f'(\\d+){unit}', f'(\\1*{val})', f)
            f = f.replace(unit, str(val))
    try:
        safe_env = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
        safe_env.update({"abs": abs, "mean": statistics.mean, "median": statistics.median, "mode": statistics.mode})
        return float(eval(f, {"__builtins__": None}, safe_env))
    except: return 0.0

# --- アプリ状態 (ウィジェットキーと重複しない名前) ---
if 'formula_state' not in st.session_state: st.session_state.formula_state = ""
if 'mode_state' not in st.session_state: st.session_state.mode_state = "通常"
if 'submode_state' not in st.session_state: st.session_state.submode_state = "なし"
if 'conv_res_state' not in st.session_state: st.session_state.conv_res_state = ""
if 'last_was_eq' not in st.session_state: st.session_state.last_was_eq = False

# --- タイトルとディスプレイ ---
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
        st.session_state.formula_state = ""; st.session_state.conv_res_state = ""; st.rerun()
with c2:
    st.markdown('<div class="eq-btn">', unsafe_allow_html=True)
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

# --- 各モード詳細 ---
curr_m = st.session_state.mode_state
if curr_m == "有料機能":
    pc1, pc2 = st.columns(2)
    if pc1.button("税金計算モード", key="sub_tax"): st.session_state.submode_state = "税金"; st.rerun()
    if pc2.button("通貨変換モード", key="sub_conv"): st.session_state.submode_state = "通貨"; st.rerun()

    if st.session_state.submode_state == "税金":
        taxes = [("税込10%", 1.1), ("税込8%", 1.08), ("所得税", "inc"), ("贈与税", "gift"), ("法人税", 0.232), ("住民税", 0.1)]
        tc = st.columns(3)
        for i, (l, v) in enumerate(taxes):
            if tc[i % 3].button(l, key=f"tax_btn_{i}"):
                base = parse_val(st.session_state.formula_state)
                if l == "所得税": r = calculate_income_tax(base)
                elif l == "贈与税": r = calculate_gift_tax(base)
                else: r = base * v
                st.session_state.formula_state = format(r, '.10g'); st.session_state.last_was_eq = True; st.rerun()

    if st.session_state.submode_state == "通貨":
        rates = fetch_rates()
        opts = [f"{c} ({CURRENCY_MAP[c]})" for c in CURRENCY_MAP.keys() if c in rates]
        cc1, cc2 = st.columns(2)
        f_cur = cc1.selectbox("元", opts, index=opts.index("USD (アメリカドル)"), key="sel_from")
        t_cur = cc2.selectbox("先", opts, index=opts.index("JPY (日本円)"), key="sel_to")
        val_in = st.text_input("数値入力", value=st.session_state.formula_state if st.session_state.formula_state else "0", key="input_conv")
        if st.button("変換実行", key="exec_conv"):
            v = parse_val(val_in)
            fc, tc = f_cur.split(" ")[0], t_cur.split(" ")[0]
            res_v = (v / rates[fc]) * rates[tc]
            st.session_state.conv_res_state = f"{format(res_v, ',.2f')} {tc} ({CURRENCY_MAP[tc]})"
            st.rerun()
        if st.session_state.conv_res_state: st.markdown(f'<div class="result-box">変換結果: {st.session_state.conv_res_state}</div>', unsafe_allow_html=True)

else:
    items = []
    if curr_m == "巨数": items = [x[0] for x in SI_PREFIXES]
    elif curr_m == "科学計算": items = ["sin(", "cos(", "tan(", "log(", "log10(", "exp(", "abs(", "sqrt(", "radians(", "degrees("]
    elif curr_m == "値数": items = ["mean([", "median([", "mode([", "stdev([", "variance([", "max([", "min([", "])", ","]
    ec = st.columns(5)
    for i, item in enumerate(items):
        if ec[i % 5].button(item, key=f"extra_{curr_m}_{i}"):
            if st.session_state.last_was_eq: st.session_state.formula_state = ""; st.session_state.last_was_eq = False
            st.session_state.formula_state += item; st.rerun()
