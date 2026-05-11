# -*- coding: utf-8 -*-
import streamlit as st
import datetime
import pandas as pd
from io import BytesIO
import calendar
import sqlite3
from openpyxl.styles import Alignment, Font, PatternFill, Border, Side

# =========================
# 1. 資料庫功能
# =========================
DB_FILE = 'stats.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS downloads (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, filename TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS visits (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

def log_download(filename):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO downloads (filename) VALUES (?)", (filename,))
    conn.commit()
    conn.close()

def log_visit():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO visits (timestamp) VALUES (CURRENT_TIMESTAMP)")
    conn.commit()
    conn.close()

def get_download_stats():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT timestamp, filename FROM downloads ORDER BY timestamp DESC", conn)
    conn.close()
    return df

def get_visit_stats():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT timestamp FROM visits ORDER BY timestamp DESC", conn)
    conn.close()
    return df

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
    """產出三段式標示，如 28/10/1"""
    mid = sum_once(total)
    if mid > 9:
        return f"{total}/{mid}/{reduce_to_digit(mid)}"
    else:
        return f"{total}/{mid}"

# =========================
# 3. 生命藍圖階段數計算 (更新年齡條件)
# =========================
def calculate_blueprint_stages(birthday: datetime.date, hour: int, minute: int):
    # 拆解生日各項加總
    y_sum = sum(int(x) for x in str(birthday.year))
    m_sum = sum(int(x) for x in f"{birthday.month:02}")
    d_sum = sum(int(x) for x in f"{birthday.day:02}")
    h_sum = sum(int(x) for x in f"{hour:02}")
    min_sum = sum(int(x) for x in f"{minute:02}")

    # 累加邏輯
    st_old = y_sum                      # 老年：年
    st_middle = st_old + m_sum          # 中年：年+月
    st_young_adult = st_middle + d_sum  # 青年：年+月+日
    st_teen = st_young_adult + h_sum    # 少年：年+月+日+時
    st_child = st_teen + min_sum        # 幼年：年+月+日+時+分

    return [
        {"name": "老年階段", "age": "60 歲以上", "val": format_layers(st_old)},
        {"name": "中年階段", "age": "40 – 60 歲", "val": format_layers(st_middle)},
        {"name": "青年階段", "age": "20 – 39 歲", "val": format_layers(st_young_adult)},
        {"name": "少年階段", "age": "10 – 19 歲", "val": format_layers(st_teen)},
        {"name": "幼年階段", "age": "0 – 09 歲", "val": format_layers(st_child)},
    ]

def calculate_life_path_number(birthday: datetime.date) -> tuple[int, int, str]:
    date_str = birthday.strftime("%Y%m%d")
    total_sum = sum(int(char) for char in date_str)
    final_num = reduce_to_digit(total_sum)
    process_str = f"{total_sum} → {final_num}"
    if total_sum != final_num and total_sum > 9:
        second_step = sum_once(total_sum)
        if second_step > 9 and second_step != final_num:
             process_str = f"{total_sum} → {second_step} → {final_num}"
    return final_num, total_sum, process_str

def life_year_number_for_date(birthday: datetime.date, query_date: datetime.date) -> int:
    cutoff = datetime.date(query_date.year, birthday.month, birthday.day)
    base_year = query_date.year - 1 if query_date < cutoff else query_date.year
    total = base_year + birthday.month + birthday.day
    return reduce_to_digit(sum_once(total))

# =========================
# 4. Streamlit 介面設定
# =========================
st.set_page_config(page_title="樂覺製所生命靈數 | Numerology", layout="centered")

if 'has_visited' not in st.session_state:
    log_visit()
    st.session_state['has_visited'] = True

st.title("🧭 樂覺製所生命靈數")
st.markdown("在數字之中，我們與自己不期而遇。\n**Be true, be you — 讓靈魂，自在呼吸。**")

# =========================
# 5. 區塊 A：生命靈數 & 階段藍圖速算
# =========================
st.subheader("🌟 生命靈數 & 階段藍圖速算 (Life Path & Blueprint)")

# --- 輸入區佈局 ---
col_in1, col_in2 = st.columns(2)

with col_in1:
    birthday = st.date_input("請輸入生日 (Birthday)", value=datetime.date(1990, 1, 1))
    
    # 時間輸入區 - 確保用戶可以看到並輸入
    st.markdown("**出生時間 (Time)**")
    t_c1, t_c2 = st.columns(2)
    with t_c1:
        birth_hour = st.number_input("時 (0-23)", 0, 23, 10, key="blue_hr")
    with t_c2:
        birth_min = st.number_input("分 (0-59)", 0, 59, 0, key="blue_min")

with col_in2:
    ref_date = st.date_input("查詢日期 (Query Date)", value=datetime.date.today())

# 計算按鈕
if st.button("🔮 計算靈數與階段藍圖 (Calculate)"):
    # --- 1. 計算主命數 ---
    life_num, life_sum, life_process = calculate_life_path_number(birthday)
    
    st.markdown("---")
    st.markdown(f"### 🔮 您的生命靈數主命數：【 {life_num} 】號人")
    st.caption(f"計算公式：{birthday.strftime('%Y/%m/%d')} → {life_process}")
    
    # --- 2. 生命藍圖：五大階段數顯示區 ---
    st.markdown("### 🗺️ 生命藍圖五大階段 (Life Blueprint Stages)")
    blueprint_stages = calculate_blueprint_stages(birthday, birth_hour, birth_min)
    
    # 橫向排列 5 個方塊：由左至右為 幼年 -> 少年 -> 青年 -> 中年 -> 老年
    s_cols = st.columns(5)
    # 使用 reversed 將計算結果 (老->幼) 反轉為顯示順序 (幼->老)
    for i, stage in enumerate(reversed(blueprint_stages)):
        with s_cols[i]:
            st.markdown(f"**{stage['name']}**")
            st.info(f"**{stage['val']}**")
            st.caption(stage['age'])
    
    st.markdown("---")
    
    # --- 3. 流年結果 ---
    today_n = life_year_number_for_date(birthday, ref_date)
    st.markdown(f"### 📊 查詢日期流年數：【 {today_n} 】")
    st.write(f"本查詢日期為 **{ref_date}**，對應之流年數字代表您當前的年度能量狀態。")

# =========================
# 6. 其他功能 (月曆與側邊欄)
# =========================
st.sidebar.markdown("---")
st.sidebar.subheader("🔒 管理員專區")
admin_pwd = st.sidebar.text_input("輸入密碼", type="password")
if admin_pwd == "admin123":
    st.sidebar.success("已登入")
    v_df = get_visit_stats()
    st.sidebar.metric("👀 總瀏覽", len(v_df))
