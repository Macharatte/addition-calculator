import streamlit as st
import math
import statistics
import re

# --- 1. ページ設定 ---
st.set_page_config(page_title="Python Calculator Premium", layout="centered")

# --- 2. 接頭語解析関数 ---
SI_DICT = {'Q':1e30,'R':1e27,'Y':1e24,'Z':1e21,'E':1e18,'P':1e15,'T':1e12,'G':1e9,'M':1e6,'k':1e3,'h':1e2,'da':10,'d':0.1,'c':0.01,'m':0.001,'μ':1e-6,'n':1e-9,'p':1e-12,'f':1e-15,'a':1e-18,'z':1e-21,'y':1e-24,'r':1e-27,'q':1e-30}

def parse_val(s):
    if not s: return 0.0
    s = s.replace(',', '')
    # 末尾が接頭語か判定
    pattern = r'^([\d\.]+)([a-zA-Zμ]+)$'
    match = re.match(pattern, s.strip())
    if match:
        num, unit = match.groups()
        return float(num) * SI_DICT.get(unit, 1.0)
    return float(s)

# --- 3. 多言語リソース ---
LANG_DATA = {
    "JP": {
        "title": "Python Calculator Premium",
        "modes": ["通常", "科学計算", "値数", "拡縮", "有料機能"],
        "tax_m": "精密税計算", "cur_m": "為替・金銀銅", "gas_m": "東京エネオス", "cry_m": "仮想通貨",
        "exec": "計算実行", "amt": "金額/接頭語入力 (例: 10k)", "heir": "法定相続人の数",
        "tax_list": ["所得税(2025累進)", "相続税(2025精密)", "贈与税(一般)", "税込10%", "税抜10%"],
        "cur_list": ["JPY (日本円)", "USD (米国ドル)", "EUR (ユーロ)", "XAU (金/g)", "XAG (銀/g)", "XCU (銅/g)"],
        "gas_list": ["レギュラー (東京平均)", "ハイオク (東京平均)", "軽油 (東京平均)"],
        "cry_list": ["BTC (ビットコイン)", "ETH (イーサリアム)", "XRP (リップル)", "SOL (ソラナ)"]
    },
    "EN": {
        "title": "Python Calculator Premium",
        "modes": ["Basic", "Scientific", "Stats", "SI Prefix", "Paid"],
        "tax_m": "Tax Calc", "cur_m": "Forex/Metal", "gas_m": "Tokyo Fuel", "cry_m": "Crypto",
        "exec": "Calculate", "amt": "Amount (e.g. 10k)", "heir": "Heirs",
        "tax_list": ["Income Tax", "Inheritance", "Gift Tax", "VAT 10%", "Excl. 10%"],
        "cur_list": ["JPY", "USD", "EUR", "XAU", "XAG", "XCU"],
        "gas_list": ["Regular (Tokyo)", "Premium (Tokyo)", "Diesel (Tokyo)"],
        "cry_list": ["BTC", "ETH", "XRP", "SOL"]
    }
}

# --- 4. CSS (iPhoneモダンブラック) ---
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
        font-weight: 900 !important; border-radius: 10px !important; border: 1px solid #444 !important;
    }
    button[key="btn_del"] { background-color: #FF3B30 !important; border: none !important; }
    button[key="btn_exe"] { background-color: #34C759 !important; border: none !important; font-size: 30px !important; }
    .res-box { border: 3px solid #000; border-radius: 12px; padding: 20px; text-align: center; font-size: 24px; font-weight: 900; background: #F8F9FA; margin-top:15px; }
</style>
""", unsafe_allow_html=True)

# --- 5. 状態管理 ---
if 'lang' not in st.session_state: st.session_state.lang = "JP"
if 'f_state' not in st.session_state: st.session_state.f_state = ""
if 'm_idx' not in st.session_state: st.session_state.m_idx = 0
if 'p_sub' not in st.session_state: st.session_state.p_sub = "tax"
if 'tax_res' not in st.session_state: st.session_state.tax_res = "---"

# 言語選択（左上）
cl1, _ = st.columns([1, 3])
with cl1:
    new_l = st.selectbox("", ["JP", "EN"], index=0 if st.session_state.lang=="JP" else 1, key="l_sel", label_visibility="collapsed")
    if new_l != st.session_state.lang: st.session_state.lang = new_l; st.rerun()

L = LANG_DATA[st.session_state.lang]
st.markdown(f'<div style="text-align:center;font-size:24px;font-weight:900;">{L["title"]}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="display">{st.session_state.f_state if st.session_state.f_state else "0"}</div>', unsafe_allow_html=True)

# 電卓本体
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
            # 拡縮接頭語置換
            for s, v in sorted(SI_DICT.items(), key=lambda x:len(x[0]), reverse=True):
                ex = re.sub(f'(\\d){s}', f'\\1*{v}', ex)
            st.session_state.f_state = format(eval(ex, {"math": math, "statistics": statistics}), '.10g')
        except: st.session_state.f_state = "Error"
        st.rerun()

st.divider()
mc = st.columns(5)
for i, m_n in enumerate(L["modes"]):
    if mc[i].button(m_n, key=f"nav_{i}"): st.session_state.m_idx = i; st.rerun()

# --- 6. 有料機能 ---
if st.session_state.m_idx == 4:
    cur_l = st.session_state.lang
    pc = st.columns(4)
    if pc[0].button(L["tax_m"]): st.session_state.p_sub = "tax"; st.rerun()
    if pc[1].button(L["cur_m"]): st.session_state.p_sub = "cur"; st.rerun()
    if pc[2].button(L["gas_m"]): st.session_state.p_sub = "gas"; st.rerun()
    if pc[3].button(L["cry_m"]): st.session_state.p_sub = "cry"; st.rerun()

    if st.session_state.p_sub == "tax":
        sel = st.selectbox("メニュー", L["tax_list"], key=f"t_s_{cur_l}")
        heirs = 1
        if "相続" in sel: heirs = st.number_input(L["heir"], 1, 10, 1)
        amt_in = st.text_input(L["amt"], key=f"t_in_{cur_l}")
        if st.button(L["exec"]):
            try:
                v = parse_val(amt_in)
                if "相続" in sel:
                    taxable = max(0, v - (30000000 + 6000000 * heirs))
                    # 精密累進課税 (国税庁速算表準拠)
                    if taxable <= 10000000: res = taxable * 0.1
                    elif taxable <= 30000000: res = taxable * 0.15 - 500000
                    elif taxable <= 50000000: res = taxable * 0.2 - 2000000
                    elif taxable <= 100000000: res = taxable * 0.3 - 7000000
                    elif taxable <= 200000000: res = taxable * 0.4 - 17000000
                    elif taxable <= 600000000: res = taxable * 0.45 - 27000000
                    else: res = taxable * 0.55 - 72000000
                    st.session_state.tax_res = f"納税額予想: {format(int(res), ',')} JPY"
                elif "所得税" in sel:
                    if v <= 1950000: r, d = 0.05, 0
                    elif v <= 3300000: r, d = 0.1, 97500
                    elif v <= 6950000: r, d = 0.2, 427500
                    elif v <= 9000000: r, d = 0.23, 636000
                    else: r, d = 0.33, 1536000
                    st.session_state.tax_res = f"概算所得税: {format(int(v*r-d), ',')} JPY"
                elif "10%" in sel:
                    res = v * 1.1 if "税込" in sel else v / 1.1
                    st.session_state.tax_res = f"結果: {format(int(res), ',')} JPY"
            except: st.session_state.tax_res = "Error"
            st.rerun()

    elif st.session_state.p_sub == "cur":
        r_map = {"JPY":1.0, "USD":156.40, "EUR":164.20, "XAU":13200.0, "XAG":155.0, "XCU":1.45}
        c1 = st.selectbox("From", L["cur_list"], key="c1")
        c2 = st.selectbox("To", L["cur_list"], key="c2")
        amt = st.text_input(L["amt"], key="c_in")
        if st.button(L["exec"]):
            try:
                v = parse_val(amt)
                res = v * (r_map[c1[:3]] / r_map[c2[:3]])
                st.session_state.tax_res = f"{format(res, ',.3f')} {c2[:3]}"
            except: st.session_state.tax_res = "Error"
            st.rerun()

    elif st.session_state.p_sub == "gas":
        g_sel = st.selectbox("Station", L["gas_list"], key="gs")
        prices = {"レギュラー": 176, "Regular": 176, "ハイオク": 187, "Premium": 187, "軽油": 155, "Diesel": 155}
        amt = st.text_input(L["amt"], key="gi")
        if st.button(L["exec"]):
            try:
                p = prices.get(next(k for k in prices if k in g_sel), 176)
                st.session_state.tax_res = f"ENEOS予想額: {format(int(parse_val(amt)*p), ',')} JPY"
            except: st.session_state.tax_res = "Error"
            st.rerun()

    elif st.session_state.p_sub == "cry":
        p_map = {"BTC":13972000, "ETH":485500, "XRP":392, "SOL":34800}
        cr = st.selectbox("Coin", L["cry_list"], key="cr")
        amt = st.text_input(L["amt"], key="cri")
        if st.button(L["exec"]):
            try:
                res = parse_val(amt) * p_map.get(cr[:3], 0)
                st.session_state.tax_res = f"時価評価額: {format(int(res), ',')} JPY"
            except: st.session_state.tax_res = "Error"
            st.rerun()

    st.markdown(f'<div class="res-box">{st.session_state.tax_res}</div>', unsafe_allow_html=True)
