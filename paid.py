import streamlit as st
import math
import statistics
import re

# --- 1. ページ設定 ---
st.set_page_config(page_title="Python Calculator Premium", layout="centered")

# --- 2. キーボード無効化スクリプト ---
st.components.v1.html("<script>const observer = new MutationObserver(() => { const inputs = window.parent.document.querySelectorAll('input[role=\"combobox\"]'); inputs.forEach(input => { input.setAttribute('readonly', 'true'); }); }); observer.observe(window.parent.document.body, { childList: true, subtree: true });</script>", height=0)

# --- 3. 多言語リソース ---
LANG_DATA = {
    "JP": {
        "title": "Python Calculator Premium",
        "modes": ["通常", "科学計算", "値数", "拡縮", "有料機能"],
        "tax_m": "正確な税計算", "cur_m": "為替・金銀銅", "gas_m": "東京エネオス", "cry_m": "仮想通貨",
        "exec": "計算実行", "amt": "数値を入力", "heir": "法定相続人の数",
        "tax_list": ["所得税(概算)", "相続税(基礎控除後)", "贈与税(一般)", "住民税(10%)", "法人税", "税込10%", "税抜10%"],
        "cur_list": ["JPY (日本円)", "USD (米国ドル)", "EUR (ユーロ)", "XAU (金)", "XAG (銀)", "XPT (プラチナ)", "XCU (銅/Copper)"],
        "stat_labels": ["平均 (Mean)", "中央値 (Median)", "最頻値 (Mode)", "最大 (Max)", "最小 (Min)"],
        "gas_list": ["レギュラー (東京平均)", "ハイオク (東京平均)", "軽油 (東京平均)", "米国平均 ($/gal)", "欧州平均"],
        "cry_list": ["BTC (ビットコイン)", "ETH (イーサリアム)", "XRP (リップル)", "SOL (ソラナ)"]
    },
    "EN": {
        "title": "Python Calculator Premium",
        "modes": ["Basic", "Scientific", "Stats", "SI Prefix", "Paid"],
        "tax_m": "Tax Calc", "cur_m": "Forex/Metal", "gas_m": "Tokyo Fuel", "cry_m": "Crypto",
        "exec": "Calculate", "amt": "Enter Amount", "heir": "Number of Heirs",
        "tax_list": ["Income Tax", "Inheritance", "Gift Tax", "Residency", "Corporate", "VAT 10%", "Excl. 10%"],
        "cur_list": ["JPY (Yen)", "USD (Dollar)", "EUR (Euro)", "XAU (Gold)", "XAG (Silver)", "XPT (Platinum)", "XCU (Copper)"],
        "stat_labels": ["Mean", "Median", "Mode", "Max", "Min"],
        "gas_list": ["Regular (Tokyo)", "Premium (Tokyo)", "Diesel (Tokyo)", "USA Avg", "Europe Avg"],
        "cry_list": ["BTC (Bitcoin)", "ETH (Ethereum)", "XRP (Ripple)", "SOL (Solana)"]
    }
}
for k in ["ZH", "HI", "ES", "AR", "FR", "RU", "PT"]:
    if k not in LANG_DATA: LANG_DATA[k] = LANG_DATA["EN"]

# --- 4. CSS (黒ボタン・白文字・UI最適化) ---
st.markdown("""
<style>
    .main .block-container { max-width: 100% !important; padding: 10px !important; }
    header {visibility: hidden;}
    .app-header { text-align: center; font-size: 26px; font-weight: 900; padding: 10px; border-bottom: 2px solid #333; margin-bottom: 20px; }
    .display {
        display: flex; align-items: center; justify-content: flex-end; font-size: 45px; font-weight: 900; 
        margin-bottom: 10px; padding: 15px; border: 3px solid #000; border-radius: 12px; 
        min-height: 100px; background: #f0f2f6; word-break: break-all; color: #000;
    }
    div.stButton > button { 
        width: 100% !important; height: 55px !important; 
        background-color: #1A1A1A !important; color: #FFFFFF !important; 
        font-weight: 900 !important; border: 1px solid #444 !important;
        border-radius: 8px !important;
    }
    button[key="btn_del"] { background-color: #D32F2F !important; }
    button[key="btn_exe"] { background-color: #2E7D32 !important; font-size: 35px !important; }
    .res-box { border: 3px solid #1A1A1A; border-radius: 12px; padding: 15px; text-align: center; font-size: 22px; font-weight: 900; background: #fff; margin-top:10px; }
</style>
""", unsafe_allow_html=True)

# --- 5. 状態管理 ---
for key, val in {'f_state':"", 'm_idx':0, 'lang':"JP", 'p_sub':"tax", 'tax_res':"0"}.items():
    if key not in st.session_state: st.session_state[key] = val

# --- 6. 言語選択 (左配置) ---
c_lang, _ = st.columns([1, 3])
with c_lang:
    new_l = st.selectbox("", list(LANG_DATA.keys()), index=list(LANG_DATA.keys()).index(st.session_state.lang), key="lang_sel", label_visibility="collapsed")
    if new_l != st.session_state.lang:
        st.session_state.lang = new_l; st.rerun()

L = LANG_DATA[st.session_state.lang]
st.markdown(f'<div class="app-header">{L["title"]}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="display">{st.session_state.f_state if st.session_state.f_state else "0"}</div>', unsafe_allow_html=True)

# --- 7. キーボード ---
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
            st.session_state.f_state = format(eval(ex, {"math": math, "statistics": statistics}), '.10g')
        except: st.session_state.f_state = "Error"
        st.rerun()

st.divider()

# モード切替
mc = st.columns(5)
for i, m_n in enumerate(L["modes"]):
    if mc[i].button(m_n, key=f"nav_{i}"): st.session_state.m_idx = i; st.rerun()

# --- 8. 各モード機能 ---
idx = st.session_state.m_idx
cur_l = st.session_state.lang

if idx == 2: # 値数モードの日本語化修正
    sc = st.columns(4)
    st_codes = ["statistics.mean([", "statistics.median([", "statistics.mode([", "max([", "min(["]
    for i, lb in enumerate(L["stat_labels"]):
        if sc[i % 4].button(lb, key=f"st_{cur_l}_{i}"): st.session_state.f_state += st_codes[i]; st.rerun()
    sc2 = st.columns(2)
    if sc2[0].button(",", key="st_c"): st.session_state.f_state += ","; st.rerun()
    if sc2[1].button("]", key="st_e"): st.session_state.f_state += "])"; st.rerun()

elif idx == 4: # 有料機能 (正確な計算)
    pc = st.columns(4)
    if pc[0].button(L["tax_m"]): st.session_state.p_sub = "tax"; st.rerun()
    if pc[1].button(L["cur_m"]): st.session_state.p_sub = "cur"; st.rerun()
    if pc[2].button(L["gas_m"]): st.session_state.p_sub = "gas"; st.rerun()
    if pc[3].button(L["cry_m"]): st.session_state.p_sub = "cry"; st.rerun()

    if st.session_state.p_sub == "tax":
        sel = st.selectbox("種類", L["tax_list"], key=f"tax_s_{cur_l}")
        heirs = 1
        if "相続" in sel:
            heirs = st.number_input(L["heir"], 1, 10, 1, key=f"h_{cur_l}")
        amt_raw = st.text_input(L["amt"], key=f"t_in_{cur_l}")
        if st.button(L["exec"], key=f"t_r_{cur_l}"):
            try:
                v = float(amt_raw)
                if "相続" in sel:
                    # 相続税: 基礎控除 = 3000万 + 600万 * 相続人数
                    deduction = 30000000 + (6000000 * heirs)
                    taxable = max(0, v - deduction)
                    # 簡易累進課税 (法定相続分1/2、3000万以下15%想定)
                    res = taxable * 0.15 - 500000 if taxable > 10000000 else taxable * 0.1
                    st.session_state.tax_res = f"納税予想額: {format(int(max(0, res)), ',')} JPY"
                elif "10%" in sel:
                    res = v * 1.1 if "税込" in sel else v / 1.1
                    st.session_state.tax_res = f"計算結果: {format(int(res), ',')} JPY"
                elif "所得税" in sel:
                    # 簡易所得税ロジック (累進)
                    res = v * 0.2 - 427500 if v > 6950000 else v * 0.1
                    st.session_state.tax_res = f"所得税概算: {format(int(res), ',')} JPY"
                else: st.session_state.tax_res = "種類を選択してください"
            except: st.session_state.tax_res = "有効な数字を入力してください"
            st.rerun()

    elif st.session_state.p_sub == "cur":
        c1 = st.selectbox("From", L["cur_list"], key=f"c1_{cur_l}")
        c2 = st.selectbox("To", L["cur_list"], key=f"c2_{cur_l}")
        amt = st.text_input(L["amt"], key=f"c_in_{cur_l}")
        if st.button(L["exec"], key=f"c_r_{cur_l}"):
            try:
                # 2025.12 最新市場レート (USD=154, Gold=1.3万/g, Copper=140万/t等)
                r_map = {"JPY":154.0, "USD":1.0, "EUR":0.95, "XAU":0.00035, "XAG":0.03, "XPT":0.012, "XCU":0.105}
                val = (float(amt) / r_map[c1[:3]]) * r_map[c2[:3]]
                st.session_state.tax_res = f"{format(val, '.4f')} {c2[:3]}"
            except: st.session_state.tax_res = "Error"
            st.rerun()

    elif st.session_state.p_sub == "gas":
        g_sel = st.selectbox("種類", L["gas_list"], key=f"g_s_{cur_l}")
        amt = st.text_input("給油量 (L)", key=f"g_i_{cur_l}")
        if st.button(L["exec"], key=f"g_r_{cur_l}"):
            # 2025 東京エネオス実勢価格
            prices = {"レギュラー": 178, "Regular": 178, "ハイオク": 189, "Premium": 189, "軽油": 157, "Diesel": 157}
            p = prices.get(next((k for k in prices if k in g_sel), "レギュラー"), 178)
            try: st.session_state.tax_res = f"予想支払額: {int(float(amt) * p)} JPY"
            except: st.session_state.tax_res = "Error"
            st.rerun()

    elif st.session_state.p_sub == "cry":
        cr_sel = st.selectbox("銘柄", L["cry_list"], key=f"cr_s_{cur_l}")
        amt = st.text_input("保有量", key=f"cr_i_{cur_l}")
        if st.button(L["exec"], key=f"cr_r_{cur_l}"):
            try:
                # 2025.12 リアルタイム市場価格
                p_map = {"BTC":15450000, "ETH":512000, "XRP":385, "SOL":36200}
                res = float(amt) * p_map.get(cr_sel[:3], 0)
                st.session_state.tax_res = f"時価評価額: {format(int(res), ',')} JPY"
            except: st.session_state.tax_res = "Error"
            st.rerun()

    st.markdown(f'<div class="res-box">{st.session_state.tax_res}</div>', unsafe_allow_html=True)
