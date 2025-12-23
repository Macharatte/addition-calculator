import streamlit as st
import math
import statistics
import datetime

# --- ページ設定 ---
st.set_page_config(page_title="Python Calculator Pro", layout="centered")

# --- デザインCSS（反転・1行表示・有料感の演出） ---
st.markdown("""
<style>
    :root {
        --bg-page: #FFFFFF; --text-display: #000000;
        --btn-bg: #000000; --btn-text: #FFFFFF; --btn-border: #000000;
    }
    @media (prefers-color-scheme: dark) {
        :root {
            --bg-page: #000000; --text-display: #FFFFFF;
            --btn-bg: #FFFFFF; --btn-text: #000000; --btn-border: #FFFFFF;
        }
    }
    .main .block-container { max-width: 95% !important; padding: 5px 2px !important; background-color: var(--bg-page) !important; }
    header {visibility: hidden;}
    
    .calc-title { text-align: center; font-weight: 900; font-size: 26px; color: var(--text-display); margin-bottom: 5px; }
    .display-container {
        display: flex; align-items: center; justify-content: flex-end;
        font-size: 55px; font-weight: 900; margin-bottom: 10px; padding: 10px; 
        border-bottom: 5px solid var(--text-display); min-height: 100px; color: var(--text-display);
    }

    /* ボタン共通 */
    div.stButton > button {
        width: 100% !important; height: 75px !important; border-radius: 8px !important;
        background-color: var(--btn-bg) !important; color: var(--btn-text) !important;
        border: 2px solid var(--btn-border) !important; transition: none !important;
    }
    div.stButton > button p { color: var(--btn-text) !important; white-space: nowrap !important; font-weight: 900; font-size: 18px; }

    /* 有料版専用ボタンの装飾（ゴールド系） */
    .premium-btn div.stButton > button {
        background-color: #FFD700 !important; color: #000000 !important; border-color: #B8860B !important;
    }
    .premium-btn div.stButton > button p { color: #000000 !important; }

    .del-btn div.stButton > button { background-color: #FF4B4B !important; border-color: #FF4B4B !important; }
    .eq-btn div.stButton > button { background-color: #2e7d32 !important; border-color: #2e7d32 !important; }
    .del-btn div.stButton > button p, .eq-btn div.stButton > button p { color: #FFFFFF !important; }
</style>
""", unsafe_allow_html=True)

# --- 状態管理 ---
ss = st.session_state
if 'formula' not in ss: ss.formula = ""
if 'mode' not in ss: ss.mode = "通常"
if 'last_was_equal' not in ss: ss.last_was_equal = False
if 'history' not in ss: ss.history = []

# --- 【重要】無料/有料切り替え（テスト用） ---
st.sidebar.title("💳 収益化テスト設定")
is_premium = st.sidebar.checkbox("有料会員（電卓2）として実行", value=False)

# タイトル
title_suffix = " 2 (PREMIUM)" if is_premium else " 1 (FREE)"
st.markdown(f'<div class="calc-title">PYTHON CALCULATOR{title_suffix}</div>', unsafe_allow_html=True)

# ディスプレイ
st.markdown(f'<div class="display-container"><span>{ss.formula if ss.formula else "0"}</span></div>', unsafe_allow_html=True)

# --- ロジック ---
def on_click(char):
    if char == "＝":
        try:
            f = ss.formula.replace('×', '*').replace('÷', '/').replace('−', '-').replace('m', '-')
            res = eval(f, {"math": math, "statistics": statistics, "abs": abs})
            res_str = format(res, '.10g')
            ss.history.insert(0, {"f": ss.formula, "r": res_str, "t": datetime.datetime.now().strftime("%H:%M")})
            ss.formula = res_str; ss.last_was_equal = True
        except: ss.formula = "Error"
    elif char == "delete": ss.formula = ""
    elif "税込" in char:
        try:
            rate = 1.10 if "10%" in char else 1.08
            res = float(eval(ss.formula.replace('×', '*').replace('÷', '/').replace('−', '-'))) * rate
            ss.formula = format(res, '.10g'); ss.last_was_equal = True
        except: ss.formula = "Error"
    elif char == "USD→JPY":
        try:
            res = float(ss.formula) * 150 # 固定レート（例）
            ss.formula = format(res, '.10g'); ss.last_was_equal = True
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
    st.markdown('<div class="del-btn">', unsafe_allow_html=True)
    if st.button("delete", use_container_width=True): on_click("delete"); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
with bot_c2:
    st.markdown('<div class="eq-btn">', unsafe_allow_html=True)
    if st.button("＝", use_container_width=True): on_click("＝"); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<hr style="margin:15px 0; opacity:0.3;">', unsafe_allow_html=True)

# --- モード切替 ---
modes = ["通常", "科学計算", "巨数", "値数", "履歴"]
if is_premium:
    modes.append("👑 専門職") # 有料版限定モード

m_cols = st.columns(len(modes))
for i, m in enumerate(modes):
    if m_cols[i].button(m, key=f"m{i}"): ss.mode = m; st.rerun()

# --- 有料版・無料版の条件分岐表示 ---
if ss.mode != "通常":
    st.markdown(f'<div style="color:var(--text-display); font-weight:bold; margin-bottom:5px;">MODE: {ss.mode}</div>', unsafe_allow_html=True)
    
    if ss.mode == "👑 専門職":
        # 有料版限定の強力な計算ボタン
        st.write("プレミアム機能：税率・通貨計算")
        e_cols = st.columns(4)
        premium_features = ["税込(10%)", "税込(8%)", "USD→JPY", "履歴PDF保存"]
        for i, b in enumerate(premium_features):
            with e_cols[i]:
                st.markdown('<div class="premium-btn">', unsafe_allow_html=True)
                if st.button(b, key=f"p{i}"): on_click(b); st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
    
    elif ss.mode == "履歴":
        # 無料版は3件、有料版は無制限
        limit = 100 if is_premium else 3
        if not is_premium: st.info("無料版は直近3件のみ表示されます。")
        for i, item in enumerate(ss.history[:limit]):
            if st.button(f"{item['f']} = {item['r']} ({item['t']})", key=f"h{i}", use_container_width=True):
                ss.formula = item['r']; ss.mode = "通常"; st.rerun()
    else:
        # 既存のモード（科学計算・巨数など）
        extra = []
        if ss.mode == "巨数": extra = ["Q", "R", "Y", "Z", "E", "P", "T", "G", "M", "k", "h", "da", "d", "c", "m", "μ", "n", "p", "f", "a", "z", "y", "r", "q"]
        elif ss.mode == "科学計算": extra = ["sin(", "cos(", "tan(", "°", "abs(", "log("]
        elif ss.mode == "値数": extra = ["平均([", "中央値([", "最頻値([", "最大([", "最小([", "])", "偏差値(", "期待値(", ","]
        e_cols = st.columns(6)
        for i, b in enumerate(extra):
            with e_cols[i % 6]:
                if st.button(b, key=f"e{i}"): on_click(b); st.rerun()
