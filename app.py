# -*- coding: utf-8 -*-
import streamlit as st
import datetime

# =========================
# 核心計算工具
# =========================
def reduce_to_digit(n: int) -> int:
    while n > 9:
        n = sum(int(c) for c in str(n))
    return n

def digit_sum(n: int) -> int:
    return sum(int(c) for c in str(n))

def format_layers(total: int) -> str:
    if total <= 9:
        return str(total)
    mid = digit_sum(total)
    if mid > 9:
        return f"{total}/{mid}/{reduce_to_digit(mid)}"
    return f"{total}/{mid}"

# =========================
# 流年計算邏輯
# =========================
def _safe_cutoff(year: int, month: int, day: int) -> datetime.date:
    """處理 2/29 生日在非閏年的情況，退回 2/28"""
    try:
        return datetime.date(year, month, day)
    except ValueError:
        return datetime.date(year, month, day - 1)

def life_year_number(birthday: datetime.date, query_date: datetime.date) -> int:
    cutoff = _safe_cutoff(query_date.year, birthday.month, birthday.day)
    base_year = query_date.year - 1 if query_date < cutoff else query_date.year
    total = base_year + birthday.month + birthday.day
    return reduce_to_digit(digit_sum(total))

# =========================
# 常量資料表
# =========================
YEAR_ADVICE = {
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

LUCKY_MAP = {
    1: {"色": "🔴 紅色", "水晶": "紅瑪瑙、石榴石", "小物": "原子筆"},
    2: {"色": "🟠 橙色", "水晶": "太陽石、橙月光", "小物": "月亮吊飾"},
    3: {"色": "🟡 黃色", "水晶": "黃水晶、黃虎眼", "小物": "紙膠帶"},
    4: {"色": "🟢 綠色", "水晶": "綠幽靈、孔雀石", "小物": "方形石頭"},
    5: {"色": "🔵 藍色", "水晶": "海藍寶、藍紋瑪瑙", "小物": "交通票卡"},
    6: {"色": "🔷 靛色", "水晶": "青金石、蘇打石", "小物": "愛心吊飾"},
    7: {"色": "🟣 紫色", "水晶": "紫水晶", "小物": "書籤"},
    8: {"色": "💗 粉色", "水晶": "粉晶、草莓晶", "小物": "鋼筆"},
    9: {"色": "⚪ 白色", "水晶": "白水晶、白月光", "小物": "小香包"},
}

UNKNOWN = "不知道"

# =========================
# 階段藍圖
# =========================
def _current_stage_index(age: int) -> int:
    if age >= 61:
        return 0
    if age >= 41:
        return 1
    if age >= 21:
        return 2
    if age >= 11:
        return 3
    return 4

def calculate_blueprint_stages(birthday, hour_str, min_str, ref_date):
    y_sum = digit_sum(birthday.year)
    month_sum = digit_sum(int(f"{birthday.month:02}"))
    day_sum = digit_sum(int(f"{birthday.day:02}"))

    stage_old = y_sum
    stage_mid = stage_old + month_sum
    stage_young = stage_mid + day_sum

    if hour_str == UNKNOWN:
        teen_display = "--"
        child_display = "--"
    else:
        hour_sum = digit_sum(int(f"{int(hour_str):02}"))
        teen_display = format_layers(stage_young + hour_sum)
        if min_str == UNKNOWN:
            child_display = "--"
        else:
            minute_sum = digit_sum(int(f"{int(min_str):02}"))
            child_display = format_layers(stage_young + hour_sum + minute_sum)

    age = ref_date.year - birthday.year - (
        (ref_date.month, ref_date.day) < (birthday.month, birthday.day)
    )
    active = _current_stage_index(age)

    return [
        ("老年階段", "61 歲以上",  format_layers(stage_old),   active == 0),
        ("中年階段", "41 – 60 歲", format_layers(stage_mid),   active == 1),
        ("青年階段", "21 – 40 歲", format_layers(stage_young), active == 2),
        ("少年階段", "11 – 20 歲", teen_display,               active == 3),
        ("幼年階段", "0 – 10 歲",  child_display,              active == 4),
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
    birthday = st.date_input(
        "請輸入生日 (Birthday)",
        value=datetime.date(1990, 1, 1),
        min_value=datetime.date(1900, 1, 1),
    )
    st.markdown("**出生時間 (Time)**")
    t_c1, t_c2 = st.columns(2)
    hour_options = [UNKNOWN] + [str(i) for i in range(24)]
    min_options = [UNKNOWN] + [str(i) for i in range(60)]
    with t_c1:
        birth_hour = st.selectbox("時 (Hour)", options=hour_options, index=11)
    with t_c2:
        birth_min = st.selectbox("分 (Min)", options=min_options, index=1)

with col_in2:
    ref_date = st.date_input("查詢日期 (Query Date)", value=datetime.date.today())

if st.button("🔮 開始計算"):
    st.markdown("---")

    # 1. 階段藍圖
    st.markdown("### 🗺️ 生命藍圖五大階段 (Life Blueprint Stages)")
    stages = calculate_blueprint_stages(birthday, birth_hour, birth_min, ref_date)
    s_cols = st.columns(5)

    ACTIVE_STYLE = (
        "background-color:#1A337E;color:white;"
        "padding:25px 10px;border-radius:15px;text-align:center;margin:15px 0;"
    )
    INACTIVE_STYLE = (
        "background-color:#E8F0FE;color:#1A337E;"
        "padding:25px 10px;border-radius:15px;text-align:center;margin:15px 0;"
    )

    for col, (name, age_range, val, is_active) in zip(s_cols, stages):
        with col:
            label = f"{name} ◀ 目前" if is_active else name
            style = ACTIVE_STYLE if is_active else INACTIVE_STYLE
            st.markdown(
                f"<p style='text-align:center;font-weight:bold;margin-bottom:-10px;'>{label}</p>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div style='{style}'>"
                f"<span style='font-size:24px;font-weight:bold;'>{val}</span></div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<p style='text-align:center;color:gray;font-size:0.8em;'>{age_range}</p>",
                unsafe_allow_html=True,
            )

    # 2. 流年結果
    st.markdown("---")
    year_num = life_year_number(birthday, ref_date)
    title, challenge, action, stars = YEAR_ADVICE.get(
        year_num, ("年度主題", "—", "—", "⭐⭐⭐")
    )
    lucky = LUCKY_MAP.get(year_num, {})

    st.markdown(f"### 📊 查詢日期流年數：【 {year_num} 】")
    st.markdown(f"**年度主題 (Theme)**：{title} \n\n**運勢指數**：{stars}")
    st.markdown(f"**挑戰 (Challenge)**：{challenge}")
    st.markdown(f"**建議行動 (Action)**：{action}")

    if lucky:
        st.info(
            f"✨ **幸運色**：{lucky['色']} ｜ "
            f"**水晶**：{lucky['水晶']} ｜ "
            f"**小物**：{lucky['小物']}"
        )

st.markdown("---")
st.caption("樂覺製所 © 2026 Numbertalk")
