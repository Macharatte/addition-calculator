import streamlit as st
import math
import statistics
import urllib.request
import json

# ==========================================
# 強制リフレッシュ用バージョン管理 (v2025_Final)
# ==========================================
if 'app_version' not in st.session_state or st.session_state.app_version != "3.0":
    st.session_state.clear()
    st.session_state.app_version = "3.0"
    st.session_state.display = ""
    st.session_state.lang = "日本語"
    st.session_state.theme = "Dark"
    st.session_state.rates = {"USD": 156.4, "BTC": 13972000, "ETH": 485500}

# --- 10言語の完全定義辞書 ---
L_MAP = {
    "日本語": {"upd": "レート更新", "thm": "テーマ", "clr": "消去", "exe": "計算実行", "si": "接頭語", "sci": "科学", "stat": "統計", "paid": "有料"},
    "English": {"upd": "UPDATE", "thm": "THEME", "clr": "CLEAR", "exe": "EXECUTE", "si": "SI UNITS", "sci": "SCI", "stat": "STAT", "paid": "PAID"},
    "中文": {"upd": "更新汇率", "thm": "主题", "clr": "清除", "exe": "计算", "si": "单位", "sci": "科学", "stat": "统计", "paid": "付费"},
    "한국어": {"upd": "환율갱신", "thm": "테마", "clr": "삭제", "exe": "계산", "si": "접두어", "sci": "과학", "stat": "통계", "paid": "유료"},
    "Español": {"upd": "ACTUALIZAR", "thm": "TEMA", "clr": "BORRAR", "exe": "IGUAL", "si": "SI", "sci": "CIEN", "stat": "ESTAD", "paid": "PAGO"},
    "Français": {"upd": "ACTUALISER", "thm": "THÈME", "clr": "EFFACER", "exe": "ÉGAL", "si": "SI", "sci": "SCI", "stat": "STAT", "paid": "PAYANT"},
    "Deutsch": {"upd": "UPDATE", "thm": "DESIGN", "clr": "LÖSCHEN", "exe": "GLEICH", "si": "SI", "sci": "WISS", "stat": "STAT", "paid": "PRO"},
    "Русский": {"upd": "ОБНОВИТЬ", "thm": "ТЕМА", "clr": "СБРОС", "exe": "ИТОГ", "si": "СИ", "sci": "НАУЧ", "stat": "СТАТ", "paid": "ПЛАТНО"},
    "Português": {"upd": "ATUALIZAR", "thm": "TEMA", "clr": "LIMPAR", "exe": "IGUAL", "si": "SI", "sci": "CIEN", "stat": "ESTAD", "paid": "PAGO"},
    "Italiano": {"upd": "AGGIORNA", "thm": "TEMA", "clr": "CANCELLA", "exe": "UGUALE", "si": "SI", "sci": "SCI", "stat": "STAT", "paid": "PRO"}
}

# --- SI接頭語（Q〜q 全20種）の完全定義 ---
SI_CONV = {
    'Q': '*1e30', 'R': '*1e27', 'Y': '*1e24', 'Z': '*1e21', 'E': '*1e18', 'P': '*1e15', 'T': '*1e12', 'G': '*1e9', 'M': '*1e6', 'k': '*1e3',
    'm': '*1e-3', 'μ': '*1e-6', 'n': '*1e-9', 'p': '*1e-12', 'f': '*1e-15', 'a': '*1e-18', 'z': '*1e-21', 'y': '*1e-24', 'r': '*1e-27', 'q': '*1e-30'
}

# --- デザイン ---
is_dark = st.session_state.theme == "Dark"
bg, txt, dbg = ("#000000", "#FFFFFF", "#111111") if is_dark else ("#FFFFFF", "#000000", "#F0F2F6")
st.markdown(f"<style>.stApp {{background-color:{bg}; color:{txt};}} .disp {{background:{dbg}; color:{txt}; padding:20px; border:3px solid {txt}; border-radius:10px; font-size:45px; text-align:right; font-family:monospace; margin-bottom:10px;}} div.stButton > button {{width:100%; border:1px solid {txt}; height:50px; background:{dbg}; color:{txt}; font-weight:bold;}}</style>", unsafe_allow_html=True)

# --- 1. トップナビ (言語と言語更新を隣同士に配置) ---
L = L_MAP[st.session_state.lang]
c1, c2, c3 = st.columns([1, 1, 1])
with c1:
    new_lang = st.selectbox("LANG_SEL", list(L_MAP.keys()), index=list(L_MAP.keys()).index(st.session_state.lang), label_visibility="collapsed")
    if new_lang != st.session_state.lang:
        st.session_state.lang = new_lang
        st.rerun()
with c2:
    if st.button(L["upd"]):
        try:
            with urllib.request.urlopen("https://open.er-api.com/v6/latest/USD") as r:
                st.session_state.rates["USD"] = json.loads(r.read())["rates"]["JPY"]
            st.toast("Updated!")
        except: st.error("Error")
with c3:
    if st.button(L["thm"]):
        st.session_state.theme = "Light" if is_dark else "Dark"; st.rerun()

# --- 2. ディスプレイ ---
st.markdown(f'<div class="disp">{st.session_state.display if st.session_state.display else "0"}</div>', unsafe_allow_html=True)

# --- 3. メインキーパッド ---
for row in [["7","8","9","÷"],["4","5","6","×"],["1","2","3","−"],["0",".","π","+"]]:
    cols = st.columns(4)
    for i, k in enumerate(row):
        if cols[i].button(k, key=f"main_{k}"):
            st.session_state.display += {"÷":"/","×":"*","−":"-"}.get(k, k); st.rerun()

c_clr, c_exe = st.columns(2)
if c_clr.button(L["clr"]): st.session_state.display = ""; st.rerun()
if c_exe.button(L["exe"]):
    try:
        expr = st.session_state.display
        for k, v in SI_CONV.items(): expr = expr.replace(k, v)
        st.session_state.display = format(eval(expr, {"math": math, "statistics": statistics}), '.10g')
    except: st.session_state.display = "Error"
    st.rerun()

st.divider()

# --- 4. SI接頭語(全20種)・科学・統計タブ ---
t_si, t_sci, t_stat, t_paid = st.tabs([L["si"], L["sci"], L["stat"], L["paid"]])

with t_si: # 20種類の接頭語
    st.write("Metric Prefixes: Q (10^30) to q (10^-30)")
    
    si_keys = list(SI_CONV.keys())
    for i in range(0, len(si_keys), 5):
        cols = st.columns(5)
        for j in range(5):
            if i+j < len(si_keys):
                p = si_keys[i+j]
                if cols[j].button(p, key=f"si_{p}"):
                    st.session_state.display += p; st.rerun()

with t_sci:
    sc = st.columns(4)
    ops = {"sin":"math.sin(", "cos":"math.cos(", "tan":"math.tan(", "√":"math.sqrt(", "log":"math.log10(", "(":"(", ")":")"}
    for i, (k, v) in enumerate(ops.items()):
        if sc[i%4].button(k, key=f"sci_{k}"): st.session_state.display += v; st.rerun()

with t_stat:
    st_c = st.columns(3)
    if st_c[0].button("MEAN"): st.session_state.display += "statistics.mean(["; st.rerun()
    if st_c[1].button("MEDIAN"): st.session_state.display += "statistics.median(["; st.rerun()
    if st_c[2].button("SUM"): st.session_state.display += "sum(["; st.rerun()
    if st.button("CLOSE ])"): st.session_state.display += "])"; st.rerun()

with t_paid:
    st.markdown(f'<div style="border:2px solid {txt}; padding:15px; border-radius:10px; background:{dbg};">', unsafe_allow_html=True)
    st.write(f"USD/JPY: {st.session_state.rates['USD']:.2f}")
    st.write(f"BTC/JPY: {st.session_state.rates['BTC']:,}")
    st.markdown('</div>', unsafe_allow_html=True)
