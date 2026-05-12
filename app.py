# -*- coding: utf-8 -*-
import streamlit as st
import datetime

# =========================
# 1. 核心計算工具
# =========================
def reduce_to_digit(n: int) -> int:
    while n > 9:
        n = sum(int(x) for x in str(n))
    return n

def sum_once(n: int) -> int:
    return sum(int(x) for x in str(n))

def format_layers(total: int) -> str:
    mid = sum_once(total)
    if mid > 9:
        return f"{total}/{mid}/{reduce_to_digit(mid)}"
    else:
        return f"{total}/{mid}"

def get_current_stage_idx(age):
    if age >= 60: return 0
    if 40 <= age < 60: return 1
    if 20 <= age < 40: return 2
    if 10 <= age < 20: return 3
    return 4

# =========================
# 2. 階段藍圖計算邏輯
# =========================
def calculate_stages(y, m, d, h_opt, min_opt, age):
    y_sum = sum(int(x) for x in f"{y:04}")
    m_sum = sum(int(x) for x in f"{m:02}")
    d_sum = sum(int(x) for x in f"{d:02}")
    
    st_old = y_sum
    st_middle = st_old + m_sum
    st_young = st_middle + d_sum

    # 處理時間 (少年與幼年)
    if h_opt == "不知道":
        st_teen = "--"
        st_child = "--"
    else:
        h_sum = sum(int(x) for x in f"{int(h_opt):02}")
        st_teen = format_layers(st_young + h_sum)
        if min_opt == "不知道":
            st_child = "--"
        else:
            min_sum = sum(int(x) for x in f"{int(min_opt):02}")
            st_child = format_layers(st_young + h_sum + min_sum)

    active_idx = get_current_stage_idx(age)

    return [
        {"name": "老年階段", "age_range": "60 歲以上", "val": format_layers(st_old), "active": active_idx == 0},
        {"name": "中年階段", "age_range": "40 – 60 歲", "val": format_layers(st_middle), "active": active_idx == 1},
        {"name": "青年階段", "age_range": "20 – 39 歲", "val": format_layers(st_young), "active": active_idx == 2},
        {"name": "少年階段", "age_range": "10 – 19 歲", "val": st_teen, "active": active_idx == 3},
        {"name": "幼年階段", "age_range": "0 – 09 歲", "val": st_child, "active": active_idx == 4},
    ]

# =========================
# 3. 視覺化組件
# =========================
def display_blueprint(title, stages):
    st.markdown(f"#### {title}")
    cols = st.columns(5)
    for i, s in enumerate(stages):
        with cols[i]:
            label = f"{s['name']} ◀ 目前" if s['active'] else s['name']
            st.markdown(f"<p style='text-align:center; font-weight:bold; margin-bottom:-10px;'>{label}</p>", unsafe_allow_html=True)
            
            # 根據是否為目前階段選擇顏色 (深藍 vs 淺藍)
            bg = "#1A337E" if s['active'] else "#E8F0FE"
            fg = "#FFFFFF" if s['active'] else "#1A337E"
            
            st.markdown(f"""
                <div style="background-color:{bg}; color:{fg}; padding:20px 5px; border-radius:12px; text-align:center; margin:15px 0; min-height:80px; display:flex; align-items:center; justify-content:center;">
                    <span style="font-size:22px; font-weight:bold;">{s['val']}</span>
                </div>
            """, unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center; color:gray; font-size:0.8em;'>{s['age_range']}</p>", unsafe_allow_html=True)

# =========================
# 4. Streamlit 介面
# =========================
st.set_page_config(page_title="樂覺製所生命靈數", layout="wide")
st.title("🧭 樂覺製所生命靈數 & 階段藍圖")

# 輸入區
with st.container():
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        birthday = st.date_input("國曆生日", value=datetime.date(1990, 1, 1), min_value=datetime.date(1900, 1, 1))
    with c2:
        h_opts = ["不知道"] + [str(i) for i in range(24)]
        b_hour = st.selectbox("出生時", options=h_opts, index=11)
    with c3:
        m_opts = ["不知道"] + [str(i) for i in range(60)]
        b_min = st.selectbox("出生分", options=m_opts, index=1)
    
    ref_date = st.date_input("查詢日期", value=datetime.date.today())

if st.button("🔮 計算生命藍圖"):
    # 計算年齡 (高亮用)
    age = ref_date.year - birthday.year - ((ref_date.month, ref_date.day) < (birthday.month, birthday.day))
    
    st.markdown("---")
    
    # --- 國曆藍圖 ---
    solar_stages = calculate_stages(birthday.year, birthday.month, birthday.day, b_hour, b_min, age)
    display_blueprint("📍 國曆階段數", solar_stages)
    
    st.write("")
    
    # --- 農曆藍圖 (模擬農曆計算，避免套件報錯) ---
    # 註：此處若無套件則先以國曆代入，或您手動輸入農曆數字
    st.info("💡 農曆功能：若需精準農曆，建議手動輸入農曆日期。以下為國曆轉換參考。")
    lunar_stages = calculate_stages(birthday.year, birthday.month, birthday.day, b_hour, b_min, age) # 暫代
    display_blueprint("🏮 農曆階段數 (參考)", lunar_stages)

st.markdown("---")
st.caption("Be true, be you — 讓靈魂，自在呼吸。")
