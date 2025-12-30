import streamlit as st
import math
import statistics
import urllib.request
import json

# --- 1. 強制リセット & 状態管理 ---
if 'v12_pro_fuel_update' not in st.session_state:
    st.session_state.clear()
    st.session_state.v12_pro_fuel_update = True
    st.session_state.display = ""
    st.session_state.lang = "日本語"
    st.session_state.theme = "Dark"
    st.session_state.rates = {"USD": 156.4}

# --- 2. 言語定義 ---
L_MAP = {
    "日本語": {"upd": "レート更新", "thm": "表示切替", "clr": "消去", "exe": "計算実行", "si": "接頭語", "sci": "科学", "stat": "値数", "paid": "有料機能", "fuel": "燃料・油種", "cur": "通貨レート", "tax": "税金計算", "mean":"平均値", "sum":"合計値", "mode":"最頻値", "med":"中央値", "max":"最大値", "min":"最小値", "dev":"偏差値", "exp":"期待値"},
    "English": {"upd": "UPDATE", "thm": "THEME", "clr": "CLEAR", "exe": "EXEC", "si": "SI", "sci": "SCI", "stat": "VALUE", "paid": "PREMIUM", "fuel": "FUEL/OIL", "cur": "FOREX", "tax": "TAX", "mean":"MEAN", "sum":"SUM", "mode":"MODE", "med":"MEDIAN", "max":"MAX", "min":"MIN", "dev":"T-SCORE", "exp":"EXPECTED"}
}

SI_CONV = {
    'Q': '*1e30', 'R': '*1e27', 'Y': '*1e24', 'Z': '*1e21', 'E': '*1e18', 'P': '*1e15', 'T': '*1e12', 'G': '*1e9', 'M': '*1e6', 'k': '*1e3',
    'm': '*1e-3', 'μ': '*1e-6', 'n': '*1e-9', 'p': '*1e-12', 'f': '*1e-15', 'a': '*1e-18', 'z': '*1e-21', 'y': '*1e-24', 'r': '*1e-27', 'q': '*1e-30'
}

# --- 3. CSSデザイン ---
is_dark = st.session_state.theme == "Dark"
bg_color = "#000000" if is_dark else "#FFFFFF"
text_color = "#FFFFFF" if is_dark else "#000000"

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg_color} !important; color: {text_color} !important; }}
    .disp {{
        background-color: {bg_color} !important; color: {text_color} !important;
        padding: 25px; border: 4px solid {text_color} !important;
        border-radius: 12px; font-size: 48px; text-align: right;
        font-family: monospace; margin-bottom: 20px; min-height: 100px;
    }}
    div.stButton > button {{
        width: 100% !important; border: 2px solid {text_color} !important;
        background-color: {bg_color} !important; color: {text_color} !important;
        font-weight: bold !important; transition: 0.1s;
    }}
    div.stButton > button:hover {{
        background-color: {text_color} !important; color: {bg_color} !important;
    }}
    .paid-box {{ border: 4px solid {text_color} !important; padding: 25px; border-radius: 15px; background-color: {bg_color} !important; }}
    label, p, span, .stMarkdown, .stRadio, .stNumberInput, .stSelectbox {{ color: {text_color} !important; font-weight: bold !important; }}
    .stTabs [data-baseweb="tab"] p {{ color: {text_color} !important; }}
</style>
""", unsafe_allow_html=True)

# --- 4. トップナビ ---
L = L_MAP.get(st.session_state.lang, L_MAP["English"])
c1, c2, c3 = st.columns([1, 1, 1])
with c1:
    new_lang = st.selectbox("L", list(L_MAP.keys()), index=list(L_MAP.keys()).index(st.session_state.lang), label_visibility="collapsed")
    if new_lang != st.session_state.lang:
        st.session_state.lang = new_lang; st.rerun()
with c2:
    if st.button(L["upd"]):
        try:
            with urllib.request.urlopen("https://open.er-api.com/v6/latest/USD") as r:
                st.session_state.rates["USD"] = json.loads(r.read())["rates"]["JPY"]
            st.toast("Updated")
        except: st.error("Error")
with c3:
    if st.button(L["thm"]):
        st.session_state.theme = "Light" if is_dark else "Dark"; st.rerun()

# --- 5. ディスプレイ ---
st.markdown(f'<div class="disp">{st.session_state.display if st.session_state.display else "0"}</div>', unsafe_allow_html=True)

# --- 6. キーパッド ---
rows = [["7","8","9","÷"],["4","5","6","×"],["1","2","3","−"],["0",".","00","+"]]
for row in rows:
    cols = st.columns(4)
    for i, k in enumerate(row):
        if cols[i].button(k, key=f"k_{k}"): 
            st.session_state.display += k; st.rerun()

cl, ex = st.columns(2)
if cl.button(L["clr"]): st.session_state.display = ""; st.rerun()
if ex.button(L["exe"]):
    try:
        expr = st.session_state.display.replace("×", "*").replace("÷", "/").replace("−", "-")
        expr = expr.replace("e", str(math.e)).replace("i", "1j").replace("π", str(math.pi))
        for k, v in SI_CONV.items(): expr = expr.replace(k, v)
        res = eval(expr, {"math": math, "statistics": statistics})
        st.session_state.display = format(res, '.10g') if not isinstance(res, complex) else str(res)
    except: st.session_state.display = "Error"
    st.rerun()

st.divider()

# --- 7. タブ機能 ---
t_si, t_sci, t_stat, t_paid = st.tabs([L["si"], L["sci"], L["stat"], L["paid"]])

with t_si:
    si_keys = list(SI_CONV.keys())
    for i in range(0, len(si_keys), 5):
        cols = st.columns(5)
        for j in range(5):
            if i+j < len(si_keys):
                p = si_keys[i+j]
                if cols[j].button(p, key=f"si_{p}"): st.session_state.display += p; st.rerun()

with t_sci:
    sc_list = [("sin","math.sin("), ("cos","math.cos("), ("tan","math.tan("), ("√","math.sqrt("), 
               ("log","math.log10("), ("π","π"), ("i","i"), ("e","e"), ("(",")")]
    for i in range(0, len(sc_list), 3):
        cols = st.columns(3)
        for j in range(3):
            if i+j < len(sc_list):
                name, val = sc_list[i+j]
                if cols[j].button(name, key=f"sci_{name}"): st.session_state.display += val; st.rerun()

with t_stat:
    r1 = st.columns(3)
    for i, k in enumerate(["mean", "med", "mode"]):
        if r1[i].button(L[k]): st.session_state.display += f"statistics.{k}(["; st.rerun()
    r2 = st.columns(3)
    for i, k in enumerate(["sum", "max", "min"]):
        if r2[i].button(L[k]): st.session_state.display += f"{k}(["; st.rerun()
    r3 = st.columns(2)
    if r3[0].button(L["dev"]): st.session_state.display += "Dev_Score(["; st.rerun()
    if r3[1].button(L["exp"]): st.session_state.display += "Expect(["; st.rerun()
    r4 = st.columns(2)
    if r4[0].button(",", key="btn_comma"): st.session_state.display += ","; st.rerun()
    if r4[1].button("CLOSE ])"): st.session_state.display += "])"; st.rerun()

with t_paid:
    st.markdown(f'<div class="paid-box">', unsafe_allow_html=True)
    st.write(f"### {L['paid']}")
    mode = st.radio(f"{L['paid']} SELECT", [L["fuel"], L["cur"], L["tax"]], horizontal=True)
    st.divider()

    if mode == L["fuel"]:
        st.subheader(f"⛽ {L['fuel']}")
        
        # 油種選択
        oil_types = {
            "レギュラー": 170, "ハイオク": 181, "軽油": 149, 
            "灯油": 115, "重油": 95, "ナフサ": 75, "アスファルト": 85, "潤滑油": 130
        }
        fuel_type = st.selectbox("油種を選択", list(oil_types.keys()))
        
        # 地方選択
        regions = {
            "全国平均": 0, "東京": 5, "神奈川": 2, "埼玉": 0, "千葉": -2, "大阪": 4, 
            "北海道": 8, "東北": 3, "中部": 1, "近畿": 4, "中国四国": 6, "九州": 10
        }
        region = st.selectbox("地方を選択", list(regions.keys()))
        
        final_unit_price = oil_types[fuel_type] + regions[region]
        st.info(f"単価: {final_unit_price} JPY/L ({fuel_type} @ {region})")
        
        # 給油量 (1Lずつの増減)
        lit = st.number_input("給油量 (L)", min_value=1.0, max_value=1000.0, value=50.0, step=1.0)
        
        st.markdown(f"## 合計: **{int(lit * final_unit_price):,} JPY**")

    elif mode == L["cur"]:
        st.subheader(f"💱 {L['cur']}")
        u = st.session_state.rates["USD"]
        amt = st.number_input("USD", 0.0, 1000000.0, 100.0, step=10.0)
        st.markdown(f"## **{amt * u:,.0f} JPY**")
        
    elif mode == L["tax"]:
        st.subheader(f"🧾 {L['tax']}")
        val = st.number_input("Amount", 0.0, 10000000.0, 10000.0, step=100.0)
        rate = st.radio("Rate", [0.08, 0.10], horizontal=True)
        st.markdown(f"## **{int(val * (1+rate)):,} JPY**")
    st.markdown('</div>', unsafe_allow_html=True)
