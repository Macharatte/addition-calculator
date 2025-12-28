import streamlit as st
import math
import statistics
import requests

# --- ページ設定 ---
st.set_page_config(page_title="Python Calculator Premium", layout="centered")

# --- キーボード強制無効化 ---
st.components.v1.html("<script>const observer = new MutationObserver(() => { const inputs = window.parent.document.querySelectorAll('input[role=\"combobox\"]'); inputs.forEach(input => { input.setAttribute('readonly', 'true'); }); }); observer.observe(window.parent.document.body, { childList: true, subtree: true });</script>", height=0)

# --- 言語リソース ---
LANG = {
    "JP": {
        "title": "Python Calculator Premium",
        "modes": ["通常", "科学計算", "値数", "拡縮", "有料機能"],
        "tax_menu": "税金計算メニュー",
        "curr_menu": "為替・貴金属メニュー",
        "res": "結果表示",
        "exec": "計算実行",
        "convert": "変換実行",
        "amount": "金額入力",
        "qty": "数量"
    },
    "EN": {
        "title": "Python Calculator Premium",
        "modes": ["Basic", "Scientific", "Stats", "SI Prefix", "Paid Features"],
        "tax_menu": "Tax Menu",
        "curr_menu": "Currency Menu",
        "res": "Result",
        "exec": "Calculate",
        "convert": "Convert",
        "amount": "Amount",
        "qty": "Quantity"
    }
}

# --- CSS（隙間ゼロ・視認性最大・左上配置） ---
st.markdown("""
<style>
    .main .block-container { max-width: 100% !important; padding: 10px !important; }
    header {visibility: hidden;}
    
    :root { --bg: #FFF; --txt: #000; --btn-bg: #1A1A1A; --btn-txt: #FFF; }
    @media (prefers-color-scheme: dark) { :root { --bg: #000; --txt: #FFFFFF; --btn-bg: #EEE; --btn-txt: #000; } }

    /* 左上言語選択のコンテナ調整 */
    .lang-container { position: absolute; top: 0; left: 0; z-index: 99; }

    .app-title-box { text-align: center; font-size: 26px; font-weight: 900; color: var(--txt); border-bottom: 3px solid var(--txt); margin-bottom: 15px; }

    .display {
        display: flex; align-items: center; justify-content: flex-end;
        font-size: 45px; font-weight: 900; margin-bottom: 10px; padding: 15px; 
        border: 4px solid var(--txt); border-radius: 12px; min-height: 110px;
        color: var(--txt); background: rgba(128,128,128,0.1); word-break: break-all;
    }
    
    div.stButton > button {
        width: 100% !important; height: 55px !important;
        font-weight: 900 !important; font-size: 20px !important;
        background-color: var(--btn-bg) !important; color: var(--btn-txt) !important;
        border: 1px solid var(--txt) !important;
    }

    /* ＋ボタン強調 */
    div.stButton > button[key*="k_5"] {
        background-color: #007AFF !important; 
        color: #FFFFFF !important;
        font-size: 40px !important;
        border: 3px solid #FFFFFF !important;
    }

    /* 隙間抹殺 */
    [data-testid="stHorizontalBlock"] { gap: 0px !important; }
    
    button[key="btn_del_main"] { 
        background-color: #FF3B30 !important; color: white !important; 
        height: 95px !important; border-radius: 12px 0 0 12px !important; border: none !important; margin-right: -1px !important;
    }
    button[key="btn_exe_main"] { 
        background-color: #34C759 !important; color: white !important; 
        height: 95px !important; font-size: 60px !important; border-radius: 0 12px 12px 0 !important; border: none !important; margin-left: -1px !important;
    }

    .tax-box { border: 4px solid var(--txt); border-radius: 12px; padding: 15px; text-align: center; font-size: 24px; font-weight: 900; color: var(--txt); }
</style>
""", unsafe_allow_html=True)

# --- 状態管理 ---
for k in ['f_state', 'm_state', 'tax_res', 'paid_sub', 'lang']:
    if k not in st.session_state: 
        st.session_state[k] = "JP" if k == 'lang' else ("" if 'state' in k else ("通常" if k=='m_state' else "結果表示"))

L = LANG[st.session_state.lang]

# --- 1. 左上言語選択とタイトル ---
col_lang, col_empty = st.columns([1, 4])
with col_lang:
    st.session_state.lang = st.selectbox("", ["JP", "EN"], label_visibility="collapsed")

st.markdown(f'<div class="app-title-box">{L["title"]}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="display">{st.session_state.f_state if st.session_state.f_state else "0"}</div>', unsafe_allow_html=True)

# --- 2. メインキーボード ---
keys = ["7","8","9","π","√","+","4","5","6","e","^^","−","1","2","3","i","(-)","×","0","00",".","(",")","÷"]
cols = st.columns(6)
for i, k in enumerate(keys):
    if cols[i % 6].button(k, key=f"k_{i}"): st.session_state.f_state += k; st.rerun()

# --- 3. DELETE & ＝ (隙間ゼロ) ---
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

# --- 4. モード切替 ---
mc = st.columns(5)
for i, m in enumerate(L["modes"]):
    if mc[i].button(m, key=f"mode_btn_{i}"): 
        # モード名は内部的に日本語基準で判定
        st.session_state.m_state = LANG["JP"]["modes"][i]
        st.rerun()

# --- 5. 各モード機能 ---
def parse_val(text):
    if not text: return 0.0
    s = str(text).replace(',', '').strip()
    si = {'Q':1e30,'R':1e27,'Y':1e24,'Z':1e21,'E':1e18,'P':1e15,'T':1e12,'G':1e9,'M':1e6,'k':1e3,'h':1e2,'da':10,'d':0.1,'c':0.01,'m':0.001,'μ':1e-6,'n':1e-9,'p':1e-12,'f':1e-15,'a':1e-18,'z':1e-21,'y':1e-24}
    units = {"兆": 1e12, "億": 1e8, "万": 1e4, "千": 1e3}
    total, ts = 0.0, s
    for u, v in units.items():
        if u in ts:
            parts = ts.split(u); total += float(parts[0]) * v; ts = parts[1]
    if total > 0: return total + (float(ts) if ts else 0)
    for k, v in si.items():
        if s.endswith(k): return float(s[:-len(k)]) * v
    try: return float(s)
    except: return 0.0

if st.session_state.m_state == "有料機能":
    sub = st.columns(2)
    if sub[0].button(L["tax_menu"]): st.session_state.paid_sub = "税金"; st.rerun()
    if sub[1].button(L["curr_menu"]): st.session_state.paid_sub = "為替"; st.rerun()
    
    if st.session_state.paid_sub == "税金":
        tt = st.selectbox("Type", ["所得税", "相続税", "法人税", "贈与税(一般)", "税込10%", "税込8%"])
        ti = st.text_input(L["amount"])
        if st.button(L["exec"]):
            v = parse_val(ti if ti else st.session_state.f_state)
            r = v * 1.1 if "10%" in tt else v * 0.2
            st.session_state.tax_res = f"{format(int(r), ',')} YEN"; st.rerun()
        st.markdown(f'<div class="tax-box">{st.session_state.tax_res}</div>', unsafe_allow_html=True)

elif st.session_state.m_state == "拡縮":
    si_l = ["Q","R","Y","Z","E","P","T","G","M","k","h","da","d","c","m","μ","n","p","f","a","z","y","r","q"]
    uc = st.columns(8)
    for i, u in enumerate(si_l):
        if uc[i % 8].button(u, key=f"si_{i}"): st.session_state.f_state += u; st.rerun()

elif st.session_state.m_state == "値数":
    sc = st.columns(4)
    for i, (l, c) in enumerate([("平均", "mean(["), ("中央値", "median(["), ("最頻値", "mode(["), ("最大", "max(["), ("最小", "min(["), (",", ","), (")]", ")]")]):
        if sc[i % 4].button(l, key=f"st_{i}"): st.session_state.f_state += c; st.rerun()

elif st.session_state.m_state == "科学計算":
    sc = st.columns(4)
    for i, s in enumerate(["sin(", "cos(", "tan(", "log(", "abs(", "sqrt(", "°"]):
        if sc[i % 4].button(s, key=f"sci_{i}"): st.session_state.f_state += s; st.rerun()
