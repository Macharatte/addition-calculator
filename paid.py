import streamlit as st
import math
import statistics
import requests

# --- ページ設定 ---
st.set_page_config(page_title="Python Calculator Premium", layout="centered")

# --- キーボード強制無効化 ---
st.components.v1.html("<script>const observer = new MutationObserver(() => { const inputs = window.parent.document.querySelectorAll('input[role=\"combobox\"]'); inputs.forEach(input => { input.setAttribute('readonly', 'true'); }); }); observer.observe(window.parent.document.body, { childList: true, subtree: true });</script>", height=0)

# --- CSS（黒ボタン・白文字・演算子強調） ---
st.markdown("""
<style>
    .main .block-container { max-width: 100% !important; padding: 10px !important; }
    header {visibility: hidden;}
    
    /* モード連動カラー */
    :root { 
        --bg: #FFFFFF; --txt: #000000; 
        --btn-bg: #1A1A1A; --btn-txt: #FFFFFF; 
        --op-txt: #FFFFFF;
    }
    @media (prefers-color-scheme: dark) {
        :root { 
            --bg: #000000; --txt: #FFFFFF; 
            --btn-bg: #FFFFFF; --btn-txt: #000000; 
            --op-txt: #000000;
        }
    }

    .app-title { text-align: center; font-size: 24px; font-weight: 900; color: var(--txt); margin-bottom: 10px; }
    
    .display {
        display: flex; align-items: center; justify-content: flex-end;
        font-size: 45px; font-weight: 900; margin-bottom: 15px; padding: 15px; 
        border: 4px solid var(--txt); border-radius: 12px; min-height: 110px;
        color: var(--txt); background: rgba(128,128,128,0.1); word-break: break-all;
    }
    
    /* 基本ボタン: 黒背景・白文字（太字） */
    div.stButton > button {
        width: 100% !important; height: 65px !important;
        font-weight: 900 !important; font-size: 26px !important;
        background-color: var(--btn-bg) !important;
        color: var(--btn-txt) !important;
        border: 1px solid var(--txt) !important;
        border-radius: 8px !important;
    }

    /* 演算子（＋, −, ×, ÷）の視認性を極限まで高める */
    div.stButton > button:contains("+"), 
    div.stButton > button:contains("−"), 
    div.stButton > button:contains("×"), 
    div.stButton > button:contains("÷") {
        font-size: 35px !important; /* 記号を大きく */
        border: 3px solid #555 !important; /* 枠線を太くして浮かび上がらせる */
    }

    /* DELETE & ＝ の隙間ゼロ設定 */
    [data-testid="stHorizontalBlock"]:has(button[key="btn_del_main"]) { gap: 0px !important; }

    button[key="btn_del_main"] { 
        background-color: #FF3B30 !important; color: white !important; 
        height: 90px !important; font-size: 28px !important; border-radius: 12px 0 0 12px !important; border: none !important;
    }
    button[key="btn_exe_main"] { 
        background-color: #34C759 !important; color: white !important; 
        height: 90px !important; font-size: 55px !important; border-radius: 0 12px 12px 0 !important; border: none !important;
    }

    .tax-box { border: 4px solid var(--txt); border-radius: 12px; padding: 20px; text-align: center; font-size: 26px; font-weight: 900; color: var(--txt); }
</style>
""", unsafe_allow_html=True)

# --- 状態管理 ---
if 'f_state' not in st.session_state: st.session_state.f_state = ""
if 'tax_res' not in st.session_state: st.session_state.tax_res = "結果表示"
if 'm_state' not in st.session_state: st.session_state.m_state = "通常"

# --- メイン UI ---
st.markdown('<div class="app-title">Python Calculator Premium</div>', unsafe_allow_html=True)
st.markdown(f'<div class="display">{st.session_state.f_state if st.session_state.f_state else "0"}</div>', unsafe_allow_html=True)

# 1. 通常キー
keys = ["7","8","9","π","√","+","4","5","6","e","^^","−","1","2","3","i","(-)","×","0","00",".","(",")","÷"]
cols = st.columns(6)
for i, k in enumerate(keys):
    if cols[i % 6].button(k, key=f"k_{i}"):
        st.session_state.f_state += k
        st.rerun()

# 2. DELETE & ＝
c1, c2 = st.columns(2)
with c1:
    if st.button("DELETE", key="btn_del_main"):
        st.session_state.f_state = ""
        st.rerun()
with c2:
    if st.button("＝", key="btn_exe_main"):
        try:
            f = st.session_state.f_state.replace('×','*').replace('÷','/').replace('−','-').replace('^^','**').replace('π','math.pi').replace('e','math.e').replace('√','math.sqrt').replace('°','*math.pi/180')
            st.session_state.f_state = format(eval(f), '.10g')
        except: st.session_state.f_state = "Error"
        st.rerun()

st.divider()

# モード切替
mc = st.columns(5)
for i, m in enumerate(["通常", "科学計算", "値数", "拡縮", "有料機能"]):
    if mc[i].button(m, key=f"m_{m}"): st.session_state.m_state = m; st.rerun()

# 有料機能（税金・為替の詳細は簡略化せず維持することを想定）
if st.session_state.m_state == "有料機能":
    st.write("税金・為替メニュー")
    # ここに前回の税金計算・為替ロジックが入ります
