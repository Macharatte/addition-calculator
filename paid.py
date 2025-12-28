import streamlit as st
import math
import statistics
import requests

# --- 1. ページ設定 ---
st.set_page_config(page_title="Python Calculator Premium", layout="centered")

# --- 2. キーボード強制無効化 JavaScript ---
st.components.v1.html("<script>const observer = new MutationObserver(() => { const inputs = window.parent.document.querySelectorAll('input[role=\"combobox\"]'); inputs.forEach(input => { input.setAttribute('readonly', 'true'); }); }); observer.observe(window.parent.document.body, { childList: true, subtree: true });</script>", height=0)

# --- 3. 全言語翻訳データ ---
LANG = {
    "JP": {"title": "Python Calculator Premium", "modes": ["通常", "科学計算", "値数", "拡縮", "有料機能"], "tax_m": "税金計算", "cur_m": "為替・貴金属", "exec": "実行", "amt": "金額/数量"},
    "EN": {"title": "Python Calculator Premium", "modes": ["Basic", "Scientific", "Stats", "SI Prefix", "Paid"], "tax_m": "Tax", "cur_m": "Currency", "exec": "Run", "amt": "Amount/Qty"},
    "ZH": {"title": "Python 计算器", "modes": ["普通", "科学", "统计", "单位", "付费"], "tax_m": "税务", "cur_m": "汇率", "exec": "计算", "amt": "金额"},
    "HI": {"title": "पायथन कैलकुलेटर", "modes": ["सामान्य", "वैज्ञानिक", "आंकड़े", "उपसर्ग", "भुगतान"], "tax_m": "कर", "cur_m": "मुद्रा", "exec": "गणना", "amt": "राशि"},
    "ES": {"title": "Calculadora Python", "modes": ["Básico", "Científico", "Estadística", "Prefijos", "Pago"], "tax_m": "Impuestos", "cur_m": "Moneda", "exec": "Calcular", "amt": "Monto"},
    "AR": {"title": "آلة حاسبة بايثون", "modes": ["أساسي", "علمي", "إحصاء", "بادئات", "مدفوع"], "tax_m": "ضريبة", "cur_m": "عملة", "exec": "احسب", "amt": "مبلغ"},
    "FR": {"title": "Calculatrice Python", "modes": ["Basique", "Scientifique", "Stats", "Préfixes", "Payant"], "tax_m": "Impôts", "cur_m": "Devise", "exec": "Calculer", "amt": "Montant"},
    "RU": {"title": "Python Калькулятор", "modes": ["Обычный", "Научный", "Стат", "Приставки", "Платное"], "tax_m": "Налоги", "cur_m": "Валюта", "exec": "Считать", "amt": "Сумма"},
    "PT": {"title": "Calculadora Python", "modes": ["Básico", "Científico", "Estatística", "Prefixos", "Pago"], "tax_m": "Impostos", "cur_m": "Moeda", "exec": "Calcular", "amt": "Quantia"}
}

# --- 4. CSS (デザイン・隙間・＋ボタン強調) ---
st.markdown("""
<style>
    .main .block-container { max-width: 100% !important; padding: 10px !important; }
    header {visibility: hidden;}
    :root { --bg: #FFF; --txt: #000; --btn-bg: #1A1A1A; --btn-txt: #FFF; }
    @media (prefers-color-scheme: dark) { :root { --bg: #000; --txt: #FFFFFF; --btn-bg: #EEE; --btn-txt: #000; } }
    .app-title-box { text-align: center; font-size: 26px; font-weight: 900; color: var(--txt); border-bottom: 3px solid var(--txt); margin-bottom: 15px; }
    .display {
        display: flex; align-items: center; justify-content: flex-end;
        font-size: 45px; font-weight: 900; margin-bottom: 10px; padding: 15px; 
        border: 4px solid var(--txt); border-radius: 12px; min-height: 110px;
        color: var(--txt); background: rgba(128,128,128,0.1); word-break: break-all;
    }
    div.stButton > button { width: 100% !important; height: 55px !important; font-weight: 900 !important; font-size: 20px !important; background-color: var(--btn-bg) !important; color: var(--btn-txt) !important; border: 1px solid var(--txt) !important; }
    /* ＋ボタンを青色で超強調 */
    div.stButton > button[key*="k_5"] { background-color: #007AFF !important; color: #FFFFFF !important; font-size: 40px !important; border: 3px solid #FFFFFF !important; }
    /* DELETEと＝の隙間をゼロにする */
    [data-testid="stHorizontalBlock"] { gap: 0px !important; }
    button[key="btn_del_main"] { background-color: #FF3B30 !important; color: white !important; height: 95px !important; border-radius: 12px 0 0 12px !important; border: none !important; margin-right: -1px !important; }
    button[key="btn_exe_main"] { background-color: #34C759 !important; color: white !important; height: 95px !important; font-size: 60px !important; border-radius: 0 12px 12px 0 !important; border: none !important; margin-left: -1px !important; }
    .tax-box { border: 4px solid var(--txt); border-radius: 12px; padding: 15px; text-align: center; font-size: 24px; font-weight: 900; color: var(--txt); }
</style>
""", unsafe_allow_html=True)

# --- 5. 状態管理の初期設定 ---
if 'f_state' not in st.session_state: st.session_state.f_state = ""
if 'm_idx' not in st.session_state: st.session_state.m_idx = 0 
if 'lang' not in st.session_state: st.session_state.lang = "JP"
if 'tax_res' not in st.session_state: st.session_state.tax_res = "0"
if 'p_sub' not in st.session_state: st.session_state.p_sub = "tax"

# 言語選択
col_l, _ = st.columns([1, 4])
with col_l:
    st.session_state.lang = st.selectbox("", list(LANG.keys()), index=list(LANG.keys()).index(st.session_state.lang), label_visibility="collapsed")

L = LANG[st.session_state.lang]

# タイトルとディスプレイ
st.markdown(f'<div class="app-title-box">{L["title"]}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="display">{st.session_state.f_state if st.session_state.f_state else "0"}</div>', unsafe_allow_html=True)

# メインキーボード
keys = ["7","8","9","π","√","+","4","5","6","e","^^","−","1","2","3","i","(-)","×","0","00",".","(",")","÷"]
cols = st.columns(6)
for i, k in enumerate(keys):
    if cols[i % 6].button(k, key=f"k_{i}"):
        st.session_state.f_state += k
        st.rerun()

# 巨大なDELETEと＝
c1, c2 = st.columns(2)
with c1:
    if st.button("DELETE", key="btn_del_main"): st.session_state.f_state = ""; st.rerun()
with c2:
    if st.button("＝", key="btn_exe_main"):
        try:
            f = st.session_state.f_state.replace('×','*').replace('÷','/').replace('−','-').replace('^^','**').replace('π','math.pi').replace('e','math.e').replace('√','math.sqrt')
            st.session_state.f_state = format(eval(f), '.10g')
        except: st.session_state.f_state = "Error"
        st.rerun()

st.divider()

# モード切替（数字インデックスで管理）
mc = st.columns(5)
for i, m_name in enumerate(L["modes"]):
    if mc[i].button(m_name, key=f"m_btn_{i}"):
        st.session_state.m_idx = i
        st.rerun()

# --- 各モードの機能詳細 ---
idx = st.session_state.m_idx

if idx == 1: # 科学計算
    sc = st.columns(4)
    s_keys = [("sin", "math.sin("), ("cos", "math.cos("), ("tan", "math.tan("), ("log", "math.log10("), ("abs", "abs("), ("sqrt", "math.sqrt("), ("π", "math.pi"), ("e", "math.e")]
    for i, (lbl, code) in enumerate(s_keys):
        if sc[i % 4].button(lbl, key=f"sci_{i}"):
            st.session_state.f_state += code; st.rerun()

elif idx == 2: # 値数 (統計)
    sc = st.columns(4)
    st_keys = [("Mean", "statistics.mean(["), ("Median", "statistics.median(["), ("Mode", "statistics.mode(["), ("Max", "max(["), ("Min", "min(["), (",", ","), ("]", "])")]
    for i, (lbl, code) in enumerate(st_keys):
        if sc[i % 4].button(lbl, key=f"st_{i}"):
            st.session_state.f_state += code; st.rerun()

elif idx == 3: # 拡縮 (SI接頭語)
    si_list = ["Q","R","Y","Z","E","P","T","G","M","k","h","da","d","c","m","μ","n","p","f","a","z","y","r","q"]
    uc = st.columns(8)
    for i, u in enumerate(si_list):
        if uc[i % 8].button(u, key=f"si_{i}"):
            st.session_state.f_state += u; st.rerun()

elif idx == 4: # 有料機能
    sub = st.columns(2)
    if sub[0].button(L["tax_m"]): st.session_state.p_sub = "tax"; st.rerun()
    if sub[1].button(L["cur_m"]): st.session_state.p_sub = "cur"; st.rerun()
    
    if st.session_state.p_sub == "tax":
        t_type = st.selectbox("Type", ["所得税(Income)", "相続税(Inheritance)", "税込10%", "税込8%"])
        amt = st.text_input(L["amt"])
        if st.button(L["exec"], key="tax_run"):
            try:
                v = float(amt) if amt else 0.0
                res = v * 1.1 if "10%" in t_type else v * 0.2
                st.session_state.tax_res = f"{format(int(res), ',')}"
            except: st.session_state.tax_res = "Error"
            st.rerun()
        st.markdown(f'<div class="tax-box">{st.session_state.tax_res}</div>', unsafe_allow_html=True)
    
    elif st.session_state.p_sub == "cur":
        c_list = ["JPY", "USD", "EUR", "XAU(Gold)"]
        c_from = st.selectbox("From", c_list)
        c_to = st.selectbox("To", c_list)
        amt_c = st.text_input(L["amt"], key="cur_amt")
        if st.button(L["exec"], key="cur_run"):
            try:
                r = requests.get("https://open.er-api.com/v6/latest/USD").json()["rates"]
                v = float(amt_c) / r[c_from[:3]] if c_from[:3] in r else float(amt_c)
                res = v * r[c_to[:3]] if c_to[:3] in r else v
                st.session_state.tax_res = f"{format(res, '.2f')} {c_to[:3]}"
            except: st.session_state.tax_res = "API Error"
            st.rerun()
        st.markdown(f'<div class="tax-box">{st.session_state.tax_res}</div>', unsafe_allow_html=True)
