import streamlit as st
import math
import statistics
import urllib.request
import json

# --- 1. 強制リセット (新しいURL/ファイル名でも確実にクリーンな状態にする) ---
if 'enforce_v4_update' not in st.session_state:
    st.session_state.clear()
    st.session_state.enforce_v4_update = True
    st.session_state.display = ""
    st.session_state.lang = "日本語"
    st.session_state.theme = "Dark"
    st.session_state.rates = {"USD": 156.4, "BTC": 13972000, "ETH": 485500}

# --- 2. 10言語完全定義 ---
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

# --- 3. デザイン設定 ---
is_dark = st.session_state.theme == "Dark"
bg, txt, dbg = ("#000000", "#FFFFFF", "#151515") if is_dark else ("#FFFFFF", "#000000", "#F0F2F6")
st.markdown(f"""<style>
    .stApp {{background-color:{bg}; color:{txt};}}
    .disp {{background:{dbg}; color:{txt}; padding:25px; border:3px solid {txt}; border-radius:10px; font-size:45px; text-align:right; font-family:monospace; margin-bottom:10px; overflow-x: auto;}}
    div.stButton > button {{width:100%; border:1px solid {txt}; height:50px; background:{dbg}; color:{txt}; font-weight:bold;}}
    .paid-box {{border:2px solid {txt}; padding:20px; border-radius:10px; background:{dbg}; margin-top:10px;}}
</style>""", unsafe_allow_html=True)

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

# --- 5. 演算子制御ロジック ---
def input_key(k):
    curr = st.session_state.display
    ops = ["+", "−", "×", "÷"]
    # 式頭の演算子防止
    if curr == "" and k in ops: return
    # 演算子の連続を置換（最新を優先）
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
    st.markdown('<div class="paid-box">', unsafe_allow_html=True)
    mode = st.radio("SELECT", [L["fuel"], L["cur"], L["tax"]], horizontal=True)
    
    if mode == L["fuel"]:
        st.subheader(L["fuel"])
        lit = st.number_input("Litre (L)", 1.0, 500.0, 50.0)
        p = st.selectbox("JPY/L", [188, 169, 176])
        st.info(f"Total: {int(lit * p):,} JPY")
    elif mode == L["cur"]:
        st.subheader(L["cur"])
        u = st.session_state.rates["USD"]
        amt = st.number_input("USD", 0.0, 1000000.0, 100.0)
        st.success(f"{amt * u:,.0f} JPY (1USD={u:.2f}JPY)")
    elif mode == L["tax"]:
        st.subheader(L["tax"])
        val = st.number_input("Amount", 0.0, 10000000.0, 10000.0)
        rate = st.radio("Rate", [0.08, 0.10], horizontal=True)
        st.warning(f"Incl. Tax: {int(val * (1+rate)):,} JPY")
    st.markdown('</div>', unsafe_allow_html=True)
