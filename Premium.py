import streamlit as st
import math
import statistics
import re
import datetime
import yfinance as yf

# --- 1. ページ構成 & 状態管理 ---
APP_ID = "v2025_12_30_YF_THEME"
if 'app_id' not in st.session_state or st.session_state.app_id != APP_ID:
    st.session_state.clear()
    st.session_state.app_id = APP_ID
    st.session_state.lang = "JP"
    st.session_state.f_state = ""
    st.session_state.m_idx = 0
    st.session_state.p_sub = "tax"
    st.session_state.tax_res = "---"
    st.session_state.theme = "Dark"  # デフォルトテーマ
    # 初期レート (API取得失敗時のバックアップ)
    st.session_state.rates = {"USD": 156.40, "BTC": 13972000, "ETH": 485500, "XAU": 13200}
    st.session_state.last_update = "未更新"

# --- 2. 本物のAPI連携 (yfinance) ---
def fetch_realtime_data():
    try:
        with st.spinner('世界市場から最新データを取得中...'):
            # 為替 (USD/JPY), 仮想通貨 (BTC-JPY, ETH-JPY), 金 (GC=F)
            tickers = {
                "USD": "JPY=X",
                "BTC": "BTC-JPY",
                "ETH": "ETH-JPY",
                "XAU": "GC=F" # 金先物(ドル建て)
            }
            data = yf.download(list(tickers.values()), period="1d", interval="1m").iloc[-1]
            
            st.session_state.rates["USD"] = float(data['Close', 'JPY=X'])
            st.session_state.rates["BTC"] = float(data['Close', 'BTC-JPY'])
            st.session_state.rates["ETH"] = float(data['Close', 'ETH-JPY'])
            # 金はドル建てなので円換算 (1トロイオンス=31.1035g)
            gold_usd_oz = float(data['Close', 'GC=F'])
            st.session_state.rates["XAU"] = (gold_usd_oz * st.session_state.rates["USD"]) / 31.1035
            
            st.session_state.last_update = datetime.datetime.now().strftime("%H:%M:%S")
            st.toast("1円単位で最新データを反映しました！")
    except Exception as e:
        st.error(f"API取得エラー: {e}")

# --- 3. デザイン定義 (テーマ切替) ---
is_dark = st.session_state.theme == "Dark"
bg_color = "#1A1A1A" if is_dark else "#F0F2F6"
text_color = "#FFFFFF" if is_dark else "#000000"
disp_bg = "#333333" if is_dark else "#FFFFFF"
btn_bg = "#333333" if is_dark else "#DDDDDD"

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg_color}; color: {text_color}; }}
    .display {{
        display: flex; align-items: center; justify-content: flex-end; font-size: 38px; font-weight: 900; 
        margin: 5px 0; padding: 15px; border: 3px solid {text_color}; border-radius: 12px; 
        min-height: 80px; background: {disp_bg}; color: {text_color};
    }}
    div.stButton > button {{ 
        width: 100% !important; background-color: {btn_bg} !important; color: {text_color} !important; 
        font-weight: 900 !important; border: 1px solid {text_color} !important;
    }}
    button[key="update_btn"] {{ background-color: #007AFF !important; color: white !important; }}
    button[key="theme_btn"] {{ background-color: #FF9500 !important; color: white !important; }}
    .res-box {{ border: 2px solid {text_color}; border-radius: 10px; padding: 10px; background: {disp_bg}; }}
</style>
""", unsafe_allow_html=True)

# --- 4. ヘッダー (API & テーマ) ---
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    st.session_state.lang = st.selectbox("", ["JP", "EN"], label_visibility="collapsed")
with col2:
    if st.button("🔄 リアル更新", key="update_btn"): fetch_realtime_data()
with col3:
    theme_label = "☀️ Light" if is_dark else "🌙 Dark"
    if st.button(theme_label, key="theme_btn"):
        st.session_state.theme = "Light" if is_dark else "Dark"
        st.rerun()

st.caption(f"最終更新: {st.session_state.last_update} | USD: {st.session_state.rates['USD']:.2f}円")

# --- 5. 電卓本体 ---
st.markdown(f'<div class="display">{st.session_state.f_state if st.session_state.f_state else "0"}</div>', unsafe_allow_html=True)

# 基本キー
keys = ["7","8","9","÷","4","5","6","×","1","2","3","−","0",".","π","+"]
cols = st.columns(4)
for i, k in enumerate(keys):
    if cols[i % 4].button(k, key=f"k_{i}"):
        st.session_state.f_state += k; st.rerun()

c1, c2 = st.columns(2)
with c1:
    if st.button("CLEAR", key="btn_del"): st.session_state.f_state = ""; st.rerun()
with c2:
    if st.button("＝", key="btn_exe"):
        try:
            ex = st.session_state.f_state.replace('×','*').replace('÷','/').replace('−','-')
            st.session_state.f_state = format(eval(ex), '.10g')
        except: st.session_state.f_state = "Error"
        st.rerun()

# --- 6. モード切替 ---
st.divider()
mc = st.columns(5)
modes = ["通常", "科学", "統計", "拡縮", "有料"]
for i, m in enumerate(modes):
    if mc[i].button(m, key=f"m_{i}"): st.session_state.m_idx = i; st.rerun()

if st.session_state.m_idx == 4: # 有料機能
    sub_c = st.columns(4)
    if sub_c[0].button("税金"): st.session_state.p_sub = "tax"; st.rerun()
    if sub_c[1].button("為替"): st.session_state.p_sub = "cur"; st.rerun()
    if sub_c[2].button("燃料"): st.session_state.p_sub = "gas"; st.rerun()
    if sub_c[3].button("仮想通貨"): st.session_state.p_sub = "cry"; st.rerun()

    sub = st.session_state.p_sub
    if sub == "cur":
        st.write("### 本物のリアルタイム為替換算")
        amt = st.text_input("金額 (例: 10k)", key="cur_in")
        v = 0.0
        # 接頭語解析
        if amt:
            match = re.match(r'^([\d\.]+)([a-zA-Z]+)$', amt)
            if match:
                num, unit = match.groups()
                v = float(num) * {"k":1e3, "M":1e6}.get(unit, 1)
            else: v = float(amt)
        
        res = v * st.session_state.rates["USD"]
        st.markdown(f'<div class="res-box">結果: {res:,.0f} JPY</div>', unsafe_allow_html=True)

    elif sub == "gas":
        st.write("### 青梅・立川 特定SS価格")
        loc = st.selectbox("地点", ["青梅市河辺町 (最高額店)", "立川市一番町 (最低額店)"])
        p = 188 if "青梅" in loc else 169
        st.info(f"現在の設定単価: {p}円/L")
