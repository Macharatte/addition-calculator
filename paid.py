import streamlit as st
import math
import statistics
import requests
import re

# --- ページ設定 (ここを完全に修正しました) ---
st.set_page_config(page_title="Python Calculator Pro 2", layout="centered")

# --- デザインCSS ---
st.markdown("""
<style>
    :root { --bg-page: #FFFFFF; --text-display: #000000; --btn-bg: #000000; --btn-text: #FFFFFF; --btn-border: #000000; }
    @media (prefers-color-scheme: dark) { :root { --bg-page: #000000; --text-display: #FFFFFF; --btn-bg: #FFFFFF; --btn-text: #000000; --btn-border: #FFFFFF; } }
    .main .block-container { max-width: 95% !important; padding: 5px 2px !important; }
    header {visibility: hidden;}
    .display-container {
        display: flex; align-items: center; justify-content: flex-end;
        font-size: 50px; font-weight: 900; margin-bottom: 10px; padding: 10px; 
        border-bottom: 5px solid var(--text-display); min-height: 100px; color: var(--text-display); word-break: break-all;
    }
    div.stButton > button {
        width: 100% !important; height: 65px !important; border-radius: 8px !important;
        background-color: var(--btn-bg) !important; color: var(--btn-text) !important;
        border: 2px solid var(--btn-border) !important; transition: none !important;
    }
    div.stButton > button p { font-weight: 900; font-size: 14px; }
    .premium-btn div.stButton > button { background-color: #FFD700 !important; color: #000000 !important; border-color: #B8860B !important; }
    .premium-btn div.stButton > button p { color: #000000 !important; }
    .del-btn div.stButton > button { background-color: #FF4B4B !important; }
    .eq-btn div.stButton > button { background-color: #2e7d32 !important; }
    .result-box { background-color: rgba(255, 215, 0, 0.1); padding: 15px; border-radius: 8px; border: 2px solid #FFD700; margin-top: 10px; text-align: center; }
</style>
""", unsafe_allow_html=True)

# --- 通貨・単位データ ---
CURRENCY_MAP = {
    "JPY": "日本円", "USD": "アメリカドル", "EUR": "ユーロ", "GBP": "イギリス・ポンド",
    "AUD": "オーストラリアドル", "CAD": "カナダドル", "CHF": "スイスフラン", "CNY": "中国人民元",
    "KRW": "韓国ウォン", "HKD": "香港ドル", "SGD": "シンガポールドル", "TWD": "台湾ドル",
    "THB": "タイバーツ", "VND": "ベトナムドン", "PHP": "フィリピンペソ", "IDR": "インドネシアルピア",
    "MYR": "マレーシアリンギット", "INR": "インドルピー", "NZD": "ニュージーランドドル", "BRL": "ブラジルレアル",
    "MXN": "メキシコペソ", "TRY": "トルコリラ", "ZAR": "南アフリカランド", "AED": "UAEディルハム"
}

SI_PREFIXES = [
    ('Q', 1e30), ('R', 1e27), ('Y', 1e24), ('Z', 1e21), ('E', 1e18), ('P', 1e15), ('T', 1e12), 
    ('G', 1e9), ('M', 1e6), ('k', 1e3), ('h', 1e2), ('da', 1e1), ('d', 1e-1), ('c', 1e-2), 
    ('m', 1e-3), ('μ', 1e-6), ('n', 1e-9), ('p', 1e-12), ('f', 1e-15), ('a', 1e-18), ('z', 1e-21), 
    ('y', 1e-24), ('r', 1e-27), ('q', 1e-30)
]

# --- ロジック ---
@st.cache_data(ttl=3600)
def get_rates():
    try:
        url = "https://open.er-api.com/v6/latest/USD"
        return requests.get(url).json()["rates"]
    except: return {"JPY": 150.0, "USD": 1.0}

def parse_formula(formula):
    if not formula or formula == "Error": return 0.0
    # 記号の置換
    f = formula.replace('×', '*').replace('÷', '/').replace('−', '-').replace('^^', '**')
    # 巨数単位の置換
    for unit, val in SI_PREFIXES:
        if unit in f:
            f = re.sub(f'(\\d+){unit}', f'(\\1*{val})', f)
            f = f.replace(unit, str(val))
    try:
        safe_dict = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
        safe_dict.update({k: getattr(statistics, k) for k in dir(statistics) if not k.startswith("_")})
        safe_dict.update({"abs": abs, "mean": statistics.mean, "median": statistics.median, "mode": statistics.mode})
        return float(eval(f, {"__builtins__": None}, safe_dict))
    except: return 0.0

def calc_tax(val, t_type):
    # 所得税 (2025年時点の速算表)
    if t_type == "tax_income":
        if val <= 1950000: return val * 0.05
        elif val <= 3300000: return val * 0.10 - 97500
        elif val <= 6950000: return val * 0.20 - 427500
        elif val <= 9000000: return val * 0.23 - 636000
        elif val <= 18000000: return val * 0.33 - 1536000
        elif val <= 40000000: return val * 0.40 - 2796000
        else: return val * 0.45 - 4796000
    # 贈与税 (一般贈与財産: 兄弟・夫婦・親子(子が20歳未満)など)
    elif t_type == "tax_gift":
        v = val - 1100000 # 基礎控除
        if v <= 0: return 0
        if v <= 2000000: return v * 0.10
        elif v <= 3000000: return v * 0.15 - 100000
        elif v <= 4000000: return v * 0.20 - 250000
        elif v <= 6000000: return v * 0.30 - 650000
        elif v <= 10000000: return v * 0.40 - 1250000
        elif v <= 15000000: return v * 0.45 - 1750000
        elif v <= 30000000: return v * 0.50 - 2500000
        else: return v * 0.55 - 4000000
    elif t_type == "tax_corp": return val * 0.232
    elif t_type == "tax_res": return val * 0.10
    return val

# --- 状態管理 ---
ss = st.session_state
for k, v in [('formula', ""), ('mode', "通常"), ('last_was_equal', False), ('premium_sub', "なし"), ('conv_result', "")]:
    if k not in ss: ss[k] = v

st.markdown(f'<div class="display-container"><span>{ss.formula if ss.formula else "0"}</span></div>', unsafe_allow_html=True)

# --- メインキーパッド ---
main_keys = ["7","8","9","π","√","+","4","5","6","e","^^","−","1","2","3","i","(-)","×","0","00",".","(",")","÷"]
cols = st.columns(6)
for i, b in enumerate(main_keys):
    with cols[i % 6]:
        if st.button(b, key=f"main_key_{i}"):
            if ss.last_was_equal: ss.formula = ""; ss.last_was_equal = False
            ss.formula += b; st.rerun()

c1, c2 = st.columns(2)
with c1:
    st.markdown('<div class="del-btn">', unsafe_allow_html=True)
    if st.button("delete", use_container_width=True, key="del_btn"): 
        ss.formula = ""; ss.conv_result = ""; st.rerun()
with c2:
    st.markdown('<div class="eq-btn">', unsafe_allow_html=True)
    if st.button("＝", use_container_width=True, key="eq_btn"):
        ss.formula = format(parse_formula(ss.formula), '.10g'); ss.last_was_equal = True; st.rerun()

st.markdown("---")

# --- モード切替 ---
m_list = ["通常", "科学計算", "巨数", "値数", "有料機能"]
m_cols = st.columns(5)
for i, m in enumerate(m_list):
    if m_cols[i].button(m, key=f"mode_sel_{i}"): 
        ss.mode = m; ss.premium_sub = "なし"; st.rerun()

# --- 各モードの拡張ボタン ---
if ss.mode == "有料機能":
    pc1, pc2 = st.columns(2)
    with pc1:
        st.markdown('<div class="premium-btn">', unsafe_allow_html=True)
        if st.button("税金計算モード", key="premium_tax_btn"): ss.premium_sub = "税金"; st.rerun()
    with pc2:
        st.markdown('<div class="premium-btn">', unsafe_allow_html=True)
        if st.button("通貨変換モード", key="premium_conv_btn"): ss.premium_sub = "通貨"; st.rerun()

    if ss.premium_sub == "税金":
        taxes = [("税込10%", "t10"), ("税込8%", "t8"), ("所得税", "tax_income"), ("贈与税", "tax_gift"), ("法人税", "tax_corp"), ("住民税", "tax_res")]
        t_cols = st.columns(3)
        for i, (l, c) in enumerate(taxes):
            if t_cols[i % 3].button(l, key=f"tax_calc_{i}"):
                v = parse_formula(ss.formula)
                if c == "t10": res = v * 1.1
                elif c == "t8": res = v * 1.08
                else: res = calc_tax(v, c)
                ss.formula = format(res, '.10g'); ss.last_was_equal = True; st.rerun()

    if ss.premium_sub == "通貨":
        rates = get_rates()
        valid_codes = [c for c in CURRENCY_MAP.keys() if c in rates]
        options = [f"{c} ({CURRENCY_MAP[c]})" for c in valid_codes]
        
        sc1, sc2 = st.columns(2)
        from_sel = sc1.selectbox("元", options, index=options.index("USD (アメリカドル)"), key="cur_from")
        to_sel = sc2.selectbox("先", options, index=options.index("JPY (日本円)"), key="cur_to")
        
        in_val = st.text_input("数値入力", value=ss.formula if ss.formula != "Error" else "0", key="cur_input")
        st.markdown('<div class="premium-btn">', unsafe_allow_html=True)
        if st.button("変換実行", key="cur_exec"):
            v = parse_formula(in_val)
            f_code = from_sel.split(" ")[0]
            t_code = to_sel.split(" ")[0]
            res = (v / rates[f_code]) * rates[t_code]
            ss.conv_result = f"{format(res, ',.2f')} {t_code} ({CURRENCY_MAP[t_code]})"
            st.rerun()
        if ss.conv_result:
            st.markdown(f'<div class="result-box">{ss.conv_result}</div>', unsafe_allow_html=True)

else:
    # 科学計算・巨数・値数の全機能ボタン
    ext_items = []
    if ss.mode == "巨数": ext_items = [p[0] for p in SI_PREFIXES]
    elif ss.mode == "科学計算": ext_items = ["sin(", "cos(", "tan(", "log(", "log10(", "exp(", "abs(", "sqrt(", "radians(", "degrees("]
    elif ss.mode == "値数": ext_items = ["mean([", "median([", "mode([", "stdev([", "variance([", "max([", "min([", "])", ","]
    
    e_cols = st.columns(5)
    for i, b in enumerate(ext_items):
        if e_cols[i % 5].button(b, key=f"extra_key_{ss.mode}_{i}"):
            if ss.last_was_equal: ss.formula = ""; ss.last_was_equal = False
            ss.formula += b; st.rerun()
