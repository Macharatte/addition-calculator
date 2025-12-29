import streamlit as st
import math
import statistics
import re

# --- 1. ページ構成 & キャッシュ強制リセット ---
APP_ID = "v2025_12_29_SPECIAL" # 以前のデータを破棄するためのキー
if 'app_id' not in st.session_state or st.session_state.app_id != APP_ID:
    st.session_state.clear()
    st.session_state.app_id = APP_ID
    st.session_state.lang = "JP"
    st.session_state.f_state = ""
    st.session_state.m_idx = 0
    st.session_state.p_sub = "tax"
    st.session_state.tax_res = "---"

# --- 2. 接頭語解析エンジン ---
SI_DICT = {'Q':1e30,'R':1e27,'Y':1e24,'Z':1e21,'E':1e18,'P':1e15,'T':1e12,'G':1e9,'M':1e6,'k':1e3,'h':1e2,'da':10,'d':0.1,'c':0.01,'m':0.001,'μ':1e-6,'n':1e-9,'p':1e-12,'f':1e-15,'a':1e-18,'z':1e-21,'y':1e-24,'r':1e-27,'q':1e-30}

def parse_val(s):
    if not s: return 0.0
    s = s.replace(',', '').strip()
    match = re.match(r'^([\d\.\-]+)([a-zA-Zμ]+)$', s)
    if match:
        num, unit = match.groups()
        return float(num) * SI_DICT.get(unit, 1.0)
    try: return float(s)
    except: return 0.0

# --- 3. データリソース ---
GAS_PRICES = {
    "最高額店 (青梅市河辺町)": {"レギュラー": 188, "ハイオク": 199, "軽油": 167},
    "最低額店 (立川市一番町)": {"レギュラー": 169, "ハイオク": 180, "軽油": 148},
    "東京 ENEOS 平均": {"レギュラー": 176, "ハイオク": 187, "軽油": 155}
}

LANG_DATA = {
    "JP": {
        "title": "Python Calculator Premium",
        "modes": ["通常", "科学計算", "値数", "拡縮", "有料機能"],
        "tax_m": "精密税計算", "cur_m": "為替・金銀銅", "gas_m": "ガソリン(東京特定)", "cry_m": "仮想通貨",
        "exec": "計算実行", "amt": "金額/数量 (例: 10k, 2M)", "heir": "法定相続人の数",
        "tax_list": ["相続税(2025精密)", "所得税(2025累進)", "贈与税(1.1M控除)", "税込10%", "税抜10%"],
        "cur_list": ["JPY (日本円)", "USD (米国ドル)", "EUR (ユーロ)", "XAU (金/g)", "XAG (銀/g)", "XCU (銅/g)"],
        "cry_list": ["BTC (1,397万)", "ETH (48.5万)", "XRP (392円)", "SOL (3.4万)"]
    },
    "EN": {
        "title": "Premium Calc v2.6",
        "modes": ["Basic", "Sci", "Stats", "SI", "Paid"],
        "tax_m": "Tax", "cur_m": "Fx/Metal", "gas_m": "Gas (Tokyo)", "cry_m": "Crypto",
        "exec": "Calculate", "amt": "Value (e.g. 10k)", "heir": "Heirs",
        "tax_list": ["Inheritance", "Income Tax", "Gift Tax", "VAT 10%", "Excl 10%"],
        "cur_list": ["JPY", "USD", "EUR", "XAU", "XAG", "XCU"],
        "cry_list": ["BTC", "ETH", "XRP", "SOL"]
    }
}

# --- 4. CSS スタイル ---
st.markdown("""
<style>
    .main .block-container { max-width: 100% !important; padding: 10px !important; }
    header {visibility: hidden;}
    .display {
        display: flex; align-items: center; justify-content: flex-end; font-size: 45px; font-weight: 900; 
        margin: 10px 0; padding: 20px; border: 3px solid #000; border-radius: 12px; 
        min-height: 90px; background: #FFF; color: #000;
    }
    div.stButton > button { 
        width: 100% !important; height: 55px !important; 
        background-color: #1A1A1A !important; color: #FFF !important; 
        font-weight: 900 !important; border-radius: 8px !important;
    }
    button[key="btn_del"] { background-color: #FF3B30 !important; }
    button[key="btn_exe"] { background-color: #34C759 !important; font-size: 30px !important; }
    .res-box { border: 3px solid #000; border-radius: 10px; padding: 15px; text-align: center; font-size: 22px; font-weight: 900; background: #F0F2F6; margin-top:10px; }
</style>
""", unsafe_allow_html=True)

# 言語選択（左）
cl, _ = st.columns([1, 3])
with cl:
    st.session_state.lang = st.selectbox("", ["JP", "EN"], index=0 if st.session_state.lang=="JP" else 1, label_visibility="collapsed")

L = LANG_DATA[st.session_state.lang]
st.markdown(f'<div style="text-align:center;font-size:22px;font-weight:900;">{L["title"]}</div>', unsafe_allow_html=True)
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
    if st.button("DELETE", key="btn_del"): st.session_state.f_state = ""; st.rerun()
with c2:
    if st.button("＝", key="btn_exe"):
        try:
            ex = st.session_state.f_state.replace('×','*').replace('÷','/').replace('−','-').replace('^^','**').replace('π','math.pi').replace('e','math.e').replace('√','math.sqrt')
            for s, v in sorted(SI_DICT.items(), key=lambda x:len(x[0]), reverse=True):
                ex = re.sub(f'(\\d){s}', f'\\1*{v}', ex)
            st.session_state.f_state = format(eval(ex, {"math": math, "statistics": statistics}), '.10g')
        except: st.session_state.f_state = "Error"
        st.rerun()

st.divider()
mc = st.columns(5)
for i, m_n in enumerate(L["modes"]):
    if mc[i].button(m_n, key=f"n_{i}"): st.session_state.m_idx = i; st.rerun()

# --- 5. 有料機能：2025年12月29日 最新データ ---
if st.session_state.m_idx == 4:
    pc = st.columns(4)
    if pc[0].button(L["tax_m"]): st.session_state.p_sub = "tax"; st.rerun()
    if pc[1].button(L["cur_m"]): st.session_state.p_sub = "cur"; st.rerun()
    if pc[2].button(L["gas_m"]): st.session_state.p_sub = "gas"; st.rerun()
    if pc[3].button(L["cry_m"]): st.session_state.p_sub = "cry"; st.rerun()

    if st.session_state.p_sub == "tax":
        sel = st.selectbox("項目", L["tax_list"], key="ts_1")
        h = 1
        if "相続" in sel: h = st.number_input(L["heir"], 1, 10, 1)
        v = parse_val(st.text_input(L["amt"], key="ti_1"))
        if st.button(L["exec"]):
            if "相続" in sel:
                taxable = max(0, v - (30000000 + 6000000 * h))
                if taxable <= 1e7: r, d = 0.1, 0
                elif taxable <= 3e7: r, d = 0.15, 5e5
                elif taxable <= 5e7: r, d = 0.2, 2e6
                elif taxable <= 1e8: r, d = 0.3, 7e6
                else: r, d = 0.4, 1.7e7
                st.session_state.tax_res = f"納税総額予想: {format(int(taxable*r-d), ',')} JPY"
            elif "10%" in sel:
                st.session_state.tax_res = f"結果: {format(int(v*1.1 if '税込' in sel else v/1.1), ',')} JPY"
            st.rerun()

    elif st.session_state.p_sub == "cur":
        # 2025/12/29 レート
        r_map = {"JPY":1.0, "USD":156.40, "EUR":164.20, "XAU":13200.0, "XAG":155.0, "XCU":1.45}
        c1 = st.selectbox("元", L["cur_list"], key="c1")
        c2 = st.selectbox("先", L["cur_list"], key="c2")
        v = parse_val(st.text_input(L["amt"], key="ci_2"))
        if st.button(L["exec"]):
            res = v * (r_map[c1[:3]] / r_map[c2[:3]])
            st.session_state.tax_res = f"{format(res, ',.3f')} {c2[:3]}"
            st.rerun()

    elif st.session_state.p_sub == "gas":
        loc = st.selectbox("地点選択", list(GAS_PRICES.keys()), key="gs_1")
        typ = st.selectbox("燃料種別", ["レギュラー", "ハイオク", "軽油"], key="gt_1")
        v = parse_val(st.text_input("給油量 (L)", key="gi_1"))
        if st.button(L["exec"]):
            p = GAS_PRICES[loc][typ]
            st.session_state.tax_res = f"{loc}\n{typ}: {p}円/L → 合計: {format(int(v*p), ',')} JPY"
            st.rerun()

    elif st.session_state.p_sub == "cry":
        p_map = {"BTC":13972000, "ETH":485500, "XRP":392, "SOL":34800}
        cr = st.selectbox("銘柄", L["cry_list"], key="cry_1")
        v = parse_val(st.text_input("保有量", key="ci_3"))
        if st.button(L["exec"]):
            res = v * p_map.get(cr[:3], 0)
            st.session_state.tax_res = f"時価評価: {format(int(res), ',')} JPY"
            st.rerun()

    st.markdown(f'<div class="res-box">{st.session_state.tax_res}</div>', unsafe_allow_html=True)
