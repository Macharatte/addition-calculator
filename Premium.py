import streamlit as st
import math
import statistics
import re
import datetime
import urllib.request
import json

# --- 1. ページ基本設定 ---
st.set_page_config(page_title="Ultimate Calculator 2025", layout="centered")

# セッション状態の初期化（一括）
if 'f_state' not in st.session_state:
    st.session_state.f_state = ""
    st.session_state.m_idx = "通常"
    st.session_state.theme = "Dark"
    st.session_state.rates = {"USD": 156.40, "BTC": 13972000, "ETH": 485500}
    st.session_state.p_sub = "燃料"

# --- 2. リアルタイムデータ取得 ---
def fetch_realtime():
    try:
        # 為替
        with urllib.request.urlopen("https://open.er-api.com/v6/latest/USD") as response:
            data = json.loads(response.read().decode())
            st.session_state.rates["USD"] = data["rates"]["JPY"]
        # 仮想通貨
        cry_url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=jpy"
        with urllib.request.urlopen(cry_url) as response:
            c_data = json.loads(response.read().decode())
            st.session_state.rates["BTC"] = c_data["bitcoin"]["jpy"]
            st.session_state.rates["ETH"] = c_data["ethereum"]["jpy"]
        st.toast("最新レートを同期しました")
    except:
        st.error("同期失敗。バックアップを使用します。")

# --- 3. デザイン定義 ---
is_dark = st.session_state.theme == "Dark"
bg, txt, dbg = ("#1A1A1A", "#FFFFFF", "#333333") if is_dark else ("#F0F2F6", "#000000", "#FFFFFF")

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg}; color: {txt}; }}
    .display {{
        display: flex; align-items: center; justify-content: flex-end; font-size: 40px; font-weight: 900; 
        margin: 10px 0; padding: 20px; border: 3px solid {txt}; border-radius: 12px; 
        min-height: 100px; background: {dbg}; color: {txt};
    }}
    div.stButton > button {{ width: 100% !important; background-color: {dbg} !important; color: {txt} !important; border: 1px solid {txt} !important; height: 50px !important; font-weight: 900 !important; }}
    button[key="update_btn"] {{ background-color: #007AFF !important; color: white !important; border: none !important; }}
    button[key="theme_btn"] {{ background-color: #FF9500 !important; color: white !important; border: none !important; }}
</style>
""", unsafe_allow_html=True)

# --- 4. ヘッダー（更新とテーマ） ---
h1, h2, h3 = st.columns([1,1,1])
with h1: st.write(f"**MODE: {st.session_state.m_idx}**")
with h2: 
    if st.button("🔄 レート更新", key="update_btn"): fetch_realtime()
with h3:
    if st.button("☀️/🌙 表示切替", key="theme_btn"):
        st.session_state.theme = "Light" if is_dark else "Dark"
        st.rerun()

# --- 5. 電卓メインディスプレイ ---
st.markdown(f'<div class="display">{st.session_state.f_state if st.session_state.f_state else "0"}</div>', unsafe_allow_html=True)

# 基本テンキー
k_cols = st.columns(4)
btns = ["7","8","9","÷","4","5","6","×","1","2","3","−","0",".","π","+"]
for i, b in enumerate(btns):
    if k_cols[i%4].button(b, key=f"main_k_{b}"):
        st.session_state.f_state += b
        st.rerun()

c1, c2 = st.columns(2)
with c1:
    if st.button("CLEAR", key="clr"): st.session_state.f_state = ""; st.rerun()
with c2:
    if st.button("＝ (計算実行)", key="exe"):
        try:
            # 記号の置換
            calc = st.session_state.f_state.replace('×','*').replace('÷','/').replace('−','-').replace('π','math.pi').replace('√','math.sqrt')
            # SI接頭語の処理
            si_map = {"k":"*1e3", "M":"*1e6", "G":"*1e9", "T":"*1e12", "m":"*1e-3", "μ":"*1e-6", "n":"*1e-9", "p":"*1e-12"}
            for k, v in si_map.items(): calc = calc.replace(k, v)
            
            st.session_state.f_state = format(eval(calc, {"math": math, "statistics": statistics}), '.10g')
        except: st.session_state.f_state = "Error"
        st.rerun()

st.divider()

# --- 6. 全機能復元：モード切替タブ ---
m_tabs = st.tabs(["科学計算", "統計", "拡縮", "有料(燃料/為替/仮想)"])

# A. 科学計算モード
with m_tabs[0]:
    st.session_state.m_idx = "科学計算"
    s_cols = st.columns(4)
    s_map = {"sin":"math.sin(", "cos":"math.cos(", "tan":"math.tan(", "log":"math.log10(", "ln":"math.log(", "exp":"math.exp(", "√":"math.sqrt(", "abs":"abs("}
    for i, (l, f) in enumerate(s_map.items()):
        if s_cols[i%4].button(l, key=f"sci_{l}"):
            st.session_state.f_state += f; st.rerun()

# B. 統計モード
with m_tabs[1]:
    st.session_state.m_idx = "統計"
    st.caption("例: 10,20,30 と入力してから計算")
    t_cols = st.columns(3)
    t_map = {"平均":"statistics.mean([", "中央値":"statistics.median([", "最大":"max([", "最小":"min([", "合計":"sum([", "個数":"len(["}
    for i, (l, f) in enumerate(t_map.items()):
        if t_cols[i%3].button(l, key=f"stat_{l}"):
            st.session_state.f_state += f; st.rerun()
    if st.button("配列を閉じる ])", key="cl_stat"): st.session_state.f_state += "])"; st.rerun()

# C. 拡縮 (SI接頭語) モード
with m_tabs[2]:
    st.session_state.m_idx = "拡縮"
    i_cols = st.columns(4)
    for i, s in enumerate(["k", "M", "G", "T", "m", "μ", "n", "p"]):
        if i_cols[i%4].button(s, key=f"si_{s}"):
            st.session_state.f_state += s; st.rerun()

# D. 有料機能モード
with m_tabs[3]:
    st.session_state.m_idx = "有料機能"
    p_choice = st.radio("カテゴリ選択", ["燃料価格", "リアル為替", "仮想通貨時価"], horizontal=True)
    
    if p_choice == "燃料価格":
        loc = st.selectbox("店舗（2025/12/30 実勢）", ["青梅市河辺町(最高額店)", "立川市一番町(最低額店)", "東京平均"])
        price = 188 if "青梅" in loc else (169 if "立川" in loc else 176)
        lit = st.number_input("給油量 (L)", 1.0, 200.0, 50.0)
        st.subheader(f"合計: {int(price * lit):,} JPY")
        
    elif p_choice == "リアル為替":
        usd_rate = st.session_state.rates["USD"]
        st.write(f"現在レート: 1 USD = **{usd_rate:.2f} JPY**")
        val = st.number_input("USD入力", 0.0, 1000000.0, 100.0)
        st.subheader(f"換算: {val * usd_rate:,.0f} JPY")

    elif p_choice == "仮想通貨時価":
        coin = st.selectbox("銘柄", ["BTC", "ETH"])
        c_rate = st.session_state.rates[coin]
        st.write(f"現在価格: 1 {coin} = **{int(c_rate):,} JPY**")
        c_val = st.number_input(f"{coin} 保有量", 0.0, 100.0, 0.1, format="%.4f")
        st.subheader(f"評価額: {int(c_val * c_rate):,} JPY")
