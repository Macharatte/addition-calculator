import streamlit as st
import math
import statistics
import urllib.request
import json

# --- 1. ページ基本設定 ---
st.set_page_config(page_title="Ultimate Pro Calc 2025", layout="centered")

# --- 2. 状態管理（Session State）の強制定義 ---
if 'display' not in st.session_state: st.session_state.display = ""
if 'lang_key' not in st.session_state: st.session_state.lang_key = "日本語"
if 'theme' not in st.session_state: st.session_state.theme = "Dark"
if 'rates' not in st.session_state: st.session_state.rates = {"USD": 156.40, "BTC": 13972000, "ETH": 485500}

# --- 3. 主要10言語の完全定義 ---
LANGS = {
    "日本語": {"upd": "レート更新", "thm": "表示切替", "clr": "消去", "exe": "計算実行", "sci": "科学", "stat": "統計", "si": "単位", "paid": "有料"},
    "English": {"upd": "UPDATE RATES", "thm": "THEME", "clr": "CLEAR", "exe": "EXECUTE", "sci": "SCI", "stat": "STAT", "si": "SI", "paid": "PAID"},
    "中文": {"upd": "更新汇率", "thm": "切换主题", "clr": "清除", "exe": "计算", "sci": "科学", "stat": "统计", "si": "单位", "paid": "付费"},
    "한국어": {"upd": "환율 갱신", "thm": "테마 변경", "clr": "삭제", "exe": "계산", "sci": "과학", "stat": "통계", "si": "접두어", "paid": "유료"},
    "Español": {"upd": "ACTUALIZAR", "thm": "TEMA", "clr": "BORRAR", "exe": "IGUAL", "sci": "CIEN", "stat": "ESTAD", "si": "SI", "paid": "PAGO"},
    "Français": {"upd": "ACTUALISER", "thm": "THÈME", "clr": "EFFACER", "exe": "ÉGAL", "sci": "SCI", "stat": "STAT", "si": "SI", "paid": "PAYANT"},
    "Deutsch": {"upd": "UPDATE", "thm": "DESIGN", "clr": "LÖSCHEN", "exe": "GLEICH", "sci": "WISS", "stat": "STAT", "si": "SI", "paid": "PRO"},
    "Русский": {"upd": "ОБНОВИТЬ", "thm": "ТЕМА", "clr": "СБРОС", "exe": "ИТОГ", "sci": "НАУЧ", "stat": "СТАТ", "si": "СИ", "paid": "ПЛАТНО"},
    "Português": {"upd": "ATUALIZAR", "thm": "TEMA", "clr": "LIMPAR", "exe": "IGUAL", "sci": "CIEN", "stat": "ESTAD", "si": "SI", "paid": "PAGO"},
    "Italiano": {"upd": "AGGIORNA", "thm": "TEMA", "clr": "CANCELLA", "exe": "UGUALE", "sci": "SCI", "stat": "STAT", "si": "SI", "paid": "PRO"}
}

# --- 4. SI接頭語（Q〜q 全20種）の定義 ---
SI_MAP = {
    'Q': '*1e30', 'R': '*1e27', 'Y': '*1e24', 'Z': '*1e21', 'E': '*1e18', 'P': '*1e15', 'T': '*1e12', 'G': '*1e9', 'M': '*1e6', 'k': '*1e3',
    'm': '*1e-3', 'μ': '*1e-6', 'n': '*1e-9', 'p': '*1e-12', 'f': '*1e-15', 'a': '*1e-18', 'z': '*1e-21', 'y': '*1e-24', 'r': '*1e-27', 'q': '*1e-30'
}

# --- 5. デザイン (CSS) ---
is_dark = st.session_state.theme == "Dark"
bg, txt, dbg = ("#0F0F0F", "#FFFFFF", "#252525") if is_dark else ("#FFFFFF", "#000000", "#F0F2F6")
st.markdown(f"""<style>
    .stApp {{background-color: {bg}; color: {txt};}}
    .calc-disp {{background-color: {dbg}; color: {txt}; padding: 25px; border: 2px solid {txt}; border-radius: 8px; font-size: 35px; text-align: right; font-family: monospace; margin: 10px 0;}}
    div.stButton > button {{width: 100%; border: 1px solid {txt}; font-weight: bold; height: 50px; background: {dbg}; color: {txt};}}
</style>""", unsafe_allow_html=True)

# --- 6. トップナビゲーション（言語とUPDATEを隣同士に） ---
L = LANGS[st.session_state.lang_key]

top_c1, top_c2, top_c3 = st.columns([1, 1, 1])
with top_c1:
    # 言語選択をUPDATEの隣に配置
    new_lang = st.selectbox("LANG", list(LANGS.keys()), index=list(LANGS.keys()).index(st.session_state.lang_key), label_visibility="collapsed")
    if new_lang != st.session_state.lang_key:
        st.session_state.lang_key = new_lang
        st.rerun()
with top_c2:
    if st.button(L["upd"]):
        try:
            with urllib.request.urlopen("https://open.er-api.com/v6/latest/USD") as r:
                st.session_state.rates["USD"] = json.loads(r.read())["rates"]["JPY"]
            st.toast("RATES UPDATED")
        except: st.error("ERR")
with top_c3:
    if st.button(L["thm"]):
        st.session_state.theme = "Light" if is_dark else "Dark"; st.rerun()

# --- 7. メインディスプレイ ---
st.markdown(f'<div class="calc-disp">{st.session_state.display if st.session_state.display else "0"}</div>', unsafe_allow_html=True)

# --- 8. 基本キーパッド ---
keys = [["7","8","9","÷"],["4","5","6","×"],["1","2","3","−"],["0",".","π","+"]]
ops = {"÷": "/", "×": "*", "−": "-"}
for row in keys:
    cols = st.columns(4)
    for i, k in enumerate(row):
        if cols[i].button(k):
            st.session_state.display += ops.get(k, k); st.rerun()

c_clr, c_exe = st.columns(2)
if c_clr.button(L["clr"]): st.session_state.display = ""; st.rerun()
if c_exe.button(L["exe"]):
    try:
        expr = st.session_state.display
        for k, v in SI_MAP.items(): expr = expr.replace(k, v)
        st.session_state.display = str(eval(expr, {"math": math, "statistics": statistics}))
    except: st.session_state.display = "Error"
    st.rerun()

st.divider()

# --- 9. 全20種のSI接頭語・科学・統計タブ ---
tabs = st.tabs([L["si"], L["sci"], L["stat"], L["paid"]])

with tabs[0]: # 接頭語 Q〜q (全20種)
    st.caption("SI Prefixes: Quetta (10^30) to Quecto (10^-30)")
    si_keys = list(SI_MAP.keys())
    for i in range(0, len(si_keys), 5):
        cols = st.columns(5)
        for j in range(5):
            if i+j < len(si_keys):
                p = si_keys[i+j]
                if cols[j].button(p, key=f"si_btn_{p}"):
                    st.session_state.display += p; st.rerun()

with tabs[1]: # 科学計算
    sc = st.columns(4)
    sf = {"sin":"math.sin(", "cos":"math.cos(", "tan":"math.tan(", "√":"math.sqrt(", "log":"math.log10(", "abs":"abs(", "(":"(", ")":")"}
    for i, (k, v) in enumerate(sf.items()):
        if sc[i%4].button(k): st.session_state.display += v; st.rerun()

with tabs[2]: # 統計
    st_c = st.columns(3)
    if st_c[0].button("MEAN"): st.session_state.display += "statistics.mean(["; st.rerun()
    if st_c[1].button("MEDIAN"): st.session_state.display += "statistics.median(["; st.rerun()
    if st_c[2].button("SUM"): st.session_state.display += "sum(["; st.rerun()
    if st.button("CLOSE ])"): st.session_state.display += "])"; st.rerun()

with tabs[3]: # 有料機能
    st.markdown(f'<div style="border:1px solid {txt}; padding:15px; border-radius:8px;">', unsafe_allow_html=True)
    m = st.radio("SELECT", ["FUEL", "FOREX", "CRYPTO"], horizontal=True)
    if m == "FUEL":
        lit = st.number_input("Litres", 1.0, 500.0, 50.0)
        st.info(f"AVG TOTAL: {int(176*lit):,} JPY")
    elif m == "FOREX":
        v = st.number_input("USD", 0.0, 100000.0, 100.0)
        st.info(f"{v * st.session_state.rates['USD']:,.0f} JPY")
    elif m == "CRYPTO":
        coin = st.selectbox("Coin", ["BTC", "ETH"])
        h = st.number_input("Amount", 0.0, 100.0, 0.1)
        st.info(f"{int(h * st.session_state.rates[coin]):,} JPY")
    st.markdown('</div>', unsafe_allow_html=True)
