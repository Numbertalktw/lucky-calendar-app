# -*- coding: utf-8 -*-
import streamlit as st
import datetime
import pandas as pd
from io import BytesIO
import calendar
import sqlite3
from openpyxl.styles import Alignment, Font, PatternFill, Border, Side

# =========================
# 1. 資料庫功能 (維持原樣)
# =========================
DB_FILE = 'stats.db'
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS downloads (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, filename TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS visits (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()

# =========================
# 2. 核心計算工具
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
# 3. 生命藍圖階段數計算 (精準年齡條件)
# =========================
def calculate_blueprint_stages(birthday: datetime.date, hour: int, minute: int):
    # 拆解各單位數字
    y_sum = sum(int(x) for x in str(birthday.year))
    m_sum = sum(int(x) for x in f"{birthday.month:02}")
    d_sum = sum(int(x) for x in f"{birthday.day:02}")
    h_sum = sum(int(x) for x in f"{hour:02}")
    min_sum = sum(int(x) for x in f"{minute:02}")

    # 累加邏輯 (老 -> 幼)
    st_old = y_sum                      # 老年
    st_middle = st_old + m_sum          # 中年
    st_young_adult = st_middle + d_sum  # 青年
    st_teen = st_young_adult + h_sum    # 少年
    st_child = st_teen + min_sum        # 幼年

    # 這裡的順序決定了畫面上輸出的內容順序
    return [
        {"name": "老年階段", "age": "60 歲以上", "val": format_layers(st_old)},
        {"name": "中年階段", "age": "40 – 60 歲", "val": format_layers(st_middle)},
        {"name": "青年階段", "age": "20 – 39 歲", "val": format_layers(st_young_adult)},
        {"name": "少年階段", "age": "10 – 19 歲", "val": format_layers(st_teen)},
        {"name": "幼年階段", "age": "0 – 09 歲", "val": format_layers(st_child)},
    ]

def calculate_life_path_number(birthday: datetime.date):
    date_str = birthday.strftime("%Y%m%d")
    total_sum = sum(int(char) for char in date_str)
    final_num = reduce_to_digit(total_sum)
    process_str = f"{total_sum} → {final_num}"
    return final_num, total_sum, process_str

def life_year_number_for_date(birthday: datetime.date, query_date: datetime.date) -> int:
    cutoff = datetime.date(query_date.year, birthday.month, birthday.day)
    base_year = query_date.year - 1 if query_date < cutoff else query_date.year
    total = base_year + birthday.month + birthday.day
    return reduce_to_digit(sum_once(total))

# =========================
# 4. Streamlit 介面
# =========================
st.set_page_config(page_title="樂覺製所生命靈數 | Numerology", layout="centered")

st.title("🧭 樂覺製所生命靈數")
st.markdown("在數字之中，我們與自己不期而遇。\n**Be true, be you — 讓靈魂，自在呼吸。**")

# --- 輸入區佈局 ---
st.subheader("🌟 生命靈數 & 階段藍圖速算")
col_in1, col_in2 = st.columns(2)

with col_in1:
    # 放寬日期範圍，避免 1980 以前的日期報錯
    birthday = st.date_input("請輸入生日 (Birthday)", 
                             value=datetime.date(1990, 1, 1),
                             min_value=datetime.date(1900, 1, 1),
                             max_value=datetime.date(2100, 12, 31))
    st.markdown("**出生時間 (Time)**")
    t_c1, t_c2 = st.columns(2)
    with t_c1:
        birth_hour = st.number_input("時 (0-23)", 0, 23, 10)
    with t_c2:
        birth_min = st.number_input("分 (0-59)", 0, 59, 0)

with col_in2:
    ref_date = st.date_input("查詢日期 (Query Date)", value=datetime.date.today())

# --- 計算按鈕與顯示 ---
if st.button("🔮 計算靈數與階段藍圖 (Calculate)"):
    life_num, life_sum, life_process = calculate_life_path_number(birthday)
    
    st.markdown("---")
    st.markdown(f"### 🔮 您的生命靈數主命數：【 {life_num} 】號人")
    
    # 顯示階段藍圖：由左至右 (老年 -> 幼年)
    st.markdown("### 🗺️ 生命藍圖五大階段 (Life Blueprint Stages)")
    blueprint_stages = calculate_blueprint_stages(birthday, birth_hour, birth_min)
    
    s_cols = st.columns(5)
    # 直接循環計算結果，不再反轉，讓「老年階段」排在最左邊
    for i, stage in enumerate(blueprint_stages):
        with s_cols[i]:
            st.markdown(f"**{stage['name']}**")
            st.info(f"**{stage['val']}**")
            st.caption(stage['age'])
    
    st.markdown("---")
    today_n = life_year_number_for_date(birthday, ref_date)
    st.markdown(f"### 📊 查詢日期流年數：【 {today_n} 】")

# =========================
# 5. 管理員側邊欄
# =========================
st.sidebar.markdown("---")
st.sidebar.subheader("🔒 管理員專區")
admin_pwd = st.sidebar.text_input("輸入密碼", type="password")
if admin_pwd == "admin123":
    st.sidebar.success("已登入")
