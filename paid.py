import streamlit as st
import math
import statistics
import requests

# --- ページ設定 ---
st.set_page_config(page_title="Python Calculator Premium", layout="centered")

# --- キーボード強制無効化 ---
st.components.v1.html("<script>const observer = new MutationObserver(() => { const inputs = window.parent.document.querySelectorAll('input[role=\"combobox\"]'); inputs.forEach(input => { input.setAttribute('readonly', 'true'); }); }); observer.observe(window.parent.document.body, { childList: true, subtree: true });</script>", height=0)

# --- 究極のCSS（OS連動・隙間ゼロ・高コントラスト） ---
st.markdown("""
<style>
    .main .block-container { max-width: 100% !important; padding: 10px !important; }
    header {visibility: hidden;}
    
    :root { --bg: #FFF; --txt: #000; --btn: #333; --btxt: #FFF; }
    @media (prefers-color-scheme: dark) { :root { --bg: #000; --txt: #FFF; --btn: #EEE; --btxt: #000; } }

    /* タイトルとディスプレイ */
    .app-title { text-align: center; font-size: 24px; font-weight: 900; color: var(--txt); margin-bottom: 10px; }
    .display {
        display: flex; align-items: center; justify-content: flex-end;
        font-size: 42px; font-weight: 900; margin-bottom: 15px; padding: 15px; 
        border: 3px solid var(--txt); border-radius: 10px; min-height: 100px;
        color: var(--txt); background: rgba(128,128,128,0.1); word-break: break-all;
    }
    
    /* 通常ボタン: 文字を太く、背景とのコントラストを最大に */
    div.stButton > button {
        width: 100% !important; height: 60px !important;
        font-weight: 900 !important; font-size: 24px !important;
        background-color: var(--btn) !important; color: var(--btxt) !important;
        border: 2px solid var(--txt) !important;
    }

    /* 巨大ボタンエリアの隙間を消す */
    .big-btn-container { display: flex; width: 100%; gap: 0 !important; }
    .big-btn-container > div { flex: 1; }
    
    /* DELETE (赤) */
    button[key="btn_del_main"] { 
        background-color: #FF0000 !important; color: white !important; 
        height: 90px !important; font-size: 28px !important; border-radius: 10px 0 0 10px !important; border: none !important;
    }
    /* ＝ (緑) */
    button[key="btn_exe_main"] { 
        background-color: #00CC00 !important; color: white !important; 
        height: 90px !important; font-size: 50px !important; border-radius: 0 10px 10px 0 !important; border: none !important;
    }

    .tax-box { background: rgba(128,128,128,0.1); border: 3px solid var(--txt); border-radius: 10px; padding: 20px; text-align: center; font-size: 24px; font-weight: 900; color: var(--txt); }
</style>
""", unsafe_allow_html=True)

# --- ロジック系 ---
def parse_val_adv(text):
    if not text: return 0.0
    s = str(text).replace(',', '').strip()
    units = {"兆": 1e12, "億": 1e8, "万": 1e4, "千": 1e3}
    si = {'Q':1e30,'R':1e27,'Y':1e24,'Z':1e21,'E':1e18,'P':1e15,'T':1e12,'G':1e9,'M':1e6,'k':1e3,'h':1e2,'da':10,'d':0.1,'c':0.01,'m':0.001,'μ':1e-6,'n':1e-9,'p':1e-12,'f':1e-15,'a':1e-18,'z':1e-21,'y':1e-24}
    total, temp_s = 0.0, s
    for u, v in units.items():
        if u in temp_s:
            parts = temp_s.split(u)
            if parts[0]: total += float(parts[0]) * v
            temp_s = parts[1]
    if total > 0: return total + (float(temp_s) if temp_s else 0)
    for k, v in si.items():
        if s.endswith(k): return float(s[:-len(k)]) * v
    try: return float(s)
    except: return 0.0

# 税金計算関数群
def calc_tax(mode, v, heirs=1):
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
        taxable = max(0, v - ex) / heirs
        if taxable <= 1e7: r, d = 0.1, 0
        elif taxable <= 3e7: r, d = 0.15, 5e5
        elif taxable <= 5e7: r, d = 0.2, 2e6
        elif taxable <= 1e8: r, d = 0.3, 7e6
        elif taxable <= 2e8: r, d = 0.4, 1.7e7
        elif taxable <= 3e8: r, d = 0.45, 2.7e7
        elif taxable <= 6e8: r, d = 0.5, 4.2e7
        else: r, d = 0.55, 7.2e7
        return (taxable * r - d) * heirs
    if mode == "法人税":
        return v * 0.15 if v <= 8e6 else (1.2e6 + (v-8e6)*0.232)
    return 0

# --- メイン UI ---
if 'f_state' not in st.session_state: st.session_state.f_state = ""
if 'tax_res' not in st.session_state: st.session_state.tax_res = "結果表示"
if 'm_state' not in st.session_state: st.session_state.m_state = "通常"
if 'paid_sub' not in st.session_state: st.session_state.paid_sub = "税金"

st.markdown('<div class="app-title">Python Calculator Premium</div>', unsafe_allow_html=True)
st.markdown(f'<div class="display">{st.session_state.f_state if st.session_state.f_state else "0"}</div>', unsafe_allow_html=True)

# 電卓キー
keys = ["7","8","9","π","√","+","4","5","6","e","^^","−","1","2","3","i","(-)","×","0","00",".","(",")","÷"]
cols = st.columns(6)
for i, k in enumerate(keys):
    if cols[i % 6].button(k, key=f"key_{i}"): st.session_state.f_state += k; st.rerun()

# DELETEと＝の隙間を消すための特別レイアウト
st.markdown('<div class="big-btn-container">', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    if st.button("DELETE", key="btn_del_main"): st.session_state.f_state = ""; st.rerun()
with c2:
    if st.button("＝", key="btn_exe_main"):
        try:
            f = st.session_state.f_state.replace('×','*').replace('÷','/').replace('−','-').replace('^^','**').replace('π','math.pi').replace('e','math.e').replace('√','math.sqrt').replace('°','*math.pi/180')
            f = f.replace('mean','statistics.mean').replace('median','statistics.median').replace('mode','statistics.mode')
            st.session_state.f_state = format(eval(f), '.10g')
        except: st.session_state.f_state = "Error"
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

st.divider()
mc = st.columns(5)
for i, m in enumerate(["通常", "科学計算", "値数", "拡縮", "有料機能"]):
    if mc[i].button(m, key=f"m_{m}"): st.session_state.m_state = m; st.rerun()

if st.session_state.m_state == "有料機能":
    sub_c = st.columns(2)
    if sub_c[0].button("税金計算"): st.session_state.paid_sub = "税金"; st.rerun()
    if sub_c[1].button("為替・貴金属"): st.session_state.paid_sub = "為替"; st.rerun()

    if st.session_state.paid_sub == "税金":
        t_type = st.selectbox("種類", ["所得税", "相続税", "法人税", "税込10%", "税込8%"])
        heirs = st.select_slider("相続人数", range(1, 11)) if t_type == "相続税" else 1
        t_in = st.text_input("金額 (10k, 1M等可)")
        if st.button("計算実行"):
            val = parse_val_adv(t_in if t_in else st.session_state.f_state)
            if t_type in ["所得税","相続税","法人税"]: res = calc_tax(t_type, val, heirs)
            else: res = val * (1.1 if "10%" in t_type else 1.08)
            st.session_state.tax_res = f"{t_type}: {format(int(res), ',')} 円"; st.rerun()
        st.markdown(f'<div class="tax-box">{st.session_state.tax_res}</div>', unsafe_allow_html=True)

    elif st.session_state.paid_sub == "為替":
        c_list = ["JPY", "USD", "EUR", "GBP", "CNY", "XAU (金)", "XAG (銀)", "COPPER (銅)"]
        cf, ct = st.selectbox("元", c_list), st.selectbox("先", c_list)
        cv = st.text_input("数量", "1")
        if st.button("為替変換実行"):
            try:
                rates = requests.get("https://open.er-api.com/v6/latest/USD", timeout=5).json()['rates']
                m_usd = {"XAU": 2650.0/31.1, "XAG": 31.0/31.1, "COPPER": 9.2}
                f_c, t_c = cf.split(' ')[0], ct.split(' ')[0]
                v_u = parse_val_adv(cv) * m_usd[f_c] if f_c in m_usd else parse_val_adv(cv) / rates[f_c]
                res = v_u / m_usd[t_c] if t_c in m_usd else v_u * rates[t_c]
                st.session_state.tax_res = f"結果: {format(res, ',.2f')} {t_c}"; st.rerun()
            except: st.error("通信失敗"); st.rerun()
        st.markdown(f'<div class="tax-box">{st.session_state.tax_res}</div>', unsafe_allow_html=True)

elif st.session_state.m_state == "科学計算":
    sc = st.columns(4)
    for i, s in enumerate(["sin(", "cos(", "tan(", "log(", "abs(", "sqrt(", "°"]):
        if sc[i % 4].button(s, key=f"sci_{i}"): st.session_state.f_state += s; st.rerun()
elif st.session_state.m_state == "値数":
    sc = st.columns(4)
    for i, l in enumerate(["平均", "中央値", "最頻値", "最大", "最小"]):
        if sc[i % 4].button(l, key=f"stat_{i}"): st.session_state.f_state += l; st.rerun()
