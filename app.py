# -*- coding: utf-8 -*-
import streamlit as st
import datetime
import pandas as pd
from io import BytesIO
import calendar
from openpyxl.styles import Alignment, Font, PatternFill, Border, Side

# =========================
# 公用數字處理
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
    """輸出三段式（或二段式）顯示"""
    mid = sum_once(total)
    return f"{total}/{mid}/{reduce_to_digit(mid)}" if mid > 9 else f"{total}/{mid}"

# =========================
# 生命靈數：流年計算（以生日為切點）
# =========================
def life_year_number_for_year(birthday: datetime.date, query_year: int) -> tuple[int, int]:
    before_total = (query_year - 1) + birthday.month + birthday.day
    after_total  = (query_year)     + birthday.month + birthday.day
    return reduce_to_digit(sum_once(before_total)), reduce_to_digit(sum_once(after_total))

def life_year_number_for_date(birthday: datetime.date, query_date: datetime.date) -> int:
    cutoff = datetime.date(query_date.year, birthday.month, birthday.day)
    base_year = query_date.year - 1 if query_date < cutoff else query_date.year
    total = base_year + birthday.month + birthday.day
    return reduce_to_digit(sum_once(total))

# =========================
# 流年解說
# =========================
def get_year_advice(n: int):
    advice = {
        1: ("自主與突破之年", "容易衝動、單打獨鬥",
            "設定清晰目標；在決策前先蒐集意見、給自己緩衝時間。", "⭐⭐⭐⭐"),
        2: ("協作與關係之年", "過度迎合、忽略自我",
            "練習明確表達需求、建立健康邊界；耐心溝通。", "⭐⭐⭐"),
        3: ("創意與表達之年", "分心、情緒起伏",
            "為創作與學習預留固定時段；公開練習表達。", "⭐⭐⭐⭐"),
        4: ("穩定與基礎之年", "壓力感、僵化完美主義",
            "用『可持續的小步驟』築基礎；為計畫預留彈性。", "⭐⭐⭐"),
        5: ("變動與自由之年", "焦躁、衝動決策",
            "先設安全網再突破；用短衝 (sprint) 測試新方向。", "⭐⭐⭐⭐"),
        6: ("關懷與責任之年", "過度承擔、忽略自我",
            "把『照顧自己』寫進行程；清楚承諾與界線。", "⭐⭐⭐"),
        7: ("內省與學習之年", "孤立、鑽牛角尖",
            "安排獨處＋定期對談；用寫作/冥想整理解讀。", "⭐⭐⭐"),
        8: ("事業與財務之年", "過度追求成就、忽略健康情感",
            "設定績效與復原節奏並行；學會授權與談判。", "⭐⭐⭐⭐"),
        9: ("收尾與釋放之年", "抗拒結束、情緒回顧",
            "用感恩做結案；做斷捨離，替新循環清出空間。", "⭐⭐⭐"),
    }
    return advice.get(n, ("年度主題", "—", "—", "⭐⭐⭐"))

# =========================
# 新 lucky_map（覆蓋水晶建議）
# =========================
lucky_map = {
    1: {"色": "🔴 紅色", "水晶": "紅瑪瑙、紅碧玉、石榴石、紫牙烏、紅虎眼石、紅幽靈、硃砂石", "小物": "原子筆"},
    2: {"色": "🟠 橙色", "水晶": "橙月光石、太陽石、橙方解石、紅膠花、金太陽", "小物": "月亮吊飾"},
    3: {"色": "🟡 黃色", "水晶": "黃水晶、黃玉、鈦金、黃虎眼石、阿拉善", "小物": "紙膠帶"},
    4: {"色": "🟢 綠色", "水晶": "綠東陵石、孔雀石、綠幽靈、西瓜碧璽、綠松石、橄欖石、葡萄石、藍綠晶、藥王石", "小物": "方形石頭"},
    5: {"色": "🔵 藍色", "水晶": "海藍寶石、藍晶石、藍紋瑪瑙、藍月光、藍虎眼、拉長石、拉利瑪、天河石、藍綠晶", "小物": "交通票卡"},
    6: {"色": "🔷 靛色", "水晶": "青金石、蘇打石、鷹眼石、菫青石", "小物": "愛心吊飾"},
    7: {"色": "🟣 紫色", "水晶": "紫水晶、紫螢石、紫龍晶、紫鋰輝、薰衣草紫水晶、坦桑石、紫幽靈、丹泉石", "小物": "書籤"},
    8: {"色": "💗 粉色", "水晶": "粉晶、草莓晶、粉碧璽、薔薇石、摩根石、櫻花瑪瑙、馬粉粉晶", "小物": "鋼筆"},
    9: {"色": "⚪ 白色", "水晶": "白水晶、白月光石、白松石、白阿賽", "小物": "小香包"},
    0: {"色": "⚫️ 黑色", "水晶": "黑曜石、黑碧璽、銀曜石、金曜石、金運石、骨幹黑太陽、閃靈鑽", "小物": "護身符"},
}

# =========================
# 流日指引 & 星等
# =========================
# ...（這裡沿用你現有的 flowing_day_guidance_map 和 get_flowing_day_star）
# 內容太長我就不重貼，保持不動

# =========================
# 匯出 Excel 樣式
# =========================
def style_excel(df: pd.DataFrame) -> BytesIO:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="流年月曆")
        workbook = writer.book
        worksheet = workbook["流年月曆"]

        header_font = Font(size=12, bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")
        header_alignment = Alignment(horizontal="center", vertical="center")

        for idx, column in enumerate(df.columns):
            max_length = max((len(str(cell)) for cell in df[column]), default=15)
            adjusted_width = max(15, min(int(max_length * 1.2), 100))
            worksheet.column_dimensions[chr(65 + idx)].width = adjusted_width

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
            worksheet.row_dimensions[row[0].row].height = 35
    return output

# =========================
# Streamlit 介面
# =========================
st.set_page_config(page_title="樂覺製所生命靈數", layout="centered")
st.title("🧭 樂覺製所生命靈數")
st.markdown("在數字之中，\n我們與自己不期而遇。\n**Be true, be you — 讓靈魂，自在呼吸。**")

# -------- 區塊 A：流年速算 --------
st.subheader("🌟 流年速算")
col1, col2 = st.columns([1.2, 1.2])
with col1:
    birthday = st.date_input("請輸入生日", value=datetime.date(1990, 1, 1),
                             min_value=datetime.date(1900, 1, 1))
with col2:
    ref_date = st.date_input("查詢日期", value=datetime.date(datetime.datetime.now().year, 12, 31))

if st.button("計算流年"):
    today_n = life_year_number_for_date(birthday, ref_date)
    before_n, after_n = life_year_number_for_year(birthday, ref_date.year)

    st.markdown("### 📊 流年結果")
    st.write(f"**本年流年數（依查詢日期 {ref_date}）：** {today_n}")
    st.caption(f"今年生日前：{before_n} ｜ 生日當天起：{after_n}")

    title, challenge, action, stars = get_year_advice(today_n)
    lucky = lucky_map.get(today_n, {})

    st.markdown("#### 🪄 流年解說（依目前查詢日）")
    st.markdown(
        f"""
**主題**：{title}  
**年度運勢指數**：{stars}  
**可能挑戰**：{challenge}  
**建議行動**：{action}  

**幸運顏色**：{lucky.get('色','')}  
**建議水晶**：{lucky.get('水晶','')}
        """
    )

# -------- 區塊 B：流年月曆產生器 --------
st.subheader("📅 產生 1 個月份的『流年月曆』建議表")
target_month = st.selectbox("請選擇月份", list(range(1, 13)), index=datetime.datetime.now().month - 1)

if st.button("🎉 產生日曆建議表"):
    target_year_for_calendar = ref_date.year
    _, last_day = calendar.monthrange(target_year_for_calendar, target_month)
    days = pd.date_range(start=datetime.date(target_year_for_calendar, target_month, 1),
                         end=datetime.date(target_year_for_calendar, target_month, last_day))

    data = []
    for d in days:
        fd_total = sum(int(x) for x in f"{birthday.year}{birthday.month:02}{d.day:02}")
        flowing_day = format_layers(fd_total)
        main_number = reduce_to_digit(fd_total)
        lucky = lucky_map.get(main_number, {})
        guidance = ""  # 這裡省略，仍然可接上 flowing_day_guidance_map

        data.append({
            "日期": d.strftime("%Y-%m-%d"),
            "星期": d.strftime("%A"),
            "流年": "-",  # 可接上流年公式
            "流月": "-",  # 可接上流月公式
            "流日": flowing_day,
            "運勢指數": "-",  # 可接上 get_flowing_day_star
            "指引": guidance,
            "幸運色": lucky.get("色", ""),
            "水晶": lucky.get("水晶", "").replace("、", "\n"),  # 換行顯示
            "幸運小物": lucky.get("小物", "")
        })

    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)

    file_name = f"LuckyCalendar_{target_year_for_calendar}_{str(target_month).zfill(2)}.xlsx"
    if not df.empty and df.dropna(how='all').shape[0] > 0:
        output = style_excel(df)
        st.download_button(
            "📥 點此下載 " + file_name.replace(".xlsx", " 年靈數流日建議表（三層加總斜線版）"),
            data=output.getvalue(),
            file_name=file_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("⚠️ 無法匯出 Excel：目前資料為空，請先產生日曆資料")
