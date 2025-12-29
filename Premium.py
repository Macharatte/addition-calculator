import streamlit as st
import math
import statistics
import urllib.request
import json

# --- 強制リセットロジック (古いキャッシュを破壊します) ---
if 'reset_v3' not in st.session_state:
    st.session_state.clear()
    st.session_state.reset_v3 = True

# --- 状態の初期化 ---
if 'display' not in st.session_state: st.session_state.display = ""
if 'lang' not in st.session_state: st.session_state.lang = "日本語"
if 'theme' not in st.session_state: st.session_state.theme = "Dark"
if 'rates' not in st.session_state: st.session_state.rates = {"USD": 156.4, "BTC": 13972000, "ETH": 485500}

# --- 10言語辞書 (確実に反映させるための定義) ---
LANG_MAP = {
    "日本語": {"upd": "レート更新", "thm": "テーマ", "clr": "消去", "exe": "計算", "si": "接頭語", "sci": "科学", "stat": "統計", "paid": "有料"},
    "English": {"upd": "UPDATE", "thm": "THEME", "clr": "CLR", "exe": "EXE", "si": "SI", "sci": "SCI", "stat": "STAT", "paid": "PAID"},
    "中文": {"upd": "更新汇率", "thm": "主题", "clr": "清除", "exe": "计算", "si": "单位", "sci": "科学", "stat": "统计", "paid": "付费"},
    "한국어": {"upd": "환율갱신", "thm": "테마", "clr": "삭제", "exe": "계산", "si": "접두어", "sci": "과학", "stat": "통계", "paid": "유료"},
    "Español": {"upd": "ACTUALIZAR", "thm": "TEMA", "clr": "BORRAR", "exe": "IGUAL", "si": "SI", "sci": "CIEN", "stat": "ESTAD", "paid": "PAGO"},
    "Français": {"upd": "ACTUALISER", "thm": "THÈME", "clr": "EFFACER", "exe": "ÉGAL", "si": "SI", "sci": "SCI", "stat": "STAT", "paid": "PAYANT"},
    "Deutsch": {"upd": "UPDATE", "thm": "DESIGN", "clr": "LÖSCHEN", "exe": "GLEICH", "si": "SI", "sci": "WISS", "stat": "STAT", "paid": "PRO"},
    "Русский": {"upd": "ОБНОВИТЬ", "thm": "ТЕМА", "clr": "СБРОС", "exe": "ИТОГ", "si": "СИ", "sci": "НАУЧ", "stat": "СТАТ", "paid": "ПЛАТНО"},
    "Português": {"upd": "ATUALIZAR", "thm": "TEMA", "clr": "LIMPAR", "exe": "IGUAL", "si": "SI", "sci": "CIEN", "stat": "ESTAD", "paid": "PAGO"},
    "Italiano": {"upd": "AGGIORNA", "thm": "TEMA", "clr": "CANCELLA", "exe": "UGUALE", "si": "SI", "sci": "SCI", "stat": "STAT", "paid": "PRO"}
}

# --- 全20種 SI接頭語 (Q~q) ---
SI_DICT = {
    'Q': '*1e30', 'R': '*1e27', 'Y': '*1e24', 'Z': '*1e21', 'E': '*1e18', 'P': '*1e15', 'T': '*1e12', 'G': '*1e9', 'M': '*1e6', 'k': '*1e3',
    'm': '*1e-3', 'μ': '*1e-6', 'n': '*1e-9', 'p': '*1e-12', 'f': '*1e-15', 'a': '*1e-18', 'z': '*1e-21', 'y': '*1e-24', 'r': '*1e-27', 'q': '*1e-30'
}

# --- ページデザイン ---
is_dark = st.session_state.theme == "Dark"
bg, txt, dbg = ("#0A0A0A", "#FFFFFF", "#1E1E1E") if is_dark else ("#FFFFFF", "#000000", "#F0F2F6")
st.markdown(f"<style>.stApp {{background-color:{bg}; color:{txt};}} .disp {{background:{dbg}; color:{txt}; padding:20px; border:2px solid {txt}; border-radius:8px; font-size:40px; text-align:right; font-family:monospace;}} div.stButton > button {{width:100%; border:1px solid {txt}; height:45px; background:{dbg}; color:{txt}; font-weight:bold;}}</style>", unsafe_allow_html=True)

# --- トップメニュー (言語と言語更新を横並びに) ---
L = LANG_MAP[st.session_state.lang]
c1, c2, c3 = st.columns([1, 1, 1])
with c1:
    new_lang = st.selectbox("L", list(LANG_MAP.keys()), index=list(LANG_MAP.keys()).index(st.session_state.lang), label_visibility="collapsed")
    if new_lang != st.session_state.lang:
        st.session_state.lang = new_lang
        st.rerun()
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

# --- 計算表示 ---
st.markdown(f'<div class="disp">{st.session_state.display if st.session_state.display else "0"}</div>', unsafe_allow_html=True)

# 数値キー
for row in [["7","8","9","÷"],["4","5","6","×"],["1","2","3","−"],["0",".","π","+"]]:
    cols = st.columns(4)
    for i, k in enumerate(row):
        if cols[i].button(k):
            st.session_state.display += {"÷":"/","×":"*","−":"-"}.get(k, k); st.rerun()

cl, ex = st.columns(2)
if cl.button(L["clr"]): st.session_state.display = ""; st.rerun()
if ex.button(L["exe"]):
    try:
        calc = st.session_state.display
        for k, v in SI_DICT.items(): calc = calc.replace(k, v)
        st.session_state.display = format(eval(calc, {"math": math, "statistics": statistics}), '.10g')
    except: st.session_state.display = "Error"
    st.rerun()

st.divider()

# --- 20種類の接頭語 & 機能 ---
t_si, t_sci, t_stat, t_paid = st.tabs([L["si"], L["sci"], L["stat"], L["paid"]])

with t_si:
    st.write("20 SI PREFIXES (Q to q)")
    
    si_keys = list(SI_DICT.keys())
    for i in range(0, len(si_keys), 5):
        cols = st.columns(5)
        for j in range(5):
            if i+j < len(si_keys):
                p = si_keys[i+j]
                if cols[j].button(p): st.session_state.display += p; st.rerun()

with t_sci:
    sc = st.columns(4)
    for i, (k, v) in enumerate({"sin":"math.sin(", "cos":"math.cos(", "tan":"math.tan(", "√":"math.sqrt(", "log":"math.log10(", "(":"(", ")":")"}.items()):
        if sc[i%4].button(k): st.session_state.display += v; st.rerun()

with t_stat:
    st_c = st.columns(3)
    if st_c[0].button("MEAN"): st.session_state.display += "statistics.mean(["; st.rerun()
    if st_c[1].button("SUM"): st.session_state.display += "sum(["; st.rerun()
    if st.button("CLOSE ])"): st.session_state.display += "])"; st.rerun()

with t_paid:
    st.markdown(f'<div style="border:1px solid {txt}; padding:10px; border-radius:5px;">FOREX: 1 USD = {st.session_state.rates["USD"]:.2f} JPY</div>', unsafe_allow_html=True)
