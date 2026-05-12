# -*- coding: utf-8 -*-
import streamlit as st
import datetime
import pandas as pd

# =========================
# 核心計算工具
# =========================
def reduce_to_digit(n: int) -> int:
    """反覆位數相加直到一位數"""
    while n > 9:
        n = sum(int(x) for x in str(n))
    return n

def sum_once(n: int) -> int:
    """只做一次位數相加"""
    return sum(int(x) for x in str(n))

def format_layers(total: int) -> str:
    """輸出三段式標示 (例如 28/10/1)"""
    mid = sum_once(total)
    if mid > 9:
        return f"{total}/{mid}/{reduce_to_digit(mid)}"
    else:
        return f"{total}/{mid}"

# =========================
# 流年計算邏輯
# =========================
def life_year_number_for_date(birthday: datetime.date, query_date: datetime.date) -> int:
    """計算指定日期的流年數"""
    cutoff = datetime.date(query_date.year, birthday.month, birthday.day)
    base_year = query_date.year - 1 if query_date < cutoff else query_date.year
    total = base_year + birthday.month + birthday.day
    return reduce_to_digit(sum_once(total))

def get_year_advice(n: int):
    advice = {
        1: ("自主與突破之年", "容易衝動、單打獨鬥", "設定清晰目標；蒐集意見、給自己緩衝時間。", "⭐⭐⭐⭐"),
        2: ("協作與關係之年", "過度迎合、忽略自我", "練習明確表達需求、建立健康邊界。", "⭐⭐⭐"),
        3: ("創意與表達之年", "分心、情緒起伏", "為創作與學習預留固定時段；公開練習。", "⭐⭐⭐⭐"),
        4: ("穩定與基礎之年", "壓力感、僵化完美主義", "用『可持續的小步驟』築基礎。", "⭐⭐⭐"),
        5: ("變動與自由之年", "焦躁、衝動決策", "先設安全網再突破；用短衝測試新方向。", "⭐⭐⭐⭐"),
        6: ("關懷與責任之年", "過度承擔、忽略自我", "把『照顧自己』寫進行程；清楚承諾。", "⭐⭐⭐"),
        7: ("內省與學習之年", "孤立、鑽牛角尖", "安排獨處＋定期對談；用寫作/冥想整理。", "⭐⭐⭐"),
        8: ("事業與財務之年", "過度追求成就、忽略健康情感", "設定績效與復原節奏並行；學會授權。", "⭐⭐⭐⭐"),
        9: ("收尾與釋放之年", "抗拒結束、情緒回顧", "用感恩做結案；做斷捨離，替新循環清出空間。", "⭐⭐⭐"),
    }
    return advice.get(n, ("年度主題", "—", "—", "⭐⭐⭐"))

lucky_map = {
    1: {"色": "🔴 紅色", "水晶": "紅瑪瑙、石榴石", "小物": "原子筆"},
    2: {"色": "🟠 橙色", "水晶": "太陽石、橙月光", "小物": "月亮吊飾"},
    3: {"色": "🟡 黃色", "水晶": "黃水晶、黃虎眼", "小物": "紙膠帶"},
    4: {"色": "🟢 綠色", "水晶": "綠幽靈", "孔雀石", "小物": "方形石頭"},
    5: {"色": "🔵 藍色", "水晶": "海藍寶、藍紋瑪瑙", "小物": "交通票卡"},
    6: {"色": "🔷 靛色", "水晶": "青金石、蘇打石", "小物": "愛心吊飾"},
    7: {"色": "🟣 紫色", "水晶": "紫水晶", "小物": "書籤"},
    8: {"色": "💗 粉色", "水晶": "粉晶、草莓晶", "小物": "鋼筆"},
    9: {"色": "⚪ 白色", "水晶": "白水晶、白月光", "小物": "小香包"},
}

# =========================
# 階段藍圖與自動高亮判斷
# =========================
def get_current_stage_idx(age):
    if age >= 61: return 0  
    if 41 <= age < 60: return 1  
    if 21 <= age < 40: return 2  
    if 11 <= age < 20: return 3  
    return 4  

def calculate_blueprint_stages(birthday, hour_val, min_val, ref_date):
    y_sum = sum(int(x) for x in str(birthday.year))
    m_sum = sum(int(x) for x in f"{birthday.month:02}")
    d_sum = sum(int(x) for x in f"{birthday.day:02}")
    
    st_old = y_sum
    st_middle = st_old + m_sum
    st_young_adult = st_middle + d_sum

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

    current_age = ref_date.year - birthday.year - ((ref_date.month, ref_date.day) < (birthday.month, birthday.day))
    active_idx = get_current_stage_idx(current_age)

    return [
        {"name": "老年階段", "age": "61 歲以上", "val": format_layers(st_old), "active": active_idx == 0},
        {"name": "中年階段", "age": "41 – 60 歲", "val": format_layers(st_middle), "active": active_idx == 1},
        {"name": "青年階段", "age": "21 – 40 歲", "val": format_layers(st_young_adult), "active": active_idx == 2},
        {"name": "少年階段", "age": "11 – 20 歲", "val": st_teen_display, "active": active_idx == 3},
        {"name": "幼年階段", "age": "0 – 10 歲", "val": st_child_display, "active": active_idx == 4},
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

if st.button("🔮 開始計算"):
    st.markdown("---")
    
    # 1. 顯示階段藍圖
    st.markdown("### 🗺️ 生命藍圖五大階段 (Life Blueprint Stages)")
    stages = calculate_blueprint_stages(birthday, birth_hour, birth_min, ref_date)
    s_cols = st.columns(5)
    
    for i, stage in enumerate(stages):
        with s_cols[i]:
            title_label = f"{stage['name']} ◀ 目前" if stage['active'] else stage['name']
            st.markdown(f"<p style='text-align: center; font-weight: bold; margin-bottom: -10px;'>{title_label}</p>", unsafe_allow_html=True)
            
            if stage['active']:
                st.markdown(f"""<div style="background-color: #1A337E; color: white; padding: 25px 10px; border-radius: 15px; text-align: center; margin: 15px 0;"><span style="font-size: 24px; font-weight: bold;">{stage['val']}</span></div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""<div style="background-color: #E8F0FE; color: #1A337E; padding: 25px 10px; border-radius: 15px; text-align: center; margin: 15px 0;"><span style="font-size: 24px; font-weight: bold;">{stage['val']}</span></div>""", unsafe_allow_html=True)
            
            st.markdown(f"<p style='text-align: center; color: gray; font-size: 0.8em;'>{stage['age']}</p>", unsafe_allow_html=True)

    # 2. 顯示流年結果
    st.markdown("---")
    today_n = life_year_number_for_date(birthday, ref_date)
    title, challenge, action, stars = get_year_advice(today_n)
    lucky = lucky_map.get(today_n, {})
    
    st.markdown(f"### 📊 查詢日期流年數：【 {today_n} 】")
    st.markdown(f"**年度主題 (Theme)**：{title} \n\n**運勢指數**：{stars}")
    st.markdown(f"**挑戰 (Challenge)**：{challenge}")
    st.markdown(f"**建議行動 (Action)**：{action}")
    
    if lucky:
        st.info(f"✨ **幸運色**：{lucky.get('色')} ｜ **水晶**：{lucky.get('水晶')} ｜ **小物**：{lucky.get('小物')}")

st.markdown("---")
st.caption("樂覺製所 © 2026 Numbertalk")
