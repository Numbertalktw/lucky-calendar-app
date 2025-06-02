
# -*- coding: utf-8 -*-
import streamlit as st
import datetime
import pandas as pd
from io import BytesIO
import calendar
from openpyxl.styles import Alignment, Font, PatternFill, Border, Side

day_meaning = {
    1: {"名稱": "創造日", "指引": "展現創意，展現自我魅力。", "星": "⭐⭐⭐⭐"},
    2: {"名稱": "連結日", "指引": "適合合作，溝通與等待機會。", "星": "⭐⭐"},
    3: {"名稱": "表達日", "指引": "表達想法，展現自我魅力。", "星": "⭐⭐⭐"},
    4: {"名稱": "實作日", "指引": "建立基礎，適合細節與規劃。", "星": "⭐⭐⭐"},
    5: {"名稱": "行動日", "指引": "啟動新的計畫，做出主動選擇。", "星": "⭐⭐⭐⭐"},
    6: {"名稱": "關係日", "指引": "接觸愛情，適當調整。", "星": "⭐⭐⭐"},
    7: {"名稱": "內省日", "指引": "適合學習、休息與自我對話。", "星": "⭐"},
    8: {"名稱": "成果日", "指引": "聚焦目標與務成就。", "星": "⭐⭐⭐⭐"},
    9: {"名稱": "釋放日", "指引": "放手，療癒與完成階段。", "星": "⭐⭐"},
}

lucky_map = {
    1: {"色": "🔴 紅色", "水晶": "紅瑪瑙", "小物": "原子筆"},
    2: {"色": "🟠 橘色", "水晶": "太陽石", "小物": "月亮吊飾"},
    3: {"色": "🟡 黃色", "水晶": "黃水晶", "小物": "紙膠帶"},
    4: {"色": "🟢 綠色", "水晶": "綠幽靈", "小物": "方形石頭"},
    5: {"色": "🔵 淺藍色", "水晶": "拉利瑪", "小物": "交通票卡"},
    6: {"色": "🔷 靛色", "水晶": "青金石", "小物": "愛心吊飾"},
    7: {"色": "🟣 紫色", "水晶": "紫水晶", "小物": "書籤"},
    8: {"色": "💗 粉色", "水晶": "粉晶", "小物": "鋼筆"},
    9: {"色": "⚪ 白色", "水晶": "白水晶", "小物": "小香包"},
}

def reduce_to_digit(n):
    while n > 9:
        n = sum(int(x) for x in str(n))
    return n

def format_layers(total):
    mid = sum(int(x) for x in str(total))
    return f"{total}/{mid}/{reduce_to_digit(mid)}" if mid > 9 else f"{total}/{mid}"

def get_additional_guidance(flowing_day_str):
    combinations = {
        "11/2": "這是合作與溝通的日子，適合建立新的合作關係，展現團隊精神。",
        "12/3": "表達自我與分享想法，創造愉快的氛圍，適合進行創意討論。",
        "13/4": "穩定與結構系列日子，適合規劃未來，建立穩固基礎。",
        "32/5": "平衡創意與行動，迎接新計畫，啟動變革。",
        "41/5": "務實行動與創意思考相結合，打造新機會。",
    }
    return combinations.get(flowing_day_str, "")

st.set_page_config(page_title="樂覺製所生命靈數", layout="centered")
st.title("🧭 樂覺製所生命靈數")
st.markdown("在數字之中，\n我們與自己不期而遇。\n**Be true, be you — 讓靈魂，自在呼吸。**")

birthday = st.date_input("請輸入生日", value=datetime.date(1990, 1, 1))
target_year = st.number_input("請選擇年份", min_value=1900, max_value=2100, value=datetime.datetime.now().year)
target_month = st.selectbox("請選擇月份", list(range(1, 13)), index=datetime.datetime.now().month - 1)

if st.button("🎉 產生日曆建議表"):
    _, last_day = calendar.monthrange(target_year, target_month)
    days = pd.date_range(start=datetime.date(target_year, target_month, 1), end=datetime.date(target_year, target_month, last_day))

    data = []
    for d in days:
        flowing_day_sum = sum(int(x) for x in f"{birthday.year}{birthday.month:02}{d.day:02}")
        flowing_day_str = format_layers(flowing_day_sum)
        main_number = reduce_to_digit(flowing_day_sum)
        meaning = day_meaning.get(main_number, {})
        lucky = lucky_map.get(main_number, {})

        guidance = meaning.get("指引", "") + " " + get_additional_guidance(flowing_day_str)

        data.append({
            "日期": d.strftime("%Y-%m-%d"),
            "星期": d.strftime("%A"),
            "流日": flowing_day_str,
            "指引": guidance,
            "幸運色": lucky.get("色", ""),
            "水晶": lucky.get("水晶", ""),
            "幸運小物": lucky.get("小物", "")
        })

    df = pd.DataFrame(data)
    st.dataframe(df)
