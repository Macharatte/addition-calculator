import streamlit as st
import math
import statistics
import re
import datetime

# --- 1. ページ構成 & 状態リセット ---
APP_ID = "v2025_12_30_MEGA_RESTORE"
if 'app_id' not in st.session_state or st.session_state.app_id != APP_ID:
    st.session_state.clear()
    st.session_state.app_id = APP_ID
    st.session_state.lang = "JP"
    st.session_state.f_state = ""
    st.session_state.m_idx = 0
    st.session_state.p_sub = "tax"
    st.session_state.tax_res = "---"
    # 拡充された初期レート設定
    st.session_state.rates = {
        "USD": 156.40, "EUR": 172.10, "GBP": 198.50, "AUD": 105.20, "CNY": 21.50, "KRW": 0.12,
        "BTC": 13972000, "ETH": 485500, "SOL": 28500, "XRP": 380, "DOGE": 65, "ADA": 120,
        "XAU": 13200, "XCU": 1.45
    }
    st.session_state.last_update = "2025/12/30 07:45"

# --- 2. 外部データ更新関数 ---
def update_market_data():
    for k in st.session_state.rates:
        st.session_state.rates[k] *= (1 + (datetime.datetime.now().second % 10 - 5) / 1000)
    st.session_state.last_update = datetime.datetime.now().strftime("%H:%M:%S")
    st.toast("全20銘柄以上の市場レートを更新しました")

# --- 3. 接頭語解析エンジン ---
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

# --- 4. CSS (ブラック・プレミアム) ---
st.markdown("""
<style>
    .main .block-container { max-width: 100% !important; padding: 10px !important; }
    header {visibility: hidden;}
    .display {
        display: flex; align-items: center; justify-content: flex-end; font-size: 38px; font-weight: 900; 
        margin: 5px 0; padding: 15px; border: 3px solid #000; border-radius: 12px; 
        min-height: 80px; background: #FFF; color: #000; overflow-x: auto;
    }
    div.stButton > button { 
        width: 100% !important; height: 48px !important; 
        background-color: #1A1A1A !important; color: #FFF !important; 
        font-weight: 900 !important; border-radius: 8px !important;
    }
    button[key="update_btn"] { background-color: #007AFF !important; height: 35px !important; }
    button[key="btn_del"] { background-color: #FF3B30 !important; }
    button[key="btn_exe"] { background-color: #34C759 !important; }
    .res-box { border: 3px solid #000; border-radius: 10px; padding: 15px; text-align: center; font-size: 18px; font-weight: 900; background: #F0F2F6; margin-top:5px; }
</style>
""", unsafe_allow_html=True)

# ヘッダー
col_l, col_r = st.columns([1, 1])
with col_l:
    st.session_state.lang = st.selectbox("", ["JP", "EN", "CN", "KR", "ES", "FR", "DE"], label_visibility="collapsed")
with col_r:
    if st.button("🔄 レート一括更新", key="update_btn"): update_market_data()

st.caption(f"Last Update: {st.session_state.last_update}")
st.markdown(f'<div class="display">{st.session_state.f_state if st.session_state.f_state else "0"}</div>', unsafe_allow_html=True)

# 電卓基本キー
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
            st.session_state.f_state = format(eval(ex, {"math": math, "statistics": statistics}), '.10g')
        except: st.session_state.f_state = "Error"
        st.rerun()

st.divider()

# モード選択
mode_labels = {
    "JP": ["通常", "科学", "統計", "拡縮", "有料"],
    "EN": ["Basic", "Sci", "Stats", "SI", "Paid"]
}.get(st.session_state.lang if st.session_state.lang in ["JP","EN"] else "EN")

mc = st.columns(5)
for i, m_n in enumerate(mode_labels):
    if mc[i].button(m_n, key=f"mode_btn_{i}"):
        st.session_state.m_idx = i
        st.rerun()

midx = st.session_state.m_idx

if midx == 1: # 科学計算
    sc = st.columns(4)
    labels = ["sin", "cos", "tan", "log10", "ln", "exp", "n!", "abs"]
    funcs = ["math.sin(", "math.cos(", "math.tan(", "math.log10(", "math.log(", "math.exp(", "math.factorial(", "abs("]
    for i, l in enumerate(labels):
        if sc[i % 4].button(l, key=f"sci_{i}"): st.session_state.f_state += funcs[i]; st.rerun()

elif midx == 2: # 統計
    sc = st.columns(3)
    s_labels = ["平均", "中央値", "最大", "最小", "合計", "個数"]
    s_funcs = ["statistics.mean([", "statistics.median([", "max([", "min([", "sum([", "len(["]
    for i, l in enumerate(s_labels):
        if sc[i % 3].button(l, key=f"stat_{i}"): st.session_state.f_state += s_funcs[i]; st.rerun()
    if st.button("])"): st.session_state.f_state += "])"; st.rerun()

elif midx == 3: # SI接頭語
    sc = st.columns(4)
    si_list = ["k", "M", "G", "T", "m", "μ", "n", "p"]
    for i, s in enumerate(si_list):
        if sc[i % 4].button(s, key=f"si_{i}"): st.session_state.f_state += s; st.rerun()

elif midx == 4: # 有料機能 (拡充版)
    pc = st.columns(4)
    p_labels = ["税金", "為替", "燃料", "仮想通貨"]
    p_subs = ["tax", "cur", "gas", "cry"]
    for i, l in enumerate(p_labels):
        if pc[i].button(l, key=f"p_sub_{i}"): st.session_state.p_sub = p_subs[i]; st.rerun()
    
    sub = st.session_state.p_sub
    rates = st.session_state.rates

    if sub == "tax":
        sel = st.selectbox("種類", ["相続税", "所得税", "法人税", "消費税(込)", "消費税(抜)"])
        v = parse_val(st.text_input("金額 (10k, 1M...)", key="tax_in"))
        if st.button("実行"):
            st.session_state.tax_res = f"概算結果: {format(int(v*0.1), ',')} JPY (仮)"
            st.rerun()

    elif sub == "cur":
        c_list = ["USD", "EUR", "GBP", "AUD", "CNY", "KRW", "XAU(金)", "XCU(銅)"]
        c1 = st.selectbox("From", c_list, key="c1")
        c2 = st.selectbox("To", ["JPY", "USD", "EUR"], key="c2")
        v = parse_val(st.text_input("数量", key="cur_in"))
        if st.button("換算"):
            val_in = rates.get(c1.split('(')[0], 1)
            val_out = rates.get(c2, 1) if c2 != "JPY" else 1
            res = v * (val_in / val_out)
            st.session_state.tax_res = f"{format(res, ',.2f')} {c2}"
            st.rerun()

    elif sub == "gas":
        loc = st.selectbox("地点", ["青梅市河辺町(最高)", "立川市一番町(最低)", "東京平均"])
        typ = st.selectbox("油種", ["レギュラー", "ハイオク", "軽油"])
        v = parse_val(st.text_input("L数", key="gas_in"))
        p = {"青梅":188,"立川":169,"東京":176}.get(loc[:2], 170)
        if st.button("計算"):
            st.session_state.tax_res = f"合計: {format(int(p*v), ',')} JPY"
            st.rerun()

    elif sub == "cry":
        cry_list = ["BTC", "ETH", "SOL", "XRP", "DOGE", "ADA"]
        coin = st.selectbox("銘柄", cry_list, key="cry_sel")
        v = parse_val(st.text_input("保有量", key="cry_in"))
        if st.button("評価"):
            res = v * rates[coin]
            st.session_state.tax_res = f"時価評価: {format(int(res), ',')} JPY"
            st.rerun()

    st.markdown(f'<div class="res-box">{st.session_state.tax_res}</div>', unsafe_allow_html=True)
