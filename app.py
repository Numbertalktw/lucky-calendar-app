st.write("🟢 成功啟動")

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
    "16/7": "整理內在與學習的好時機，感到精神渙散時，需要讓自己靜下來。今天適合寫作、閱讀，讓思緒重新歸位。",
    "17/8": "會特別想處理與金錢、服務或管理相關的問題。這也是收穫成果和關係的時刻，適合謀劃、打交道，追求更高品質與效率。",
    "18/9": "在新階段來臨之前，先學會放下、告別與結束，讓舊故事畫上句點。今天適合理清關係、承認錯誤、給予原諒與表達感謝之意。",
    "19/10/1": "會發現自己比平時更容易接收到來自內在或外在的靈感，適合冥想、記錄夢境，或展開具有靈性意圖的計畫。",
    "20/2": "內在外在都將迎來翻轉式的改變，藉此時候讓自己透過不同角度的交換，去洞見更加清晰的真相。",
    "21/3": "今天點子和想法會比平常要多，好好運用溝通和表達來創造。適合簡報、創作、教學、社交活動。",
    "22/4": "多任務、多變動的一天。保持耐心與行動力，同時照顧好自己的身體與情緒狀態。",
    "23/5": "是時候接收新的刺激和變動，過程難免會受到一些阻力，但這同時也是在考驗自己是否有足夠勇氣。",
    "24/6": "關心自己身邊親近的家人朋友，承諾與責任是今天的主題。適合整理居家空間、放鬆和照顧自己的身體。",
    "25/7": "專注在自己的事情上，在這當中找回內在的平靜與和諧感。適合進行個人計畫或閱讀、寫作、靜坐練習。",
    "26/8": "強化自信與擔當，適合接下責任、處理財務、設定下一步策略。",
    "27/9": "透過真理看見真相，有意識地放下是今天的重點。適合從事志工、服務、或療癒性的對談與釋放。",
    "28/10/1": "有強大顯化力與執行力的日子。保持務實、負責的態度，適合思考一個遠大的目標，和規劃財務相關的事情。",
    "29/11/2": "透過傾聽和觀察，從更高乃至於智慧和靈性的層次，來解讀來到自己眼前的事情。適合處理文書工作、手作、合作。",
    "30/3": "今天的主題是溝通與協調，運用創意來做包裝和行銷，讓想法和點子得以表現出來。適合做發想、藝術創作、設計、銷售相關的事情。",
    "31/4": "創造中蘊含結構，靈感需要被規劃來落地。今天適合制定章程、流程、或開始長期創作計畫。",
    "32/5": "保持靈活和彈性，敞開心釋放和接收愛，有機會突破或碰上有趣的邂逅。適合旅遊、陌生開發、跳脫舒適圈。",
    "33/6": "用創意、好玩的方式去服務和關愛，適合關注家庭、孩子，進行深度對話，這是一個釋放壓抑與傳遞愛的好時機。",
    "34/7": "今日會想獨處反思，注意情緒管控。適合回顧和整理思緒、學習吸收新知，直覺和靈感將從寧靜與平靜中到來。",
    "35/8": "推進與擴張的日子，結合創意與商業頭腦。適合進行工作業務推展、投資、開創和收穫人脈與財富資源。",
    "36/9": "在理想與現實之間取得平衡點，透過服務與奉獻幫助他人。今天是極具和諧感的一天，適合藝術、療癒、或在關係中給予溫柔陪伴。",
    "37/10/1": "適時站出來為自己發聲，或成為真理的代言人，勇敢展現和展開新的行動。",
    "38/11/2": "運用之前累積的生命經驗來協助身邊重要的夥伴、家人，用風趣的方式點出問題，讓一切繼續進行。",
    "39/12/3": "聲音和語言是具有非常大能量的，用聲音和話語去讚美自己和他人。適合統整想法、產生共識、聊天談心。",
    "40/4": "以團且穩固為前提，專注於更新現有的框架和架構，再次建立新的且扎實的結構，避免過度墨守規則。",
    "41/5": "穩定中尋求自由。突破常規，學會在變動中保持平衡與對生命的熱忱，靈活應對。",
    "42/6": "規矩紀律需與人際關係並重，把守規律的同時，也需考量到感性層面的事情，與家人或團隊共進。",
    "43/7": "有強大的組織和分析能力，需留意自己的情緒控管與說話的方式。適合重看過去不理解的關係、書籍，重新找出重點。",
    "44/8": "今天你將具強大執行力與影響力，繼續扎穩腳步的同時，一邊等待機運與突破口，需避免固執而忽略他人聲音。",
    "45/9": "運用理性、邏輯的方式，深入核心去省思，以成就自身智慧。適合做段捨離、幫助和成就他人。",
    "46/10/1": "成為工作或家庭中的帶動者，展現組織團隊及合作能力，聚焦目標為責任與承諾付諸行動。",
    "47/11/2": "扮演好一個穩定且可靠的關鍵角色，在重要時刻協助他人過關。適合找與人進行合作、近一步拉近關係。",
    "48/12/3": "在審慎評估、留意細節的前提下，做出一些變化和富有創意的決策。適合做評估和調查、制定行銷方案。",
    "49/13/4": "在穩定的基礎下，做出取捨和更新當下的狀態，透過智慧提升到更高的境界。適合帶領團隊、或處理家庭問題。",
    "50/5": "在變動與不平穩之中，隱藏著意想不到的機會，享受和把握這美好的時刻。適合開拓新領域或拓展眼界和人際關係。",
    "51/6": "勇敢的面對自己的恐懼和創傷，唯有與自己和解才能真正脫離情緒上的束縛。適合從事自我療癒、陪伴他人談心。",
    "52/7": "從事情的核心切入，一層一層的剖析和理解，最終將看見真相。今天適合獨處深思，觀察情緒波動背後的原因。",
    "53/8": "有機會創造可觀的財富收入或人生經驗，保持開放多接觸會有收穫。適合去做體驗、推廣自己的服務或商品。",
    "54/9": "是時候從漫無目的慢慢收斂聚焦，有意識地放下感謝過往自己的努力。適合讓事情和關係告一段落，準備進入下個階段。",
    "55/10/1": "極度的外放和自我展現，背後產生的是冒犯與侵略。留意行車狀態、練習保持專注。",
    "56/11/2": "個人的自由與承諾之間形成矛盾關係，如何跳脫二元對立的思維模式，是今天的重點。",
    "57/12/3": "留意自己內在的想法和直覺，很多方向和答案都在那裡。適合嘗試新媒介、新寫作、新表演形式或學習新語言。",
    "58/13/4": "在各種變動的情況中，整合出新流程和規則。今天可設定行程、修正結構、找回穩定節奏。",
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
