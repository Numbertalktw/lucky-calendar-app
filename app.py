import streamlit as st
import datetime
import pandas as pd
from io import BytesIO
import calendar
from openpyxl.styles import Alignment, Font, PatternFill, Border, Side

# ===== 主日數與幸運物件資料 =====
day_meaning = {}

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

# ===== 對應組合數指引字典 =====
flowing_day_guidance_map = {
    "11/2": "與自己的內在靈性連結，打開心眼從心去看清楚背後的真相。今天適合保持耐心，專注且細膩地與人合作，共創和諧和成長。",
    "12/3": "創意的想法和能量正在湧現，用純粹且動聽的方式傳遞出來。今天是和記錄靈感，或公開向他人表達自己的想法和觀點。",
    "13/4": "讓想法不再只是想像，是時候設法落實到自己的現實生活中。今天適合撰寫計畫、安排流程、理清脈絡，讓一切更明確。",
    "14/5": "轉化現有的狀態，從固有和凝滯的工作、關係中解脫，將內在矛盾的能量，轉變為生命的張力。適合打破常規、勇敢面對內在渴望。",
    "15/6": "會特別渴望與某人深入交談、分享心事。這也是個適合在工作中與夥伴溝通理想、清晰表達你期望成果的日子。",
    "59/14/5": "富有挑戰性的一天，過去所學將在此迎來挑戰、轉化與成長。建議保有靈活的彈性，也需謹慎面對過去未解議題。"
}

def reduce_to_digit(n):
    while n > 9:
        n = sum(int(x) for x in str(n))
    return n

def format_layers(total):
    mid = sum(int(x) for x in str(total))
    return f"{total}/{mid}/{reduce_to_digit(mid)}" if mid > 9 else f"{total}/{mid}"

def get_flowing_year_ref(query_date, bday):
    query_date = query_date.date() if hasattr(query_date, "date") else query_date
    cutoff = datetime.date(query_date.year, bday.month, bday.day)
    return query_date.year - 1 if query_date < cutoff else query_date.year

def get_flowing_month_ref(query_date, birthday):
    query_date = query_date.date() if hasattr(query_date, "date") else query_date
    if query_date.day < birthday.day:
        return query_date.month - 1 if query_date.month > 1 else 12
    return query_date.month

def get_flowing_day_guidance(flowing_day_str):
    return flowing_day_guidance_map.get(flowing_day_str, "")

def get_flowing_day_star(flowing_day_str):
    star_map = {
        "11/2": "⭐⭐",
        "12/3": "⭐⭐⭐⭐",
        "13/4": "⭐⭐⭐⭐",
        "14/5": "⭐⭐",
        "15/6": "⭐⭐⭐⭐",
        "16/7": "⭐⭐⭐",
        "17/8": "⭐⭐⭐⭐⭐",
        "18/9": "⭐⭐",
        "19/10/1": "⭐⭐⭐⭐",
        "20/2": "⭐⭐⭐",
        "21/3": "⭐⭐⭐⭐",
        "22/4": "⭐⭐⭐",
        "23/5": "⭐⭐⭐⭐",
        "24/6": "⭐⭐⭐",
        "25/7": "⭐⭐",
        "26/8": "⭐⭐⭐⭐⭐",
        "27/9": "⭐⭐⭐",
        "28/10/1": "⭐⭐⭐⭐⭐",
        "29/11/2": "⭐⭐⭐",
        "30/3": "⭐⭐⭐⭐",
        "31/4": "⭐⭐⭐⭐",
        "32/5": "⭐⭐⭐⭐",
        "33/6": "⭐⭐⭐",
        "34/7": "⭐⭐",
        "35/8": "⭐⭐⭐⭐⭐",
        "36/9": "⭐⭐⭐⭐",
        "37/10/1": "⭐⭐⭐⭐⭐",
        "38/11/2": "⭐⭐⭐",
        "39/12/3": "⭐⭐⭐⭐",
        "40/4": "⭐⭐⭐",
        "41/5": "⭐⭐⭐⭐",
        "42/6": "⭐⭐⭐",
        "43/7": "⭐⭐⭐",
        "44/8": "⭐⭐⭐⭐",
        "45/9": "⭐⭐⭐",
        "46/10/1": "⭐⭐⭐⭐",
        "47/11/2": "⭐⭐⭐",
        "48/12/3": "⭐⭐⭐⭐",
        "49/13/4": "⭐⭐⭐",
        "50/5": "⭐⭐⭐⭐",
        "51/6": "⭐⭐",
        "52/7": "⭐⭐⭐",
        "53/8": "⭐⭐⭐⭐",
        "54/9": "⭐⭐",
        "55/10/1": "⭐⭐⭐",
        "56/11/2": "⭐⭐",
        "57/12/3": "⭐⭐⭐⭐",
        "58/13/4": "⭐⭐⭐",
        "59/14/5": "⭐⭐⭐⭐⭐"
    }
    return star_map.get(flowing_day_str, "⭐⭐⭐")

def style_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="流年月曆")
        workbook = writer.book
        worksheet = workbook["流年月曆"]
        header_font = Font(size=12, bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")
        header_alignment = Alignment(horizontal="center", vertical="center")
        for idx, column in enumerate(df.columns):
            worksheet.column_dimensions[chr(65 + idx)].width = 15
        for cell in worksheet[1]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
        thin_border = Border(left=Side(style='thin'), right=Side(style='thin'),
                             top=Side(style='thin'), bottom=Side(style='thin'))
        for row in worksheet.iter_rows():
            for cell in row:
                cell.border = thin_border
                cell.alignment = Alignment(horizontal="center", vertical="center")
        for row in worksheet.iter_rows():
            worksheet.row_dimensions[row[0].row].height = 35
    return output

st.set_page_config(page_title="樂覺製所生命靈數", layout="centered")
st.title("🧭 樂覺製所生命靈數")
st.markdown("在數字之中，\n我們與自己不期而遇。\n**Be true, be you — 讓靈魂，自在呼吸。**")

birthday = st.date_input("請輸入生日", value=datetime.date(1990, 1, 1), min_value=datetime.date(1900, 1, 1))
target_year = st.number_input("請選擇年份", min_value=1900, max_value=2100, value=datetime.datetime.now().year)
target_month = st.selectbox("請選擇月份", list(range(1, 13)), index=datetime.datetime.now().month - 1)

if st.button("🎉 產生日曆建議表"):
    _, last_day = calendar.monthrange(target_year, target_month)
    days = pd.date_range(start=datetime.date(target_year, target_month, 1),
                         end=datetime.date(target_year, target_month, last_day))
    data = []
    for d in days:
        fd_total = sum(int(x) for x in f"{birthday.year}{birthday.month:02}{d.day:02}")
        flowing_day = format_layers(fd_total)
        main_number = reduce_to_digit(fd_total)
        meaning = day_meaning.get(main_number, {})
        lucky = lucky_map.get(main_number, {})
        guidance = get_flowing_day_guidance(flowing_day)
        year_ref = get_flowing_year_ref(d, birthday)
        fy_total = sum(int(x) for x in f"{year_ref}{birthday.month:02}{birthday.day:02}")
        flowing_year = format_layers(fy_total)
        fm_ref = get_flowing_month_ref(d, birthday)
        fm_total = sum(int(x) for x in f"{birthday.year}{fm_ref:02}{birthday.day:02}")
        flowing_month = format_layers(fm_total)
        date_str = d.strftime("%Y-%m-%d")
        weekday_str = d.strftime("%A")
        data.append({
            "日期": date_str,
            "運勢指數": get_flowing_day_star(flowing_day),
            "星期": weekday_str,
            "流年": flowing_year,
            "流月": flowing_month,
            "流日": flowing_day,
            "運勢指數": meaning.get("星", ""),
            "指引": guidance,
            "幸運色": lucky.get("色", ""),
            "水晶": lucky.get("水晶", ""),
            "幸運小物": lucky.get("小物", "")
        })
    df = pd.DataFrame(data)
    st.dataframe(df)
    file_name = f"LuckyCalendar_{target_year}_{str(target_month).zfill(2)}.xlsx"
    title = "樂覺製所生命靈數"
    subtitle = "在數字之中，我們與自己不期而遇。Be true, be you — 讓靈魂，自在呼吸。"
    if not df.empty and df.dropna(how='all').shape[0] > 0:
        output = style_excel(df)
        st.markdown(f"### {title}")
        st.markdown(f"**{subtitle}**")
        st.download_button(
            "📥 點此下載 " + file_name.replace(".xlsx", " 年靈數流日建議表（三層加總斜線版）"),
            data=output.getvalue(),
            file_name=file_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("⚠️ 無法匯出 Excel：目前資料為空，請先產生日曆資料")
