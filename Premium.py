import streamlit as st
import math
import statistics
import urllib.request
import json
import datetime

# --- 1. ページ基本設定 ---
st.set_page_config(page_title="Global SI-Master Calc 2025", layout="centered")

# --- 2. 状態管理の初期化 ---
if 'display' not in st.session_state:
    st.session_state.display = ""
if 'rates' not in st.session_state:
    st.session_state.rates = {"USD": 156.40, "BTC": 13972000, "ETH": 485500}
if 'theme' not in st.session_state:
    st.session_state.theme = "Dark"
if 'lang' not in st.session_state:
    st.session_state.lang = "日本語"

# --- 3. 10言語辞書定義 ---
LANG_DICT = {
    "日本語": {"upd": "レート更新", "thm": "表示切替", "clr": "消去", "exe": "計算実行", "sci": "科学", "stat": "統計", "si": "接頭語", "paid": "有料", "fuel": "燃料", "cur": "為替", "cry": "仮想通貨"},
    "English": {"upd": "Update", "thm": "Theme", "clr": "CLR", "exe": "EXEC", "sci": "SCI", "stat": "STAT", "si": "SI", "paid": "PAID", "fuel": "Fuel", "cur": "Forex", "cry": "Crypto"},
    "中文": {"upd": "更新汇率", "thm": "切换主题", "clear": "清除", "exe": "计算", "sci": "科学", "stat": "统计", "si": "单位", "paid": "付费", "fuel": "燃料", "cur": "货币", "cry": "加密货币"},
    "한국어": {"upd": "환율 갱신", "thm": "테마 변경", "clr": "삭제", "exe": "실행", "sci": "과학", "stat": "통계", "si": "접두어", "paid": "유료", "fuel": "연료", "cur": "환율", "cry": "코인"},
    "Español": {"upd": "Actualizar", "thm": "Tema", "clr": "BORRAR", "exe": "EJECUTAR", "sci": "SCI", "stat": "ESTAD", "si": "SI", "paid": "PAGO", "fuel": "Gas", "cur": "Moneda", "cry": "Cripto"},
    "Français": {"upd": "Actualiser", "thm": "Thème", "clr": "EFFACER", "exe": "EXEC", "sci": "SCI", "stat": "STAT", "si": "SI", "paid": "PAGO", "fuel": "Carburant", "cur": "Devise", "cry": "Crypto"},
    "Deutsch": {"upd": "Update", "thm": "Design", "clr": "LÖSCHEN", "exe": "BERECHNEN", "sci": "SCI", "stat": "STAT", "si": "SI", "paid": "PRO", "fuel": "Sprit", "cur": "Währung", "cry": "Krypto"},
    "Русский": {"upd": "Обновить", "thm": "Тема", "clr": "СБРОС", "exe": "ИТОГ", "sci": "НАУЧ", "stat": "СТАТ", "si": "СИ", "paid": "ПЛАТНО", "fuel": "Топливо", "cur": "Валюта", "cry": "Крипто"},
    "Português": {"upd": "Atualizar", "thm": "Tema", "clr": "LIMPAR", "exe": "EXEC", "sci": "SCI", "stat": "ESTAD", "si": "SI", "paid": "PAGO", "fuel": "Gás", "cur": "Moeda", "cry": "Cripto"},
    "Italiano": {"upd": "Aggiorna", "thm": "Tema", "clr": "CANCELLA", "exe": "ESEGUI", "sci": "SCI", "stat": "STAT", "si": "SI", "paid": "PRO", "fuel": "Benzina", "cur": "Valuta", "cry": "Cripto"}
}

# --- 4. SI接頭語定義 (Q ~ q 全20種) ---
SI_MAP = {
    'Q': '*1e30', 'R': '*1e27', 'Y': '*1e24', 'Z': '*1e21', 'E': '*1e18', 'P': '*1e15', 'T': '*1e12', 'G': '*1e9', 'M': '*1e6', 'k': '*1e3',
    'm': '*1e-3', 'μ': '*1e-6', 'n': '*1e-9', 'p': '*1e-12', 'f': '*1e-15', 'a': '*1e-18', 'z': '*1e-21', 'y': '*1e-24', 'r': '*1e-27', 'q': '*1e-30'
}

# --- 5. デザイン設定 ---
is_dark = st.session_state.theme == "Dark"
bg, txt, dbg = ("#0F0F0F", "#FFFFFF", "#1E1E1E") if is_dark else ("#FFFFFF", "#000000", "#F0F2F6")
border = "#444444" if is_dark else "#CCCCCC"

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg}; color: {txt}; }}
    .display-box {{
        background-color: {dbg}; color: {txt}; padding: 25px; border: 2px solid {txt};
        border-radius: 8px; font-size: 40px; text-align: right; font-family: 'Courier New', monospace;
    }}
    div.stButton > button {{ width: 100%; height: 48px; font-weight: bold; border: 1px solid {border}; }}
    .frame-box {{ border: 1px solid {border}; padding: 15px; border-radius: 8px; background: {dbg}; margin-top: 10px; }}
</style>
""", unsafe_allow_html=True)

# --- 6. トップナビゲーション ---
L = LANG_DICT.get(st.session_state.lang, LANG_DICT["English"])

c_lang, c_upd, c_thm = st.columns([1, 1, 1])
with c_lang:
    # 言語変更時に即座に再描画
    new_lang = st.selectbox("LANG", list(LANG_DICT.keys()), index=list(LANG_DICT.keys()).index(st.session_state.lang), label_visibility="collapsed")
    if new_lang != st.session_state.lang:
        st.session_state.lang = new_lang
        st.rerun()
with c_upd:
    if st.button(L["upd"]):
        try:
            with urllib.request.urlopen("https://open.er-api.com/v6/latest/USD") as r:
                st.session_state.rates["USD"] = json.loads(r.read())["rates"]["JPY"]
            st.toast("Updated")
        except: st.error("Error")
with c_thm:
    if st.button(L["thm"]):
        st.session_state.theme = "Light" if is_dark else "Dark"
        st.rerun()

# --- 7. ディスプレイ ---
st.markdown(f'<div class="display-box">{st.session_state.display if st.session_state.display else "0"}</div>', unsafe_allow_html=True)

# --- 8. 基本キーパッド ---
keys = [["7","8","9","÷"],["4","5","6","×"],["1","2","3","−"],["0",".","π","+"]]
ops = {"÷": "/", "×": "*", "−": "-"}
for row in keys:
    cols = st.columns(4)
    for i, k in enumerate(row):
        if cols[i].button(k):
            st.session_state.display += ops.get(k, k); st.rerun()

b_clr, b_exe = st.columns(2)
if b_clr.button(L["clr"]): st.session_state.display = ""; st.rerun()
if b_exe.button(L["exe"]):
    try:
        expr = st.session_state.display
        for k, v in SI_MAP.items(): expr = expr.replace(k, v)
        st.session_state.display = str(eval(expr, {"math": math, "statistics": statistics}))
    except: st.session_state.display = "Error"
    st.rerun()

st.divider()

# --- 9. 機能切り替えエリア ---
tabs = st.tabs([L["sci"], L["stat"], L["si"], L["paid"]])

with tabs[0]: # 科学計算
    sc = st.columns(4)
    s_f = {"sin":"math.sin(", "cos":"math.cos(", "tan":"math.tan(", "√":"math.sqrt(", "log":"math.log10(", "exp":"math.exp(", "abs":"abs(", "(":"("}
    for i, (k, v) in enumerate(s_f.items()):
        if sc[i%4].button(k): st.session_state.display += v; st.rerun()
    if st.button(" ) "): st.session_state.display += ")"; st.rerun()

with tabs[1]: # 統計
    st_c = st.columns(3)
    if st_c[0].button("MEAN"): st.session_state.display += "statistics.mean(["; st.rerun()
    if st_c[1].button("MEDIAN"): st.session_state.display += "statistics.median(["; st.rerun()
    if st_c[2].button("SUM"): st.session_state.display += "sum(["; st.rerun()
    if st.button("CLOSE ])"): st.session_state.display += "])"; st.rerun()

with tabs[2]: # SI接頭語 Q ~ q
    st.caption("Q(10^30) to q(10^-30)")
    si_keys = list(SI_MAP.keys())
    for i in range(0, len(si_keys), 5):
        cols = st.columns(5)
        for j in range(5):
            if i+j < len(si_keys):
                p = si_keys[i+j]
                if cols[j].button(p): st.session_state.display += p; st.rerun()

with tabs[3]: # 有料
    st.markdown('<div class="frame-box">', unsafe_allow_html=True)
    m = st.radio("SELECT", [L["fuel"], L["cur"], L["cry"]], horizontal=True)
    if L["fuel"] in m:
        loc = st.selectbox("SS", ["OME(188)", "TACHI(169)", "AVG(176)"])
        p = 188 if "OME" in loc else (169 if "TACHI" in loc else 176)
        lit = st.number_input("L", 1.0, 500.0, 50.0)
        st.info(f"Total: {int(p*lit):,} JPY")
    elif L["cur"] in m:
        u = st.session_state.rates["USD"]
        v = st.number_input("USD", 0.0, 100000.0, 100.0)
        st.info(f"{v * u:,.0f} JPY")
    elif L["cry"] in m:
        c = st.selectbox("Coin", ["BTC", "ETH"])
        h = st.number_input("Amount", 0.0, 100.0, 0.1)
        st.info(f"{int(h * st.session_state.rates[c]):,} JPY")
    st.markdown('</div>', unsafe_allow_html=True)
