import streamlit as st
import math
import statistics
import requests

# --- ページ設定 ---
st.set_page_config(page_title="Python Calculator Premium", layout="centered")

# --- キーボード強制無効化 ---
st.components.v1.html("<script>const observer = new MutationObserver(() => { const inputs = window.parent.document.querySelectorAll('input[role=\"combobox\"]'); inputs.forEach(input => { input.setAttribute('readonly', 'true'); }); }); observer.observe(window.parent.document.body, { childList: true, subtree: true });</script>", height=0)

# --- CSS（隙間ゼロ・視認性最大・全機能表示） ---
st.markdown("""
<style>
    .main .block-container { max-width: 100% !important; padding: 10px !important; }
    header {visibility: hidden;}
    
    :root { --bg: #FFF; --txt: #000; --btn-bg: #1A1A1A; --btn-txt: #FFF; }
    @media (prefers-color-scheme: dark) { :root { --bg: #000; --txt: #FFF; --btn-bg: #EEE; --btn-txt: #000; } }

    .app-title-box { text-align: center; font-size: 26px; font-weight: 900; color: var(--txt); border-bottom: 3px solid var(--txt); margin-bottom: 15px; }

    .display {
        display: flex; align-items: center; justify-content: flex-end;
        font-size: 45px; font-weight: 900; margin-bottom: 10px; padding: 15px; 
        border: 4px solid var(--txt); border-radius: 12px; min-height: 110px;
        color: var(--txt); background: rgba(128,128,128,0.1); word-break: break-all;
    }
    
    div.stButton > button {
        width: 100% !important; height: 60px !important;
        font-weight: 900 !important; font-size: 24px !important;
        background-color: var(--btn-bg) !important; color: var(--btn-txt) !important;
        border: 1px solid var(--txt) !important;
    }

    /* 【解決】＋ボタン強調 */
    div.stButton > button[key*="k_5"] {
        background-color: #007AFF !important; 
        color: #FFFFFF !important;
        font-size: 45px !important;
        border: 3px solid #FFFFFF !important;
    }

    /* 【解決】隙間抹殺 */
    [data-testid="stHorizontalBlock"] { gap: 0px !important; }
    
    button[key="btn_del_main"] { 
        background-color: #FF3B30 !important; color: white !important; 
        height: 95px !important; border-radius: 12px 0 0 12px !important; border: none !important; margin-right: -1px !important;
    }
    button[key="btn_exe_main"] { 
        background-color: #34C759 !important; color: white !important; 
        height: 95px !important; font-size: 60px !important; border-radius: 0 12px 12px 0 !important; border: none !important; margin-left: -1px !important;
    }

    .tax-box { border: 4px solid var(--txt); border-radius: 12px; padding: 15px; text-align: center; font-size: 26px; font-weight: 900; color: var(--txt); background: rgba(128,128,128,0.05); }
</style>
""", unsafe_allow_html=True)

# --- 計算・解析ロジック（完全版） ---
def parse_val(text):
    if not text: return 0.0
    s = str(text).replace(',', '').strip()
    units = {"兆": 1e12, "億": 1e8, "万": 1e4, "千": 1e3}
    si = {'Q':1e30,'R':1e27,'Y':1e24,'Z':1e21,'E':1e18,'P':1e15,'T':1e12,'G':1e9,'M':1e6,'k':1e3,'h':1e2,'da':10,'d':0.1,'c':0.01,'m':0.001,'μ':1e-6,'n':1e-9,'p':1e-12,'f':1e-15,'a':1e-18,'z':1e-21,'y':1e-24}
    total, ts = 0.0, s
    for u, v in units.items():
        if u in ts:
            parts = ts.split(u)
            if parts[0]: total += float(parts[0]) * v
            ts = parts[1]
    if total > 0: return total + (float(ts) if ts else 0)
    for k, v in si.items():
        if s.endswith(k): return float(s[:-len(k)]) * v
    try: return float(s)
    except: return 0.0

def calc_tax_all(mode, v, heirs=1):
    if mode == "所得税":
        if v <= 1.95e6: return v*0.05
        elif v <= 3.3e6: return v*0.1-97500
        elif v <= 6.95e6: return v*0.2-427500
        elif v <= 8.99e6: return v*0.23-636000
        elif v <= 1.79e7: return v*0.33-1536000
        elif v <= 3.99e7: return v*0.4-2796000
        else: return v*0.45-4796000
    if mode == "相続税":
        ex = 3e7 + (6e6 * heirs)
        tx = max(0, v - ex) / heirs
        if tx <= 1e7: r, d = 0.1, 0
        elif tx <= 3e7: r, d = 0.15, 5e5
        elif tx <= 5e7: r, d = 0.2, 2e6
        elif tx <= 1e8: r, d = 0.3, 7e6
        elif tx <= 2e8: r, d = 0.4, 1.7e7
        elif tx <= 3e8: r, d = 0.45, 2.7e7
        elif tx <= 6e8: r, d = 0.5, 4.2e7
        else: r, d = 0.55, 7.2e7
        return (tx * r - d) * heirs
    if mode == "法人税":
        return v * 0.15 if v <= 8e6 else (1.2e6 + (v-8e6)*0.232)
    return 0

# --- 状態管理 ---
for k in ['f_state', 'm_state', 'tax_res', 'paid_sub']:
    if k not in st.session_state: st.session_state[k] = "" if 'state' in k else ("通常" if k=='m_state' else "結果表示")

# --- UI ---
st.markdown('<div class="app-title-box">Python Calculator Premium</div>', unsafe_allow_html=True)
st.markdown(f'<div class="display">{st.session_state.f_state if st.session_state.f_state else "0"}</div>', unsafe_allow_html=True)

# 1. 電卓キー
keys = ["7","8","9","π","√","+","4","5","6","e","^^","−","1","2","3","i","(-)","×","0","00",".","(",")","÷"]
cols = st.columns(6)
for i, k in enumerate(keys):
    if cols[i % 6].button(k, key=f"k_{i}"): st.session_state.f_state += k; st.rerun()

# 2. DELETE & ＝
c1, c2 = st.columns(2)
with c1:
    if st.button("DELETE", key="btn_del_main"): st.session_state.f_state = ""; st.rerun()
with c2:
    if st.button("＝", key="btn_exe_main"):
        try:
            f = st.session_state.f_state.replace('×','*').replace('÷','/').replace('−','-').replace('^^','**').replace('π','math.pi').replace('e','math.e').replace('√','math.sqrt').replace('°','*math.pi/180')
            st.session_state.f_state = format(eval(f), '.10g')
        except: st.session_state.f_state = "Error"
        st.rerun()

st.divider()
# 3. モード切替
mc = st.columns(5)
for i, m in enumerate(["通常", "科学計算", "値数", "拡縮", "有料機能"]):
    if mc[i].button(m, key=f"m_{m}"): st.session_state.m_state = m; st.rerun()

# --- 各モード詳細 ---
if st.session_state.m_state == "有料機能":
    sub = st.columns(2)
    if sub[0].button("税金計算メニュー"): st.session_state.paid_sub = "税金"; st.rerun()
    if sub[1].button("為替・貴金属メニュー"): st.session_state.paid_sub = "為替"; st.rerun()

    if st.session_state.paid_sub == "税金":
        tt = st.selectbox("税種", ["所得税", "相続税", "法人税", "贈与税(一般)", "贈与税(特例)", "固定資産税", "税込10%", "税込8%"])
        hs = st.select_slider("相続人数", range(1, 11)) if tt == "相続税" else 1
        ti = st.text_input("金額 (万億・SI対応)")
        if st.button("計算実行"):
            v = parse_val(ti if ti else st.session_state.f_state)
            if tt in ["所得税", "相続税", "法人税"]: r = calc_tax_all(tt, v, hs)
            elif "贈与" in tt: r = v - 1100000 # 簡易
            elif tt == "固定資産税": r = v * 0.014
            else: r = v * 1.1 if "10%" in tt else v * 1.08
            st.session_state.tax_res = f"{tt}: {format(int(r), ',')} 円"; st.rerun()
        st.markdown(f'<div class="tax-box">{st.session_state.tax_res}</div>', unsafe_allow_html=True)

    elif st.session_state.paid_sub == "為替":
        cl = ["JPY", "USD", "EUR", "GBP", "CNY", "AUD", "XAU (金)", "XAG (銀)", "COPPER (銅)"]
        cf, ct = st.selectbox("元", cl), st.selectbox("先", cl)
        cv = st.text_input("数量", "1")
        if st.button("変換"):
            try:
                rates = requests.get("https://open.er-api.com/v6/latest/USD").json()['rates']
                m_u = {"XAU": 2650/31.1, "XAG": 31/31.1, "COPPER": 9.2}
                fc, tc = cf.split(' ')[0], ct.split(' ')[0]
                vu = parse_val(cv) * m_u[fc] if fc in m_u else parse_val(cv) / rates[fc]
                res = vu / m_u[tc] if tc in m_u else vu * rates[tc]
                st.session_state.tax_res = f"結果: {format(res, ',.2f')} {tc}"; st.rerun()
            except: st.error("通信失敗"); st.rerun()
        st.markdown(f'<div class="tax-box">{st.session_state.tax_res}</div>', unsafe_allow_html=True)

elif st.session_state.m_state == "科学計算":
    sc = st.columns(4)
    for i, s in enumerate(["sin(", "cos(", "tan(", "log(", "abs(", "sqrt(", "°"]):
        if sc[i % 4].button(s, key=f"sci_{i}"): st.session_state.f_state += s; st.rerun()

elif st.session_state.m_state == "値数":
    sc = st.columns(4)
    for i, (l, c) in enumerate([("平均", "mean(["), ("中央値", "median(["), ("最頻値", "mode(["), ("最大", "max(["), ("最小", "min(["), (",", ","), (")]", ")]")]):
        if sc[i % 4].button(l, key=f"st_{i}"): st.session_state.f_state += c; st.rerun()

elif st.session_state.m_state == "拡縮":
    si_l = ["Q","R","Y","Z","E","P","T","G","M","k","h","da","d","c","m","μ","n","p","f","a","z","y"]
    uc = st.columns(6)
    for i, u in enumerate(si_l):
        if uc[i % 6].button(u, key=f"si_{i}"): st.session_state.f_state += u; st.rerun()
