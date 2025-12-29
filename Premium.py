import streamlit as st
import math
import statistics
import urllib.request
import json
import datetime

# --- 1. ページ設定 ---
st.set_page_config(page_title="Global Professional Calc 2025", layout="centered")

# --- 2. 状態管理 ---
if 'display' not in st.session_state:
    st.session_state.display = ""
if 'rates' not in st.session_state:
    st.session_state.rates = {"USD": 156.40, "BTC": 13972000, "ETH": 485500}
if 'theme' not in st.session_state:
    st.session_state.theme = "Dark"
if 'lang' not in st.session_state:
    st.session_state.lang = "日本語"

# --- 3. 言語辞書 (10言語) ---
LANG_DICT = {
    "日本語": {"update": "レート更新", "theme": "テーマ切替", "clear": "クリア", "exe": "計算実行", "sci": "科学計算", "stat": "統計", "si": "接頭語", "paid": "有料機能", "fuel": "燃料価格", "cur": "為替換算", "cry": "仮想通貨"},
    "English": {"update": "Update Rates", "theme": "Switch Theme", "clear": "CLEAR", "exe": "EXECUTE", "sci": "SCIENTIFIC", "stat": "STATISTICS", "si": "SI UNITS", "paid": "PAID", "fuel": "FUEL", "cur": "CURRENCY", "cry": "CRYPTO"},
    "中文": {"update": "更新汇率", "theme": "切换主题", "clear": "清除", "exe": "计算", "sci": "科学计算", "stat": "统计", "si": "单位", "paid": "付费功能", "fuel": "燃料", "cur": "货币", "cry": "加密货币"},
    "한국어": {"update": "환율 업데이트", "theme": "테마 변경", "clear": "삭제", "exe": "계산", "sci": "과학 계산", "stat": "통계", "si": "접두어", "paid": "유료 기능", "fuel": "연료", "cur": "환율", "cry": "가상화폐"},
    "Español": {"update": "Actualizar", "theme": "Cambiar Tema", "clear": "BORRAR", "exe": "EJECUTAR", "sci": "CIENTÍFICA", "stat": "ESTADÍSTICA", "si": "SI", "paid": "PAGO", "fuel": "COMBUSTIBLE", "cur": "MONEDA", "cry": "CRIPTO"},
    "Français": {"update": "Actualiser", "theme": "Thème", "clear": "EFFACER", "exe": "CALCULER", "sci": "SCIENTIFIQUE", "stat": "STATISTIQUES", "si": "SI", "paid": "PAYANT", "fuel": "CARBURANT", "cur": "DEVISE", "cry": "CRYPTO"},
    "Deutsch": {"update": "Aktualisieren", "theme": "Design", "clear": "LÖSCHEN", "exe": "BERECHNEN", "sci": "WISSENSCHAFT", "stat": "STATISTIK", "si": "SI", "paid": "PRO", "fuel": "KRAFTSTOFF", "cur": "WÄHRUNG", "cry": "CRYPTO"},
    "Русский": {"update": "Обновить", "theme": "Тема", "clear": "СБРОС", "exe": "ИТОГ", "sci": "НАУЧНЫЙ", "stat": "СТАТИСТИКА", "si": "СИ", "paid": "ПЛАТНО", "fuel": "ТОПЛИВО", "cur": "VALUTA", "cry": "КРИПТО"},
    "Português": {"update": "Atualizar", "theme": "Tema", "clear": "LIMPAR", "exe": "EXECUTAR", "sci": "CIENTÍFICA", "stat": "ESTATÍSTICA", "si": "SI", "paid": "PAGO", "fuel": "COMBUSTÍVEL", "cur": "MOEDA", "cry": "CRIPTO"},
    "Italiano": {"update": "Aggiorna", "theme": "Tema", "clear": "CANCELLA", "exe": "ESEGUI", "sci": "SCIENTIFICA", "stat": "STATISTICA", "si": "SI", "paid": "PAGAMENTO", "fuel": "CARBURANTE", "cur": "VALUTA", "cry": "CRIPTO"}
}

# --- 4. SI接頭語辞書 (Qからqまで) ---
SI_MAP = {
    'Q': '*1e30', 'R': '*1e27', 'Y': '*1e24', 'Z': '*1e21', 'E': '*1e18', 'P': '*1e15', 'T': '*1e12', 'G': '*1e9', 'M': '*1e6', 'k': '*1e3',
    'm': '*1e-3', 'μ': '*1e-6', 'n': '*1e-9', 'p': '*1e-12', 'f': '*1e-15', 'a': '*1e-18', 'z': '*1e-21', 'y': '*1e-24', 'r': '*1e-27', 'q': '*1e-30'
}

# --- 5. デザイン (CSS) ---
is_dark = st.session_state.theme == "Dark"
bg, txt, dbg = ("#121212", "#FFFFFF", "#252525") if is_dark else ("#F5F5F5", "#000000", "#FFFFFF")
border_color = "#444444" if is_dark else "#CCCCCC"

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg}; color: {txt}; }}
    .calc-display {{
        background-color: {dbg}; color: {txt};
        padding: 20px; border: 2px solid {txt}; border-radius: 4px;
        font-size: 36px; font-weight: 700; text-align: right;
        min-height: 80px; margin-bottom: 20px; font-family: monospace;
    }}
    div.stButton > button {{
        width: 100% !important; height: 45px !important;
        font-weight: 700 !important; background-color: {dbg} !important; color: {txt} !important;
        border: 1px solid {border_color} !important; border-radius: 2px !important;
    }}
    .input-group {{ border: 1px solid {border_color}; padding: 15px; border-radius: 4px; background-color: {dbg}; }}
</style>
""", unsafe_allow_html=True)

# --- 6. UIコンポーネント ---
L = LANG_DICT[st.session_state.lang]

col_lang, col_upd, col_thm = st.columns([1, 1, 1])
with col_lang:
    st.session_state.lang = st.selectbox("LANGUAGE", list(LANG_DICT.keys()), label_visibility="collapsed")
with col_upd:
    if st.button(L["update"]): 
        try:
            with urllib.request.urlopen("https://open.er-api.com/v6/latest/USD") as response:
                st.session_state.rates["USD"] = json.loads(response.read())["rates"]["JPY"]
            st.toast("UPDATED")
        except: st.error("ERROR")
with col_thm:
    if st.button(L["theme"]):
        st.session_state.theme = "Light" if is_dark else "Dark"; st.rerun()

st.markdown(f'<div class="calc-display">{st.session_state.display if st.session_state.display else "0"}</div>', unsafe_allow_html=True)

# --- 7. キーパッド ---
rows = [["7","8","9","÷"],["4","5","6","×"],["1","2","3","−"],["0",".","π","+"]]
op_map = {"÷": "/", "×": "*", "−": "-"}
for row in rows:
    cols = st.columns(4)
    for i, label in enumerate(row):
        if cols[i].button(label):
            st.session_state.display += op_map.get(label, label); st.rerun()

c1, c2 = st.columns(2)
if c1.button(L["clear"]): st.session_state.display = ""; st.rerun()
if c2.button(L["exe"]):
    try:
        calc_str = st.session_state.display
        for k, v in SI_MAP.items(): calc_str = calc_str.replace(k, v)
        st.session_state.display = format(eval(calc_str, {"math": math, "statistics": statistics}), '.10g')
    except: st.session_state.display = "ERROR"
    st.rerun()

st.divider()

# --- 8. 機能タブ ---
t1, t2, t3, t4 = st.tabs([L["sci"], L["stat"], L["si"], L["paid"]])

with t1:
    s_map = {"sin":"math.sin(", "cos":"math.cos(", "tan":"math.tan(", "sqrt":"math.sqrt(", "log":"math.log10(", "abs":"abs(", "^":"**"}
    cols = st.columns(4)
    for i, (k, v) in enumerate(s_map.items()):
        if cols[i % 4].button(k): st.session_state.display += v; st.rerun()

with t2:
    cols = st.columns(3)
    if cols[0].button("MEAN"): st.session_state.display += "statistics.mean(["; st.rerun()
    if cols[1].button("MEDIAN"): st.session_state.display += "statistics.median(["; st.rerun()
    if cols[2].button("SUM"): st.session_state.display += "sum(["; st.rerun()
    if st.button("CLOSE ARRAY ( ]) )"): st.session_state.display += "])"; st.rerun()

with t3:
    # Qからqまでの全接頭語
    si_keys = list(SI_MAP.keys())
    for i in range(0, len(si_keys), 5):
        cols = st.columns(5)
        for j in range(5):
            if i + j < len(si_keys):
                k = si_keys[i+j]
                if cols[j].button(k): st.session_state.display += k; st.rerun()

with t4:
    st.markdown('<div class="input-group">', unsafe_allow_html=True)
    m = st.radio("SELECT", [L["fuel"], L["cur"], L["cry"]], horizontal=True)
    if L["fuel"] in m:
        loc = st.selectbox("SS", ["OME (188)", "TACHIKAWA (169)", "AVG (176)"])
        p = 188 if "OME" in loc else (169 if "TACHIKAWA" in loc else 176)
        lit = st.number_input("L", 1.0, 500.0, 50.0)
        st.info(f"TOTAL: {int(p*lit):,} JPY")
    elif L["cur"] in m:
        u = st.session_state.rates["USD"]
        amt = st.number_input("USD", 0.0, 100000.0, 100.0)
        st.info(f"{amt * u:,.0f} JPY")
    elif L["cry"] in m:
        coin = st.selectbox("COIN", ["BTC", "ETH"])
        p = st.session_state.rates[coin]
        hold = st.number_input("HOLD", 0.0, 100.0, 0.1, format="%.4f")
        st.info(f"{int(hold * p):,} JPY")
    st.markdown('</div>', unsafe_allow_html=True)
