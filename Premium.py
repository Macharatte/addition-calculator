import streamlit as st
import math
import statistics
import urllib.request
import json

# --- 1. ページ基本設定 ---
st.set_page_config(page_title="Global Multi-Calc 2025", layout="centered")

# --- 2. 状態管理の初期化 (絶対リセットされない書き方) ---
if 'display' not in st.session_state: st.session_state.display = ""
if 'lang' not in st.session_state: st.session_state.lang = "日本語"
if 'theme' not in st.session_state: st.session_state.theme = "Dark"
if 'rates' not in st.session_state: st.session_state.rates = {"USD": 156.40, "BTC": 13972000, "ETH": 485500}

# --- 3. 10言語辞書 (正確な翻訳) ---
LANGS = {
    "日本語": {"upd": "レート更新", "thm": "テーマ切替", "clr": "消去", "exe": "計算", "sci": "科学", "stat": "統計", "si": "接頭語", "paid": "有料", "fuel": "燃料", "cur": "為替", "cry": "仮想通貨"},
    "English": {"upd": "Update", "thm": "Theme", "clr": "Clear", "exe": "Equal", "sci": "Sci", "stat": "Stat", "si": "SI", "paid": "Paid", "fuel": "Fuel", "cur": "Cur", "cry": "Cry"},
    "中文": {"upd": "更新汇率", "thm": "切换主题", "clr": "清除", "exe": "计算", "sci": "科学", "stat": "统计", "si": "接头语", "paid": "付费", "fuel": "燃料", "cur": "货币", "cry": "加密"},
    "한국어": {"upd": "환율 갱신", "thm": "테마 변경", "clr": "삭제", "exe": "계산", "sci": "과학", "stat": "통계", "si": "접두어", "paid": "유료", "fuel": "연료", "cur": "환율", "cry": "코인"},
    "Español": {"upd": "Actualizar", "thm": "Tema", "clr": "Borrar", "exe": "Igual", "sci": "Cien", "stat": "Estad", "si": "SI", "paid": "Pago", "fuel": "Gas", "cur": "Moneda", "cry": "Cripto"},
    "Français": {"upd": "Actualiser", "thm": "Thème", "clr": "Effacer", "exe": "Egal", "sci": "Sci", "stat": "Stat", "si": "SI", "paid": "Paie", "fuel": "Carbu", "cur": "Devise", "cry": "Cryp"},
    "Deutsch": {"upd": "Update", "thm": "Design", "clr": "Löschen", "exe": "Gleich", "sci": "Wiss", "stat": "Stat", "si": "SI", "paid": "Pro", "fuel": "Sprit", "cur": "Währ", "cry": "Krypto"},
    "Русский": {"upd": "Обновить", "thm": "Тема", "clr": "Сброс", "exe": "Итог", "sci": "Науч", "stat": "Стат", "si": "СИ", "paid": "Плат", "fuel": "Топливо", "cur": "Валют", "cry": "Крипт"},
    "Português": {"upd": "Atualizar", "thm": "Tema", "clr": "Limpar", "exe": "Igual", "sci": "Cien", "stat": "Estat", "si": "SI", "paid": "Pago", "fuel": "Comb", "cur": "Moeda", "cry": "Cripto"},
    "Italiano": {"upd": "Aggiorna", "thm": "Tema", "clr": "Cancella", "exe": "Uguale", "sci": "Sci", "stat": "Stat", "si": "SI", "paid": "Pag", "fuel": "Benz", "cur": "Valuta", "cry": "Cripto"}
}

# --- 4. SI接頭語 (Q~q 全20種) ---
SI_DATA = {
    'Q': '*1e30', 'R': '*1e27', 'Y': '*1e24', 'Z': '*1e21', 'E': '*1e18', 'P': '*1e15', 'T': '*1e12', 'G': '*1e9', 'M': '*1e6', 'k': '*1e3',
    'm': '*1e-3', 'μ': '*1e-6', 'n': '*1e-9', 'p': '*1e-12', 'f': '*1e-15', 'a': '*1e-18', 'z': '*1e-21', 'y': '*1e-24', 'r': '*1e-27', 'q': '*1e-30'
}

# --- 5. インタラクション用関数 ---
def add_to_display(val): st.session_state.display += str(val)
def clear_display(): st.session_state.display = ""
def run_calc():
    try:
        expr = st.session_state.display.replace('÷','/').replace('×','*').replace('−','-')
        for k, v in SI_DATA.items(): expr = expr.replace(k, v)
        st.session_state.display = format(eval(expr, {"math": math, "statistics": statistics}), '.10g')
    except: st.session_state.display = "Error"

# --- 6. デザイン ---
is_dark = st.session_state.theme == "Dark"
bg, txt, dbg = ("#111111", "#FFFFFF", "#222222") if is_dark else ("#FFFFFF", "#000000", "#F0F0F0")
st.markdown(f"<style>.stApp {{background-color:{bg}; color:{txt};}} div.stButton > button {{width:100%; border:1px solid {txt}; background:{dbg}; color:{txt}; font-weight:bold;}}</style>", unsafe_allow_html=True)

# --- 7. メインUI ---
L = LANGS[st.session_state.lang]

c1, c2, c3 = st.columns([1.5, 1, 1])
with c1: 
    st.session_state.lang = st.selectbox("LANG", list(LANGS.keys()), index=list(LANGS.keys()).index(st.session_state.lang), label_visibility="collapsed")
with c2: 
    if st.button(L["upd"]): pass # (Fetch logic here if needed)
with c3:
    if st.button(L["thm"]): st.session_state.theme = "Light" if is_dark else "Dark"; st.rerun()

st.markdown(f"<div style='background:{dbg}; color:{txt}; padding:20px; border:2px solid {txt}; border-radius:10px; font-size:40px; text-align:right; font-family:monospace; margin-bottom:10px;'>{st.session_state.display if st.session_state.display else '0'}</div>", unsafe_allow_html=True)

# キーパッド
rows = [["7","8","9","÷"],["4","5","6","×"],["1","2","3","−"],["0",".","π","+"]]
for row in rows:
    cols = st.columns(4)
    for i, k in enumerate(row):
        if cols[i].button(k, key=f"key_{k}"): add_to_display(k); st.rerun()

c_clr, c_exe = st.columns(2)
if c_clr.button(L["clr"], on_click=clear_display): st.rerun()
if c_exe.button(L["exe"], on_click=run_calc): st.rerun()

st.divider()

# --- 8. 全機能復元タブ ---
t_sci, t_stat, t_si, t_paid = st.tabs([L["sci"], L["stat"], L["si"], L["paid"]])

with t_sci:
    sc = st.columns(4)
    sci_ops = {"sin":"math.sin(", "cos":"math.cos(", "tan":"math.tan(", "√":"math.sqrt(", "log":"math.log10(", "abs":"abs(", "(":"(", ")":")"}
    for i, (k, v) in enumerate(sci_ops.items()):
        if sc[i%4].button(k): add_to_display(v); st.rerun()

with t_stat:
    st_c = st.columns(3)
    if st_c[0].button("MEAN"): add_to_display("statistics.mean(["); st.rerun()
    if st_c[1].button("MEDIAN"): add_to_display("statistics.median(["); st.rerun()
    if st_c[2].button("SUM"): add_to_display("sum(["); st.rerun()
    if st.button("CLOSE ])"): add_to_display("])"); st.rerun()

with t_si:
    # Qからqまで全20種を5列で表示
    si_keys = list(SI_DATA.keys())
    for i in range(0, len(si_keys), 5):
        si_cols = st.columns(5)
        for j in range(5):
            if i+j < len(si_keys):
                name = si_keys[i+j]
                if si_cols[j].button(name): add_to_display(name); st.rerun()

with t_paid:
    st.markdown(f"<div style='border:1px solid {txt}; padding:15px; border-radius:10px; background:{dbg};'>", unsafe_allow_html=True)
    p_mode = st.radio("SELECT", [L["fuel"], L["cur"], L["cry"]], horizontal=True)
    if L["fuel"] in p_mode:
        loc = st.selectbox("SS", ["OME(188)", "TACHI(169)", "AVG(176)"])
        p = 188 if "OME" in loc else (169 if "TACHI" in loc else 176)
        lit = st.number_input("L", 1.0, 500.0, 50.0)
        st.write(f"**TOTAL: {int(p*lit):,} JPY**")
    elif L["cur"] in p_mode:
        u = st.session_state.rates["USD"]
        amt = st.number_input("USD", 0.0, 100000.0, 100.0)
        st.write(f"**{amt * u:,.0f} JPY**")
    elif L["cry"] in p_mode:
        coin = st.selectbox("Coin", ["BTC", "ETH"])
        hold = st.number_input("Amount", 0.0, 100.0, 0.1)
        st.write(f"**{int(hold * st.session_state.rates[coin]):,} JPY**")
    st.markdown("</div>", unsafe_allow_html=True)
