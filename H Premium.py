import streamlit as st
import math
import statistics
import urllib.request
import json

# --- 1. システム状態管理 (永続化) ---
if 'display' not in st.session_state: st.session_state.display = ""
if 'lang' not in st.session_state: st.session_state.lang = "日本語"
if 'theme' not in st.session_state: st.session_state.theme = "Dark"
# 有料機能の選択状態を保持するキー
if 'paid_mode' not in st.session_state: st.session_state.paid_mode = "燃料"
if 'tax_type' not in st.session_state: st.session_state.tax_type = "消費税 (標準 10%)"
if 'tax_base' not in st.session_state: st.session_state.tax_base = 10000.0
if 'rates' not in st.session_state:
    st.session_state.rates = {
        "USD": 156.4, "EUR": 168.2, "GBP": 195.5, "AUD": 102.3, "CAD": 113.8,
        "CHF": 174.5, "CNH": 21.5, "HKD": 20.0, "SGD": 115.2, "NZD": 94.8,
        "BTC": 13972000, "ETH": 485500
    }

# --- 2. 言語定義 ---
L_MAP = {
    "日本語": {"upd": "更新", "thm": "表示切替", "clr": "消去", "exe": "実行", "si": "接頭語", "sci": "科学", "stat": "値数", "paid": "プロ", "fuel": "燃料", "cur": "通貨", "tax": "税金", "mean":"平均", "sum":"合計", "mode":"最頻", "med":"中央", "max":"最大", "min":"最小", "dev":"偏差値", "exp":"期待値"},
    "English": {"upd": "UPD", "thm": "THEME", "clr": "CLR", "exe": "EXE", "si": "SI", "sci": "SCI", "stat": "VAL", "paid": "PRO", "fuel": "FUEL", "cur": "FOREX", "tax": "TAX", "mean":"MEAN", "sum":"SUM", "mode":"MODE", "med":"MED", "max":"MAX", "min":"MIN", "dev":"T-SCR", "exp":"EXP"}
}

SI_CONV = {
    'Q': '*1e30', 'R': '*1e27', 'Y': '*1e24', 'Z': '*1e21', 'E': '*1e18', 'P': '*1e15', 'T': '*1e12', 'G': '*1e9', 'M': '*1e6', 'k': '*1e3',
    'm': '*1e-3', 'μ': '*1e-6', 'n': '*1e-9', 'p': '*1e-12', 'f': '*1e-15', 'a': '*1e-18', 'z': '*1e-21', 'y': '*1e-24', 'r': '*1e-27', 'q': '*1e-30'
}

# --- 3. UIデザイン ---
is_dark = st.session_state.theme == "Dark"
bg_color = "#000000" if is_dark else "#FFFFFF"
text_color = "#FFFFFF" if is_dark else "#000000"
accent_color = "#1E88E5"

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg_color} !important; color: {text_color} !important; }}
    .disp {{
        background-color: {bg_color} !important; color: {text_color} !important;
        padding: 25px; border: 4px solid {text_color} !important;
        border-radius: 12px; font-size: 42px; text-align: right;
        font-family: monospace; margin-bottom: 20px; min-height: 90px;
    }}
    div.stButton > button {{
        width: 100% !important; border: 2px solid {text_color} !important;
        background-color: {bg_color} !important; color: {text_color} !important;
        font-weight: bold !important;
    }}
    div.stButton > button:hover {{ background-color: {text_color} !important; color: {bg_color} !important; }}
    .result-card {{
        background-color: {text_color}11 !important; 
        padding: 20px; border-radius: 10px; border-left: 5px solid {accent_color};
        margin-top: 15px;
    }}
    label, p, span {{ color: {text_color} !important; font-weight: bold !important; }}
</style>
""", unsafe_allow_html=True)

# --- 4. メイン操作 ---
L = L_MAP.get(st.session_state.lang, L_MAP["English"])
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
            st.toast("Success")
        except: st.error("ERR")
with c3:
    if st.button(L["thm"]):
        st.session_state.theme = "Light" if is_dark else "Dark"
        st.rerun()

st.markdown(f'<div class="disp">{st.session_state.display if st.session_state.display else "0"}</div>', unsafe_allow_html=True)

# --- 5. キーパッド ---
rows = [["7","8","9","÷"],["4","5","6","×"],["1","2","3","−"],["0",".","00","+"]]
for row in rows:
    cols = st.columns(4)
    for i, k in enumerate(row):
        if cols[i].button(k, key=f"k_{k}"): st.session_state.display += k; st.rerun()

cl, ex = st.columns(2)
if cl.button(L["clr"]): st.session_state.display = ""; st.rerun()
if ex.button(L["exe"]):
    try:
        expr = st.session_state.display.replace("×", "*").replace("÷", "/").replace("−", "-")
        expr = expr.replace("e", str(math.e)).replace("i", "1j").replace("π", str(math.pi))
        for k, v in SI_CONV.items(): expr = expr.replace(k, v)
        res = eval(expr, {"math": math, "statistics": statistics})
        st.session_state.display = format(res, '.10g') if not isinstance(res, (complex, list)) else str(res)
    except: st.session_state.display = "Error"
    st.rerun()

st.divider()

# --- 6. タブ機能 ---
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
    sc_list = [("sin","math.sin("), ("cos","math.cos("), ("tan","math.tan("), ("√","math.sqrt("), 
               ("log","math.log10("), ("π","π"), ("i","i"), ("e","e"), ("(",")")]
    for i in range(0, len(sc_list), 3):
        cols = st.columns(3)
        for j in range(3):
            if i+j < len(sc_list):
                name, val = sc_list[i+j]
                if cols[j].button(name, key=f"sci_{name}"): st.session_state.display += val; st.rerun()

with t_stat:
    r1 = st.columns(3)
    if r1[0].button(L["mean"]): st.session_state.display += "statistics.mean(["; st.rerun()
    if r1[1].button(L["med"]): st.session_state.display += "statistics.median(["; st.rerun()
    if r1[2].button(L["mode"]): st.session_state.display += "statistics.mode(["; st.rerun()
    if st.button(L["dev"]): st.session_state.display += "[(x-statistics.mean(d))/statistics.stdev(d)*10+50 for d in [["; st.rerun()
    if st.button("CLOSE ])"): st.session_state.display += "])"; st.rerun()

# --- 7. プロ機能 (状態保持版) ---
with t_paid:
    # 状態保持
    st.session_state.paid_mode = st.radio("FUNC", [L["fuel"], L["cur"], L["tax"]], 
                                         index=[L["fuel"], L["cur"], L["tax"]].index(st.session_state.paid_mode),
                                         horizontal=True, label_visibility="collapsed")
    
    if st.session_state.paid_mode == L["fuel"]:
        f_col1, f_col2 = st.columns(2)
        oil_dict = {"レギュラー": 170, "ハイオク": 181, "軽油": 149, "灯油": 115, "重油": 95, "ナフサ": 75, "アスファルト": 85}
        reg_dict = {"全国平均": 0, "東京": 5, "神奈川": 2, "大阪": 4, "北海道": 8, "九州": 10}
        f_type = f_col1.selectbox("油種", list(oil_dict.keys()))
        reg = f_col2.selectbox("地方", list(reg_dict.keys()))
        lit = st.number_input("数量 (L)", 1.0, 1000.0, 50.0, step=1.0)
        u_p = oil_dict[f_type] + reg_dict[reg]
        st.markdown(f'<div class="result-card"><h3>合計: {int(lit * u_p):,} JPY</h3><p>単価: {u_p}円/L</p></div>', unsafe_allow_html=True)

    elif st.session_state.paid_mode == L["cur"]:
        cur_list = ["USD", "EUR", "GBP", "AUD", "CAD", "CHF", "CNH", "HKD", "SGD", "NZD", "BTC", "ETH"]
        c_target = st.selectbox("通貨", cur_list)
        amt = st.number_input("変換元の数量", 0.0, 1000000.0, 1.0, step=0.1)
        rate = st.session_state.rates.get(c_target, 1.0)
        st.markdown(f'<div class="result-card"><h3>結果: {amt * rate:,.2f} JPY</h3><p>1 {c_target} = {rate:,.2f}円</p></div>', unsafe_allow_html=True)

    elif st.session_state.paid_mode == L["tax"]:
        jp_taxes = {
            "消費税 (標準 10%)": 0.10, "消費税 (軽減 8%)": 0.08,
            "所得税 (目安 20%)": 0.20, "所得税 (高所得 45%)": 0.45,
            "法人税 (普通 23.2%)": 0.232, "法人税 (中小 15%)": 0.15,
            "固定資産税 (標準 1.4%)": 0.014,
            "相続税 (最高 55%)": 0.55, "相続税 (最低 10%)": 0.10,
            "源泉徴収 (10.21%)": 0.1021, "投資 (20.315%)": 0.20315
        }
        # 状態保持のためにindexを計算
        current_tax_list = list(jp_taxes.keys()) + ["カスタム入力"]
        if st.session_state.tax_type not in current_tax_list: st.session_state.tax_type = current_tax_list[0]
        
        st.session_state.tax_type = st.selectbox("日本の税目・税率", current_tax_list, 
                                                index=current_tax_list.index(st.session_state.tax_type))
        
        st.session_state.tax_base = st.number_input("金額 (ベース)", 0.0, 10000000.0, st.session_state.tax_base, step=100.0)
        
        t_rate = jp_taxes[st.session_state.tax_type] if st.session_state.tax_type != "カスタム入力" else st.slider("カスタム (%)", 0.0, 60.0, 15.0) / 100
            
        st.markdown(f"""
        <div class="result-card">
            <h3>計算結果: {int(st.session_state.tax_base * (1+t_rate)):,} JPY</h3>
            <p>対象額: {st.session_state.tax_base:,.0f}円 / 税額・徴収額: {int(st.session_state.tax_base * t_rate):,}円 ({t_rate*100:.3f}%)</p>
        </div>
        """, unsafe_allow_html=True)
