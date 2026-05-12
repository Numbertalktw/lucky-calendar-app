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
# 2. 簡易農曆轉換邏輯 (不需外部套件)
# =========================
def get_lunar_date(solar_date):
    """
    這是一個簡化的國農曆對照邏輯。
    在實際生產環境中，若需極高精準度可安裝 borax，
    此處提供基礎演算法以確保程式碼能直接執行。
    """
    # 這裡使用一個基礎偏移量來估算，為了示範邏輯完整性
    # 實際上農曆計算複雜，此處示範如何將轉換後的 Y, M, D 帶入公式
    # 假設轉換結果 (示範用，建議正式環境使用 borax)
    lunar_year = solar_date.year if solar_date.month > 2 else solar_date.year - 1
    lunar_month = (solar_date.month + 10) % 12 or 12
    lunar_day = solar_date.day # 簡化邏輯
    return lunar_year, lunar_month, lunar_day

# =========================
# 3. 階段藍圖計算邏輯
# =========================
def calculate_stages(y, m, d, h_opt, min_opt, age):
    y_sum = sum(int(x) for x in f"{y:04}")
    m_sum = sum(int(x) for x in f"{m:02}")
    d_sum = sum(int(x) for x in f"{d:02}")
    
    st_old = y_sum
    st_middle = st_old + m_sum
    st_young = st_middle + d_sum

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
# 4. 視覺化組件
# =========================
def display_blueprint(title, stages):
    st.markdown(f"#### {title}")
    cols = st.columns(5)
    for i, s in enumerate(stages):
        with cols[i]:
            label = f"{s['name']} ◀ 目前" if s['active'] else s['name']
            st.markdown(f"<p style='text-align:center; font-weight:bold; margin-bottom:-10px; font-size:16px;'>{label}</p>", unsafe_allow_html=True)
            
            bg = "#1A337E" if s['active'] else "#E8F0FE"
            fg = "#FFFFFF" if s['active'] else "#1A337E"
            
            st.markdown(f"""
                <div style="background-color:{bg}; color:{fg}; padding:25px 5px; border-radius:15px; text-align:center; margin:15px 0; min-height:90px; display:flex; flex-direction:column; align-items:center; justify-content:center; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
                    <span style="font-size:24px; font-weight:bold;">{s['val']}</span>
                </div>
            """, unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center; color:gray; font-size:0.85em;'>{s['age_range']}</p>", unsafe_allow_html=True)

# =========================
# 5. Streamlit 主頁面
# =========================
st.set_page_config(page_title="樂覺製所生命靈數", layout="wide")

st.title("🧭 樂覺製所生命靈數 & 階段藍圖")
st.markdown("---")

# 輸入區塊
with st.container():
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        birthday = st.date_input("請輸入國曆生日 (Solar Birthday)", value=datetime.date(1990, 1, 1), min_value=datetime.date(1900, 1, 1))
    with c2:
        h_opts = ["不知道"] + [str(i) for i in range(24)]
        b_hour = st.selectbox("出生時 (Hour)", options=h_opts, index=11)
    with c3:
        m_opts = ["不知道"] + [str(i) for i in range(60)]
        b_min = st.selectbox("出生分 (Minute)", options=m_opts, index=1)
    
    ref_date = st.date_input("查詢日期 (用於判斷目前階段)", value=datetime.date.today())

if st.button("🔮 開始計算國農曆藍圖"):
    # 1. 計算年齡
    age = ref_date.year - birthday.year - ((ref_date.month, ref_date.day) < (birthday.month, birthday.day))
    
    # 2. 獲取農曆日期 (模擬轉換)
    ly, lm, ld = get_lunar_date(birthday)
    
    st.markdown("---")
    
    # --- 顯示國曆藍圖 ---
    solar_stages = calculate_stages(birthday.year, birthday.month, birthday.day, b_hour, b_min, age)
    display_blueprint(f"📍 國曆階段藍圖 (生日：{birthday})", solar_stages)
    
    st.write("")
    st.write("")
    
    # --- 顯示農曆藍圖 ---
    lunar_stages = calculate_stages(ly, lm, ld, b_hour, b_min, age)
    display_blueprint(f"🏮 農曆階段藍圖 (轉換參考：{ly}年{lm}月{ld}日)", lunar_stages)

st.markdown("---")
st.caption("Be true, be you — 讓靈魂，自在呼吸。 | 樂覺製所 © 2026")
