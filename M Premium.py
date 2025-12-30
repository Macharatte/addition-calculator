import streamlit as st
import math
import statistics
import urllib.request
import json

# --- 1. システム状態管理 ---
if 'display' not in st.session_state: st.session_state.display = ""
if 'lang' not in st.session_state: st.session_state.lang = "日本語"
if 'theme' not in st.session_state: st.session_state.theme = "Dark"
if 'rates' not in st.session_state:
    st.session_state.rates = {"USD": 156.0, "EUR": 168.0, "BTC": 14000000}

# --- 2. 10言語辞書定義 ---
L_MAP = {
    "日本語": {"upd": "レート更新", "thm": "モード切替", "clr": "消去", "exe": "実行", "si": "接頭語", "sci": "科学", "paid": "プロ設定", "fuel": "燃料", "cur": "通貨", "tax": "税金", "get": "表示値を反映"},
    "English": {"upd": "Update", "thm": "Theme", "clr": "CLR", "exe": "EXE", "si": "SI", "sci": "SCI", "paid": "PRO", "fuel": "Fuel", "cur": "Forex", "tax": "Tax", "get": "Get Disp"},
    "中文": {"upd": "更新", "thm": "主题", "clr": "清除", "exe": "確認", "si": "单位", "sci": "科学", "paid": "专业", "fuel": "燃料", "cur": "货币", "tax": "税收", "get": "反映数值"},
    "한국어": {"upd": "업데이트", "thm": "테마", "clr": "삭제", "exe": "실행", "si": "접두사", "sci": "과학", "paid": "프로", "fuel": "연료", "cur": "통화", "tax": "세금", "get": "수치 반영"},
    "Français": {"upd": "Actualiser", "thm": "Thème", "clr": "Effacer", "exe": "Calcul", "si": "SI", "sci": "SCI", "paid": "PRO", "fuel": "Carburant", "cur": "Devise", "tax": "Taxe", "get": "Prendre valeur"},
    "Deutsch": {"upd": "Aktualisieren", "thm": "Design", "clr": "Löschen", "exe": "Ausführen", "si": "SI", "sci": "SCI", "paid": "PRO", "fuel": "Kraftstoff", "cur": "Währung", "tax": "Steuer", "get": "Wert übernehmen"},
    "Español": {"upd": "Actualizar", "thm": "Tema", "clr": "Borrar", "exe": "Ejecutar", "si": "SI", "sci": "SCI", "paid": "PRO", "fuel": "Combustible", "cur": "Moneda", "tax": "Impuesto", "get": "Reflejar valor"},
    "Italiano": {"upd": "Aggiorna", "thm": "Tema", "clr": "Cancella", "exe": "Esegui", "si": "SI", "sci": "SCI", "paid": "PRO", "fuel": "Carburante", "cur": "Valuta", "tax": "Tasse", "get": "Rifletti valore"},
    "Русский": {"upd": "Обновить", "thm": "Тема", "clr": "Очистить", "exe": "Пуск", "si": "СИ", "sci": "Науч", "paid": "ПРО", "fuel": "Топливо", "cur": "Валюта", "tax": "Налог", "get": "Взять число"},
    "Português": {"upd": "Atualizar", "thm": "Tema", "clr": "Limpar", "exe": "Executar", "si": "SI", "sci": "SCI", "paid": "PRO", "fuel": "Combustível", "cur": "Moeda", "tax": "Imposto", "get": "Refletir valor"}
}

# --- 3. 累進課税ロジック ---
def calc_complex_tax(amount, tax_type):
    if amount <= 0: return 0, 0
    if "所得税" in tax_type:
        brackets = [(45e6,0.45,4796000),(18e6,0.40,2796000),(9e6,0.33,1536000),(6.95e6,0.23,636000),(3.3e6,0.20,427500),(1.95e6,0.10,97500),(0,0.05,0)]
    elif "法人税" in tax_type:
        return ((8e6*0.15)+(amount-8e6)*0.232, 0.232) if amount > 8e6 else (amount*0.15, 0.15)
    elif "相続税" in tax_type:
        brackets = [(600e6,0.55,72e6),(300e6,0.50,42e6),(200e6,0.45,27e6),(100e6,0.40,17e6),(50e6,0.30,7e6),(30e6,0.20,2e6),(10e6,0.15,0.5e6),(0,0.10,0)]
    else: return 0, 0
    for limit, rate, deduction in brackets:
        if amount > limit: return amount * rate - deduction, rate
    return 0, 0

# --- 4. UI設定 ---
is_dark = st.session_state.theme == "Dark"
bg_color = "#000000" if is_dark else "#FFFFFF"
text_color = "#FFFFFF" if is_dark else "#000000"
L = L_MAP[st.session_state.lang]

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg_color} !important; color: {text_color} !important; }}
    .disp {{
        background-color: {bg_color} !important; color: {text_color} !important;
        padding: 25px; border: 4px solid {text_color} !important;
        border-radius: 12px; font-size: 42px; text-align: right; margin-bottom: 20px;
    }}
    div.stButton > button {{
        width: 100% !important; border: 2px solid {text_color} !important;
        background-color: {bg_color} !important; color: {text_color} !important;
        font-weight: bold !important;
    }}
    div.stButton > button:hover {{ background-color: {text_color} !important; color: {bg_color} !important; }}
    label, p, span {{ color: {text_color} !important; font-weight: bold !important; }}
    div[data-baseweb="select"] input {{ cursor: pointer !important; caret-color: transparent !important; }}
    .result-card {{ background-color: {text_color}11 !important; padding: 20px; border-radius: 10px; border-left: 5px solid #1E88E5; margin-top: 15px; }}
</style>
""", unsafe_allow_html=True)

# --- 5. ヘッダー (言語・テーマ) ---
c1, c2, c3 = st.columns([1, 1, 1])
with c1:
    new_lang = st.selectbox("Lang", list(L_MAP.keys()), index=list(L_MAP.keys()).index(st.session_state.lang), label_visibility="collapsed")
    if new_lang != st.session_state.lang: st.session_state.lang = new_lang; st.rerun()
with c2:
    if st.button(L["upd"]):
        try:
            with urllib.request.urlopen("https://open.er-api.com/v6/latest/USD") as r:
                data = json.loads(r.read())
                for c in ["EUR", "GBP", "AUD", "CAD", "CHF", "HKD", "SGD", "NZD"]:
                    st.session_state.rates[c] = data["rates"]["JPY"] / data["rates"][c]
                st.session_state.rates["USD"] = data["rates"]["JPY"]
            st.toast("Updated")
        except: st.error("Error")
with c3:
    if st.button(L["thm"]): st.session_state.theme = "Light" if is_dark else "Dark"; st.rerun()

st.markdown(f'<div class="disp">{st.session_state.display if st.session_state.display else "0"}</div>', unsafe_allow_html=True)

# キーパッド
rows = [["7","8","9","÷"],["4","5","6","×"],["1","2","3","−"],["0",".","00","+"]]
for row in rows:
    cols = st.columns(4)
    for i, k in enumerate(row):
        if cols[i].button(k, key=f"btn_{k}"): st.session_state.display += k; st.rerun()

cl, ex = st.columns(2)
if cl.button(L["clr"]): st.session_state.display = ""; st.rerun()
if ex.button(L["exe"]):
    try:
        expr = st.session_state.display.replace("×", "*").replace("÷", "/").replace("−", "-")
        si_map = {'Q':'*1e30','R':'*1e27','Y':'*1e24','Z':'*1e21','E':'*1e18','P':'*1e15','T':'*1e12','G':'*1e9','M':'*1e6','k':'*1e3','m':'*1e-3','μ':'*1e-6','n':'*1e-9','p':'*1e-12'}
        for k, v in si_map.items(): expr = expr.replace(k, v)
        expr = expr.replace("π", str(math.pi)).replace("e", str(math.e)).replace("i", "1j")
        st.session_state.display = format(eval(expr, {"math": math}), '.10g'); st.rerun()
    except: st.session_state.display = "Error"; st.rerun()

st.divider()

# --- 6. タブ機能 ---
t_si, t_sci, t_paid = st.tabs([L["si"], L["sci"], L["paid"]])

with t_si:
    si_list = ['k','M','G','T','P','m','μ','n','p','f']
    cols = st.columns(5)
    for i, s in enumerate(si_list):
        if cols[i%5].button(s, key=f"si_{s}"): st.session_state.display += s; st.rerun()

with t_sci:
    sci_funcs = [("sin","math.sin("), ("cos","math.cos("), ("tan","math.tan("), ("√","math.sqrt("), ("log","math.log10("), ("ln","math.log("), ("π","π"), ("i","i"), ("(","("), (")",")")]
    cols = st.columns(5)
    for i, (name, val) in enumerate(sci_funcs):
        if cols[i%5].button(name, key=f"sci_{name}"): st.session_state.display += val; st.rerun()

with t_paid:
    # 修正：ラジオボタンで確実にモードを切り替え
    p_mode = st.radio("Mode", [L["fuel"], L["cur"], L["tax"]], horizontal=True, label_visibility="collapsed")
    
    # 共通：表示値の数値化
    cur_num = 0.0
    try:
        e_exp = st.session_state.display.replace("×", "*").replace("÷", "/").replace("−", "-")
        for k, v in {'k':'*1e3','M':'*1e6','G':'*1e9','T':'*1e12'}.items(): e_exp = e_exp.replace(k, v)
        cur_num = float(eval(e_exp, {"math": math}))
    except: pass

    if p_mode == L["fuel"]:
        f1, f2 = st.columns(2)
        oil = f1.selectbox("Oil", ["レギュラー", "ハイオク", "軽油", "灯油"])
        reg = f2.selectbox("Region", ["全国平均", "東京", "神奈川", "大阪", "北海道", "九州"])
        lit = st.number_input("Liters", value=50.0)
        if st.button(f"{L['get']} (L)"): st.session_state.f_lit = cur_num; st.rerun()
        u_p = {"レギュラー":170, "ハイオク":181, "軽油":149, "灯油":115}[oil] + {"全国平均":0, "東京":5, "神奈川":2, "大阪":4, "北海道":8, "九州":10}[reg]
        st.markdown(f'<div class="result-card"><h3>Total: {int(st.session_state.get("f_lit", lit) * u_p):,} JPY</h3></div>', unsafe_allow_html=True)

    elif p_mode == L["cur"]:
        cur_list = ["USD", "EUR", "GBP", "AUD", "CAD", "CHF", "CNH", "HKD", "SGD", "NZD", "BTC", "ETH"]
        target = st.selectbox("Currency", cur_list)
        amt = st.number_input("Amount", value=1.0)
        if st.button(f"{L['get']} ({target})"): st.session_state.c_amt = cur_num; st.rerun()
        rate = st.session_state.rates.get(target, 1.0)
        st.markdown(f'<div class="result-card"><h3>{st.session_state.get("c_amt", amt) * rate:,.2f} JPY</h3></div>', unsafe_allow_html=True)

    elif p_mode == L["tax"]:
        tax_target = st.selectbox("Tax Type", ["所得税 (自動累進)", "法人税 (自動累進)", "相続税 (自動累進)", "消費税 (10%)", "消費税 (8%)", "源泉徴収 (10.21%)"])
        base = st.number_input("Base Amount", value=0.0)
        if st.button(f"{L['get']} (JPY)"): st.session_state.t_base = cur_num; st.rerun()
        fb = st.session_state.get("t_base", base)
        if "自動累進" in tax_target:
            val, r = calc_complex_tax(fb, tax_target)
            st.markdown(f'<div class="result-card"><h3>Tax: {int(val):,} JPY</h3><p>Rate: {r*100:.1f}%</p></div>', unsafe_allow_html=True)
        else:
            r = 0.10 if "10%" in tax_target else 0.08 if "8%" in tax_target else 0.1021
            st.markdown(f'<div class="result-card"><h3>Total: {int(fb*(1+r)):,} JPY</h3></div>', unsafe_allow_html=True)
