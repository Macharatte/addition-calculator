import streamlit as st
import math
import requests

# --- ページ設定 ---
st.set_page_config(page_title="Python Calculator Premium", layout="centered")

# --- キーボード強制無効化スクリプト ---
st.components.v1.html("""
<script>
    const observer = new MutationObserver(() => {
        const inputs = window.parent.document.querySelectorAll('input[role="combobox"]');
        inputs.forEach(input => {
            input.setAttribute('readonly', 'true');
        });
    });
    observer.observe(window.parent.document.body, { childList: true, subtree: true });
</script>
""", height=0)

# --- デザインCSS ---
st.markdown("""
<style>
    :root { --bg-page: #FFFFFF; --text-display: #000000; --btn-bg: #000000; --btn-text: #FFFFFF; }
    @media (prefers-color-scheme: dark) { :root { --bg-page: #000000; --text-display: #FFFFFF; --btn-bg: #FFFFFF; --btn-text: #000000; } }
    .main .block-container { max-width: 95% !important; padding: 10px !important; }
    header {visibility: hidden;}
    .app-title { text-align: center; font-size: 26px; font-weight: 900; color: var(--text-display); border-bottom: 2px solid var(--text-display); margin-bottom: 10px; }
    .display-container {
        display: flex; align-items: center; justify-content: flex-end;
        font-size: 38px; font-weight: 900; margin-bottom: 15px; padding: 15px; 
        border-bottom: 5px solid var(--text-display); min-height: 90px; color: var(--text-display); word-break: break-all;
    }
    .tax-result-box {
        background-color: #f0f2f6; border-radius: 8px; padding: 15px; margin-bottom: 10px;
        text-align: center; font-size: 24px; font-weight: 900; color: #000000; border: 2px solid #000000;
    }
    @media (prefers-color-scheme: dark) { .tax-result-box { background-color: #1e1e1e; color: #ffffff; border: 2px solid #ffffff; } }
    div.stButton > button {
        width: 100% !important; height: 50px !important; border-radius: 6px !important;
        background-color: var(--btn-bg) !important; color: var(--btn-text) !important;
        font-weight: 900; font-size: 14px; border: 1px solid var(--text-display) !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 共通解析ロジック ---
def parse_val(text):
    if not text: return 0.0
    s = str(text).replace(',', '').strip()
    # 日本語単位の変換
    units = {"兆": 1e12, "億": 1e8, "万": 1e4, "千": 1e3}
    total = 0.0
    for u, v in units.items():
        if u in s:
            parts = s.split(u)
            if parts[0]:
                try: total += float(parts[0]) * v
                except: pass
            s = parts[1]
    if s:
        try: total += float(s)
        except: pass
    return total if total != 0 else (float(text) if str(text).replace('.','').isdigit() else 0.0)

# --- 相続税計算ロジック ---
def calc_inheritance(assets, heirs):
    # 基礎控除
    exemption = 30000000 + (6000000 * heirs)
    taxable = assets - exemption
    if taxable <= 0: return 0
    # 法定相続分での分割（均等配分）
    each_amt = taxable / heirs
    # 速算表適用
    if each_amt <= 10000000: tax = each_amt * 0.10
    elif each_amt <= 30000000: tax = each_amt * 0.15 - 500000
    elif each_amt <= 50000000: tax = each_amt * 0.20 - 2000000
    elif each_amt <= 100000000: tax = each_amt * 0.30 - 7000000
    elif each_amt <= 200000000: tax = each_amt * 0.40 - 17000000
    elif each_amt <= 300000000: tax = each_amt * 0.45 - 27000000
    elif each_amt <= 600000000: tax = each_amt * 0.50 - 42000000
    else: tax = each_amt * 0.55 - 72000000
    return tax * heirs

# --- 状態管理 ---
if 'formula_state' not in st.session_state: st.session_state.formula_state = ""
if 'tax_res' not in st.session_state: st.session_state.tax_res = "結果表示"
if 'mode_state' not in st.session_state: st.session_state.mode_state = "通常"
if 'sub_mode' not in st.session_state: st.session_state.sub_mode = "税金"

# --- メイン表示 ---
st.markdown('<div class="app-title">Python Calculator Premium</div>', unsafe_allow_html=True)
st.markdown(f'<div class="display-container">{st.session_state.formula_state if st.session_state.formula_state else "0"}</div>', unsafe_allow_html=True)

# 電卓
keys = ["7","8","9","+","4","5","6","−","1","2","3","×","0",".","＝","÷"]
cols = st.columns(4)
for i, k in enumerate(keys):
    if cols[i % 4].button(k):
        if k == "＝":
            try: st.session_state.formula_state = str(eval(st.session_state.formula_state.replace('×','*').replace('−','-').replace('÷','/')))
            except: st.session_state.formula_state = "Error"
        else: st.session_state.formula_state += k
        st.rerun()

if st.button("Clear"): st.session_state.formula_state = ""; st.rerun()

st.divider()

# モード
m_cols = st.columns(2)
if m_cols[0].button("通常モード"): st.session_state.mode_state = "通常"; st.rerun()
if m_cols[1].button("有料機能"): st.session_state.mode_state = "有料"; st.rerun()

if st.session_state.mode_state == "有料":
    t_cols = st.columns(2)
    if t_cols[0].button("税金計算"): st.session_state.sub_mode = "税金"; st.rerun()
    if t_cols[1].button("通貨・金"): st.session_state.sub_mode = "通貨"; st.rerun()

    if st.session_state.sub_mode == "税金":
        type_list = ["相続税", "固定資産税", "税込10%", "税込8%"]
        sel_type = st.selectbox("種類を選択", type_list)
        heirs_val = st.select_slider("相続人数", options=list(range(1, 11))) if sel_type == "相続税" else 1
        input_amt = st.text_input("金額(万, 億 対応)", value="0")
        
        if st.button("計算実行"):
            val = parse_val(input_amt)
            if sel_type == "相続税": res = calc_inheritance(val, heirs_val)
            elif sel_type == "固定資産税": res = val * 0.014
            elif sel_type == "税込10%": res = val * 1.1
            else: res = val * 1.08
            st.session_state.tax_res = f"{sel_type}: {format(int(res), ',')} 円"
            st.rerun()
        st.markdown(f'<div class="tax-result-box">{st.session_state.tax_res}</div>', unsafe_allow_html=True)

    elif st.session_state.sub_mode == "通貨":
        c_list = ["JPY", "USD", "EUR", "XAU (金)"]
        c_from = st.selectbox("変換元", c_list)
        c_to = st.selectbox("変換先", c_list)
        c_amt = st.text_input("数量", value="1")
        
        if st.button("変換実行"):
            f_code = c_from.split(' ')[0]
            t_code = c_to.split(' ')[0]
            rate = 1.0
            
            # API試行
            try:
                res = requests.get(f"https://open.er-api.com/v6/latest/{f_code}", timeout=2).json()
                rate = res['rates'][t_code]
            except:
                # 失敗時の予備レート
                backups = {
                    "USDJPY": 150.0, "JPYUSD": 0.0066,
                    "EURJPY": 160.0, "JPYEUR": 0.0062,
                    "XAUJPY": 13000.0 # 1g概算
                }
                rate = backups.get(f_code+t_code, 1.0)
                st.warning("通信エラーのため予備レートを使用しました。")

            if f_code == "XAU": rate /= 31.1035 if "XAU" in c_from else 1
            
            final = parse_val(c_amt) * rate
            st.success(f"結果: {format(final, ',.2f')} {t_code}")
