import streamlit as st
import math
import statistics
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
    .main .block-container { max-width: 98% !important; padding: 10px !important; }
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
    
    /* ボタンの基本スタイル */
    div.stButton > button {
        width: 100% !important; height: 50px !important; border-radius: 6px !important;
        background-color: var(--btn-bg) !important; color: var(--btn-text) !important;
        font-weight: 900; font-size: 16px; border: 1px solid var(--text-display) !important;
    }
    
    /* DELETEとイコールの隙間を埋める設定 */
    div[data-testid="stHorizontalBlock"] { gap: 0.5rem !important; }
    .del-btn-big div.stButton > button { background-color: #FF4B4B !important; color: white !important; border: none !important; height: 70px !important; font-size: 22px !important; }
    .exe-btn-big div.stButton > button { background-color: #28a745 !important; color: white !important; border: none !important; height: 70px !important; font-size: 32px !important; }
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
    if total == 0:
        si = {'Q':1e30,'R':1e27,'Y':1e24,'Z':1e21,'E':1e18,'P':1e15,'T':1e12,'G':1e9,'M':1e6,'k':1e3,'h':1e2,'da':10,'d':0.1,'c':0.01,'m':0.001,'μ':1e-6,'n':1e-9,'p':1e-12,'f':1e-15,'a':1e-18,'z':1e-21,'y':1e-24,'r':1e-27,'q':1e-30}
        for k, v in si.items():
            if s.endswith(k):
                try: return float(s[:-len(k)]) * v
                except: pass
        try: return float(s)
        except: return 0.0
    return total

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

# --- UI表示 ---
st.markdown('<div class="app-title">Python Calculator Premium</div>', unsafe_allow_html=True)
st.markdown(f'<div class="display-container">{st.session_state.formula_state if st.session_state.formula_state else "0"}</div>', unsafe_allow_html=True)

# 電卓キー (6列)
keys = ["7","8","9","π","√","+","4","5","6","e","^^","−","1","2","3","i","(-)","×","0","00",".","(",")","÷"]
cols = st.columns(6)
for i, k in enumerate(keys):
    if cols[i % 6].button(k): st.session_state.formula_state += k; st.rerun()

# DELETEと＝を隙間なく大きく表示
c_big = st.columns(2)
with c_big[0]:
    st.markdown('<div class="del-btn-big">', unsafe_allow_html=True)
    if st.button("DELETE"): st.session_state.formula_state = ""; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
with c_big[1]:
    st.markdown('<div class="exe-btn-big">', unsafe_allow_html=True)
    if st.button("＝"):
        try:
            f = st.session_state.formula_state.replace('×','*').replace('÷','/').replace('−','-').replace('^^','**').replace('π', 'math.pi').replace('e', 'math.e').replace('√', 'math.sqrt').replace('mean', 'statistics.mean').replace('median', 'statistics.median').replace('mode', 'statistics.mode').replace('stdev', 'statistics.stdev')
            st.session_state.formula_state = format(eval(f), '.10g')
        except: st.session_state.formula_state = "Error"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# モード切替
modes = ["通常", "科学計算", "拡縮", "値数", "有料機能"]
mc = st.columns(5)
for i, m in enumerate(modes):
    if mc[i].button(m): st.session_state.mode_state = m; st.rerun()

if st.session_state.mode_state == "有料機能":
    sc1, sc2 = st.columns(2)
    if sc1.button("税金計算"): st.session_state.sub_mode = "税金"; st.rerun()
    if sc2.button("通貨・貴金属"): st.session_state.sub_mode = "通貨"; st.rerun()

    if st.session_state.sub_mode == "税金":
        t_type = st.selectbox("種類", ["相続税", "所得税", "法人税", "住民税", "固定資産税", "税込10%", "税込8%"])
        heirs = st.select_slider("法定相続人の数", options=list(range(1, 21)), value=1) if t_type == "相続税" else 1
        tax_in = st.text_input("金額(万/億 対応)")
        st.markdown(f'<div class="tax-result-box">{st.session_state.tax_res}</div>', unsafe_allow_html=True)
        if st.button("計算実行", key="tax_exe"):
            base = parse_japanese_and_si(tax_in if tax_in else st.session_state.formula_state)
            if t_type == "相続税": r = calculate_inheritance_tax_precise(base, heirs)
            elif t_type == "固定資産税": r = base * 0.014
            elif t_type == "税込10%": r = base * 1.1
            else: r = base * 1.08
            st.session_state.tax_res = f"{t_type}: {format(r, ',.0f')} 円"; st.rerun()

    elif st.session_state.sub_mode == "通貨":
        c_list = ["JPY", "USD", "EUR", "GBP", "CNY", "AUD", "XAU (金 1g)", "XAG (銀 1g)", "COPPER (銅 1kg)"]
        c_from, c_to = st.selectbox("変換元", c_list), st.selectbox("変換先", c_list)
        c_val = st.text_input("数量", value="1")
        if st.button("変換実行"):
            f_code, t_code = c_from.split(' ')[0], c_to.split(' ')[0]
            try:
                rates = requests.get("https://open.er-api.com/v6/latest/USD", timeout=3).json()['rates']
                m_usd = {"XAU": 2650.0/31.1035, "XAG": 31.0/31.1035, "COPPER": 9.2}
                v_usd = parse_japanese_and_si(c_val) * m_usd[f_code] if f_code in m_usd else parse_japanese_and_si(c_val) / rates[f_code]
                res = v_usd / m_usd[t_code] if t_code in m_usd else v_usd * rates[t_code]
                st.success(f"結果: {format(res, ',.2f')} {t_code}")
            except: st.error("通信エラー")

elif st.session_state.mode_state == "科学計算":
    sci_keys = ["sin(", "cos(", "tan(", "log(", "abs(", "sqrt(", "exp("]
    sc = st.columns(4)
    for i, s in enumerate(sci_keys):
        if sc[i % 4].button(s): st.session_state.formula_state += s; st.rerun()

elif st.session_state.mode_state == "拡縮":
    si_units = ["Q","R","Y","Z","E","P","T","G","M","k","h","da","d","c","m","μ","n","p","f","a","z","y","r","q"]
    uc = st.columns(6)
    for i, u in enumerate(si_units):
        if uc[i % 6].button(u):
            last_char = st.session_state.formula_state[-1] if st.session_state.formula_state else ""
            if last_char not in si_units:
                st.session_state.formula_state += u; st.rerun()

elif st.session_state.mode_state == "値数":
    stats = [("平均", "mean(["), ("中央値", "median(["), ("最頻値", "mode(["), ("最大", "max(["), ("最小", "min(["), (",", ","), (")]", ")]")]
    sc = st.columns(4)
    for i, (l, c) in enumerate(stats):
        if sc[i % 4].button(l): st.session_state.formula_state += c; st.rerun()
