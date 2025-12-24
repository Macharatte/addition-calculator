import streamlit as st
import math
import statistics
import datetime
import requests # リアルタイムレート取得用

# --- ページ設定 ---
st.set_page_config(page_title="Python Calculator Pro", layout="centered")

# --- デザインCSS ---
st.markdown("""
<style>
    :root { --bg-page: #FFFFFF; --text-display: #000000; --btn-bg: #000000; --btn-text: #FFFFFF; --btn-border: #000000; }
    @media (prefers-color-scheme: dark) { :root { --bg-page: #000000; --text-display: #FFFFFF; --btn-bg: #FFFFFF; --btn-text: #000000; --btn-border: #FFFFFF; } }
    .main .block-container { max-width: 95% !important; padding: 5px 2px !important; background-color: var(--bg-page) !important; }
    header {visibility: hidden;}
    .display-container {
        display: flex; align-items: center; justify-content: flex-end;
        font-size: 55px; font-weight: 900; margin-bottom: 10px; padding: 10px; 
        border-bottom: 5px solid var(--text-display); min-height: 100px; color: var(--text-display);
    }
    div.stButton > button {
        width: 100% !important; height: 75px !important; border-radius: 8px !important;
        background-color: var(--btn-bg) !important; color: var(--btn-text) !important;
        border: 2px solid var(--btn-border) !important; transition: none !important;
    }
    div.stButton > button p { color: var(--btn-text) !important; white-space: nowrap !important; font-weight: 900; font-size: 18px; }
    
    /* 有料版限定デザイン */
    .premium-btn div.stButton > button { background-color: #FFD700 !important; color: #000000 !important; border-color: #B8860B !important; }
    .premium-btn div.stButton > button p { color: #000000 !important; }
    
    .del-btn div.stButton > button { background-color: #FF4B4B !important; }
    .eq-btn div.stButton > button { background-color: #2e7d32 !important; }
</style>
""", unsafe_allow_html=True)

# --- 為替レート取得関数 ---
@st.cache_data(ttl=3600) # 1時間はキャッシュして速度を維持
def get_rate(base_currency="JPY"):
    try:
        # 無料のAPIを使用（キーなしで動くデモ用URLですが、本番は登録推奨）
        url = f"https://open.er-api.com/v6/latest/{base_currency}"
        data = requests.get(url).json()
        return data["rates"]
    except:
        return {"USD": 0.0067, "EUR": 0.0061, "GBP": 0.0052, "CNY": 0.048} # エラー時の予備レート

# --- 状態管理 ---
ss = st.session_state
if 'formula' not in ss: ss.formula = ""
if 'mode' not in ss: ss.mode = "通常"
if 'last_was_equal' not in ss: ss.last_was_equal = False
if 'currency_select' not in ss: ss.currency_select = False

st.markdown('<div style="text-align:center; font-weight:900; font-size:26px; color:var(--text-display);">PYTHON CALCULATOR 2 (PREMIUM)</div>', unsafe_allow_html=True)
st.markdown(f'<div class="display-container"><span>{ss.formula if ss.formula else "0"}</span></div>', unsafe_allow_html=True)

# --- ロジック ---
def on_click(char):
    if char == "＝":
        try:
            f = ss.formula.replace('×', '*').replace('÷', '/').replace('−', '-').replace('m', '-')
            ss.formula = format(eval(f, {"math": math, "statistics": statistics, "abs": abs}), '.10g')
            ss.last_was_equal = True
        except: ss.formula = "Error"
    elif char == "delete": ss.formula = ""
    elif "税込" in char:
        try:
            rate = 1.10 if "10%" in char else 1.08
            ss.formula = format(float(eval(ss.formula.replace('×', '*').replace('÷', '/').replace('−', '-'))) * rate, '.10g')
            ss.last_was_equal = True
        except: ss.formula = "Error"
    elif "→JPY" in char:
        currency = char.split("→")[0]
        rates = get_rate("JPY")
        # レートの逆数をとって計算（1円が何ドルか、から、1ドルが何円かを算出）
        try:
            val = float(eval(ss.formula.replace('×', '*').replace('÷', '/').replace('−', '-')))
            jpy_rate = 1 / rates[currency]
            ss.formula = format(val * jpy_rate, '.10g')
            ss.last_was_equal = True
            ss.currency_select = False
        except: ss.formula = "Error"
    else:
        if ss.last_was_equal: ss.formula = ""; ss.last_was_equal = False
        ss.formula += str(char)

# --- メインキーパッド ---
main_btns = ["7","8","9","π","√","+","4","5","6","e","^^","−","1","2","3","i","(-)","×","0","00",".","(",")","÷"]
cols = st.columns(6)
for i, b in enumerate(main_btns):
    with cols[i % 6]:
        if st.button(b, key=f"k{i}"): on_click(b); st.rerun()

# --- 下部ボタン ---
st.write("") 
bot_c1, bot_c2 = st.columns(2)
with bot_c1:
    st.markdown('<div class="del-btn">', unsafe_allow_html=True); st.button("delete", use_container_width=True, on_click=lambda: on_click("delete"))
with bot_c2:
    st.markdown('<div class="eq-btn">', unsafe_allow_html=True); st.button("＝", use_container_width=True, on_click=lambda: on_click("＝"))

st.markdown('<hr style="margin:15px 0; opacity:0.3;">', unsafe_allow_html=True)

# --- モード切替 ---
m_cols = st.columns(5)
modes = ["通常", "科学計算", "巨数", "値数", "有料機能"]
for i, m in enumerate(modes):
    if m_cols[i].button(m, key=f"m{i}"): ss.mode = m; ss.currency_select = False; st.rerun()

# --- 👑 専門職モードの中身 ---
if ss.mode == "有料機能":
    st.markdown('<div style="color:var(--text-display); font-weight:bold;">PREMIUM: 専門職モード</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="premium-btn">', unsafe_allow_html=True)
        if st.button("税込(10%)"): on_click("税込(10%)"); st.rerun()
    with c2:
        st.markdown('<div class="premium-btn">', unsafe_allow_html=True)
        if st.button("税込(8%)"): on_click("税込(8%)"); st.rerun()
    with c3:
        st.markdown('<div class="premium-btn">', unsafe_allow_html=True)
        # 為替レートボタン：押すと選択肢を表示
        if st.button("為替レート"): ss.currency_select = not ss.currency_select; st.rerun()

    # 通貨選択ボタン（為替レートが押された時だけ表示）
    if ss.currency_select:
        st.info("変換したい通貨を選んでください（現在の入力値を日本円に換算します）")
        currencies = ["USD", "EUR", "GBP", "CNY", "KRW", "AUD", "CAD", "SGD"]
        c_cols = st.columns(4)
        for i, curr in enumerate(currencies):
            with c_cols[i % 4]:
                if st.button(f"{curr}→JPY", key=f"curr{i}"): on_click(f"{curr}→JPY"); st.rerun()
