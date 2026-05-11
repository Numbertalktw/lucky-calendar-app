# -*- coding: utf-8 -*-
import streamlit as st
import datetime
import pandas as pd

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

# =========================
# 階段藍圖與自動高亮判斷
# =========================
def get_current_stage_idx(age):
    """根據年齡判斷目前處於哪個階段索引 (0-4)"""
    if age >= 60: return 0  # 老年
    if 40 <= age <= 60: return 1  # 中年
    if 20 <= age <= 39: return 2  # 青年
    if 10 <= age <= 19: return 3  # 少年
    return 4  # 幼年

def calculate_blueprint_stages(birthday, hour_val, min_val, ref_date):
    y_sum = sum(int(x) for x in str(birthday.year))
    m_sum = sum(int(x) for x in f"{birthday.month:02}")
    d_sum = sum(int(x) for x in f"{birthday.day:02}")
    
    st_old = y_sum
    st_middle = st_old + m_sum
    st_young_adult = st_middle + d_sum

    # 處理時間相關階段
    if hour_val == "不知道":
        st_teen_display = "--"
        st_child_display = "--"
    else:
        h_sum = sum(int(x) for x in f"{int(hour_val):02}")
        st_teen_display = format_layers(st_young_adult + h_sum)
        if min_val == "不知道":
            st_child_display = "--"
        else:
            m_sum_val = sum(int(x) for x in f"{int(min_val):02}")
            st_child_display = format_layers(st_young_adult + h_sum + m_sum_val)

    # 計算當下年齡
    current_age = ref_date.year - birthday.year - ((ref_date.month, ref_date.day) < (birthday.month, birthday.day))
    active_idx = get_current_stage_idx(current_age)

    return [
        {"name": "老年階段", "age": "60 歲以上", "val": format_layers(st_old), "active": active_idx == 0},
        {"name": "中年階段", "age": "40 – 60 歲", "val": format_layers(st_middle), "active": active_idx == 1},
        {"name": "青年階段", "age": "20 – 39 歲", "val": format_layers(st_young_adult), "active": active_idx == 2},
        {"name": "少年階段", "age": "10 – 19 歲", "val": st_teen_display, "active": active_idx == 3},
        {"name": "幼年階段", "age": "0 – 09 歲", "val": st_child_display, "active": active_idx == 4},
    ]

# =========================
# Streamlit 介面
# =========================
st.set_page_config(page_title="樂覺製所生命靈數", layout="centered")

st.title("🧭 樂覺製所生命靈數")
st.markdown("在數字之中，我們與自己不期而遇。")

st.subheader("🌟 生命靈數 & 階段藍圖速算")
col_in1, col_in2 = st.columns(2)

with col_in1:
    birthday = st.date_input("請輸入生日 (Birthday)", 
                             value=datetime.date(1990, 1, 1),
                             min_value=datetime.date(1900, 1, 1))
    st.markdown("**出生時間 (Time)**")
    t_c1, t_c2 = st.columns(2)
    hour_options = ["不知道"] + [str(i) for i in range(24)]
    min_options = ["不知道"] + [str(i) for i in range(60)]
    with t_c1:
        birth_hour = st.selectbox("時 (Hour)", options=hour_options, index=11)
    with t_c2:
        birth_min = st.selectbox("分 (Min)", options=min_options, index=1)

with col_in2:
    ref_date = st.date_input("查詢日期 (Query Date)", value=datetime.date.today())

if st.button("🔮 計算階段藍圖"):
    st.markdown("---")
    st.markdown("### 🗺️ 生命藍圖五大階段 (Life Blueprint Stages)")
    
    stages = calculate_blueprint_stages(birthday, birth_hour, birth_min, ref_date)
    s_cols = st.columns(5)
    
    for i, stage in enumerate(stages):
        with s_cols[i]:
            # 判斷是否為目前階段
            title_label = f"{stage['name']} ◀ 目前" if stage['active'] else stage['name']
            
            # 顯示階段標題
            st.markdown(f"<p style='text-align: center; font-weight: bold; margin-bottom: -10px;'>{title_label}</p>", unsafe_allow_html=True)
            
            # 使用自定義 CSS 模擬高亮方塊
            if stage['active']:
                # 高亮樣式：深藍背景，白字
                st.markdown(f"""
                    <div style="background-color: #1A337E; color: white; padding: 25px 10px; border-radius: 15px; text-align: center; margin: 15px 0;">
                        <span style="font-size: 24px; font-weight: bold;">{stage['val']}</span>
                    </div>
                """, unsafe_allow_html=True)
            else:
                # 普通樣式：淺灰藍背景，深藍字
                st.markdown(f"""
                    <div style="background-color: #E8F0FE; color: #1A337E; padding: 25px 10px; border-radius: 15px; text-align: center; margin: 15px 0;">
                        <span style="font-size: 24px; font-weight: bold;">{stage['val']}</span>
                    </div>
                """, unsafe_allow_html=True)
            
            # 顯示年齡範圍
            st.markdown(f"<p style='text-align: center; color: gray; font-size: 0.8em;'>{stage['age']}</p>", unsafe_allow_html=True)

st.markdown("---")
