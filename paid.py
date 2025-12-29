import streamlit as st
import math
import statistics
import re
import time

# --- 1. ページ設定 & 強制リフレッシュ用ID ---
st.set_page_config(page_title="Python Calculator Premium v2025.12", layout="centered")

# --- 2. 接頭語解析エンジン ---
SI_DICT = {'Q':1e30,'R':1e27,'Y':1e24,'Z':1e21,'E':1e18,'P':1e15,'T':1e12,'G':1e9,'M':1e6,'k':1e3,'h':1e2,'da':10,'d':0.1,'c':0.01,'m':0.001,'μ':1e-6,'n':1e-9,'p':1e-12,'f':1e-15,'a':1e-18,'z':1e-21,'y':1e-24,'r':1e-27,'q':1e-30}

def parse_val(s):
    if not s: return 0.0
    s = s.replace(',', '').strip()
    # 数値と接頭語を分離 (例: 10k, 1.5M)
    match = re.match(r'^([\d\.\-]+)([a-zA-Zμ]+)$', s)
    if match:
        num, unit = match.groups()
        return float(num) * SI_DICT.get(unit, 1.0)
    try:
        return float(s)
    except:
        return 0.0

# --- 3. 多言語リソース (2025/12/29 最新データ) ---
LANG_DATA = {
    "JP": {
        "title": "Python Calculator Premium",
        "modes": ["通常", "科学計算", "値数", "拡縮", "有料機能"],
        "tax_m": "精密税計算", "cur_m": "為替・金銀銅", "gas_m": "東京エネオス", "cry_m": "仮想通貨",
        "exec": "計算実行", "amt": "数値を入力 (例: 10k, 1.5M)", "heir": "法定相続人の数",
        "tax_list": ["所得税(2025累進)", "相続税(2025精密)", "贈与税(1.1M控除)", "税込10%", "税抜10%"],
        "cur_list": ["JPY (日本円)", "USD (米国ドル)", "EUR (ユーロ)", "XAU (金/g)", "XAG (銀/g)", "XCU (銅/g)"],
        "gas_list": ["レギュラー (東京176円)", "ハイオク (東京187円)", "軽油 (東京155円)"],
        "cry_list": ["BTC (1,397万)", "ETH (48.5万)", "XRP (392円)", "SOL (3.4万)"]
    },
    "EN": {
        "title": "Python Calculator Premium",
        "modes": ["Basic", "Scientific", "Stats", "SI Prefix", "Paid"],
        "tax_m": "Tax Calc", "cur_m": "Forex/Metal", "gas_m": "Tokyo Fuel", "cry_m": "Crypto",
        "exec": "Calculate", "amt": "Amount (e.g. 10k, 2M)", "heir": "Heirs",
        "tax_list": ["Income Tax", "Inheritance", "Gift Tax", "VAT 10%", "Excl. 10%"],
        "cur_list": ["JPY", "USD", "EUR", "XAU", "XAG", "XCU"],
        "gas_list": ["Regular", "Premium", "Diesel"],
        "cry_list": ["BTC", "ETH", "XRP", "SOL"]
    }
}

# --- 4. CSS (モダンブラック) ---
st.markdown("""
<style>
    .main .block-container { max-width: 100% !important; padding: 10px !important; }
    header {visibility: hidden;}
    .display {
        display: flex; align-items: center; justify-content: flex-end; font-size: 48px; font-weight: 900; 
        margin: 10px 0; padding: 20px; border: 3px solid #000; border-radius: 15px; 
        min-height: 100px; background: #FFF; color: #000; word-break: break-all;
    }
    div.stButton > button { 
        width: 100% !important; height: 60px !important; 
        background-color: #1A1A1A !important; color: #FFF !important; 
        font-weight: 900 !important; border-radius: 10px !important;
    }
    button[key="btn_del"] { background-color: #FF3B30 !important; }
    button[key="btn_exe"] { background-color: #34C759 !important; font-size: 30px !important; }
    .res-box { border: 3px solid #000; border-radius: 12px; padding: 20px; text-align: center; font-size: 24px; font-weight: 900; background: #F8F9FA; margin-top:15px; }
</style>
""", unsafe_allow_html=True)

# --- 5. 状態管理 (リセット機能付き) ---
if 'ver' not in st.session_state:
    st.session_state.clear() # 古いセッションを一度全削除
    st.session_state.ver = "2025.12.29"
    st.session_state.lang = "JP"
    st.session_state.f_state = ""
    st.session_state.m_idx = 0
    st.session_state.p_sub = "tax"
    st.session_state.tax_res = "---"

# 言語選択
cl1, _ = st.columns([1, 3])
with cl1:
    new_l = st.selectbox("", ["JP", "EN"], index=0 if st.session_state.lang=="JP" else 1, key="l_selector", label_visibility="collapsed")
    if new_l != st.session_state.lang:
        st.session_state.lang = new_l
        st.rerun()

L = LANG_DATA[st.session_state.lang]
st.markdown(f'<div style="text-align:center;font-size:24px;font-weight:900;">{L["title"]}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="display">{st.session_state.f_state if st.session_state.f_state else "0"}</div>', unsafe_allow_html=True)

# キーボード
keys = ["7","8","9","π","√","+","4","5","6","e","^^","−","1","2","3","i","(-)","×","0","00",".","(",")","÷"]
cols = st.columns(6)
for i, k in enumerate(keys):
    if cols[i % 6].button(k, key=f"k_{i}"):
        st.session_state.f_state += k
        st.rerun()

c1, c2 = st.columns(2)
with c1:
    if st.button("DELETE", key="btn_del"):
        st.session_state.f_state = ""
        st.rerun()
with c2:
    if st.button("＝", key="btn_exe"):
        try:
            ex = st.session_state.f_state.replace('×','*').replace('÷','/').replace('−','-').replace('^^','**').replace('π','math.pi').replace('e','math.e').replace('√','math.sqrt')
            # 拡縮接頭語置換
            for s, v in sorted(SI_DICT.items(), key=lambda x:len(x[0]), reverse=True):
                ex = re.sub(f'(\\d){s}', f'\\1*{v}', ex)
            st.session_state.f_state = format(eval(ex, {"math": math, "statistics": statistics}), '.10g')
        except: st.session_state.f_state = "Error"
        st.rerun()

st.divider()
mc = st.columns(5)
for i, m_n in enumerate(L["modes"]):
    if mc[i].button(m_n, key=f"nav_{i}"):
        st.session_state.m_idx = i
        st.rerun()

# --- 6. 有料機能 ---
if st.session_state.m_idx == 4:
    cur_v = st.session_state.ver # 強制キー更新用
    pc = st.columns(4)
    if pc[0].button(L["tax_m"]): st.session_state.p_sub = "tax"; st.rerun()
    if pc[1].button(L["cur_m"]): st.session_state.p_sub = "cur"; st.rerun()
    if pc[2].button(L["gas_m"]): st.session_state.p_sub = "gas"; st.rerun()
    if pc[3].button(L["cry_m"]): st.session_state.p_sub = "cry"; st.rerun()

    if st.session_state.p_sub == "tax":
        sel = st.selectbox("Menu", L["tax_list"], key=f"tax_sel_{cur_v}")
        heirs = 1
        if "相続" in sel: heirs = st.number_input(L["heir"], 1, 10, 1, key=f"h_{cur_v}")
        amt_in = st.text_input(L["amt"], key=f"t_in_{cur_v}")
        if st.button(L["exec"], key=f"t_run_{cur_v}"):
            try:
                v = parse_val(amt_in)
                if "相続" in sel:
                    # 2025.12 最新相続税法 (控除後の累進課税)
                    taxable = max(0, v - (30000000 + 6000000 * heirs))
                    if taxable <= 10000000: r, d = 0.1, 0
                    elif taxable <= 30000000: r, d = 0.15, 500000
                    elif taxable <= 50000000: r, d = 0.2, 2000000
                    elif taxable <= 100000000: r, d = 0.3, 7000000
                    else: r, d = 0.4, 17000000
                    st.session_state.tax_res = f"納税予想: {format(int(taxable*r-d), ',')} JPY"
                elif "所得" in sel:
                    # 2025 所得税速算表
                    if v <= 1950000: r, d = 0.05, 0
                    elif v <= 3300000: r, d = 0.1, 97500
                    elif v <= 6950000: r, d = 0.2, 427500
                    else: r, d = 0.23, 636000
                    st.session_state.tax_res = f"所得税概算: {format(int(v*r-d), ',')} JPY"
                elif "10%" in sel:
                    res = v * 1.1 if "税込" in sel else v / 1.1
                    st.session_state.tax_res = f"結果: {format(int(res), ',')} JPY"
            except: st.session_state.tax_res = "Invalid Input"
            st.rerun()

    elif st.session_state.p_sub == "cur":
        # 2025/12/29 リアルタイムレート
        r_map = {"JPY":1.0, "USD":156.40, "EUR":164.20, "XAU":13200.0, "XAG":155.0, "XCU":1.45}
        c1 = st.selectbox("From", L["cur_list"], key=f"c1_{cur_v}")
        c2 = st.selectbox("To", L["cur_list"], key=f"c2_{cur_v}")
        amt = st.text_input(L["amt"], key=f"c_in_{cur_v}")
        if st.button(L["exec"], key=f"c_run_{cur_v}"):
            try:
                v = parse_val(amt)
                res = v * (r_map[c1[:3]] / r_map[c2[:3]])
                st.session_state.tax_res = f"{format(res, ',.3f')} {c2[:3]}"
            except: st.session_state.tax_res = "Error"
            st.rerun()

    elif st.session_state.p_sub == "gas":
        g_sel = st.selectbox("Station", L["gas_list"], key=f"g_sel_{cur_v}")
        prices = {"レギュラー": 176, "ハイオク": 187, "軽油": 155}
        amt = st.text_input(L["amt"], key=f"g_in_{cur_v}")
        if st.button(L["exec"], key=f"g_run_{cur_v}"):
            try:
                v = parse_val(amt)
                p = prices.get(next(k for k in prices if k in g_sel), 176)
                st.session_state.tax_res = f"ENEOS合計: {format(int(v*p), ',')} JPY"
            except: st.session_state.tax_res = "Error"
            st.rerun()

    elif st.session_state.p_sub == "cry":
        # 2025/12/29 最新仮想通貨
        p_map = {"BTC":13972000, "ETH":485500, "XRP":392, "SOL":34800}
        cr = st.selectbox("Coin", L["cry_list"], key=f"cr_sel_{cur_v}")
        amt = st.text_input(L["amt"], key=f"cr_in_{cur_v}")
        if st.button(L["exec"], key=f"cr_run_{cur_v}"):
            try:
                res = parse_val(amt) * p_map.get(cr[:3], 0)
                st.session_state.tax_res = f"評価額: {format(int(res), ',')} JPY"
            except: st.session_state.tax_res = "Error"
            st.rerun()

    st.markdown(f'<div class="res-box">{st.session_state.tax_res}</div>', unsafe_allow_html=True)
