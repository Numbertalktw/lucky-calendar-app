if st.button("🎉 產生日曆建議表"):

    _, last_day = calendar.monthrange(target_year, target_month)
    days = pd.date_range(start=datetime.date(target_year, target_month, 1),
                         end=datetime.date(target_year, target_month, last_day))

    data = []
    for d in days:
        # 🔢 流日：用生日年 + 查詢月 + 查詢日
        fd_sum = sum(int(x) for x in f"{birthday.year}{d.month:02}{d.day:02}")
        fd_mid = sum(int(x) for x in str(fd_sum))
        fd_final = reduce_to_digit(fd_mid)
        flow_day = f"{fd_sum}/{fd_mid}/{fd_final}"

        # 指引查表（若無資料則顯示空白）
        guidance = flowday_guidance.get(flow_day, "")

        # 🔢 流月：用生日年 + 查詢月 + 出生日
        fm_sum = sum(int(x) for x in f"{birthday.year}{d.month:02}{birthday.day:02}")
        fm_mid = sum(int(x) for x in str(fm_sum))
        fm_final = reduce_to_digit(fm_mid)
        flow_month = f"{fm_sum}/{fm_mid}/{fm_final}"

        # 🔢 流年：以生日為切換點（若查詢日期早於今年生日，則用去年年份）
        base_year = d.year - 1 if d < datetime.date(d.year, birthday.month, birthday.day) else d.year
        fy_sum = sum(int(x) for x in f"{base_year}{birthday.month:02}{birthday.day:02}")
        fy_mid = sum(int(x) for x in str(fy_sum))
        fy_final = reduce_to_digit(fy_mid)
        flow_year = f"{fy_sum}/{fy_mid}/{fy_final}"

        # 📅 日期與星期
        date_str = d.strftime("%Y-%m-%d")
        weekday_str = d.strftime("%A")

        data.append({
            "日期": date_str,
            "星期": weekday_str,
            "流年": flow_year,
            "流月": flow_month,
            "流日": flow_day,
            "指引": guidance
        })

    df = pd.DataFrame(data)
    st.dataframe(df)

    # 📥 Excel 下載
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="流年月曆")
        workbook = writer.book
        sheet = workbook.active

        # 美化表頭
        for cell in sheet[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")
            cell.alignment = Alignment(horizontal="center", vertical="center")

        # 自動寬度與邊框
        for row in sheet.iter_rows():
            for cell in row:
                cell.alignment = Alignment(horizontal="center", vertical="center")
                cell.border = Border(
                    left=Side(style='thin'), right=Side(style='thin'),
                    top=Side(style='thin'), bottom=Side(style='thin')
                )
        for col in sheet.columns:
            max_len = max(len(str(cell.value)) for cell in col)
            sheet.column_dimensions[col[0].column_letter].width = max_len + 4

    output.seek(0)
    st.download_button(
        label="📥 下載流日建議表",
        data=output,
        file_name=f"lucky_calendar_{target_year}_{target_month:02}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
