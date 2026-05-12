# -*- coding: utf-8 -*-
import streamlit as st
import datetime
import pandas as pd
from borax.calendars.lunardate import LunarDate # 請確保環境有安裝 borax

# =========================
# 核心計算工具
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
    """判斷目前年齡對應的階段索引"""
    if age >= 60: return 0
    if 40 <= age < 60: return 1
    if 20 <= age < 40: return 2
    if 10 <= age < 20: return 3
    return 4

# =========================
# 階段藍圖計算邏輯 (通用型)
# =========================
def calculate_generic_stages(y, m, d, hour_val, min_val, ref_date, birth_date_for_age):
    y_sum = sum(int(x) for x in f"{y:04}")
    m_sum = sum(int(x) for x in f"{m:02}")
    d_sum = sum(int(x) for x in f"{d:02}")
    
    st_old = y_sum
    st_middle = st_old + m_sum
    st_young_adult = st_middle + d_sum

    # 少年
    if hour_val == "不知道":
        st_teen_display = "--"
        st_child_display = "--"
    else:
        h_sum = sum(int(x) for x in f"{int(hour_val):02}")
        st_teen_display = format_layers(st_young_adult + h_sum)
        # 幼年
        if min_val == "不知道":
            st_child_display = "--"
        else:
            min_sum_val = sum(int(x) for x in f"{int(min_val):02}")
            st_child_display = format_layers(st_young_adult + h_sum + min_sum_val)

    # 計算年齡用來高亮 (以國曆生日為準)
    age = ref_date.year - birth_date_for_age.year - ((ref_date.month, ref_date.day) < (birth_date_for_age.month, birth_date_for_age.day))
    active_idx = get_current_stage_idx(age)

    return [
        {"name": "老年階段", "age": "60 歲以上", "val": format_layers(st_old), "active": active_idx == 0},
        {"name": "中年階段", "age": "40 – 60 歲", "val": format_layers(st_middle), "active": active_idx == 1},
        {"name": "青年階段", "age": "20 – 39 歲", "val": format_layers(st_young_adult), "active": active_idx == 2},
        {"name": "少年階段", "age": "10 – 19 歲", "val": st_teen_display, "active": active_idx == 3},
        {"name": "幼年階段", "age": "0 – 09 歲", "val": st_child_display, "active": active_idx == 4},
    ]

# =========================
# UI 顯示組件
# =========================
def display_stage_row(title, stages):
    st.markdown(f"#### {title}")
    cols = st.columns(5)
    for i, stage in enumerate(stages):
        with cols[i]:
            title_label = f"{stage['name']} ◀ 目前" if stage['active'] else stage['name']
            st.markdown(f"<p style='text-align: center; font-size: 0.9em; font-weight: bold; margin-bottom: -5px;'>{title_label}</p>", unsafe_allow_html=True)
            
            bg_color = "#1A337E" if stage['active'] else "#E8F0FE"
            text_color = "white" if stage['active'] else "#1A337E"
            
            st.markdown(f"""
                <div style="background-color: {bg_color}; color: {text_color}; padding: 20px 5px; border-radius: 12px; text-align: center; margin: 10px 0; border: 1px solid #d1d1d1;">
                    <span style="font-size: 20px; font-weight: bold;">{stage['val']}</span>
                </div>
            """, unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center; color: gray; font-size: 0.75em;'>{stage['age']}</p>", unsafe_allow_html=True)

# =========================
# Streamlit 主介面
# =========================
st.set_page_config(page_title="樂覺製所生命靈數", layout="wide")

st.title("🧭 樂覺製所生命靈數 & 生命藍圖")
st.markdown("在數字之中，我們與自己不期而遇。 (In numbers, we meet ourselves unexpectedly.)")

# 輸入區
with st.expander("📝 輸入生日資訊", expanded=True):
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        birthday = st.date_input("國曆生日", value=datetime.date(1990, 1, 1), min_value=datetime.date(1900, 1, 1))
    with c2:
        hour_opts = ["不知道"] + [str(i) for i in range(24)]
        birth_hour = st.selectbox("出生時", options=hour_opts, index=11)
    with c3:
        min_opts = ["不知道"] + [str(i) for i in range(60)]
        birth_min = st.selectbox("出生分", options=min_opts, index=1)
    
    ref_date = st.date_input("查詢日期", value=datetime.date.today())

if st.button("🔮 開始計算藍圖"):
    st.markdown("---")
    
    # 1. 取得農曆日期
    try:
        lunar = LunarDate.from_solar_date(birthday.year, birthday.month, birthday.day)
        lunar_str = f"農曆：{lunar.year}年{lunar.month}月{lunar.day}日"
    except:
        lunar_str = "農曆轉換失敗"

    # 2. 計算階段
    solar_stages = calculate_generic_stages(birthday.year, birthday.month, birthday.day, birth_hour, birth_min, ref_date, birthday)
    lunar_stages = calculate_generic_stages(lunar.year, lunar.month, lunar.day, birth_hour, birth_min, ref_date, birthday)

    # 3. 渲染畫面
    st.subheader(f"📅 國曆生日：{birthday} ｜ {lunar_str}")
    
    # 顯示國曆
    display_stage_row("📍 國曆階段數", solar_stages)
    
    st.write("") # 間距
    
    # 顯示農曆
    display_stage_row("🏮 農曆階段數", lunar_stages)

st.markdown("---")
st.caption("樂覺製所 © 2026 Numbertalk")
