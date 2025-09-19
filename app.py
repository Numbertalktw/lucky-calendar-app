# -*- coding: utf-8 -*-
"""
LuckyCalendar Streamlit App — 整合『農曆＋流年/流月/流日』完整版
------------------------------------------------------------------
本版功能：
1) 正確依規則計算：
   - 流年：若查詢日期「未過當年生日」，以『前一年』作為基準年；顯示格式預設為：加總值/中和值（可切換為加總值/中和值/主數）。
   - 流月：依規則『保留出生年與日，僅更換查詢月』→ 以（出生年 + 查詢月 + 出生日）做三層加總，顯示為：總和/中和/主數。
   - 流日：以（出生年 + 出生月 + 查詢日）做三層加總。
   - 主日數：以『流日』的主數作為當天主日數；並映射主日名稱（1~9）。
2) 加入農曆欄位（以 `lunardate` 轉換）：
   - 農曆（數字）：YYYY-MM-DD（獨立顯示，閏月以布林欄位標示）
   - 農曆（漢字）：如「八月廿七」，閏月顯示為「閏八月廿七」
   - 是否閏月：True / False
3) 匯出 Excel：檔名 `LuckyCalendar_YYYY_MM.xlsx`（月份補0），會包含所有欄位。
4) 介面：品牌名稱與標語、當月表格預覽。

相依：
- streamlit
- pandas
- xlsxwriter
- lunardate==0.2.1

備註：
- 指引（1~59 組合）、幸運色/水晶/小物、運勢星等完整對應表可於後續以外部 CSV/Google Sheets 載入；此版先放少量示例映射與預設值，確保 App 可立即運行。
"""

import io
import calendar
import datetime as dt
from dataclasses import dataclass
from typing import Dict, Tuple

import pandas as pd
import streamlit as st

# ✅ 農曆：以 lunardate 為主；若沒安裝會顯示提示
try:
    from lunardate import LunarDate
except Exception:
    LunarDate = None

# -----------------------------
# 工具：整數 → 漢字（農曆月/日）
# -----------------------------
CN_MONTHS = [
    "正月", "二月", "三月", "四月", "五月", "六月",
    "七月", "八月", "九月", "十月", "冬月", "臘月"
]
CN_DAYS = [
    "初一", "初二", "初三", "初四", "初五", "初六", "初七", "初八", "初九", "初十",
    "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九", "二十",
    "廿一", "廿二", "廿三", "廿四", "廿五", "廿六", "廿七", "廿八", "廿九", "三十"
]

def lunar_zh(month: int, day: int, is_leap: bool) -> str:
    m_name = CN_MONTHS[(month - 1) % 12]
    d_name = CN_DAYS[(day - 1) % 30]
    prefix = "閏" if is_leap else ""
    return f"{prefix}{m_name}{d_name}"

@dataclass
class LunarInfo:
    y: int
    m: int
    d: int
    leap: bool

    @property
    def as_iso(self) -> str:
        return f"{self.y:04d}-{self.m:02d}-{self.d:02d}"

    @property
    def as_cn(self) -> str:
        return lunar_zh(self.m, self.d, self.leap)

def to_lunar(gdate: dt.date) -> LunarInfo:
    if LunarDate is None:
        st.error("找不到 lunardate 套件，請在 requirements.txt 加入：lunardate==0.2.1")
        return LunarInfo(gdate.year, 1, 1, False)
    try:
        ld: LunarDate = LunarDate.fromSolarDate(gdate.year, gdate.month, gdate.day)
        # 某些版本以屬性 isLeapMonth 標示閏月，若無則預設 False
        is_leap = getattr(ld, "isLeapMonth", False)
        return LunarInfo(ld.year, ld.month, ld.day, is_leap)
    except Exception:
        return LunarInfo(gdate.year, 1, 1, False)

# ------------------------------------------------------
# 生命靈數：常用工具
# ------------------------------------------------------

def digital_root(n: int) -> int:
    while n > 9:
        s = 0
        x = n
        while x:
            s += x % 10
            x //= 10
        n = s
    return n


def sum_mid_final(numbers) -> Tuple[int, int, int]:
    s = sum(numbers)
    mid = digital_root(s)
    final = digital_root(mid)
    return s, mid, final

# 主日名稱（可依你的命名偏好調整）
MAIN_DAY_NAME: Dict[int, str] = {
    1: "太陽 │ 創始領導",
    2: "月亮 │ 關係協調",
    3: "水星 │ 表達創意",
    4: "土星 │ 結構踏實",
    5: "赫耳墨斯 │ 自由變動",
    6: "金星 │ 關愛責任",
    7: "海王 │ 內省智慧",
    8: "火星 │ 權能行動",
    9: "木星 │ 完成博愛",
}

# 少量示例：『流日組合→指引/運勢/建議』映射（完整 1~59 可外部載入）
GUIDE_MAP: Dict[str, Dict[str, str]] = {
    "11/2": {"guide": "放慢判斷，讓直覺先說話。", "stars": "⭐⭐⭐⭐", "tips": "白色/藍色；白水晶"},
    "14/5": {"guide": "嘗試新路徑，但保留復原時間。", "stars": "⭐⭐⭐", "tips": "橙色；太陽石"},
    "19/10/1": {"guide": "收回分散能量，聚焦一件大事。", "stars": "⭐⭐⭐⭐", "tips": "紅色；紅瑪瑙"},
    "27/9": {"guide": "成全與放下，讓善意完成循環。", "stars": "⭐⭐⭐⭐", "tips": "紫色；紫水晶"},
    "36/9": {"guide": "整理故事，轉成對外分享的力量。", "stars": "⭐⭐⭐", "tips": "藍紫；海藍寶/紫水晶"},
}

# ------------------------------------------------------
# 依先前約定規則計算：流年/流月/流日（西曆）
# ------------------------------------------------------

def calc_liunian(query_date: dt.date, birth: dt.date) -> Tuple[int, int, int]:
    """流年（西曆）：未過生日→用前一年。"""
    baseline_year = query_date.year if (query_date.month, query_date.day) >= (birth.month, birth.day) else query_date.year - 1
    s, mid, final = sum_mid_final([baseline_year, birth.month, birth.day])
    return s, mid, final


def calc_liuyue(query_date: dt.date, birth: dt.date) -> Tuple[int, int, int]:
    """流月（西曆）：出生『年+日』＋查詢『月』 → 三層。"""
    return sum_mid_final([birth.year, query_date.month, birth.day])


def calc_liuri(query_date: dt.date, birth: dt.date) -> Tuple[int, int, int]:
    """流日（西曆）：出生『年+月』＋查詢『日』 → 三層。"""
    return sum_mid_final([birth.year, birth.month, query_date.day])

# ------------------------------------------------------
# 與西曆規則一致的『農曆版』流年/流月/流日
# （不對閏月做加權；閏月=其月數字）
# ------------------------------------------------------

def calc_liunian_lunar(lunar_query: LunarInfo, lunar_birth: LunarInfo) -> Tuple[int, int, int]:
    """流年（農曆）：若查詢農曆日期未過『農曆生日』，以前一個農曆年作基準。
    組合：基準農曆年 + 農曆出生月 + 農曆出生日。
    """
    # 判斷是否已過農曆生日（僅以月/日判斷，不對閏月加權）
    passed = (lunar_query.m, lunar_query.d) >= (lunar_birth.m, lunar_birth.d)
    baseline_lyear = lunar_query.y if passed else lunar_query.y - 1
    return sum_mid_final([baseline_lyear, lunar_birth.m, lunar_birth.d])


def calc_liuyue_lunar(lunar_query: LunarInfo, lunar_birth: LunarInfo) -> Tuple[int, int, int]:
    """流月（農曆）：農曆出生『年+日』＋查詢『農曆月』 → 三層。"""
    return sum_mid_final([lunar_birth.y, lunar_query.m, lunar_birth.d])


def calc_liuri_lunar(lunar_query: LunarInfo, lunar_birth: LunarInfo) -> Tuple[int, int, int]:
    """流日（農曆）：農曆出生『年+月』＋查詢『農曆日』 → 三層。"""
    return sum_mid_final([lunar_birth.y, lunar_birth.m, lunar_query.d])

# ------------------------------------------------------
# Streamlit UI
# ------------------------------------------------------

st.set_page_config(page_title="樂覺製所生命靈數 · LuckyCalendar", page_icon="✨", layout="wide")

st.markdown(
    """
# 樂覺製所生命靈數 · LuckyCalendar
在數字之中，遇見每日的自己。**Be true, be you — 讓靈魂自在呼吸。**

> 本版整合 **農曆欄位** 與 **流年/流月/流日** 全邏輯；支援 Excel 下載。
"""
)

with st.sidebar:
    st.subheader("設定")
    y = st.number_input("年份 (西曆)", min_value=1900, max_value=2100, value=2025, step=1)
    m = st.number_input("月份", min_value=1, max_value=12, value=9, step=1)
    b = st.date_input("生日 (西曆)", value=dt.date(1989, 7, 5), format="YYYY-MM-DD")

    show_ly_final = st.toggle("流年顯示三段（總和/中和/主數）", value=False)

first_day = dt.date(int(y), int(m), 1)
last_day = dt.date(int(y), int(m), calendar.monthrange(int(y), int(m))[1])
all_days = [first_day + dt.timedelta(days=i) for i in range((last_day - first_day).days + 1)]

rows = []
for d in all_days:
    # 西曆版本
    ln_s, ln_mid, ln_final = calc_liunian(d, b)
    lm_s, lm_mid, lm_final = calc_liuyue(d, b)
    ld_s, ld_mid, ld_final = calc_liuri(d, b)

    # 主日（取西曆流日主數）
    main_num = ld_final
    main_name = MAIN_DAY_NAME.get(main_num, "—")

    # 農曆資訊（查詢日 & 出生日）
    lunar_q = to_lunar(d)
    lunar_b = to_lunar(b)

    # 農曆版組合（規則與西曆一致）
    l_ln_s, l_ln_mid, l_ln_final = calc_liunian_lunar(lunar_q, lunar_b)
    l_lm_s, l_lm_mid, l_lm_final = calc_liuyue_lunar(lunar_q, lunar_b)
    l_ld_s, l_ld_mid, l_ld_final = calc_liuri_lunar(lunar_q, lunar_b)

    # 指引/運勢（仍以西曆流日鍵為主；需要時可改成農曆鍵或雙鍵混合）
    key_candidates = [f"{ld_s}/{ld_mid}/{ld_final}", f"{ld_mid}/{ld_final}"]
    guide_pack = None
    for k in key_candidates:
        if k in GUIDE_MAP:
            guide_pack = GUIDE_MAP[k]
            break
    if guide_pack is None:
        guide_pack = {"guide": "今日以穩定節奏完成重點任務。", "stars": "⭐⭐⭐", "tips": "—"}

    rows.append({
        "日期": d.strftime("%Y-%m-%d"),
        # 農曆基本資訊
        "農曆（數字）": f"{lunar_q.y:04d}-{lunar_q.m:02d}-{lunar_q.d:02d}",
        "農曆（漢字）": lunar_q.as_cn,
        "是否閏月": lunar_q.leap,
        # 西曆組合
        "流年": f"{ln_s}/{ln_mid}/{ln_final}" if show_ly_final else f"{ln_s}/{ln_mid}",
        "流月": f"{lm_s}/{lm_mid}/{lm_final}",
        "流日": f"{ld_s}/{ld_mid}/{ld_final}",
        # 農曆組合（與西曆規則一致）
        "農曆流年": f"{l_ln_s}/{l_ln_mid}/{l_ln_final}",
        "農曆流月": f"{l_lm_s}/{l_lm_mid}/{l_lm_final}",
        "農曆流日": f"{l_ld_s}/{l_ld_mid}/{l_ld_final}",
        # 其他欄位
        "主日數": main_num,
        "主日名稱": main_name,
        "指引": guide_pack["guide"],
        "幸運色": guide_pack.get("tips", "—"),
        "水晶": "—",
        "幸運小物": "—",
        "運勢": guide_pack["stars"],
    })


df = pd.DataFrame(rows)

st.dataframe(df, use_container_width=True, hide_index=True)

# 下載 Excel（含所有欄位）
@st.cache_data(show_spinner=False)
def to_excel_bytes(_df: pd.DataFrame) -> bytes:
    if _df.empty:
        return b""
    out = io.BytesIO()
    with pd.ExcelWriter(out, engine="xlsxwriter") as writer:
        _df.to_excel(writer, index=False, sheet_name="LuckyCalendar")
    return out.getvalue()

fn = f"LuckyCalendar_{int(y):04d}_{int(m):02d}.xlsx"
st.download_button(
    label=f"📥 點此下載 {int(y)} 年 {int(m)} 月靈數流日建議表（三層加總斜線版）",
    data=to_excel_bytes(df),
    file_name=fn,
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    disabled=df.empty,
)

# 小提醒：缺套件時的提示
if LunarDate is None:
    with st.expander("安裝 lunardate 套件說明"):
        st.markdown(
            """
            本機或雲端部署請在 requirements.txt 加入：

            ```
            lunardate==0.2.1
            ```

            Streamlit Cloud：專案頁 → **⚙️ Settings** → **Dependencies**（或 repo 的 requirements.txt）。
            """
        )
