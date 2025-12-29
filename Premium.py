import streamlit as st
import math
import statistics
import urllib.request
import json
import datetime

# --- 1. ページ基本設定 ---
st.set_page_config(page_title="Ultra Calculator 2025", layout="centered")

# --- 2. 状態管理（Session State）の強制初期化 ---
if 'display' not in st.session_state:
    st.session_state.display = ""
if 'rates' not in st.session_state:
    st.session_state.rates = {"USD": 156.40, "BTC": 13972000, "ETH": 485500}
if 'theme' not in st.session_state:
    st.session_state.theme = "Dark"

# --- 3. リアルタイムデータ取得関数 ---
def update_rates():
    try:
        # 為替取得
        with urllib.request.urlopen("https://open.er-api.com/v6/latest/USD") as response:
            data = json.loads(response.read().decode())
            st.session_state.rates["USD"] = data["rates"]["JPY"]
        # 仮想通貨取得
        cry_url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=jpy"
        with urllib.request.urlopen(cry_url) as response:
            c_data = json.loads(response.read().decode())
            st.session_state.rates["BTC"] = c_data["bitcoin"]["jpy"]
            st.session_state.rates["ETH"] = c_data["ethereum"]["jpy"]
        st.toast("市場データを更新しました！")
    except:
        st.error("ネットワークエラーが発生しました。")

# --- 4. デザイン (CSS) ---
is_dark = st.session_state.theme == "Dark"
bg, txt, dbg = ("#1A1A1A", "#FFFFFF", "#333333") if is_dark else ("#F0F2F6", "#000000", "#FFFFFF")

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg}; color: {txt}; }}
    .calc-display {{
        background-color: {dbg}; color: {txt};
        padding: 20px; border: 3px solid {txt}; border-radius: 12px;
        font-size: 45px; font-weight: 900; text-align: right;
        min-height: 100px; margin-bottom: 20px; overflow-x: auto;
    }}
    div.stButton > button {{
        width: 100% !important; height: 55px !important;
        font-weight: 900 !important; font-size: 18px !important;
        background-color: {dbg} !important; color: {txt} !important;
        border: 2px solid {txt} !important; border-radius: 10px !important;
    }}
    button[key="exe_btn"] {{ background-color: #34C759 !important; color: white !important; border: none !important; }}
    button[key="clr_btn"] {{ background-color: #FF3B30 !important; color: white !important; border: none !important; }}
</style>
""", unsafe_allow_html=True)

# --- 5. ヘッダー ---
h1, h2 = st.columns([1, 1])
with h1:
    if st.button("🔄 レート一括更新"):
        update_rates()
with h2:
    if st.button("☀️/🌙 テーマ切替"):
        st.session_state.theme = "Light" if is_dark else "Dark"
        st.rerun()

# --- 6. ディスプレイ表示 ---
st.markdown(f'<div class="calc-display">{st.session_state.display if st.session_state.display else "0"}</div>', unsafe_allow_html=True)

# --- 7. 電卓キーパッド (クリック時に即座に状態を更新) ---
# 行1
c1, c2, c3, c4 = st.columns(4)
if c1.button("7"): st.session_state.display += "7"; st.rerun()
if c2.button("8"): st.session_state.display += "8"; st.rerun()
if c3.button("9"): st.session_state.display += "9"; st.rerun()
if c4.button("÷"): st.session_state.display += "÷"; st.rerun()

# 行2
c5, c6, c7, c8 = st.columns(4)
if c5.button("4"): st.session_state.display += "4"; st.rerun()
if c6.button("5"): st.session_state.display += "5"; st.rerun()
if c7.button("6"): st.session_state.display += "6"; st.rerun()
if c8.button("×"): st.session_state.display += "×"; st.rerun()

# 行3
c9, c10, c11, c12 = st.columns(4)
if c9.button("1"): st.session_state.display += "1"; st.rerun()
if c10.button("2"): st.session_state.display += "2"; st.rerun()
if c11.button("3"): st.session_state.display += "3"; st.rerun()
if c12.button("−"): st.session_state.display += "−"; st.rerun()

# 行4
c13, c14, c15, c16 = st.columns(4)
if c13.button("0"): st.session_state.display += "0"; st.rerun()
if c14.button("."): st.session_state.display += "."; st.rerun()
if c15.button("π"): st.session_state.display += "math.pi"; st.rerun()
if c16.button("+"): st.session_state.display += "+"; st.rerun()

# クリアと計算実行
b1, b2 = st.columns(2)
if b1.button("CLEAR (全消去)", key="clr_btn"):
    st.session_state.display = ""
    st.rerun()

if b2.button("＝ (計算結果を表示)", key="exe_btn"):
    try:
        # 記号置換
        expr = st.session_state.display.replace('×', '*').replace('÷', '/').replace('−', '-')
        # 接頭語置換
        si_prefixes = {"k":"*1e3", "M":"*1e6", "G":"*1e9", "T":"*1e12", "m":"*1e-3", "μ":"*1e-6", "n":"*1e-9", "p":"*1e-12"}
        for k, v in si_prefixes.items(): expr = expr.replace(k, v)
        
        # 計算実行
        result = eval(expr, {"math": math, "statistics": statistics})
        st.session_state.display = format(result, '.10g')
    except:
        st.session_state.display = "Error"
    st.rerun()

st.divider()

# --- 8. 全機能タブ (科学・統計・拡縮・有料) ---
tab_sci, tab_stat, tab_si, tab_paid = st.tabs(["🧬 科学計算", "📊 統計", "📏 拡縮(SI)", "💎 有料機能"])

with tab_sci:
    st.write("関数選択（ディスプレイに追加されます）")
    sc1, sc2, sc3, sc4 = st.columns(4)
    if sc1.button("sin"): st.session_state.display += "math.sin("; st.rerun()
    if sc2.button("cos"): st.session_state.display += "math.cos("; st.rerun()
    if sc3.button("tan"): st.session_state.display += "math.tan("; st.rerun()
    if sc4.button("√"): st.session_state.display += "math.sqrt("; st.rerun()
    sc5, sc6, sc7, sc8 = st.columns(4)
    if sc5.button("log"): st.session_state.display += "math.log10("; st.rerun()
    if sc6.button("ln"): st.session_state.display += "math.log("; st.rerun()
    if sc7.button("abs"): st.session_state.display += "abs("; st.rerun()
    if sc8.button(" ( ) "): st.session_state.display += "("; st.rerun()
    if st.button(" ) を閉じる"): st.session_state.display += ")"; st.rerun()

with tab_stat:
    st.write("統計関数（例: 10,20,30 と入力して閉じる）")
    st1, st2, st3 = st.columns(3)
    if st1.button("平均"): st.session_state.display += "statistics.mean(["; st.rerun()
    if st2.button("中央値"): st.session_state.display += "statistics.median(["; st.rerun()
    if st3.button("合計"): st.session_state.display += "sum(["; st.rerun()
    if st.button("配列を閉じる ]) "): st.session_state.display += "])"; st.rerun()

with tab_si:
    st.write("SI接頭語（数値の後につけて計算できます）")
    si1, si2, si3, si4 = st.columns(4)
    if si1.button("k (キロ)"): st.session_state.display += "k"; st.rerun()
    if si2.button("M (メガ)"): st.session_state.display += "M"; st.rerun()
    if si3.button("G (ギガ)"): st.session_state.display += "G"; st.rerun()
    if si4.button("T (テラ)"): st.session_state.display += "T"; st.rerun()
    si5, si6, si7, si8 = st.columns(4)
    if si5.button("m (ミリ)"): st.session_state.display += "m"; st.rerun()
    if si6.button("μ (マイクロ)"): st.session_state.display += "μ"; st.rerun()
    if si7.button("n (ナノ)"): st.session_state.display += "n"; st.rerun()
    if si8.button("p (ピコ)"): st.session_state.display += "p"; st.rerun()

with tab_paid:
    mode = st.radio("機能選択", ["燃料価格(青梅・立川)", "リアル為替換算", "仮想通貨時価"], horizontal=True)
    if mode == "燃料価格(青梅・立川)":
        loc = st.selectbox("対象店舗", ["青梅市河辺町(最高額SS)", "立川市一番町(最低額SS)", "東京平均価格"])
        p = 188 if "青梅" in loc else (169 if "立川" in loc else 176)
        lit = st.number_input("給油量(L)", 1.0, 500.0, 50.0)
        st.subheader(f"合計金額: {int(p*lit):,} JPY")
    elif mode == "リアル為替換算":
        u = st.session_state.rates["USD"]
        st.write(f"現在レート: 1 USD = {u:.2f} 円")
        amt = st.number_input("ドル(USD)を入力", 0.0, 1000000.0, 100.0)
        st.subheader(f"日本円換算: {amt * u:,.0f} JPY")
    elif mode == "仮想通貨時価":
        coin = st.selectbox("銘柄", ["BTC", "ETH"])
        price = st.session_state.rates[coin]
        st.write(f"1 {coin} = {int(price):,} JPY")
        hold = st.number_input(f"{coin}の保有量", 0.0, 1000.0, 0.1, format="%.4f")
        st.subheader(f"現在価値: {int(hold * price):,} JPY")
