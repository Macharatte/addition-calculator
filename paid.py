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

# --- CSS（OSモード連動カラー・巨大ボタン） ---
st.markdown("""
<style>
    .main .block-container { max-width: 100% !important; padding: 10px !important; }
    header {visibility: hidden;}
    
    :root { --bg-color: #FFFFFF; --text-color: #000000; --btn-bg: #000000; --btn-text: #FFFFFF; }
    @media (prefers-color-scheme: dark) { :root { --bg-color: #000000; --text-color: #FFFFFF; --btn-bg: #FFFFFF; --btn-text: #000000; } }

    .app-title-box { text-align: center; font-size: 26px; font-weight: 900; color: var(--text-color); border-bottom: 3px solid; margin-bottom: 15px; }

    .display-container {
        display: flex; align-items: center; justify-content: flex-end;
        font-size: 42px; font-weight: 900; margin-bottom: 15px; padding: 15px; 
        border: 2px solid var(--text-color); border-radius: 10px; min-height: 100px;
        color: var(--text-color); word-break: break-all;
    }
    
    div.stButton > button {
        width: 100% !important; height: 60px !important; font-weight: 900 !important; font-size: 20px !important;
        background-color: var(--btn-bg) !important; color: var(--btn-text) !important;
        border: 1px solid var(--text-color) !important; border-radius: 8px !important;
    }
    
    div.stButton > button[key="btn_del_main"] { background-color: #FF4B4B !important; color: white !important; height: 85px !important; font-size: 26px !important; border: none !important; }
    div.stButton > button[key="btn_exe_main"] { background-color: #28a745 !important; color: white !important; height: 85px !important; font-size: 45px !important; border: none !important; }
    
    .tax-result-box {
        background-color: rgba(128,128,128,0.1); border-radius: 8px; padding: 20px; margin-top: 15px;
        text-align: center; font-size: 26px; font-weight: 900; color: var(--text-color); border: 4px solid var(--text-color);
    }
</style>
""", unsafe_allow_html=True)

# --- 強化版：SI接頭語・日本語解析ロジック ---
def parse_val_advanced(text):
    if not text: return 0.0
    s = str(text).replace(',', '').strip()
    # 日本語単位
    units = {"兆": 1e12, "億": 1e8, "万": 1e4, "千": 1e3}
    # SI接頭語
    si = {'Q':1e30,'R':1e27,'Y':1e24,'Z':1e21,'E':1e18,'P':1e15,'T':1e12,'G':1e9,'M':1e6,'k':1e3,'h':1e2,'da':10,'d':0.1,'c':0.01,'m':0.001,'μ':1e-6,'n':1e-9,'p':1e-12,'f':1e-15,'a':1e-18,'z':1e-21,'y':1e-24}
    
    # 日本語解析
    total = 0.0
    temp_s = s
    for u, v in units.items():
        if u in temp_s:
            parts = temp_s.split(u)
            if parts[0]:
                try: total += float(parts[0]) * v
                except: pass
            temp_s = parts[1]
    if total > 0:
        if temp_s:
            try: total += float(temp_s)
            except: pass
        return total

    # SI接頭語解析
    for k, v in si.items():
        if s.endswith(k):
            try: return float(s[:-len(k)]) * v
            except: pass
    
    try: return float(s.replace('Error','0'))
    except: return 0.0

# --- 各種計算関数 ---
def calc_inheritance(assets, heirs):
    ex = 30000000 + (6000000 * heirs)
    taxable = assets - ex
    if taxable <= 0: return 0
    share = taxable / heirs
    def get_step(a):
        if a <= 1e7: return a * 0.1
        elif a <= 3e7: return a * 0.15 - 5e5
        elif a <= 5e7: return a * 0.2 - 2e6
        elif a <= 1e8: return a * 0.3 - 7e6
        elif a <= 2e8: return a * 0.4 - 1.7e7
        elif a <= 3e8: return a * 0.45 - 2.7e7
        elif a <= 6e8: return a * 0.5 - 4.2e7
        else: return a * 0.55 - 7.2e7
    return get_step(share) * heirs

def calc_income_tax(income):
    if income <= 1950000: return income * 0.05
    elif income <= 3300000: return income * 0.10 - 97500
    elif income <= 6950000: return income * 0.20 - 427500
    elif income <= 8999000: return income * 0.23 - 636000
    elif income <= 17999000: return income * 0.33 - 1536000
    elif income <= 39999000: return income * 0.40 - 2796000
    else: return income * 0.45 - 4796000

def calc_corp_tax(profit):
    if profit <= 8000000: return profit * 0.15
    else: return (8000000 * 0.15) + ((profit - 8000000) * 0.232)

def calc_gift(amt, is_special):
    t = amt - 1100000
    if t <= 0: return 0
    steps = [(2000000, 0.1, 0), (4000000, 0.15, 100000), (6000000, 0.2, 300000), (10000000, 0.3, 900000), (15000000, 0.4, 1900000), (30000000, 0.45, 2650000), (45000000, 0.5, 4150000)] if is_special else [(2000000, 0.1, 0), (3000000, 0.15, 100000), (4000000, 0.2, 250000), (6000000, 0.3, 650000), (10000000, 0.4, 1250000), (15000000, 0.45, 1750000), (30000000, 0.5, 2500000)]
    for limit, r, d in steps:
        if t <= limit: return t * r - d
    return t * 0.55 - (6400000 if is_special else 4000000)

# --- 状態管理 ---
if 'f_state' not in st.session_state: st.session_state.f_state = ""
if 'tax_res' not in st.session_state: st.session_state.tax_res = "結果表示"
if 'm_state' not in st.session_state: st.session_state.m_state = "通常"
if 'paid_sub' not in st.session_state: st.session_state.paid_sub = "税金"

# --- UI ---
st.markdown('<div class="app-title-box">Python Calculator Premium</div>', unsafe_allow_html=True)
st.markdown(f'<div class="display-container">{st.session_state.f_state if st.session_state.f_state else "0"}</div>', unsafe_allow_html=True)

# 電卓
keys = ["7","8","9","π","√","+","4","5","6","e","^^","−","1","2","3","i","(-)","×","0","00",".","(",")","÷"]
cols = st.columns(6)
for i, k in enumerate(keys):
    if cols[i % 6].button(k, key=f"k_{i}"): st.session_state.f_state += k; st.rerun()

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
mc = st.columns(5)
for i, m in enumerate(["通常", "科学計算", "値数", "拡縮", "有料機能"]):
    if mc[i].button(m, key=f"m_{m}"): st.session_state.m_state = m; st.rerun()

if st.session_state.m_state == "有料機能":
    sub_c = st.columns(2)
    if sub_c[0].button("税金計算メニュー"): st.session_state.paid_sub = "税金"; st.rerun()
    if sub_c[1].button("為替・貴金属メニュー"): st.session_state.paid_sub = "為替"; st.rerun()

    if st.session_state.paid_sub == "税金":
        t_type = st.selectbox("税種", ["所得税", "相続税", "法人税", "贈与税(一般)", "贈与税(特例)", "固定資産税", "税込10%", "税込8%"])
        heirs = st.select_slider("相続人数", options=list(range(1, 11))) if t_type == "相続税" else 1
        t_in = st.text_input("金額 (SI接頭語OK: 100k, 1M等)")
        if st.button("計算実行"):
            v = parse_val_advanced(t_in if t_in else st.session_state.f_state)
            if t_type == "所得税": r = calc_income_tax(v)
            elif t_type == "相続税": r = calc_inheritance(v, heirs)
            elif t_type == "法人税": r = calc_corp_tax(v)
            elif "贈与税" in t_type: r = calc_gift(v, "特例" in t_type)
            elif t_type == "固定資産税": r = v * 0.014
            else: r = v * 1.1 if "10%" in t_type else v * 1.08
            st.session_state.tax_res = f"{t_type}: {format(int(r), ',')} 円"; st.rerun()
        st.markdown(f'<div class="tax-result-box">{st.session_state.tax_res}</div>', unsafe_allow_html=True)

    elif st.session_state.paid_sub == "為替":
        c_list = ["JPY", "USD", "EUR", "GBP", "CNY", "AUD", "XAU (金1g)", "XAG (銀1g)", "COPPER (銅1kg)"]
        cf, ct = st.selectbox("元", c_list), st.selectbox("先", c_list)
        cv = st.text_input("数量 (SI接頭語OK)", value="1")
        if st.button("為替変換"):
            try:
                res_api = requests.get("https://open.er-api.com/v6/latest/USD", timeout=5).json()
                rates = res_api['rates']
                m_usd = {"XAU": 2650.0/31.1035, "XAG": 31.0/31.1035, "COPPER": 9.2}
                f_code, t_code = cf.split(' ')[0], ct.split(' ')[0]
                v_u = parse_val_advanced(cv) * m_usd[f_code] if f_code in m_usd else parse_val_advanced(cv) / rates[f_code]
                res = v_u / m_usd[t_code] if t_code in m_usd else v_u * rates[t_code]
                st.session_state.tax_res = f"結果: {format(res, ',.2f')} {t_code}"
            except: st.session_state.tax_res = "通信環境を確認してください"
            st.rerun()
        st.markdown(f'<div class="tax-result-box">{st.session_state.tax_res}</div>', unsafe_allow_html=True)

elif st.session_state.m_state == "科学計算":
    sc = st.columns(4)
    for i, s in enumerate(["sin(", "cos(", "tan(", "log(", "abs(", "sqrt("]):
        if sc[i % 4].button(s, key=f"s_{s}"): st.session_state.f_state += s; st.rerun()
elif st.session_state.m_state == "値数":
    sc = st.columns(4)
    for i, (l, c) in enumerate([("平均", "mean(["), ("中央値", "median(["), ("最頻値", "mode(["), ("最大", "max(["), ("最小", "min(["), (",", ","), (")]", ")]")]):
        if sc[i % 4].button(l, key=f"st_{l}"): st.session_state.f_state += c; st.rerun()
elif st.session_state.m_state == "拡縮":
    si_list = ["Q","R","Y","Z","E","P","T","G","M","k","h","da","d","c","m","μ","n","p","f","a","z","y"]
    uc = st.columns(6)
    for i, u in enumerate(si_list):
        if uc[i % 6].button(u, key=f"si_{u}"): st.session_state.f_state += u; st.rerun()
