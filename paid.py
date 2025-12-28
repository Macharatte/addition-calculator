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
    "JP": {"title": "Python Calculator Premium", "modes": ["通常", "科学計算", "値数", "拡縮", "有料機能"], "tax_menu": "税金計算メニュー", "curr_menu": "為替・貴金属メニュー", "res": "結果表示", "exec": "計算実行", "amount": "金額入力"},
    "EN": {"title": "Python Calculator Premium", "modes": ["Basic", "Scientific", "Stats", "SI Prefix", "Paid Features"], "tax_menu": "Tax Menu", "curr_menu": "Currency Menu", "res": "Result", "exec": "Calculate", "amount": "Amount"},
    "ZH": {"title": "Python 计算器", "modes": ["普通", "科学", "统计", "单位", "付费功能"], "tax_menu": "税务", "curr_menu": "汇率汇率", "res": "结果", "exec": "计算", "amount": "金额"},
    "HI": {"title": "पायथन कैलकुलेटर", "modes": ["सामान्य", "वैज्ञानिक", "आंकड़े", "उपसर्ग", "भुगतान"], "tax_menu": "कर", "curr_menu": "मुद्रा", "res": "परिणाम", "exec": "गणना", "amount": "राशि"},
    "ES": {"title": "Calculadora Python", "modes": ["Básico", "Científico", "Estadística", "Prefijos", "Pago"], "tax_menu": "Impuestos", "curr_menu": "Moneda", "res": "Resultado", "exec": "Calcular", "amount": "Monto"},
    "AR": {"title": "آلة حاسبة بايثون", "modes": ["أساسي", "علمي", "إحصاء", "بادئات", "مدفوع"], "tax_menu": "ضريبة", "curr_menu": "عملة", "res": "نتيجة", "exec": "احسب", "amount": "مبلغ"},
    "FR": {"title": "Calculatrice Python", "modes": ["Basique", "Scientifique", "Stats", "Préfixes", "Payant"], "tax_menu": "Impôts", "curr_menu": "Devise", "res": "Résultat", "exec": "Calculer", "amount": "Montant"},
    "RU": {"title": "Python Калькулятор", "modes": ["Обычный", "Научный", "Стат", "Приставки", "Платное"], "tax_menu": "Налоги", "curr_menu": "Валюта", "res": "Результат", "exec": "Считать", "amount": "Сумма"},
    "PT": {"title": "Calculadora Python", "modes": ["Básico", "Científico", "Estatística", "Prefixos", "Pago"], "tax_menu": "Impostos", "curr_menu": "Moeda", "res": "Resultado", "exec": "Calcular", "amount": "Quantia"}
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
    div.stButton > button[key*="k_5"] { background-color: #007AFF !important; color: #FFFFFF !important; font-size: 40px !important; border: 3px solid #FFFFFF !important; }
    [data-testid="stHorizontalBlock"] { gap: 0px !important; }
    button[key="btn_del_main"] { background-color: #FF3B30 !important; color: white !important; height: 95px !important; border-radius: 12px 0 0 12px !important; border: none !important; margin-right: -1px !important; }
    button[key="btn_exe_main"] { background-color: #34C759 !important; color: white !important; height: 95px !important; font-size: 60px !important; border-radius: 0 12px 12px 0 !important; border: none !important; margin-left: -1px !important; }
    .tax-box { border: 4px solid var(--txt); border-radius: 12px; padding: 15px; text-align: center; font-size: 24px; font-weight: 900; color: var(--txt); }
</style>
""", unsafe_allow_html=True)

# --- ロジック関数 ---
def parse_val(text):
    if not text: return 0.0
    s = str(text).replace(',', '').strip()
    si = {'Q':1e30,'R':1e27,'Y':1e24,'Z':1e21,'E':1e18,'P':1e15,'T':1e12,'G':1e9,'M':1e6,'k':1e3,'h':1e2,'da':10,'d':0.1,'c':0.01,'m':0.001,'μ':1e-6,'n':1e-9,'p':1e-12,'f':1e-15,'a':1e-18,'z':1e-21,'y':1e-24}
    units = {"兆": 1e12, "億": 1e8, "万": 1e4, "千": 1e3}
    total, ts = 0.0, s
    for u, v in units.items():
        if u in ts:
            parts = ts.split(u); total += float(parts[0]) * v; ts = parts[1]
    if total > 0: return total + (float(ts) if ts else 0.0)
    for k, v in si.items():
        if s.endswith(k): return float(s[:-len(k)]) * v
    try: return float(s)
    except: return 0.0

# --- 状態管理 ---
for k in ['f_state', 'm_state', 'tax_res', 'paid_sub', 'lang']:
    if k not in st.session_state: 
        st.session_state[k] = "JP" if k == 'lang' else ("通常" if k == 'm_state' else ("" if 'state' in k else "結果表示"))

# --- UI：言語選択とタイトル ---
col_lang, _ = st.columns([1, 4])
with col_lang:
    selected_lang = st.selectbox("", list(LANG.keys()), index=list(LANG.keys()).index(st.session_state.lang), label_visibility="collapsed")
    if selected_lang != st.session_state.lang:
        st.session_state.lang = selected_lang
        st.rerun()

L = LANG[st.session_state.lang]
st.markdown(f'<div class="app-title-box">{L["title"]}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="display">{st.session_state.f_state if st.session_state.f_state else "0"}</div>', unsafe_allow_html=True)

# --- メインキーボード ---
keys = ["7","8","9","π","√","+","4","5","6","e","^^","−","1","2","3","i","(-)","×","0","00",".","(",")","÷"]
cols = st.columns(6)
for i, k in enumerate(keys):
    if cols[i % 6].button(k, key=f"k_{i}"): st.session_state.f_state += k; st.rerun()

# DELETE & ＝
c1, c2 = st.columns(2)
with c1:
    if st.button("DELETE", key="btn_del_main"): st.session_state.f_state = ""; st.rerun()
with c2:
    if st.button("＝", key="btn_exe_main"):
        try:
            f = st.session_state.f_state.replace('×','*').replace('÷','/').replace('−','-').replace('^^','**').replace('π','math.pi').replace('e','math.e').replace('√','math.sqrt').replace('°','*math.pi/180')
            st.session_state.f_state = format(eval(f), '.10g')
        except: st.session_state.f_state = "Error"
        st.rerun()

st.divider()

# --- モード切替 ---
mc = st.columns(5)
for i, m in enumerate(L["modes"]):
    if mc[i].button(m, key=f"mode_btn_{i}"): 
        st.session_state.m_state = LANG["JP"]["modes"][i] # 内部判定は日本語で固定
        st.rerun()

# --- 機能ロジック復元 ---
cur_m = st.session_state.m_state

if cur_m == "科学計算":
    sc = st.columns(4)
    for i, s in enumerate(["sin(", "cos(", "tan(", "log(", "abs(", "sqrt(", "°"]):
        if sc[i % 4].button(s, key=f"sci_{i}"): st.session_state.f_state += s; st.rerun()

elif cur_m == "値数":
    sc = st.columns(4)
    for i, (l, c) in enumerate([("平均", "mean(["), ("中央値", "median(["), ("最頻値", "mode(["), ("最大", "max(["), ("最小", "min(["), (",", ","), (")]", ")]")]):
        if sc[i % 4].button(l, key=f"st_{i}"): st.session_state.f_state += c; st.rerun()

elif cur_m == "拡縮":
    si_l = ["Q","R","Y","Z","E","P","T","G","M","k","h","da","d","c","m","μ","n","p","f","a","z","y","r","q"]
    uc = st.columns(8)
    for i, u in enumerate(si_l):
        if uc[i % 8].button(u, key=f"si_{i}"): st.session_state.f_state += u; st.rerun()

elif cur_m == "有料機能":
    sub = st.columns(2)
    if sub[0].button(L["tax_menu"]): st.session_state.paid_sub = "税金"; st.rerun()
    if sub[1].button(L["curr_menu"]): st.session_state.paid_sub = "為替"; st.rerun()
    
    if st.session_state.paid_sub == "税金":
        tt = st.selectbox("Type", ["所得税", "相続税", "法人税", "税込10%", "税込8%"])
        ti = st.text_input(L["amount"])
        if st.button(L["exec"]):
            v = parse_val(ti if ti else st.session_state.f_state)
            r = v * 1.1 if "10%" in tt else v * 0.2
            st.session_state.tax_res = f"{format(int(r), ',')} YEN"; st.rerun()
        st.markdown(f'<div class="tax-box">{st.session_state.tax_res}</div>', unsafe_allow_html=True)
