import streamlit as st
import math
import statistics
import requests
import re

# --- 1. ページ設定 ---
st.set_page_config(page_title="Python Calculator Premium", layout="centered")

# --- 2. キーボード強制無効化 JS ---
st.components.v1.html("<script>const observer = new MutationObserver(() => { const inputs = window.parent.document.querySelectorAll('input[role=\"combobox\"]'); inputs.forEach(input => { input.setAttribute('readonly', 'true'); }); }); observer.observe(window.parent.document.body, { childList: true, subtree: true });</script>", height=0)

# --- 3. 全言語リソース (多言語対応メニュー) ---
LANG = {
    "JP": {
        "title": "Python Calculator Premium", "modes": ["通常", "科学計算", "値数", "拡縮", "有料機能"],
        "tax_m": "税金", "cur_m": "為替・貴金属", "gas_m": "ガソリン", "cry_m": "仮想通貨", "exec": "計算実行", "amt": "入力",
        "tax_list": ["所得税", "相続税", "法人税", "贈与税", "住民税", "税込10%", "税込8%", "税抜計算"],
        "cur_list": ["JPY (円)", "USD (ドル)", "EUR (ユーロ)", "GBP (ポンド)", "XAU (金)", "XAG (銀)", "XPT (白金)"],
        "gas_list": ["日本 (Regular)", "米国 (Premium)", "中国", "欧州平均"],
        "cry_list": ["BTC (ビットコイン)", "ETH (イーサリアム)"]
    },
    "EN": {
        "title": "Python Calculator Premium", "modes": ["Basic", "Scientific", "Stats", "SI Prefix", "Paid"],
        "tax_m": "Tax", "cur_m": "Forex/Metal", "gas_m": "Gasoline", "cry_m": "Crypto", "exec": "Run", "amt": "Amount",
        "tax_list": ["Income Tax", "Inheritance", "Corporate", "Gift Tax", "Residency", "VAT 10%", "VAT 8%", "Excl. Tax"],
        "cur_list": ["JPY (Yen)", "USD (Dollar)", "EUR (Euro)", "GBP (Pound)", "XAU (Gold)", "XAG (Silver)", "XPT (Platinum)"],
        "gas_list": ["Japan", "USA", "China", "Europe"],
        "cry_list": ["BTC (Bitcoin)", "ETH (Ethereum)"]
    },
    "ZH": {
        "title": "Python 计算器", "modes": ["普通", "科学", "统计", "单位", "付费"],
        "tax_m": "税务", "cur_m": "汇率/贵金属", "gas_m": "汽油", "cry_m": "虚拟货币", "exec": "计算", "amt": "金额",
        "tax_list": ["所得税", "遗产税", "企业税", "赠与税", "居民税", "增值税10%", "增值税8%", "不含税"],
        "cur_list": ["JPY (日元)", "USD (美元)", "EUR (欧元)", "GBP (英镑)", "XAU (黄金)", "XAG (白银)", "XPT (铂金)"],
        "gas_list": ["中国", "日本", "美国", "欧洲"],
        "cry_list": ["BTC (比特币)", "ETH (以太坊)"]
    }
}
# 他の言語もENをベースに補完
for k in ["HI", "ES", "AR", "FR", "RU", "PT"]:
    if k not in LANG: LANG[k] = LANG["EN"]

# --- 4. CSS (デザイン) ---
st.markdown("""
<style>
    .main .block-container { max-width: 100% !important; padding: 10px !important; }
    header {visibility: hidden;}
    :root { --bg: #FFF; --txt: #000; --btn-bg: #1A1A1A; --btn-txt: #FFF; }
    @media (prefers-color-scheme: dark) { :root { --bg: #000; --txt: #FFFFFF; --btn-bg: #EEE; --btn-txt: #000; } }
    .app-title-box { text-align: center; font-size: 26px; font-weight: 900; color: var(--txt); border-bottom: 3px solid var(--txt); margin-bottom: 15px; }
    .display {
        display: flex; align-items: center; justify-content: flex-end; font-size: 45px; font-weight: 900; 
        margin-bottom: 10px; padding: 15px; border: 4px solid var(--txt); border-radius: 12px; 
        min-height: 110px; color: var(--txt); background: rgba(128,128,128,0.1); word-break: break-all;
    }
    div.stButton > button { width: 100% !important; height: 55px !important; font-weight: 900 !important; font-size: 20px !important; background-color: var(--btn-bg) !important; color: var(--btn-txt) !important; border: 1px solid var(--txt) !important; }
    div.stButton > button[key*="k_5"] { background-color: #007AFF !important; color: #FFFFFF !important; font-size: 40px !important; border: 3px solid #FFFFFF !important; }
    [data-testid="stHorizontalBlock"] { gap: 0px !important; }
    button[key="btn_del_main"] { background-color: #FF3B30 !important; color: white !important; height: 95px !important; border-radius: 12px 0 0 12px !important; border: none !important; margin-right: -1px !important; }
    button[key="btn_exe_main"] { background-color: #34C759 !important; color: white !important; height: 95px !important; font-size: 60px !important; border-radius: 0 12px 12px 0 !important; border: none !important; margin-left: -1px !important; }
    .tax-box { border: 4px solid var(--txt); border-radius: 12px; padding: 15px; text-align: center; font-size: 24px; font-weight: 900; color: var(--txt); margin-top:10px; }
</style>
""", unsafe_allow_html=True)

# --- 5. 状態保持 ---
for key, val in {'f_state':"", 'm_idx':0, 'lang':"JP", 'p_sub':"tax", 'tax_res':"0"}.items():
    if key not in st.session_state: st.session_state[key] = val

SI_MAP = {'Q':1e30,'R':1e27,'Y':1e24,'Z':1e21,'E':1e18,'P':1e15,'T':1e12,'G':1e9,'M':1e6,'k':1e3,'h':1e2,'da':10,'d':0.1,'c':0.01,'m':0.001,'μ':1e-6,'n':1e-9,'p':1e-12,'f':1e-15,'a':1e-18,'z':1e-21,'y':1e-24,'r':1e-27,'q':1e-30}

# 言語選択
col_l, _ = st.columns([1, 4])
with col_l:
    new_l = st.selectbox("", list(LANG.keys()), index=list(LANG.keys()).index(st.session_state.lang), label_visibility="collapsed")
    if new_l != st.session_state.lang:
        st.session_state.lang = new_l; st.rerun()

L = LANG[st.session_state.lang]

# 画面描画
st.markdown(f'<div class="app-title-box">{L["title"]}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="display">{st.session_state.f_state if st.session_state.f_state else "0"}</div>', unsafe_allow_html=True)

# メインキーボード
keys = ["7","8","9","π","√","+","4","5","6","e","^^","−","1","2","3","i","(-)","×","0","00",".","(",")","÷"]
cols = st.columns(6)
for i, k in enumerate(keys):
    if cols[i % 6].button(k, key=f"k_{i}"): st.session_state.f_state += k; st.rerun()

c1, c2 = st.columns(2)
with c1:
    if st.button("DELETE", key="btn_del_main"): st.session_state.f_state = ""; st.rerun()
with c2:
    if st.button("＝", key="btn_exe_main"):
        try:
            ex = st.session_state.f_state.replace('×','*').replace('÷','/').replace('−','-').replace('^^','**').replace('π','math.pi').replace('e','math.e').replace('√','math.sqrt')
            # 拡縮（SI接頭語）置換ロジック強化
            sorted_si = sorted(SI_MAP.items(), key=lambda x: len(x[0]), reverse=True)
            for s, v in sorted_si: ex = re.sub(f'(\\d){s}', f'\\1*{v}', ex); ex = re.sub(f'^{s}', f'{v}', ex)
            st.session_state.f_state = format(eval(ex, {"math": math, "statistics": statistics}), '.10g')
        except: st.session_state.f_state = "Error"
        st.rerun()

st.divider()

# モードナビ
mc = st.columns(5)
for i, m_n in enumerate(L["modes"]):
    if mc[i].button(m_n, key=f"nav_{i}"): st.session_state.m_idx = i; st.rerun()

# --- 機能ロジック ---
idx = st.session_state.m_idx
if idx == 1: # 科学
    sc = st.columns(4)
    items = [("sin", "math.sin("), ("cos", "math.cos("), ("tan", "math.tan("), ("log", "math.log10("), ("abs", "abs("), ("sqrt", "math.sqrt("), ("π", "math.pi"), ("e", "math.e")]
    for i, (lb, cd) in enumerate(items):
        if sc[i % 4].button(lb, key=f"s_{i}"): st.session_state.f_state += cd; st.rerun()

elif idx == 2: # 統計
    sc = st.columns(4)
    items = [("Mean", "statistics.mean(["), ("Median", "statistics.median(["), ("Mode", "statistics.mode(["), ("Max", "max(["), ("Min", "min(["), (",", ","), ("]", "])")]
    for i, (lb, cd) in enumerate(items):
        if sc[i % 4].button(lb, key=f"st_{i}"): st.session_state.f_state += cd; st.rerun()

elif idx == 3: # 拡縮
    uc = st.columns(8)
    si_keys = ["Q","R","Y","Z","E","P","T","G","M","k","h","da","d","c","m","μ","n","p","f","a","z","y","r","q"]
    for i, u in enumerate(si_keys):
        if uc[i % 8].button(u, key=f"si_{i}"): st.session_state.f_state += u; st.rerun()

elif idx == 4: # 有料
    pc = st.columns(4)
    if pc[0].button(L["tax_m"]): st.session_state.p_sub = "tax"; st.rerun()
    if pc[1].button(L["cur_m"]): st.session_state.p_sub = "cur"; st.rerun()
    if pc[2].button(L["gas_m"]): st.session_state.p_sub = "gas"; st.rerun()
    if pc[3].button(L["cry_m"]): st.session_state.p_sub = "cry"; st.rerun()
    
    if st.session_state.p_sub == "tax":
        sel = st.selectbox("Type", L["tax_list"], key="tax_sel")
        amt = st.text_input(L["amt"], key="t_in")
        if st.button(L["exec"], key="t_run"):
            try:
                v = float(amt)
                r = v * 1.1 if "10%" in sel else v * 1.08 if "8%" in sel else v / 1.1 if "税抜" in sel or "Excl" in sel else v * 0.2
                st.session_state.tax_res = f"Result: {format(int(r), ',')}"
            except: st.session_state.tax_res = "Error"
            st.rerun()
    elif st.session_state.p_sub == "cur":
        c1, c2 = st.selectbox("From", L["cur_list"]), st.selectbox("To", L["cur_list"])
        amt = st.text_input(L["amt"], key="c_in")
        if st.button(L["exec"], key="c_run"):
            try:
                rates = {"JPY":154.0, "USD":1.0, "EUR":0.95, "GBP":0.79, "XAU":0.00038, "XAG":0.032, "XPT":0.01}
                res = (float(amt) / rates[c1[:3]]) * rates[c2[:3]]
                st.session_state.tax_res = f"{format(res, '.4f')} {c2[:3]}"
            except: st.session_state.tax_res = "Error"
            st.rerun()
    elif st.session_state.p_sub == "gas":
        g_sel = st.selectbox("Region", L["gas_list"])
        amt = st.text_input(L["amt"] + " (Litre)", key="g_in")
        if st.button(L["exec"], key="g_run"):
            prices = {"日本": 175, "Japan": 175, "米国": 140, "USA": 140, "中国": 160, "China": 160, "欧州": 280, "Europe": 280}
            try: st.session_state.tax_res = f"Cost: {int(float(amt) * prices.get(g_sel.split()[0], 175))} JPY"
            except: st.session_state.tax_res = "Error"
            st.rerun()
    elif st.session_state.p_sub == "cry":
        cr_sel = st.selectbox("Coin", L["cry_list"])
        amt = st.text_input(L["amt"], key="cr_in")
        if st.button(L["exec"], key="cr_run"):
            try:
                price = 14500000 if "BTC" in cr_sel else 400000 # 概算リアルタイム風
                st.session_state.tax_res = f"Value: {format(int(float(amt) * price), ',')} JPY"
            except: st.session_state.tax_res = "Error"
            st.rerun()

    st.markdown(f'<div class="tax-box">{st.session_state.tax_res}</div>', unsafe_allow_html=True)
