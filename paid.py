import streamlit as st
import math
import statistics
import requests

# --- ページ設定 ---
st.set_page_config(page_title="Python Calculator Premium", layout="centered")

# --- キーボード強制無効化 ---
st.components.v1.html("<script>const observer = new MutationObserver(() => { const inputs = window.parent.document.querySelectorAll('input[role=\"combobox\"]'); inputs.forEach(input => { input.setAttribute('readonly', 'true'); }); }); observer.observe(window.parent.document.body, { childList: true, subtree: true });</script>", height=0)

# --- CSS（隙間ゼロ・全ボタン黒背景白字・演算子巨大化） ---
st.markdown("""
<style>
    .main .block-container { max-width: 100% !important; padding: 10px !important; }
    header {visibility: hidden;}
    
    :root { --bg: #FFF; --txt: #000; --btn-bg: #1A1A1A; --btn-txt: #FFF; }
    @media (prefers-color-scheme: dark) { :root { --bg: #000; --txt: #FFF; --btn-bg: #EEE; --btn-txt: #000; } }

    .display {
        display: flex; align-items: center; justify-content: flex-end;
        font-size: 45px; font-weight: 900; margin-bottom: 10px; padding: 15px; 
        border: 4px solid var(--txt); border-radius: 12px; min-height: 110px;
        color: var(--txt); background: rgba(128,128,128,0.1); word-break: break-all;
    }
    
    /* 全てのボタンを黒背景・白文字に */
    div.stButton > button {
        width: 100% !important; height: 60px !important;
        font-weight: 900 !important; font-size: 24px !important;
        background-color: var(--btn-bg) !important; color: var(--btn-txt) !important;
        border: 1px solid var(--txt) !important; border-radius: 8px !important;
    }

    /* ＋ボタンの文字を巨大化して絶対に見えるようにする */
    div.stButton > button:contains("+") {
        font-size: 45px !important; color: var(--btn-txt) !important; line-height: 1 !important;
    }

    /* DELETEと＝の隙間を物理的に抹殺 */
    [data-testid="stHorizontalBlock"] { gap: 0px !important; }
    
    button[key="btn_del_main"] { background-color: #FF3B30 !important; color: white !important; height: 85px !important; border-radius: 10px 0 0 10px !important; border: none !important; }
    button[key="btn_exe_main"] { background-color: #34C759 !important; color: white !important; height: 85px !important; font-size: 50px !important; border-radius: 0 10px 10px 0 !important; border: none !important; }

    .tax-box { border: 4px solid var(--txt); border-radius: 10px; padding: 15px; text-align: center; font-size: 24px; font-weight: 900; color: var(--txt); }
</style>
""", unsafe_allow_html=True)

# --- 解析・計算ロジック ---
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

def calc_tax_logic(mode, v, heirs=1):
    if mode == "所得税":
        steps = [(1.95e6, 0.05, 0), (3.3e6, 0.1, 97500), (6.95e6, 0.2, 427500), (8.99e6, 0.23, 636000), (1.79e7, 0.33, 1536000), (3.99e7, 0.4, 2796000)]
        for limit, r, d in steps:
            if v <= limit: return v * r - d
        return v * 0.45 - 4796000
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
for k in ['f_state', 'tax_res', 'm_state', 'paid_sub']:
    if k not in st.session_state: st.session_state[k] = "" if 'state' in k else ("通常" if k=='m_state' else "結果表示")

# --- メイン表示 ---
st.markdown(f'<div class="display">{st.session_state.f_state if st.session_state.f_state else "0"}</div>', unsafe_allow_html=True)

# 電卓
keys = ["7","8","9","π","√","+","4","5","6","e","^^","−","1","2","3","i","(-)","×","0","00",".","(",")","÷"]
cols = st.columns(6)
for i, k in enumerate(keys):
    if cols[i % 6].button(k, key=f"k_{i}"):
        st.session_state.f_state += k
        st.rerun()

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
mc = st.columns(5)
for i, m in enumerate(["通常", "科学計算", "値数", "拡縮", "有料機能"]):
    if mc[i].button(m, key=f"m_{m}"): st.session_state.m_state = m; st.rerun()

# --- 各モード機能 ---
if st.session_state.m_state == "有料機能":
    sub = st.columns(2)
    if sub[0].button("税金計算"): st.session_state.paid_sub = "税金"; st.rerun()
    if sub[1].button("為替・貴金属"): st.session_state.paid_sub = "為替"; st.rerun()

    if st.session_state.paid_sub == "税金":
        tt = st.selectbox("種類", ["所得税", "相続税", "法人税", "贈与税(一般)", "税込10%"])
        hs = st.select_slider("相続人数", range(1, 11)) if tt == "相続税" else 1
        ti = st.text_input("金額 (SI接頭語可)")
        if st.button("計算実行"):
            val = parse_val(ti if ti else st.session_state.f_state)
            if tt in ["所得税","相続税","法人税"]: res = calc_tax_logic(tt, val, hs)
            else: res = val * 1.1
            st.session_state.tax_res = f"{tt}: {format(int(res), ',')} 円"; st.rerun()
        st.markdown(f'<div class="tax-box">{st.session_state.tax_res}</div>', unsafe_allow_html=True)

    elif st.session_state.paid_sub == "為替":
        cl = ["JPY", "USD", "EUR", "XAU (金)", "XAG (銀)", "COPPER (銅)"]
        cf, ct = st.selectbox("元", cl), st.selectbox("先", cl)
        cv = st.text_input("数量", "1")
        if st.button("変換"):
            try:
                rates = requests.get("https://open.er-api.com/v6/latest/USD", timeout=5).json()['rates']
                m_u = {"XAU": 2650.0/31.1, "XAG": 31.0/31.1, "COPPER": 9.2}
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
    for i, (l, c) in enumerate([("平均", "mean(["), ("中央値", "median(["), ("最頻値", "mode(["), ("最大", "max(["), ("最小", "min([")]):
        if sc[i % 4].button(l, key=f"stat_{i}"): st.session_state.f_state += c; st.rerun()

elif st.session_state.m_state == "拡縮":
    si_l = ["Q","R","Y","Z","E","P","T","G","M","k","m","μ","n","p"]
    uc = st.columns(7)
    for i, u in enumerate(si_l):
        if uc[i % 7].button(u, key=f"si_{i}"): st.session_state.f_state += u; st.rerun()
