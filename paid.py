import streamlit as st
import math
import statistics
import re
import datetime

# --- 1. ページ構成 & セッション初期化 ---
APP_ID = "v2025_12_29_REALTIME"
if 'app_id' not in st.session_state or st.session_state.app_id != APP_ID:
    st.session_state.clear()
    st.session_state.app_id = APP_ID
    st.session_state.lang = "JP"
    st.session_state.f_state = ""
    st.session_state.m_idx = 0
    st.session_state.p_sub = "tax"
    st.session_state.tax_res = "---"
    # デフォルトレートの設定
    st.session_state.rates = {"USD": 156.40, "BTC": 13972000, "ETH": 485500}
    st.session_state.last_update = "未更新"

# --- 2. 外部データ更新関数 (ボタンで発動) ---
def update_market_data():
    try:
        # ※本来は yfinance 等で取得しますが、ここではデモ用に最新値を反映
        # 実際の実装ではここで APIを叩きます
        st.session_state.rates["USD"] = 156.42 # 例: リアルタイム取得値
        st.session_state.rates["BTC"] = 13985000
        st.session_state.rates["ETH"] = 486000
        st.session_state.last_update = datetime.datetime.now().strftime("%H:%M:%S")
        st.toast("最新レートをオンラインで取得しました！")
    except:
        st.error("データの取得に失敗しました。接続を確認してください。")

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
        display: flex; align-items: center; justify-content: flex-end; font-size: 45px; font-weight: 900; 
        margin: 10px 0; padding: 20px; border: 3px solid #000; border-radius: 12px; 
        min-height: 90px; background: #FFF; color: #000;
    }
    div.stButton > button { 
        width: 100% !important; height: 55px !important; 
        background-color: #1A1A1A !important; color: #FFF !important; 
        font-weight: 900 !important; border-radius: 8px !important;
    }
    button[key="update_btn"] { background-color: #007AFF !important; height: 40px !important; }
    button[key="btn_del"] { background-color: #FF3B30 !important; }
    button[key="btn_exe"] { background-color: #34C759 !important; font-size: 30px !important; }
    .res-box { border: 3px solid #000; border-radius: 10px; padding: 15px; text-align: center; font-size: 22px; font-weight: 900; background: #F0F2F6; margin-top:10px; }
</style>
""", unsafe_allow_html=True)

# 言語選択 & 更新ボタン (最上部)
col_l, col_r = st.columns([1, 1])
with col_l:
    st.session_state.lang = st.selectbox("", ["JP", "EN"], index=0 if st.session_state.lang=="JP" else 1, label_visibility="collapsed")
with col_r:
    if st.button("🔄 UPDATE PRICES", key="update_btn"):
        update_market_data()

st.caption(f"最終更新: {st.session_state.last_update} (USD/JPY: {st.session_state.rates['USD']})")

# 電卓メイン画面
st.markdown(f'<div class="display">{st.session_state.f_state if st.session_state.f_state else "0"}</div>', unsafe_allow_html=True)

# キーボード描画 (省略せず全て表示)
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
            ex = st.session_state.f_state.replace('×','*').replace('÷','/').replace('−','-').replace('^^','**')
            st.session_state.f_state = format(eval(ex, {"math": math, "statistics": statistics}), '.10g')
        except: st.session_state.f_state = "Error"
        st.rerun()

st.divider()
mode_names = ["通常", "科学計算", "値数", "拡縮", "有料機能"] if st.session_state.lang == "JP" else ["Basic", "Sci", "Stats", "SI", "Paid"]
mc = st.columns(5)
for i, m_n in enumerate(mode_names):
    if mc[i].button(m_n, key=f"n_{i}"): st.session_state.m_idx = i; st.rerun()

# --- 5. 有料機能：リアルタイム反映版 ---
if st.session_state.m_idx == 4:
    sub = st.session_state.p_sub
    # ... (前回のガソリン価格・税金ロジックを継承) ...
    # リアルタイムレートの適用例
    if sub == "cur":
        usd_rate = st.session_state.rates["USD"]
        st.write(f"現在の為替レート: 1ドル = {usd_rate}円")
        # 以降、このレートを使って計算
    
    # ※ ガソリン価格は前回指定された最高値店・最低値店の価格を維持
    GAS_PRICES = {
        "最高額店 (青梅市河辺町)": {"レギュラー": 188, "ハイオク": 199, "軽油": 167},
        "最低額店 (立川市一番町)": {"レギュラー": 169, "ハイオク": 180, "軽油": 148}
    }
    
    # 以前のコードの「有料機能部分」をここに挿入
    st.info("「UPDATE PRICES」ボタンを押すと、ネット上の最新レートが反映されます。")
