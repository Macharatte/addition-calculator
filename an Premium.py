import streamlit as st
import math
import statistics
import urllib.request
import json

# --- 1. 強制リセット & 状態管理 ---
if 'v10_final_plus' not in st.session_state:
    st.session_state.clear()
    st.session_state.v10_final_plus = True
    st.session_state.display = ""
    st.session_state.lang = "日本語"
    st.session_state.theme = "Dark"
    st.session_state.rates = {"USD": 156.4, "BTC": 13972000, "ETH": 485500}

# --- 2. 10言語定義 ---
L_MAP = {
    "日本語": {"upd": "レート更新", "thm": "表示切替", "clr": "消去", "exe": "計算実行", "si": "接頭語", "sci": "科学", "stat": "値数", "paid": "有料機能", "fuel": "ガソリン", "cur": "通貨レート", "tax": "税金計算", "mean":"平均値", "sum":"合計値", "mode":"最頻値", "med":"中央値", "max":"最大値", "min":"最小値"},
    "English": {"upd": "UPDATE", "thm": "THEME", "clr": "CLEAR", "exe": "EXEC", "si": "SI", "sci": "SCI", "stat": "VALUE", "paid": "PREMIUM", "fuel": "FUEL", "cur": "FOREX", "tax": "TAX", "mean":"MEAN", "sum":"SUM", "mode":"MODE", "med":"MEDIAN", "max":"MAX", "min":"MIN"},
    "中文": {"upd": "更新汇率", "thm": "主题", "clr": "清除", "exe": "计算", "si": "单位", "sci": "科学", "stat": "数值", "paid": "付费功能", "fuel": "汽油", "cur": "汇率", "tax": "税金", "mean":"平均", "sum":"总和", "mode":"众数", "med":"中位数", "max":"最大", "min":"最小"},
    "한국어": {"upd": "환율갱신", "thm": "테마", "clr": "삭제", "exe": "계산", "si": "접두어", "sci": "과학", "stat": "수치", "paid": "유료기능", "fuel": "가솔린", "cur": "환율", "tax": "세금", "mean":"평균", "sum":"합계", "mode":"최빈값", "med":"중앙값", "max":"최대", "min":"최소"},
    "Español": {"upd": "ACTUALIZAR", "thm": "TEMA", "clr": "BORRAR", "exe": "IGUAL", "si": "SI", "sci": "CIEN", "stat": "VALOR", "paid": "PAGO", "fuel": "GAS", "cur": "MONEDA", "tax": "IMPUESTO", "mean":"PROM", "sum":"SUMA", "mode":"MODA", "med":"MEDIANA", "max":"MAX", "min":"MIN"},
    "Français": {"upd": "ACTUALISER", "thm": "THÈME", "clr": "EFFACER", "exe": "ÉGAL", "si": "SI", "sci": "SCI", "stat": "VALEUR", "paid": "PAYANT", "fuel": "ESSENCE", "cur": "DEVISE", "tax": "TAXE", "mean":"MOY", "sum":"SOMME", "mode":"MODE", "med":"MEDIANE", "max":"MAX", "min":"MIN"},
    "Deutsch": {"upd": "UPDATE", "thm": "DESIGN", "clr": "LÖSCHEN", "exe": "GLEICH", "si": "SI", "sci": "WISS", "stat": "WERTE", "paid": "PRO", "fuel": "SPRIT", "cur": "KURS", "tax": "STEUER", "mean":"MITTEL", "sum":"SUMME", "mode":"MODUS", "med":"MEDIAN", "max":"MAX", "min":"MIN"},
    "Русский": {"upd": "ОБНОВИТЬ", "thm": "ТЕМА", "clr": "СБРОС", "exe": "ИТОГ", "si": "СИ", "sci": "НАУЧ", "stat": "ЧИСЛА", "paid": "ПЛАТНО", "fuel": "БЕНЗИН", "cur": "КУРС", "tax": "НАЛОГ", "mean":"СРЕД", "sum":"СУММ", "mode":"MODA", "med":"MED", "max":"MAX", "min":"MIN"},
    "Português": {"upd": "ATUALIZAR", "thm": "TEMA", "clr": "LIMPAR", "exe": "IGUAL", "si": "SI", "sci": "CIEN", "stat": "VALOR", "paid": "PAGO", "fuel": "GASOL", "cur": "MOEDA", "tax": "IMPOSTO", "mean":"MED", "sum":"SOMA", "mode":"MODA", "med":"MEDIANA", "max":"MAX", "min":"MIN"},
    "Italiano": {"upd": "AGGIORNA", "thm": "TEMA", "clr": "CANCELLA", "exe": "UGUALE", "si": "SI", "sci": "SCI", "stat": "VALORE", "paid": "PRO", "fuel": "BENZINA", "cur": "VALUTA", "tax": "TASSE", "mean":"MEDIA", "sum":"SOMMA", "mode":"MODA", "med":"MEDIANA", "max":"MAX", "min":"MIN"}
}

SI_CONV = {
    'Q': '*1e30', 'R': '*1e27', 'Y': '*1e24', 'Z': '*1e21', 'E': '*1e18', 'P': '*1e15', 'T': '*1e12', 'G': '*1e9', 'M': '*1e6', 'k': '*1e3',
    'm': '*1e-3', 'μ': '*1e-6', 'n': '*1e-9', 'p': '*1e-12', 'f': '*1e-15', 'a': '*1e-18', 'z': '*1e-21', 'y': '*1e-24', 'r': '*1e-27', 'q': '*1e-30'
}

# --- 3. デザイン設定 ---
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
        font-family: monospace; margin-bottom: 20px; min-height: 100px; overflow-x: auto;
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
    label, p, span, .stMarkdown, .stRadio, .stNumberInput, .stSelectbox {{ color: {text_color} !important; }}
    .stTabs [data-baseweb="tab"] p {{ color: {text_color} !important; }}
</style>
""", unsafe_allow_html=True)

# --- 4. トップナビ ---
L = L_MAP[st.session_state.lang]
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
            st.toast("Success")
        except: st.error("Error")
with c3:
    if st.button(L["thm"]):
        st.session_state.theme = "Light" if is_dark else "Dark"; st.rerun()

# --- 5. 入力制御 ---
def input_key(k):
    curr = st.session_state.display
    ops = ["+", "−", "×", "÷"]
    if curr == "" and k in ops: return
    if len(curr) > 0 and curr[-1] in ops and k in ops:
        st.session_state.display = curr[:-1] + k
    else: st.session_state.display += k

# --- 6. ディスプレイ ---
st.markdown(f'<div class="disp">{st.session_state.display if st.session_state.display else "0"}</div>', unsafe_allow_html=True)

# --- 7. キーパッド ---
rows = [["7","8","9","÷"],["4","5","6","×"],["1","2","3","−"],["0",".","π","+"]]
for row in rows:
    cols = st.columns(4)
    for i, k in enumerate(row):
        if cols[i].button(k, key=f"k_{k}"): input_key(k); st.rerun()

cl, ex = st.columns(2)
if cl.button(L["clr"]): st.session_state.display = ""; st.rerun()
if ex.button(L["exe"]):
    try:
        expr = st.session_state.display.replace("×", "*").replace("÷", "/").replace("−", "-")
        # 科学定数と虚数単位の処理
        expr = expr.replace("e", str(math.e)).replace("i", "1j")
        for k, v in SI_CONV.items(): expr = expr.replace(k, v)
        res = eval(expr, {"math": math, "statistics": statistics})
        st.session_state.display = format(res, '.10g') if not isinstance(res, complex) else str(res)
    except: st.session_state.display = "Error"
    st.rerun()

st.divider()

# --- 8. タブ機能 ---
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
    sc = st.columns(4)
    # i と e を追加
    sf = {"sin":"math.sin(", "cos":"math.cos(", "tan":"math.tan(", "√":"math.sqrt(", "log":"math.log10(", "(":"(", ")":")", "i":"i", "e":"e"}
    sf_list = list(sf.items())
    for i in range(0, len(sf_list), 4):
        cols = st.columns(4)
        for j in range(4):
            if i+j < len(sf_list):
                k, v = sf_list[i+j]
                if cols[j].button(k, key=f"sc_{k}"): st.session_state.display += v; st.rerun()

with t_stat:
    # --- 値数タブ: カンマを追加 ---
    r1 = st.columns(3)
    if r1[0].button(L["mean"]): st.session_state.display += "statistics.mean(["; st.rerun()
    if r1[1].button(L["med"]): st.session_state.display += "statistics.median(["; st.rerun()
    if r1[2].button(L["mode"]): st.session_state.display += "statistics.mode(["; st.rerun()
    
    r2 = st.columns(3)
    if r2[0].button(L["sum"]): st.session_state.display += "sum(["; st.rerun()
    if r2[1].button(L["max"]): st.session_state.display += "max(["; st.rerun()
    if r2[2].button(L["min"]): st.session_state.display += "min(["; st.rerun()
    
    r3 = st.columns(2)
    if r3[0].button(",", key="btn_comma"): st.session_state.display += ","; st.rerun()
    if r3[1].button("CLOSE ])"): st.session_state.display += "])"; st.rerun()

with t_paid:
    st.markdown(f'<div class="paid-box">', unsafe_allow_html=True)
    st.write(f"### {L['paid']}")
    mode = st.radio(f"{L['paid']} SELECT", [L["fuel"], L["cur"], L["tax"]], horizontal=True)
    st.divider()
    if mode == L["fuel"]:
        st.subheader(f"⛽ {L['fuel']}")
        lit = st.number_input("Litre", 1.0, 500.0, 50.0)
        p = st.selectbox("JPY/L", [188, 169, 176])
        st.markdown(f"## **{int(lit * p):,} JPY**")
    elif mode == L["cur"]:
        st.subheader(f"💱 {L['cur']}")
        u = st.session_state.rates["USD"]
        amt = st.number_input("USD", 0.0, 1000000.0, 100.0)
        st.markdown(f"## **{amt * u:,.0f} JPY**")
    elif mode == L["tax"]:
        st.subheader(f"🧾 {L['tax']}")
        val = st.number_input("Amount", 0.0, 10000000.0, 10000.0)
        rate = st.radio("Rate", [0.08, 0.10], horizontal=True)
        st.markdown(f"## **{int(val * (1+rate)):,} JPY**")
    st.markdown('</div>', unsafe_allow_html=True)
