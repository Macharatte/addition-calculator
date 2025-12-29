import streamlit as st
import math
import statistics
import re

# --- 1. ページ設定 ---
st.set_page_config(page_title="Python Calculator Premium", layout="centered")

# --- 2. キーボード無効化スクリプト ---
st.components.v1.html("<script>const observer = new MutationObserver(() => { const inputs = window.parent.document.querySelectorAll('input[role=\"combobox\"]'); inputs.forEach(input => { input.setAttribute('readonly', 'true'); }); }); observer.observe(window.parent.document.body, { childList: true, subtree: true });</script>", height=0)

# --- 3. 完全多言語リソース (項目を1つずつ日本語化) ---
LANG_DATA = {
    "JP": {
        "title": "Python Calculator Premium",
        "modes": ["通常", "科学計算", "値数", "拡縮", "有料機能"],
        "tax_m": "税金計算", "cur_m": "為替・金銀", "gas_m": "ガソリン", "cry_m": "仮想通貨",
        "exec": "計算実行", "amt": "金額/数量を入力",
        "tax_list": ["所得税", "相続税", "贈与税", "住民税", "法人税", "固定資産税", "事業税", "税込10%", "税込8%", "税抜10%", "税抜8%"],
        "cur_list": ["JPY (日本円)", "USD (米国ドル)", "EUR (ユーロ)", "GBP (英国ポンド)", "CNY (中国元)", "KRW (韓国ウォン)", "AUD (豪ドル)", "CAD (加ドル)", "XAU (金)", "XAG (銀)", "XPT (プラチナ)"],
        "stat_labels": ["平均 (Mean)", "中央値 (Median)", "最頻値 (Mode)", "最大値 (Max)", "最小値 (Min)"],
        "gas_list": ["日本 (レギュラー)", "日本 (ハイオク)", "日本 (軽油)", "米国 (Premium)", "中国 (汽油)", "欧州平均"],
        "cry_list": ["BTC (ビットコイン)", "ETH (イーサリアム)", "XRP (リップル)", "SOL (ソラナ)"]
    },
    "EN": {
        "title": "Python Calculator Premium",
        "modes": ["Basic", "Scientific", "Stats", "SI Prefix", "Paid"],
        "tax_m": "Tax", "cur_m": "Forex/Metal", "gas_m": "Gasoline", "cry_m": "Crypto",
        "exec": "Calculate", "amt": "Enter Amount",
        "tax_list": ["Income Tax", "Inheritance", "Gift Tax", "Residency", "Corporate", "Property Tax", "Business Tax", "VAT 10%", "VAT 8%", "Excl. 10%", "Excl. 8%"],
        "cur_list": ["JPY (Yen)", "USD (Dollar)", "EUR (Euro)", "GBP (Pound)", "CNY (Yuan)", "KRW (Won)", "AUD (Dollar)", "CAD (Dollar)", "XAU (Gold)", "XAG (Silver)", "XPT (Platinum)"],
        "stat_labels": ["Mean", "Median", "Mode", "Max", "Min"],
        "gas_list": ["Japan (Reg)", "Japan (High)", "Japan (Diesel)", "USA (Gas)", "China (Gas)", "Europe"],
        "cry_list": ["BTC (Bitcoin)", "ETH (Ethereum)", "XRP (Ripple)", "SOL (Solana)"]
    }
}
# 他の言語はENをミラーリング
for k in ["ZH", "HI", "ES", "AR", "FR", "RU", "PT"]:
    if k not in LANG_DATA: LANG_DATA[k] = LANG_DATA["EN"]

# --- 4. CSS ---
st.markdown("""
<style>
    .main .block-container { max-width: 100% !important; padding: 10px !important; }
    header {visibility: hidden;}
    :root { --bg: #FFF; --txt: #000; --btn-bg: #1A1A1A; --btn-txt: #FFF; }
    @media (prefers-color-scheme: dark) { :root { --bg: #000; --txt: #FFFFFF; --btn-bg: #EEE; --btn-txt: #000; } }
    .display {
        display: flex; align-items: center; justify-content: flex-end; font-size: 45px; font-weight: 900; 
        margin-bottom: 10px; padding: 15px; border: 4px solid var(--txt); border-radius: 12px; 
        min-height: 110px; color: var(--txt); background: rgba(128,128,128,0.1); word-break: break-all;
    }
    div.stButton > button { width: 100% !important; height: 55px !important; font-weight: 900 !important; font-size: 20px !important; background-color: var(--btn-bg) !important; color: var(--btn-txt) !important; border: 1px solid var(--txt) !important; }
    [data-testid="stHorizontalBlock"] { gap: 0px !important; }
    button[key="btn_del_main"] { background-color: #FF3B30 !important; color: white !important; height: 95px !important; border-radius: 12px 0 0 12px !important; border: none !important; }
    button[key="btn_exe_main"] { background-color: #34C759 !important; color: white !important; height: 95px !important; font-size: 60px !important; border-radius: 0 12px 12px 0 !important; border: none !important; }
    .tax-box { border: 4px solid var(--txt); border-radius: 12px; padding: 15px; text-align: center; font-size: 24px; font-weight: 900; color: var(--txt); margin-top:10px; }
</style>
""", unsafe_allow_html=True)

# --- 5. 状態管理 ---
for key, val in {'f_state':"", 'm_idx':0, 'lang':"JP", 'p_sub':"tax", 'tax_res':"0"}.items():
    if key not in st.session_state: st.session_state[key] = val

SI_MAP = {'Q':1e30,'R':1e27,'Y':1e24,'Z':1e21,'E':1e18,'P':1e15,'T':1e12,'G':1e9,'M':1e6,'k':1e3,'h':1e2,'da':10,'d':0.1,'c':0.01,'m':0.001,'μ':1e-6,'n':1e-9,'p':1e-12,'f':1e-15,'a':1e-18,'z':1e-21,'y':1e-24,'r':1e-27,'q':1e-30}

# 言語選択
new_l = st.selectbox("", list(LANG_DATA.keys()), index=list(LANG_DATA.keys()).index(st.session_state.lang), key="lang_select_box")
if new_l != st.session_state.lang:
    st.session_state.lang = new_l; st.rerun()

L = LANG_DATA[st.session_state.lang]

# ディスプレイ
st.markdown(f'<div class="display">{st.session_state.f_state if st.session_state.f_state else "0"}</div>', unsafe_allow_html=True)

# キーボード
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
            sorted_si = sorted(SI_MAP.items(), key=lambda x: len(x[0]), reverse=True)
            for s, v in sorted_si: ex = re.sub(f'(\\d){s}', f'\\1*{v}', ex); ex = re.sub(f'^{s}', f'{v}', ex)
            st.session_state.f_state = format(eval(ex, {"math": math, "statistics": statistics}), '.10g')
        except: st.session_state.f_state = "Error"
        st.rerun()

st.divider()

# モード切替
mc = st.columns(5)
for i, m_n in enumerate(L["modes"]):
    if mc[i].button(m_n, key=f"nav_btn_{i}"): st.session_state.m_idx = i; st.rerun()

# --- 機能ロジック ---
idx = st.session_state.m_idx
if idx == 1: # 科学
    sc = st.columns(4)
    sc_its = [("sin", "math.sin("), ("cos", "math.cos("), ("tan", "math.tan("), ("log", "math.log10("), ("abs", "abs("), ("sqrt", "math.sqrt("), ("π", "math.pi"), ("e", "math.e")]
    for i, (lb, cd) in enumerate(sc_its):
        if sc[i % 4].button(lb, key=f"sci_{i}"): st.session_state.f_state += cd; st.rerun()

elif idx == 2: # 値数 (ここを翻訳対応)
    sc = st.columns(4)
    st_codes = ["statistics.mean([", "statistics.median([", "statistics.mode([", "max([", "min(["]
    for i, lb in enumerate(L["stat_labels"]):
        if sc[i % 4].button(lb, key=f"st_btn_{st.session_state.lang}_{i}"):
            st.session_state.f_state += st_codes[i]; st.rerun()
    # カンマと閉じカッコ
    sc2 = st.columns(4)
    if sc2[0].button(",", key="st_comma"): st.session_state.f_state += ","; st.rerun()
    if sc2[1].button("]", key="st_end"): st.session_state.f_state += "])"; st.rerun()

elif idx == 3: # 拡縮
    uc = st.columns(8)
    si_ks = ["Q","R","Y","Z","E","P","T","G","M","k","h","da","d","c","m","μ","n","p","f","a","z","y","r","q"]
    for i, u in enumerate(si_ks):
        if uc[i % 8].button(u, key=f"si_btn_{i}"): st.session_state.f_state += u; st.rerun()

elif idx == 4: # 有料 (動的Keyで強制更新)
    pc = st.columns(4)
    if pc[0].button(L["tax_m"], key="paid_tax"): st.session_state.p_sub = "tax"; st.rerun()
    if pc[1].button(L["cur_m"], key="paid_cur"): st.session_state.p_sub = "cur"; st.rerun()
    if pc[2].button(L["gas_m"], key="paid_gas"): st.session_state.p_sub = "gas"; st.rerun()
    if pc[3].button(L["cry_m"], key="paid_cry"): st.session_state.p_sub = "cry"; st.rerun()
    
    cur_lang = st.session_state.lang # 現在の言語をキーに含める
    
    if st.session_state.p_sub == "tax":
        sel = st.selectbox("Type", L["tax_list"], key=f"tax_sel_{cur_lang}")
        amt = st.text_input(L["amt"], key=f"t_in_{cur_lang}")
        if st.button(L["exec"], key=f"t_run_{cur_lang}"):
            try:
                v = float(amt)
                r = v * 1.1 if "10%" in sel and "税抜" not in sel else v / 1.1 if "10%" in sel and "税抜" in sel else v * 1.08 if "8%" in sel and "税抜" not in sel else v / 1.08 if "8%" in sel and "税抜" in sel else v * 0.2
                st.session_state.tax_res = f"Result: {format(int(r), ',')}"
            except: st.session_state.tax_res = "Error"
            st.rerun()

    elif st.session_state.p_sub == "cur":
        c1 = st.selectbox("From", L["cur_list"], key=f"c1_sel_{cur_lang}")
        c2 = st.selectbox("To", L["cur_list"], key=f"c2_sel_{cur_lang}")
        amt = st.text_input(L["amt"], key=f"c_in_{cur_lang}")
        if st.button(L["exec"], key=f"c_run_{cur_lang}"):
            try:
                r_map = {"JPY":154.0, "USD":1.0, "EUR":0.95, "GBP":0.79, "CNY":7.2, "KRW":1400.0, "AUD":1.5, "CAD":1.4, "XAU":0.00038, "XAG":0.032, "XPT":0.01}
                val = (float(amt) / r_map[c1[:3]]) * r_map[c2[:3]]
                st.session_state.tax_res = f"{format(val, '.4f')} {c2[:3]}"
            except: st.session_state.tax_res = "Error"
            st.rerun()

    elif st.session_state.p_sub == "gas":
        g_sel = st.selectbox("Region", L["gas_list"], key=f"g_sel_{cur_lang}")
        amt = st.text_input(L["amt"] + " (L)", key=f"g_in_{cur_lang}")
        if st.button(L["exec"], key=f"g_run_{cur_lang}"):
            prices = {"日本":175, "Japan":175, "米国":140, "USA":140, "中国":160, "China":160, "欧州":280, "Europe":280}
            try: st.session_state.tax_res = f"Cost: {int(float(amt) * prices.get(g_sel[:2], 175))} JPY"
            except: st.session_state.tax_res = "Error"
            st.rerun()

    elif st.session_state.p_sub == "cry":
        cr_sel = st.selectbox("Coin", L["cry_list"], key=f"cr_sel_{cur_lang}")
        amt = st.text_input(L["amt"], key=f"cr_in_{cur_lang}")
        if st.button(L["exec"], key=f"cr_run_{cur_lang}"):
            try:
                p_map = {"BTC":15000000, "ETH":500000, "XRP":300, "SOL":30000}
                res = float(amt) * p_map.get(cr_sel[:3], 0)
                st.session_state.tax_res = f"Value: {format(int(res), ',')} JPY"
            except: st.session_state.tax_res = "Error"
            st.rerun()

    st.markdown(f'<div class="tax-box">{st.session_state.tax_res}</div>', unsafe_allow_html=True)
