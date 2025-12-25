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

# --- 解析ロジック ---
def parse_japanese_and_si(text):
    if not text: return 0.0
    s = str(text).replace(',', '').split(':')[0].strip()
    units = {"兆": 1e12, "億": 1e8, "万": 1e4, "千": 1e3}
    total = 0.0
    temp_s = s
    for unit, val in units.items():
        if unit in temp_s:
            parts = temp_s.split(unit)
            if parts[0]:
                try: total += float(parts[0]) * val
                except: pass
            temp_s = parts[1]
    if temp_s:
        try: total += float(temp_s)
        except: pass
    return total if total != 0 else (float(s) if s.replace('.','').isdigit() else 0.0)

# --- 相続税 ---
def calculate_inheritance_tax_precise(total_assets, num_heirs):
    exemption = 30000000 + (6000000 * num_heirs)
    taxable_total = total_assets - exemption
    if taxable_total <= 0: return 0
    amount_per_heir = taxable_total / num_heirs
    def get_tax_step(amt):
        if amt <= 10000000: return amt * 0.10
        elif amt <= 30000000: return amt * 0.15 - 500000
        elif amt <= 50000000: return amt * 0.20 - 2000000
        elif amt <= 100000000: return amt * 0.30 - 7000000
        elif amt <= 200000000: return amt * 0.40 - 17000000
        elif amt <= 300000000: return amt * 0.45 - 27000000
        elif amt <= 600000000: return amt * 0.50 - 42000000
        else: return amt * 0.55 - 72000000
    return get_tax_step(amount_per_heir) * num_heirs

# --- 状態管理 ---
if 'formula_state' not in st.session_state: st.session_state.formula_state = ""
if 'tax_res' not in st.session_state: st.session_state.tax_res = "結果がここに表示されます"
if 'mode_state' not in st.session_state: st.session_state.mode_state = "通常"
if 'sub_mode' not in st.session_state: st.session_state.sub_mode = "税金"

# --- UI ---
st.markdown('<div class="app-title">Python Calculator Premium</div>', unsafe_allow_html=True)
st.markdown(f'<div class="display-container">{st.session_state.formula_state if st.session_state.formula_state else "0"}</div>', unsafe_allow_html=True)

# 電卓
keys = ["7","8","9","π","√","+","4","5","6","e","^^","−","1","2","3","i","(-)","×","0","00",".","(",")","÷"]
cols = st.columns(6)
for i, k in enumerate(keys):
    if cols[i % 6].button(k, key=f"k_{i}"): st.session_state.formula_state += k; st.rerun()

st.divider()

modes = ["通常", "科学計算", "拡縮", "値数", "有料機能"]
mc = st.columns(5)
for i, m in enumerate(modes):
    if mc[i].button(m): st.session_state.mode_state = m; st.rerun()

if st.session_state.mode_state == "有料機能":
    sc1, sc2 = st.columns(2)
    if sc1.button("税金計算"): st.session_state.sub_mode = "税金"; st.rerun()
    if sc2.button("通貨・貴金属"): st.session_state.sub_mode = "通貨"; st.rerun()

    if st.session_state.sub_mode == "税金":
        t_type = st.selectbox("税金の種類", ["相続税", "所得税", "法人税", "住民税", "固定資産税", "贈与税", "税込10%", "税込8%"])
        heirs = st.select_slider("法定相続人の数", options=list(range(1, 21)), value=1) if t_type == "相続税" else 0
        tax_in = st.text_input("金額入力", placeholder="例: 1.2億")
        if st.button("計算実行"):
            base = parse_japanese_and_si(tax_in if tax_in else st.session_state.formula_state)
            if t_type == "相続税": r = calculate_inheritance_tax_precise(base, heirs)
            elif t_type == "固定資産税": r = base * 0.014
            elif t_type == "税込10%": r = base * 1.1
            else: r = base * 1.08
            st.session_state.tax_res = f"{t_type}: {format(r, ',.0f')} 円"; st.rerun()
        st.markdown(f'<div class="tax-result-box">{st.session_state.tax_res}</div>', unsafe_allow_html=True)

    elif st.session_state.sub_mode == "通貨":
        c_list = ["JPY", "USD", "EUR", "GBP", "XAU (金)", "XAG (銀)"]
        c_from_raw = st.selectbox("変換元", c_list)
        c_to_raw = st.selectbox("変換先", c_list)
        c_val = st.text_input("数量入力", value="1")
        
        if st.button("レート変換を実行"):
            cf, ct = c_from_raw.split(' ')[0], c_to_raw.split(' ')[0]
            rate = None
            try:
                # リアルタイム取得
                res = requests.get(f"https://open.er-api.com/v6/latest/{cf}", timeout=5).json()
                if res.get("result") == "success": rate = res['rates'][ct]
            except:
                # API失敗時の予備（2024年初頭の参考固定レート）
                st.warning("リアルタイム通信に失敗しました。予備レートを使用します。")
                fixed_rates = {"USDJPY": 150.0, "EURJPY": 160.0, "GBPJPY": 190.0}
                if cf+ct in fixed_rates: rate = fixed_rates[cf+ct]
                elif ct+cf in fixed_rates: rate = 1/fixed_rates[ct+cf]
            
            if rate:
                if cf in ["XAU", "XAG"]: rate /= 31.1035 # 1g単価
                res_val = parse_japanese_and_si(c_val) * rate
                st.success(f"結果: {format(res_val, ',.2f')} {ct}")
            else: st.error("現在レートを取得できません。")
