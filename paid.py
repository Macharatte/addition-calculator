import streamlit as st
import math
import statistics
import re

# --- 1. ページ設定 ---
st.set_page_config(page_title="Python Calculator Premium", layout="centered")

# --- 2. キーボード無効化スクリプト ---
st.components.v1.html("<script>const observer = new MutationObserver(() => { const inputs = window.parent.document.querySelectorAll('input[role=\"combobox\"]'); inputs.forEach(input => { input.setAttribute('readonly', 'true'); }); }); observer.observe(window.parent.document.body, { childList: true, subtree: true });</script>", height=0)

# --- 3. 完全多言語リソース ---
LANG_DATA = {
    "JP": {
        "title": "Python Calculator Premium",
        "modes": ["通常", "科学計算", "値数", "拡縮", "有料機能"],
        "tax_m": "税金計算", "cur_m": "為替・金銀銅", "gas_m": "ガソリンレート", "cry_m": "仮想通貨",
        "exec": "計算実行", "amt": "金額/数量を入力",
        "heir": "相続人の人数",
        "tax_list": ["所得税", "相続税 (控除後)", "贈与税", "住民税", "法人税", "税込10%", "税抜10%"],
        "cur_list": ["JPY (日本円)", "USD (米国ドル)", "EUR (ユーロ)", "XAU (金)", "XAG (銀)", "XPT (白金)", "XCU (銅)"],
        "stat_labels": ["平均 (Mean)", "中央値 (Median)", "最頻値 (Mode)", "最大値 (Max)", "最小値 (Min)"],
        "gas_list": ["東京 ENEOS (レギュラー)", "東京 ENEOS (ハイオク)", "東京 ENEOS (軽油)", "米国平均", "欧州平均"],
        "cry_list": ["BTC (ビットコイン)", "ETH (イーサリアム)", "XRP (リップル)", "SOL (ソラナ)"]
    },
    "EN": {
        "title": "Python Calculator Premium",
        "modes": ["Basic", "Scientific", "Stats", "SI Prefix", "Paid"],
        "tax_m": "Tax", "cur_m": "Forex/Metal", "gas_m": "Tokyo Fuel", "cry_m": "Crypto",
        "exec": "Calculate", "amt": "Enter Amount",
        "heir": "Number of Heirs",
        "tax_list": ["Income Tax", "Inheritance Tax", "Gift Tax", "Residency", "Corporate", "VAT 10%", "Excl. 10%"],
        "cur_list": ["JPY (Yen)", "USD (Dollar)", "EUR (Euro)", "XAU (Gold)", "XAG (Silver)", "XPT (Platinum)", "XCU (Copper)"],
        "stat_labels": ["Mean", "Median", "Mode", "Max", "Min"],
        "gas_list": ["Tokyo (Regular)", "Tokyo (Premium)", "Tokyo (Diesel)", "USA Avg", "Europe Avg"],
        "cry_list": ["BTC (Bitcoin)", "ETH (Ethereum)", "XRP (Ripple)", "SOL (Solana)"]
    }
}
for k in ["ZH", "HI", "ES", "AR", "FR", "RU", "PT"]:
    if k not in LANG_DATA: LANG_DATA[k] = LANG_DATA["EN"]

# --- 4. CSS ---
st.markdown("""
<style>
    .main .block-container { max-width: 100% !important; padding: 10px !important; }
    header {visibility: hidden;}
    .display {
        display: flex; align-items: center; justify-content: flex-end; font-size: 45px; font-weight: 900; 
        margin-bottom: 10px; padding: 15px; border: 4px solid #000; border-radius: 12px; 
        min-height: 110px; background: rgba(128,128,128,0.1); word-break: break-all;
    }
    div.stButton > button { width: 100% !important; height: 55px !important; font-weight: 900 !important; }
    .tax-box { border: 4px solid #34C759; border-radius: 12px; padding: 15px; text-align: center; font-size: 24px; font-weight: 900; margin-top:10px; background: rgba(52,199,89,0.1); }
</style>
""", unsafe_allow_html=True)

# --- 5. 状態管理 ---
for key, val in {'f_state':"", 'm_idx':0, 'lang':"JP", 'p_sub':"tax", 'tax_res':"0"}.items():
    if key not in st.session_state: st.session_state[key] = val

SI_MAP = {'Q':1e30,'R':1e27,'Y':1e24,'Z':1e21,'E':1e18,'P':1e15,'T':1e12,'G':1e9,'M':1e6,'k':1e3,'h':1e2,'da':10,'d':0.1,'c':0.01,'m':0.001,'μ':1e-6,'n':1e-9,'p':1e-12,'f':1e-15,'a':1e-18,'z':1e-21,'y':1e-24,'r':1e-27,'q':1e-30}

# 言語選択
new_l = st.selectbox("", list(LANG_DATA.keys()), index=list(LANG_DATA.keys()).index(st.session_state.lang), key="main_lang_sel")
if new_l != st.session_state.lang:
    st.session_state.lang = new_l; st.rerun()

L = LANG_DATA[st.session_state.lang]

# 画面描画
st.markdown(f'<div class="display">{st.session_state.f_state if st.session_state.f_state else "0"}</div>', unsafe_allow_html=True)

# キーボード
keys = ["7","8","9","π","√","+","4","5","6","e","^^","−","1","2","3","i","(-)","×","0","00",".","(",")","÷"]
cols = st.columns(6)
for i, k in enumerate(keys):
    if cols[i % 6].button(k, key=f"k_{i}"): st.session_state.f_state += k; st.rerun()

c1, c2 = st.columns(2)
with c1:
    if st.button("DELETE", key="btn_del"): st.session_state.f_state = ""; st.rerun()
with c2:
    if st.button("＝", key="btn_exe"):
        try:
            ex = st.session_state.f_state.replace('×','*').replace('÷','/').replace('−','-').replace('^^','**').replace('π','math.pi').replace('e','math.e').replace('√','math.sqrt')
            sorted_si = sorted(SI_MAP.items(), key=lambda x: len(x[0]), reverse=True)
            for s, v in sorted_si: ex = re.sub(f'(\\d){s}', f'\\1*{v}', ex); ex = re.sub(f'^{s}', f'{v}', ex)
            st.session_state.f_state = format(eval(ex, {"math": math, "statistics": statistics}), '.10g')
        except: st.session_state.f_state = "Error"
        st.rerun()

st.divider()

# モード切替
mc = st.columns(5)
for i, m_n in enumerate(L["modes"]):
    if mc[i].button(m_n, key=f"nav_{i}"): st.session_state.m_idx = i; st.rerun()

# --- 機能ロジック ---
idx = st.session_state.m_idx
cur_lang = st.session_state.lang

if idx == 1: # 科学
    sc = st.columns(4)
    its = [("sin", "math.sin("), ("cos", "math.cos("), ("tan", "math.tan("), ("log", "math.log10("), ("abs", "abs("), ("sqrt", "math.sqrt("), ("π", "math.pi"), ("e", "math.e")]
    for i, (lb, cd) in enumerate(its):
        if sc[i % 4].button(lb, key=f"sci_{i}"): st.session_state.f_state += cd; st.rerun()

elif idx == 2: # 値数
    sc = st.columns(4)
    st_codes = ["statistics.mean([", "statistics.median([", "statistics.mode([", "max([", "min(["]
    for i, lb in enumerate(L["stat_labels"]):
        if sc[i % 4].button(lb, key=f"st_btn_{cur_lang}_{i}"): st.session_state.f_state += st_codes[i]; st.rerun()
    sc2 = st.columns(4)
    if sc2[0].button(",", key="st_c"): st.session_state.f_state += ","; st.rerun()
    if sc2[1].button("]", key="st_e"): st.session_state.f_state += "])"; st.rerun()

elif idx == 3: # 拡縮
    uc = st.columns(8)
    si_ks = ["Q","R","Y","Z","E","P","T","G","M","k","h","da","d","c","m","μ","n","p","f","a","z","y","r","q"]
    for i, u in enumerate(si_ks):
        if uc[i % 8].button(u, key=f"si_{i}"): st.session_state.f_state += u; st.rerun()

elif idx == 4: # 有料
    pc = st.columns(4)
    if pc[0].button(L["tax_m"], key="p_t"): st.session_state.p_sub = "tax"; st.rerun()
    if pc[1].button(L["cur_m"], key="p_c"): st.session_state.p_sub = "cur"; st.rerun()
    if pc[2].button(L["gas_m"], key="p_g"): st.session_state.p_sub = "gas"; st.rerun()
    if pc[3].button(L["cry_m"], key="p_y"): st.session_state.p_sub = "cry"; st.rerun()
    
    if st.session_state.p_sub == "tax":
        sel = st.selectbox("Menu", L["tax_list"], key=f"tax_s_{cur_lang}")
        heirs = 1
        if "相続" in sel or "Inheritance" in sel:
            heirs = st.number_input(L["heir"], 1, 10, 1, key=f"heir_in_{cur_lang}")
        amt = st.text_input(L["amt"], key=f"t_in_{cur_lang}")
        if st.button(L["exec"], key=f"t_r_{cur_lang}"):
            try:
                v = float(amt)
                if "相続" in sel or "Inheritance" in sel:
                    deduction = 30000000 + (6000000 * heirs)
                    taxable = max(0, v - deduction)
                    res = taxable * 0.15 # 簡易レート
                elif "10%" in sel: res = v * 1.1 if "税込" in sel else v / 1.1
                else: res = v * 0.2
                st.session_state.tax_res = f"Result: {format(int(res), ',')}"
            except: st.session_state.tax_res = "Error"
            st.rerun()

    elif st.session_state.p_sub == "cur":
        c1 = st.selectbox("From", L["cur_list"], key=f"c1_{cur_lang}")
        c2 = st.selectbox("To", L["cur_list"], key=f"c2_{cur_lang}")
        amt = st.text_input(L["amt"], key=f"c_in_{cur_lang}")
        if st.button(L["exec"], key=f"c_r_{cur_lang}"):
            try:
                # 銅(XCU)を追加レート設定 (154円/USD前提)
                r_map = {"JPY":154.0, "USD":1.0, "EUR":0.95, "XAU":0.00038, "XAG":0.032, "XPT":0.01, "XCU":0.11}
                val = (float(amt) / r_map[c1[:3]]) * r_map[c2[:3]]
                st.session_state.tax_res = f"{format(val, '.4f')} {c2[:3]}"
            except: st.session_state.tax_res = "Error"
            st.rerun()

    elif st.session_state.p_sub == "gas":
        g_sel = st.selectbox("Station", L["gas_list"], key=f"g_s_{cur_lang}")
        amt = st.text_input(L["amt"] + " (L)", key=f"g_i_{cur_lang}")
        if st.button(L["exec"], key=f"g_r_{cur_lang}"):
            # 東京ENEOS実勢レート (2025/12)
            prices = {"東京": 178, "Tokyo": 178, "High": 189, "ハイオク": 189, "Diesel": 158, "軽油": 158}
            p = prices.get(next((k for k in prices if k in g_sel), "東京"), 178)
            try: st.session_state.tax_res = f"ENEOS Price: {int(float(amt) * p)} JPY"
            except: st.session_state.tax_res = "Error"
            st.rerun()

    elif st.session_state.p_sub == "cry":
        cr_sel = st.selectbox("Coin", L["cry_list"], key=f"cr_s_{cur_lang}")
        amt = st.text_input(L["amt"], key=f"cr_i_{cur_lang}")
        if st.button(L["exec"], key=f"cr_r_{cur_lang}"):
            try:
                p_map = {"BTC":15200000, "ETH":510000, "XRP":380, "SOL":35000}
                res = float(amt) * p_map.get(cr_sel[:3], 0)
                st.session_state.tax_res = f"Market Value: {format(int(res), ',')} JPY"
            except: st.session_state.tax_res = "Error"
            st.rerun()

    st.markdown(f'<div class="tax-box">{st.session_state.tax_res}</div>', unsafe_allow_html=True)
