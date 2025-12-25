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

# --- 強力なCSSカスタマイズ ---
st.markdown("""
<style>
    /* ページ全体の幅を最大化 */
    .main .block-container { max-width: 100% !important; padding: 10px !important; }
    header {visibility: hidden;}
    
    .app-title { text-align: center; font-size: 26px; font-weight: 900; border-bottom: 2px solid; margin-bottom: 10px; }
    .display-container {
        display: flex; align-items: center; justify-content: flex-end;
        font-size: 38px; font-weight: 900; margin-bottom: 15px; padding: 15px; 
        border-bottom: 5px solid; min-height: 90px; word-break: break-all;
    }
    
    /* ボタンの基本サイズ */
    div.stButton > button {
        width: 100% !important; height: 55px !important; font-weight: 900 !important; font-size: 18px !important;
    }
    
    /* DELETEとイコールを横いっぱいに広げるための設定 */
    div[data-testid="stHorizontalBlock"] { gap: 4px !important; }

    /* DELETEボタン（赤） */
    div.stButton > button[kind="secondary"]:first-child { 
        background-color: #FF4B4B !important; color: white !important; height: 80px !important; font-size: 24px !important;
    }
    /* ＝ボタン（緑） */
    .exe-btn div.stButton > button {
        background-color: #28a745 !important; color: white !important; height: 80px !important; font-size: 40px !important;
    }
    
    .tax-result-box {
        background-color: #f0f2f6; border-radius: 8px; padding: 15px; margin-top: 10px;
        text-align: center; font-size: 24px; font-weight: 900; color: #000000; border: 3px solid #000000;
    }
    @media (prefers-color-scheme: dark) { .tax-result-box { background-color: #1e1e1e; color: #ffffff; border: 3px solid #ffffff; } }
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
    return total if total != 0 else (float(text) if str(text).replace('.','').isdigit() else 0.0)

def calc_inheritance(assets, heirs):
    # 相続税: 5億2人で1億5210万になるロジック
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
    # 贈与税（110万控除後）
    target = amt - 1100000
    if target <= 0: return 0
    if is_special: # 特例贈与
        if target <= 200万: r, d = 0.10, 0
        elif target <= 400万: r, d = 0.15, 10万
        elif target <= 600万: r, d = 0.20, 30万
        elif target <= 1000万: r, d = 0.30, 90万
        elif target <= 1500万: r, d = 0.40, 190万
        elif target <= 3000万: r, d = 0.45, 265万
        elif target <= 4500万: r, d = 0.50, 415万
        else: r, d = 0.55, 640万
    else: # 一般贈与
        if target <= 200万: r, d = 0.10, 0
        elif target <= 300万: r, d = 0.15, 10万
        elif target <= 400万: r, d = 0.20, 25万
        elif target <= 600万: r, d = 0.30, 65万
        elif target <= 1000万: r, d = 0.40, 125万
        elif target <= 1500万: r, d = 0.45, 175万
        elif target <= 3000万: r, d = 0.50, 250万
        else: r, d = 0.55, 400万
    return target * r - d

# --- 状態管理 ---
if 'f_state' not in st.session_state: st.session_state.f_state = ""
if 'tax_res' not in st.session_state: st.session_state.tax_res = "結果表示"
if 'm_state' not in st.session_state: st.session_state.m_state = "通常"

# --- UI表示 ---
st.markdown(f'<div class="display-container">{st.session_state.f_state if st.session_state.f_state else "0"}</div>', unsafe_allow_html=True)

# 電卓
keys = ["7","8","9","π","√","+","4","5","6","e","^^","−","1","2","3","i","(-)","×","0","00",".","(",")","÷"]
cols = st.columns(6)
for i, k in enumerate(keys):
    if cols[i % 6].button(k): st.session_state.f_state += k; st.rerun()

# DELETEと＝の横並び最大化
c1, c2 = st.columns(2)
with c1:
    if st.button("DELETE", key="btn_del"): st.session_state.f_state = ""; st.rerun()
with c2:
    st.markdown('<div class="exe-btn">', unsafe_allow_html=True)
    if st.button("＝", key="btn_exe"):
        try:
            f = st.session_state.f_state.replace('×','*').replace('÷','/').replace('−','-').replace('^^','**').replace('π', 'math.pi').replace('e', 'math.e').replace('√', 'math.sqrt').replace('mean', 'statistics.mean').replace('median', 'statistics.median').replace('mode', 'statistics.mode').replace('stdev', 'statistics.stdev')
            st.session_state.f_state = format(eval(f), '.10g')
        except: st.session_state.f_state = "Error"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# モード切替
mc = st.columns(5)
for i, m in enumerate(["通常", "科学計算", "拡縮", "値数", "有料機能"]):
    if mc[i].button(m): st.session_state.m_state = m; st.rerun()

if st.session_state.m_state == "有料機能":
    t_type = st.selectbox("税種・機能", ["相続税", "贈与税(一般)", "贈与税(特例)", "固定資産税", "税込10%", "税込8%", "通貨・貴金属"])
    
    if t_type == "通貨・貴金属":
        c_list = ["JPY", "USD", "EUR", "XAU (金1g)", "XAG (銀1g)", "COPPER (銅1kg)"]
        c_f, c_t = st.selectbox("元", c_list), st.selectbox("先", c_list)
        c_v = st.text_input("数量", value="1")
        if st.button("変換実行"):
            try:
                r = requests.get("https://open.er-api.com/v6/latest/USD", timeout=3).json()['rates']
                m_usd = {"XAU": 2650.0/31.1035, "XAG": 31.0/31.1035, "COPPER": 9.2}
                v_u = parse_val(c_v) * m_usd[c_f.split(' ')[0]] if c_f.split(' ')[0] in m_usd else parse_val(c_v) / r[c_f.split(' ')[0]]
                res = v_u / m_usd[c_t.split(' ')[0]] if c_t.split(' ')[0] in m_usd else v_u * r[c_t.split(' ')[0]]
                st.success(f"{format(res, ',.2f')} {c_t.split(' ')[0]}")
            except: st.error("通信失敗")
    else:
        heirs = st.select_slider("相続人数", options=list(range(1, 11))) if t_type == "相続税" else 1
        tax_in = st.text_input("金額 (例: 5億, 2000万)")
        if st.button("税金計算"):
            v = parse_val(tax_in if tax_in else st.session_state.f_state)
            if t_type == "相続税": res = calc_inheritance(v, heirs)
            elif "贈与税" in t_type: res = calc_gift(v, "特例" in t_type)
            elif t_type == "固定資産税": res = v * 0.014
            elif t_type == "税込10%": res = v * 1.1
            else: res = v * 1.08
            st.session_state.tax_res = f"{t_type}: {format(int(res), ',')} 円"; st.rerun()
        st.markdown(f'<div class="tax-result-box">{st.session_state.tax_res}</div>', unsafe_allow_html=True)

elif st.session_state.m_state == "科学計算":
    sc = st.columns(4)
    for i, s in enumerate(["sin(", "cos(", "tan(", "log(", "abs(", "sqrt("]):
        if sc[i % 4].button(s): st.session_state.f_state += s; st.rerun()
elif st.session_state.m_state == "拡縮":
    si = ["Q","R","Y","Z","E","P","T","G","M","k","h","da","d","c","m","μ","n","p","f","a","z","y","r","q"]
    uc = st.columns(6)
    for i, u in enumerate(si):
        if uc[i % 6].button(u):
            if not st.session_state.f_state or st.session_state.f_state[-1] not in si:
                st.session_state.f_state += u; st.rerun()
elif st.session_state.m_state == "値数":
    sc = st.columns(4)
    for i, (l, c) in enumerate([("平均", "mean(["), ("中央値", "median(["), ("最頻値", "mode(["), ("最大", "max(["), ("最小", "min(["), (",", ","), (")]", ")]")]):
        if sc[i % 4].button(l): st.session_state.f_state += c; st.rerun()
