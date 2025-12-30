import streamlit as st
import math
import statistics
import urllib.request
import json

# --- 1. 強制リセット & 状態管理 ---
if 'v7_visibility_fix' not in st.session_state:
    st.session_state.clear()
    st.session_state.v7_visibility_fix = True
    st.session_state.display = ""
    st.session_state.lang = "日本語"
    st.session_state.theme = "Dark"
    st.session_state.rates = {"USD": 156.4, "BTC": 13972000, "ETH": 485500}

# --- 2. 10言語定義 ---
L_MAP = {
    "日本語": {"upd": "レート更新", "thm": "表示切替", "clr": "消去", "exe": "計算実行", "si": "接頭語", "sci": "科学", "stat": "統計", "paid": "有料機能", "fuel": "ガソリン", "cur": "通貨レート", "tax": "税金計算"},
    "English": {"upd": "UPDATE", "thm": "THEME", "clr": "CLEAR", "exe": "EXEC", "si": "SI", "sci": "SCI", "stat": "STAT", "paid": "PREMIUM", "fuel": "FUEL", "cur": "FOREX", "tax": "TAX"},
    "中文": {"upd": "更新汇率", "thm": "主题", "clr": "清除", "exe": "计算", "si": "单位", "sci": "科学", "stat": "统计", "paid": "付费功能", "fuel": "汽油", "cur": "汇率", "tax": "税金"},
    "한국어": {"upd": "환율갱신", "thm": "테마", "clr": "삭제", "exe": "계산", "si": "접두어", "sci": "과학", "stat": "통계", "paid": "유료기능", "fuel": "가솔린", "cur": "환율", "tax": "세금"},
    "Español": {"upd": "ACTUALIZAR", "thm": "TEMA", "clr": "BORRAR", "exe": "IGUAL", "si": "SI", "sci": "CIEN", "stat": "ESTAD", "paid": "PAGO", "fuel": "GAS", "cur": "MONEDA", "tax": "IMPUESTO"},
    "Français": {"upd": "ACTUALISER", "thm": "THÈME", "clr": "EFFACER", "exe": "ÉGAL", "si": "SI", "sci": "SCI", "stat": "STAT", "paid": "PAYANT", "fuel": "ESSENCE", "cur": "DEVISE", "tax": "TAXE"},
    "Deutsch": {"upd": "UPDATE", "thm": "DESIGN", "clr": "LÖSCHEN", "exe": "GLEICH", "si": "SI", "sci": "WISS", "stat": "STAT", "paid": "PRO", "fuel": "SPRIT", "cur": "KURS", "tax": "STEUER"},
    "Русский": {"upd": "ОБНОВИТЬ", "thm": "ТЕМА", "clr": "СБРОС", "exe": "ИТОГ", "si": "СИ", "sci": "НАУЧ", "stat": "СТАТ", "paid": "ПЛАТНО", "fuel": "БЕНЗИН", "cur": "КУРС", "tax": "НАЛОГ"},
    "Português": {"upd": "ATUALIZAR", "thm": "TEMA", "clr": "LIMPAR", "exe": "IGUAL", "si": "SI", "sci": "CIEN", "stat": "ESTAD", "paid": "PAGO", "fuel": "GASOL", "cur": "MOEDA", "tax": "IMPOSTO"},
    "Italiano": {"upd": "AGGIORNA", "thm": "TEMA", "clr": "CANCELLA", "exe": "UGUALE", "si": "SI", "sci": "SCI", "stat": "STAT", "paid": "PRO", "fuel": "BENZINA", "cur": "VALUTA", "tax": "TASSE"}
}

SI_CONV = {
    'Q': '*1e30', 'R': '*1e27', 'Y': '*1e24', 'Z': '*1e21', 'E': '*1e18', 'P': '*1e15', 'T': '*1e12', 'G': '*1e9', 'M': '*1e6', 'k': '*1e3',
    'm': '*1e-3', 'μ': '*1e-6', 'n': '*1e-9', 'p': '*1e-12', 'f': '*1e-15', 'a': '*1e-18', 'z': '*1e-21', 'y': '*1e-24', 'r': '*1e-27', 'q': '*1e-30'
}

# --- 3. 動的ハイコントラスト・デザイン (完全上書き) ---
is_dark = st.session_state.theme == "Dark"
bg_color = "#000000" if is_dark else "#FFFFFF"
text_color = "#FFFFFF" if is_dark else "#000000"

st.markdown(f"""
<style>
    /* 1. アプリ全体の背景と文字色 */
    .stApp {{ background-color: {bg_color} !important; color: {text_color} !important; }}
    
    /* 2. 計算機ディスプレイの枠と文字 */
    .disp {{
        background-color: {bg_color} !important; 
        color: {text_color} !important;
        padding: 25px; border: 4px solid {text_color} !important;
        border-radius: 12px; font-size: 48px; text-align: right;
        font-family: 'Courier New', monospace; margin-bottom: 20px;
    }}

    /* 3. ボタンの文字色を強制固定 (重要) */
    div.stButton > button {{
        width: 100% !important;
        border: 2px solid {text_color} !important;
        background-color: {bg_color} !important;
        color: {text_color} !important; /* ここで文字色を強制 */
        font-weight: bold !important;
        font-size: 18px !important;
    }}

    /* 4. ボタンホバー時（マウスを乗せた時）の設定 */
    div.stButton > button:hover {{
        background-color: {text_color} !important;
        color: {bg_color} !important; /* 背景と文字を反転させて視認性確保 */
        border: 2px solid {text_color} !important;
    }}

    /* 5. 有料機能ボックス内の文字色を強制 */
    .paid-box {{
        border: 4px solid {text_color} !important;
        padding: 25px; border-radius: 15px;
        background-color: {bg_color} !important;
        margin-top: 10px;
    }}

    /* 6. ラベル、ラジオボタンの選択肢、入力欄の文字 */
    label, p, span, div, .stMarkdown, .stRadio, .stNumberInput, .stSelectbox, .stCaption {{
        color: {text_color} !important;
    }}
    
    /* 7. タブの文字色 */
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
    else:
        st.session_state.display += k

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
        for k, v in SI_CONV.items(): expr = expr.replace(k, v)
        st.session_state.display = format(eval(expr, {"math": math, "statistics": statistics}), '.10g')
    except: st.session_state.display = "Error"
    st.rerun()

st.divider()

# --- 8. 各種機能タブ ---
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
    sf = {"sin":"math.sin(", "cos":"math.cos(", "tan":"math.tan(", "√":"math.sqrt(", "log":"math.log10(", "(":"(", ")":")"}
    for i, (k, v) in enumerate(sf.items()):
        if sc[i%4].button(k, key=f"sc_{k}"): st.session_state.display += v; st.rerun()

with t_stat:
    st_c = st.columns(3)
    if st_c[0].button("MEAN"): st.session_state.display += "statistics.mean(["; st.rerun()
    if st_c[1].button("SUM"): st.session_state.display += "sum(["; st.rerun()
    if st.button("CLOSE ])"): st.session_state.display += "])"; st.rerun()

with t_paid:
    st.markdown(f'<div class="paid-box">', unsafe_allow_html=True)
    st.write(f"### {L['paid']}")
    mode = st.radio(f"{L['paid']} カテゴリ", [L["fuel"], L["cur"], L["tax"]], horizontal=True)
    
    st.divider()

    if mode == L["fuel"]:
        st.subheader(f"⛽ {L['fuel']}")
        lit = st.number_input("給油量 (Litre)", 1.0, 500.0, 50.0)
        p = st.selectbox("単価 (JPY/L)", [188, 169, 176])
        st.markdown(f"## 合計: **{int(lit * p):,} JPY**")
        
    elif mode == L["cur"]:
        st.subheader(f"💱 {L['cur']}")
        u = st.session_state.rates["USD"]
        amt = st.number_input("USD", 0.0, 1000000.0, 100.0)
        st.markdown(f"## **{amt * u:,.0f} JPY**")
        
    elif mode == L["tax"]:
        st.subheader(f"🧾 {L['tax']}")
        val = st.number_input("税抜金額", 0.0, 10000000.0, 10000.0)
        rate = st.radio("税率", [0.08, 0.10], horizontal=True)
        st.markdown(f"## 税込合計: **{int(val * (1+rate)):,} JPY**")
    
    st.markdown('</div>', unsafe_allow_html=True)
