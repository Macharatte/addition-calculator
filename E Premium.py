import streamlit as st
import math
import statistics
import urllib.request
import json

# --- 1. システム状態管理 ---
if 'v14_ui_cleanup' not in st.session_state:
    st.session_state.clear()
    st.session_state.v14_ui_cleanup = True
    st.session_state.display = ""
    st.session_state.lang = "日本語"
    st.session_state.theme = "Dark"
    st.session_state.rates = {"USD": 156.4, "BTC": 13972000, "ETH": 485500}

# --- 2. 10言語完全定義 ---
L_MAP = {
    "日本語": {"upd": "更新", "thm": "テーマ", "clr": "消去", "exe": "実行", "si": "接頭語", "sci": "科学", "stat": "値数", "paid": "プロ", "fuel": "燃料", "cur": "通貨", "tax": "税金", "mean":"平均", "sum":"合計", "mode":"最頻", "med":"中央", "max":"最大", "min":"最小", "dev":"偏差値", "exp":"期待値"},
    "English": {"upd": "UPD", "thm": "THEME", "clr": "CLR", "exe": "EXE", "si": "SI", "sci": "SCI", "stat": "VAL", "paid": "PRO", "fuel": "FUEL", "cur": "FOREX", "tax": "TAX", "mean":"MEAN", "sum":"SUM", "mode":"MODE", "med":"MED", "max":"MAX", "min":"MIN", "dev":"T-SCR", "exp":"EXP"},
    "中文": {"upd": "更新", "thm": "主题", "clr": "清除", "exe": "计算", "si": "单位", "sci": "科学", "stat": "数值", "paid": "专业", "fuel": "汽油", "cur": "汇率", "tax": "税金", "mean":"平均", "sum":"总和", "mode":"众数", "med":"中位", "max":"最大", "min":"最小", "dev":"偏差", "exp":"期望"},
    "한국어": {"upd": "갱신", "thm": "테마", "clr": "삭제", "exe": "계산", "si": "접두어", "sci": "과학", "stat": "수치", "paid": "유료", "fuel": "가솔린", "cur": "환율", "tax": "세금", "mean":"평균", "sum":"합계", "mode":"최빈", "med":"중앙", "max":"최대", "min":"최소", "dev":"편차", "exp":"기대"},
    "Español": {"upd": "ACT", "thm": "TEMA", "clr": "BORRAR", "exe": "IGUAL", "si": "SI", "sci": "CIEN", "stat": "VALOR", "paid": "PAGO", "fuel": "GAS", "cur": "MONEDA", "tax": "IMP", "mean":"PROM", "sum":"SUMA", "mode":"MODA", "med":"MED", "max":"MAX", "min":"MIN", "dev":"T-PUNT", "exp":"EXP"},
    "Français": {"upd": "MAJ", "thm": "THÈME", "clr": "EFFACER", "exe": "ÉGAL", "si": "SI", "sci": "SCI", "stat": "VALEUR", "paid": "PAYANT", "fuel": "ESSENCE", "cur": "DEVISE", "tax": "TAXE", "mean":"MOY", "sum":"SOMME", "mode":"MODE", "med":"MED", "max":"MAX", "min":"MIN", "dev":"T-SCR", "exp":"EXP"},
    "Deutsch": {"upd": "UPD", "thm": "DESIGN", "clr": "LÖSCHEN", "exe": "GLEICH", "si": "SI", "sci": "WISS", "stat": "WERTE", "paid": "PRO", "fuel": "SPRIT", "cur": "KURS", "tax": "STEUER", "mean":"MITTEL", "sum":"SUMME", "mode":"MODUS", "med":"MEDIAN", "max":"MAX", "min":"MIN", "dev":"T-WERT", "exp":"EW"},
    "Русский": {"upd": "ОБН", "thm": "ТЕМА", "clr": "СБРОС", "exe": "ИТОГ", "si": "СИ", "sci": "НАУЧ", "stat": "ЧИСЛА", "paid": "ПЛАТНО", "fuel": "БЕНЗИН", "cur": "КУРС", "tax": "НАЛОГ", "mean":"СРЕД", "sum":"СУММ", "mode":"MODA", "med":"MED", "max":"MAX", "min":"MIN", "dev":"Т-ОЦ", "exp":"MO"},
    "Português": {"upd": "ATU", "thm": "TEMA", "clr": "LIMPAR", "exe": "IGUAL", "si": "SI", "sci": "CIEN", "stat": "VALOR", "paid": "PAGO", "fuel": "GASOL", "cur": "MOEDA", "tax": "IMP", "mean":"MED", "sum":"SOMA", "mode":"MODA", "med":"MED", "max":"MAX", "min":"MIN", "dev":"T-PUNT", "exp":"EXP"},
    "Italiano": {"upd": "AGG", "thm": "TEMA", "clr": "CANC", "exe": "UGUALE", "si": "SI", "sci": "SCI", "stat": "VALORE", "paid": "PRO", "fuel": "BENZ", "cur": "VALUTA", "tax": "TASSE", "mean":"MEDIA", "sum":"SOMMA", "mode":"MODA", "med":"MED", "max":"MAX", "min":"MIN", "dev":"T-PUNT", "exp":"EV"}
}

SI_CONV = {
    'Q': '*1e30', 'R': '*1e27', 'Y': '*1e24', 'Z': '*1e21', 'E': '*1e18', 'P': '*1e15', 'T': '*1e12', 'G': '*1e9', 'M': '*1e6', 'k': '*1e3',
    'm': '*1e-3', 'μ': '*1e-6', 'n': '*1e-9', 'p': '*1e-12', 'f': '*1e-15', 'a': '*1e-18', 'z': '*1e-21', 'y': '*1e-24', 'r': '*1e-27', 'q': '*1e-30'
}

# --- 3. UIデザイン ---
is_dark = st.session_state.theme == "Dark"
bg_color = "#000000" if is_dark else "#FFFFFF"
text_color = "#FFFFFF" if is_dark else "#000000"
accent_color = "#1E88E5" # 計算結果用のアクセントカラー

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg_color} !important; color: {text_color} !important; }}
    .disp {{
        background-color: {bg_color} !important; color: {text_color} !important;
        padding: 25px; border: 4px solid {text_color} !important;
        border-radius: 12px; font-size: 42px; text-align: right;
        font-family: monospace; margin-bottom: 20px; min-height: 90px;
    }}
    div.stButton > button {{
        width: 100% !important; border: 2px solid {text_color} !important;
        background-color: {bg_color} !important; color: {text_color} !important;
        font-weight: bold !important; transition: 0.1s;
    }}
    div.stButton > button:hover {{
        background-color: {text_color} !important; color: {bg_color} !important;
    }}
    /* 有料機能の計算結果カード */
    .result-card {{
        background-color: {text_color}22 !important; 
        padding: 20px; border-radius: 10px; border-left: 5px solid {accent_color};
        margin-top: 15px;
    }}
    label, p, span {{ color: {text_color} !important; font-weight: bold !important; }}
</style>
""", unsafe_allow_html=True)

# --- 4. メインディスプレイ ---
L = L_MAP.get(st.session_state.lang, L_MAP["English"])
c1, c2, c3 = st.columns([1, 1, 1])
with c1:
    new_lang = st.selectbox("Lang", list(L_MAP.keys()), index=list(L_MAP.keys()).index(st.session_state.lang), label_visibility="collapsed")
    if new_lang != st.session_state.lang: st.session_state.lang = new_lang; st.rerun()
with c2:
    if st.button(L["upd"]):
        try:
            with urllib.request.urlopen("https://open.er-api.com/v6/latest/USD") as r:
                data = json.loads(r.read())
                st.session_state.rates["USD"] = data["rates"]["JPY"]
            st.toast("Success")
        except: st.error("ERR")
with c3:
    if st.button(L["thm"]):
        st.session_state.theme = "Light" if is_dark else "Dark"; st.rerun()

st.markdown(f'<div class="disp">{st.session_state.display if st.session_state.display else "0"}</div>', unsafe_allow_html=True)

# --- 5. キーパッド ---
rows = [["7","8","9","÷"],["4","5","6","×"],["1","2","3","−"],["0",".","00","+"]]
for row in rows:
    cols = st.columns(4)
    for i, k in enumerate(row):
        if cols[i].button(k, key=f"k_{k}"): st.session_state.display += k; st.rerun()

cl, ex = st.columns(2)
if cl.button(L["clr"]): st.session_state.display = ""; st.rerun()
if ex.button(L["exe"]):
    try:
        expr = st.session_state.display.replace("×", "*").replace("÷", "/").replace("−", "-")
        expr = expr.replace("e", str(math.e)).replace("i", "1j").replace("π", str(math.pi))
        for k, v in SI_CONV.items(): expr = expr.replace(k, v)
        res = eval(expr, {"math": math, "statistics": statistics})
        st.session_state.display = format(res, '.10g') if not isinstance(res, (complex, list)) else str(res)
    except: st.session_state.display = "Error"
    st.rerun()

st.divider()

# --- 6. タブ機能 ---
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
    if r1[0].button(L["mean"]): st.session_state.display += "statistics.mean(["; st.rerun()
    if r1[1].button(L["med"]): st.session_state.display += "statistics.median(["; st.rerun()
    if r1[2].button(L["mode"]): st.session_state.display += "statistics.mode(["; st.rerun()
    r2 = st.columns(3)
    if r2[0].button(L["sum"]): st.session_state.display += "sum(["; st.rerun()
    if r2[1].button(L["max"]): st.session_state.display += "max(["; st.rerun()
    if r2[2].button(L["min"]): st.session_state.display += "min(["; st.rerun()
    r3 = st.columns(2)
    if r3[0].button(L["dev"]): st.session_state.display += "[(x-statistics.mean(d))/statistics.stdev(d)*10+50 for d in [["; st.rerun()
    if r3[1].button(L["exp"]): st.session_state.display += "sum([x*p for x,p in zip([値],[率])])"; st.rerun()
    r4 = st.columns(2)
    if r4[0].button(","): st.session_state.display += ","; st.rerun()
    if r4[1].button("CLOSE ])"): st.session_state.display += "])"; st.rerun()

# --- 7. プロ機能 (UI改善版) ---
with t_paid:
    mode = st.radio("MODE", [L["fuel"], L["cur"], L["tax"]], horizontal=True, label_visibility="collapsed")
    
    if mode == L["fuel"]:
        f_col1, f_col2 = st.columns(2)
        oil_types = {"レギュラー": 170, "ハイオク": 181, "軽油": 149, "灯油": 115, "重油": 95, "ナフサ": 75, "アスファルト": 85, "潤滑油": 130}
        regions = {"全国平均": 0, "東京": 5, "神奈川": 2, "埼玉": 0, "千葉": -2, "大阪": 4, "北海道": 8, "東北": 3, "中部": 1, "近畿": 4, "中国四国": 6, "九州": 10}
        with f_col1: f_type = st.selectbox("油種", list(oil_types.keys()))
        with f_col2: reg = st.selectbox("地方", list(regions.keys()))
        u_price = oil_types[f_type] + regions[reg]
        lit = st.number_input("数量 (L)", 1.0, 1000.0, 50.0, step=1.0)
        st.markdown(f'<div class="result-card"><h3>合計: {int(lit * u_price):,} JPY</h3><p>{f_type} / {reg} (単価: {u_price}円)</p></div>', unsafe_allow_html=True)

    elif mode == L["cur"]:
        cur_type = st.radio("TARGET", ["USD", "BTC", "ETH"], horizontal=True)
        amt = st.number_input("変換量", 0.0, 1000000.0, 1.0, step=0.1)
        rate = st.session_state.rates.get(cur_type, 1.0)
        st.markdown(f'<div class="result-card"><h3>結果: {amt * rate:,.2f} JPY</h3><p>現在のレート: 1 {cur_type} = {rate:,.2f}円</p></div>', unsafe_allow_html=True)

    elif mode == L["tax"]:
        base_amt = st.number_input("金額 (税抜)", 0.0, 10000000.0, 10000.0, step=100.0)
        tax_sel = st.radio("税率設定", ["8%", "10%", "Custom"], horizontal=True)
        tax_rate = (st.slider("Rate (%)", 0, 50, 15) / 100) if tax_sel == "Custom" else (0.08 if tax_sel == "8%" else 0.10)
        st.markdown(f'<div class="result-card"><h3>税込合計: {int(base_amt * (1+tax_rate)):,} JPY</h3><p>消費税額: {int(base_amt * tax_rate):,} JPY ({int(tax_rate*100)}%)</p></div>', unsafe_allow_html=True)
