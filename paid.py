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

# --- 究極のCSS（OSモード連動カラー・巨大ボタン） ---
st.markdown("""
<style>
    .main .block-container { max-width: 100% !important; padding: 10px !important; }
    header {visibility: hidden;}
    
    /* モード連動カラー設定 */
    :root {
        --bg-color: #FFFFFF;
        --text-color: #000000;
        --btn-bg: #000000;
        --btn-text: #FFFFFF;
    }
    @media (prefers-color-scheme: dark) {
        :root {
            --bg-color: #000000;
            --text-color: #FFFFFF;
            --btn-bg: #FFFFFF;
            --btn-text: #000000;
        }
    }

    .app-title-box {
        text-align: center; font-size: 26px; font-weight: 900; 
        color: var(--text-color); border-bottom: 3px solid; margin-bottom: 15px;
    }

    .display-container {
        display: flex; align-items: center; justify-content: flex-end;
        font-size: 42px; font-weight: 900; margin-bottom: 15px; padding: 15px; 
        border: 2px solid var(--text-color); border-radius: 10px; min-height: 100px;
        color: var(--text-color); word-break: break-all;
    }
    
    /* ボタンの共通設定 */
    div.stButton > button {
        width: 100% !important;
        height: 60px !important;
        font-weight: 900 !important;
        font-size: 20px !important;
        background-color: var(--btn-bg) !important;
        color: var(--btn-text) !important;
        border: 1px solid var(--text-color) !important;
        border-radius: 8px !important;
    }
    
    [data-testid="stHorizontalBlock"] { gap: 5px !important; }

    /* DELETEボタン（赤固定） */
    div.stButton > button[key="btn_del_main"] {
        background-color: #FF4B4B !important; color: white !important; height: 85px !important; font-size: 26px !important; border: none !important;
    }

    /* ＝ボタン（緑固定） */
    div.stButton > button[key="btn_exe_main"] {
        background-color: #28a745 !important; color: white !important; height: 85px !important; font-size: 45px !important; border: none !important;
    }
    
    .tax-result-box {
        background-color: rgba(128,128,128,0.1); border-radius: 8px; padding: 20px; margin-top: 15px;
        text-align: center; font-size: 26px; font-weight: 900; color: var(--text-color); border: 4px solid var(--text-color);
    }
</style>
""", unsafe_allow_html=True)

# --- ロジック関数 ---
def parse_val(text):
    if not text: return 0.0
    s = str(text).replace(',', '').strip()
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
    try: return total if total != 0 else float(text.replace('Error','0'))
    except: return 0.0

def calc_inheritance(assets, heirs):
    exemption = 30000000 + (6000000 * heirs)
    taxable = assets - exemption
    if taxable <= 0: return 0
    share = taxable / heirs
    def get_step(a):
        if a <= 10000000: return a * 0.10
        elif a <= 30000000: return a * 0.15 - 500000
        elif a <= 50000000: return a * 0.20 - 2000000
        elif a <= 100000000: return a * 0.30 - 7000000
        elif a <= 200000000: return a * 0.40 - 17000000
        elif a <= 300000000: return a * 0.45 - 27000000
        elif a <= 600000000: return a * 0.50 - 42000000
        else: return a * 0.55 - 72000000
    return get_step(share) * heirs

def calc_gift(amt, is_special):
    target = amt - 1100000
    if target <= 0: return 0
    if is_special:
        if target <= 2000000: r, d = 0.10, 0
        elif target <= 4000000: r, d = 0.15, 100000
        elif target <= 6000000: r, d = 0.20, 300000
        elif target <= 10000000: r, d = 0.30, 900000
        elif target <= 15000000: r, d = 0.40, 1900000
        elif target <= 30000000: r, d = 0.45, 2650000
        elif target <= 45000000: r, d = 0.50, 4150000
        else: r, d = 0.55, 6400000
    else:
        if target <= 2000000: r, d = 0.10, 0
        elif target <= 3000000: r, d = 0.15, 100000
        elif target <= 4000000: r, d = 0.20, 250000
        elif target <= 6000000: r, d = 0.30, 650000
        elif target <= 10000000: r, d = 0.40, 1250000
        elif target <= 15000000: r, d = 0.45, 1750000
        elif target <= 30000000: r, d = 0.50, 2500000
        else: r, d = 0.55, 4000000
    return target * r - d

# --- 状態管理 ---
if 'f_state' not in st.session_state: st.session_state.f_state = ""
if 'tax_res' not in st.session_state: st.session_state.tax_res = "結果表示"
if 'm_state' not in st.session_state: st.session_state.m_state = "通常"

# --- UI表示 ---
st.markdown('<div class="app-title-box">Python Calculator Premium</div>', unsafe_allow_html=True)
st.markdown(f'<div class="display-container">{st.session_state.f_state if st.session_state.f_state else "0"}</div>', unsafe_allow_html=True)

# 電卓
keys = ["7","8","9","π","√","+","4","5","6","e","^^","−","1","2","3","i","(-)","×","0","00",".","(",")","÷"]
cols = st.columns(6)
for i, k in enumerate(keys):
    if cols[i % 6].button(k, key=f"k_{i}"): st.session_state.f_state += k; st.rerun()

# DELETEと＝
c_exe = st.columns(2)
with c_exe[0]:
    if st.button("DELETE", key="btn_del_main"): st.session_state.f_state = ""; st.rerun()
with c_exe[1]:
    if st.button("＝", key="btn_exe_main"):
        try:
            f = st.session_state.f_state.replace('×','*').replace('÷','/').replace('−','-').replace('^^','**').replace('π', 'math.pi').replace('e', 'math.e').replace('√', 'math.sqrt').replace('mean', 'statistics.mean').replace('median', 'statistics.median').replace('mode', 'statistics.mode').replace('stdev', 'statistics.stdev')
            st.session_state.f_state = format(eval(f), '.10g')
        except: st.session_state.f_state = "Error"
        st.rerun()

st.divider()

# モード切替（税金と為替を分離）
modes = ["通常", "科学計算", "値数", "税金", "為替"]
mc = st.columns(5)
for i, m in enumerate(modes):
    if mc[i].button(m, key=f"m_{m}"): st.session_state.m_state = m; st.rerun()

# 各モードのUI
if st.session_state.m_state == "税金":
    t_type = st.selectbox("税金の種類", ["相続税", "贈与税(一般)", "贈与税(特例)", "固定資産税", "税込10%", "税込8%"])
    heirs = st.select_slider("法定相続人の数", options=list(range(1, 11))) if t_type == "相続税" else 1
    t_in = st.text_input("計算する金額 (例: 5億, 3000万)")
    if st.button("税金計算実行"):
        v = parse_val(t_in if t_in else st.session_state.f_state)
        if t_type == "相続税": r = calc_inheritance(v, heirs)
        elif "贈与税" in t_type: r = calc_gift(v, "特例" in t_type)
        elif t_type == "固定資産税": r = v * 0.014
        else: r = v * 1.1 if "10%" in t_type else v * 1.08
        st.session_state.tax_res = f"{t_type}: {format(int(r), ',')} 円"; st.rerun()
    st.markdown(f'<div class="tax-result-box">{st.session_state.tax_res}</div>', unsafe_allow_html=True)

elif st.session_state.m_state == "為替":
    c_list = ["JPY", "USD", "EUR", "CNY", "XAU (金1g)", "XAG (銀1g)"]
    cf, ct = st.selectbox("変換元", c_list), st.selectbox("変換先", c_list)
    cv = st.text_input("数量", value="1")
    if st.button("為替・貴金属 変換実行"):
        try:
            rates = requests.get("https://open.er-api.com/v6/latest/USD", timeout=3).json()['rates']
            m_usd = {"XAU": 2650.0/31.1035, "XAG": 31.0/31.1035}
            v_u = parse_val(cv) * m_usd[cf.split(' ')[0]] if cf.split(' ')[0] in m_usd else parse_val(cv) / rates[cf.split(' ')[0]]
            res = v_u / m_usd[ct.split(' ')[0]] if ct.split(' ')[0] in m_usd else v_u * rates[ct.split(' ')[0]]
            st.session_state.tax_res = f"結果: {format(res, ',.2f')} {ct.split(' ')[0]}"; st.rerun()
        except: st.error("データ取得失敗")
    st.markdown(f'<div class="tax-result-box">{st.session_state.tax_res}</div>', unsafe_allow_html=True)

elif st.session_state.m_state == "科学計算":
    sc = st.columns(4)
    for i, s in enumerate(["sin(", "cos(", "tan(", "log(", "abs(", "sqrt("]):
        if sc[i % 4].button(s, key=f"s_{s}"): st.session_state.f_state += s; st.rerun()

elif st.session_state.m_state == "値数":
    sc = st.columns(4)
    for i, (l, c) in enumerate([("平均", "mean(["), ("中央値", "median(["), ("最頻値", "mode(["), ("最大", "max(["), ("最小", "min(["), (",", ","), (")]", ")]")]):
        if sc[i % 4].button(l, key=f"st_{l}"): st.session_state.f_state += c; st.rerun()
