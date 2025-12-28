import streamlit as st
import math
import statistics
import requests

# --- ページ設定 ---
st.set_page_config(page_title="Python Calculator Premium", layout="centered")

# --- キーボード強制無効化 ---
st.components.v1.html("<script>const observer = new MutationObserver(() => { const inputs = window.parent.document.querySelectorAll('input[role=\"combobox\"]'); inputs.forEach(input => { input.setAttribute('readonly', 'true'); }); }); observer.observe(window.parent.document.body, { childList: true, subtree: true });</script>", height=0)

# --- 全言語リソース ---
LANG = {
    "JP": {"title": "Python Calculator Premium", "modes": ["通常", "科学計算", "値数", "拡縮", "有料機能"], "tax_menu": "税金計算メニュー", "curr_menu": "為替・貴金属メニュー", "exec": "計算実行", "amount": "金額入力"},
    "EN": {"title": "Python Calculator Premium", "modes": ["Basic", "Scientific", "Stats", "SI Prefix", "Paid Features"], "tax_menu": "Tax Menu", "curr_menu": "Currency Menu", "exec": "Calculate", "amount": "Amount"},
    "ZH": {"title": "Python 计算器", "modes": ["普通", "科学", "统计", "单位", "付费功能"], "tax_menu": "税务", "curr_menu": "汇率", "exec": "计算", "amount": "金额"},
    "HI": {"title": "पायथन कैलकुलेटर", "modes": ["सामान्य", "वैज्ञानिक", "आंकड़े", "उपसर्ग", "भुगतान"], "tax_menu": "कर", "curr_menu": "मुद्रा", "exec": "गणना", "amount": "राशि"},
    "ES": {"title": "Calculadora Python", "modes": ["Básico", "Científico", "Estadística", "Prefijos", "Pago"], "tax_menu": "Impuestos", "curr_menu": "Moneda", "exec": "Calcular", "amount": "Monto"},
    "AR": {"title": "آلة حاسبة بايثون", "modes": ["أساسي", "علمي", "إحصاء", "بادئات", "مدفوع"], "tax_menu": "ضريبة", "curr_menu": "عملة", "exec": "احسب", "amount": "مبلغ"},
    "FR": {"title": "Calculatrice Python", "modes": ["Basique", "Scientifique", "Stats", "Préfixes", "Payant"], "tax_menu": "Impôts", "curr_menu": "Devise", "exec": "Calculer", "amount": "Montant"},
    "RU": {"title": "Python Калькулятор", "modes": ["Обычный", "Научный", "Стат", "Приставки", "Платное"], "tax_menu": "Налоги", "curr_menu": "Валюта", "exec": "Считать", "amount": "Сумма"},
    "PT": {"title": "Calculadora Python", "modes": ["Básico", "Científico", "Estatística", "Prefixos", "Pago"], "tax_menu": "Impostos", "curr_menu": "Moeda", "exec": "Calcular", "amount": "Quantia"}
}

# --- CSS設定 ---
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
    /* ＋ボタン強調 */
    div.stButton > button[key*="k_5"] { background-color: #007AFF !important; color: #FFFFFF !important; font-size: 40px !important; border: 3px solid #FFFFFF !important; }
    /* 隙間抹殺 */
    [data-testid="stHorizontalBlock"] { gap: 0px !important; }
    button[key="btn_del_main"] { background-color: #FF3B30 !important; color: white !important; height: 95px !important; border-radius: 12px 0 0 12px !important; border: none !important; margin-right: -1px !important; }
    button[key="btn_exe_main"] { background-color: #34C759 !important; color: white !important; height: 95px !important; font-size: 60px !important; border-radius: 0 12px 12px 0 !important; border: none !important; margin-left: -1px !important; }
    .tax-box { border: 4px solid var(--txt); border-radius: 12px; padding: 15px; text-align: center; font-size: 24px; font-weight: 900; color: var(--txt); }
</style>
""", unsafe_allow_html=True)

# --- 状態管理の初期化 ---
if 'f_state' not in st.session_state: st.session_state.f_state = ""
if 'm_idx' not in st.session_state: st.session_state.m_idx = 0 # 0:通常, 1:科学, 2:値数, 3:拡縮, 4:有料
if 'lang' not in st.session_state: st.session_state.lang = "JP"
if 'tax_res' not in st.session_state: st.session_state.tax_res = "Result"
if 'paid_sub' not in st.session_state: st.session_state.paid_sub = "tax"

# --- 言語選択 ---
col_lang, _ = st.columns([1, 4])
with col_lang:
    st.session_state.lang = st.selectbox("", list(LANG.keys()), index=list(LANG.keys()).index(st.session_state.lang), label_visibility="collapsed")

L = LANG[st.session_state.lang]

# --- メイン画面表示 ---
st.markdown(f'<div class="app-title-box">{L["title"]}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="display">{st.session_state.f_state if st.session_state.f_state else "0"}</div>', unsafe_allow_html=True)

# 電卓キーボード (24キー)
keys = ["7","8","9","π","√","+","4","5","6","e","^^","−","1","2","3","i","(-)","×","0","00",".","(",")","÷"]
cols = st.columns(6)
for i, k in enumerate(keys):
    if cols[i % 6].button(k, key=f"k_{i}"):
        st.session_state.f_state += k
        st.rerun()

# DELETE & ＝
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

# --- モード選択 (インデックス管理で言語不問) ---
mc = st.columns(5)
for i, m_name in enumerate(L["modes"]):
    if mc[i].button(m_name, key=f"m_btn_{i}"):
        st.session_state.m_idx = i
        st.rerun()

# --- 各モードの機能展開 ---
m_idx = st.session_state.m_idx

if m_idx == 1: # 科学計算
    sc = st.columns(4)
    s_keys = ["math.sin(", "math.cos(", "math.tan(", "math.log(", "abs(", "math.sqrt(", "math.pi", "math.e"]
    for i, s in enumerate(s_keys):
        if sc[i % 4].button(s.replace('math.',''), key=f"sci_{i}"):
            st.session_state.f_state += s; st.rerun()

elif m_idx == 2: # 値数
    sc = st.columns(4)
    stat_keys = [("Mean", "statistics.mean(["), ("Median", "statistics.median(["), ("Max", "max(["), ("Min", "min(["), (",", ","), ("]", "])")]
    for i, (label, code) in enumerate(stat_keys):
        if sc[i % 4].button(label, key=f"stat_{i}"):
            st.session_state.f_state += code; st.rerun()

elif m_idx == 3: # 拡縮 (SI接頭語)
    si_list = ["Q","R","Y","Z","E","P","T","G","M","k","h","da","d","c","m","μ","n","p","f","a","z","y","r","q"]
    uc = st.columns(8)
    for i, u in enumerate(si_list):
        if uc[i % 8].button(u, key=f"si_{i}"):
            st.session_state.f_state += u; st.rerun()

elif m_idx == 4: # 有料機能
    sub = st.columns(2)
    if sub[0].button(L["tax_menu"]): st.session_state.paid_sub = "tax"; st.rerun()
    if sub[1].button(L["curr_menu"]): st.session_state.paid_sub = "curr"; st.rerun()
    
    if st.session_state.paid_sub == "tax":
        tax_type = st.selectbox("Type", ["Income Tax", "Inheritance Tax", "Consumption 10%"])
        ti = st.text_input(L["amount"])
        if st.button(L["exec"]):
            try:
                val = float(ti) if ti else 0.0
                res = val * 1.1 if "10%" in tax_type else val * 0.2
                st.session_state.tax_res = f"Result: {format(int(res), ',')}"
            except: st.session_state.tax_res = "Error"
            st.rerun()
        st.markdown(f'<div class="tax-box">{st.session_state.tax_res}</div>', unsafe_allow_html=True)
