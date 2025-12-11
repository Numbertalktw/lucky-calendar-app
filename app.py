import streamlit as st
import pandas as pd
from datetime import date, datetime
import os
import time

# ==========================================
# 1. 核心設定與欄位定義 (完全對應 Excel)
# ==========================================

PAGE_TITLE = "商品庫存管理系統 (Excel 對應版)"
INVENTORY_FILE = 'inventory_data_v3.csv'
HISTORY_FILE = 'history_data_excel_v3.csv'

# --- 核心重點：依照您的 Excel 截圖定義 18 個欄位 ---
# 對應順序：
# A:單號, B:日期, C:系列, D:分類, E:品名, F:貨號, G:出庫單號(可複寫), H:出入庫
# I:數量, J:經手人, K:訂單單號, L:出貨日期, M:貨號備註, N:運費, O:款項結清
# P:工資, Q:發票, R:備註
HISTORY_COLUMNS = [
    '單號', 
    '日期', 
    '系列', 
    '分類', 
    '品名', 
    '貨號', 
    '出庫單號(可複寫)', 
    '出入庫', 
    '數量', 
    '經手人', 
    '訂單單號', 
    '出貨日期', 
    '貨號備註',   
    '運費',       
    '款項結清',   
    '工資', 
    '發票', 
    '備註'
]

# 庫存檔 (只記錄當前狀態)
INVENTORY_COLUMNS = [
    '貨號', '系列', '分類', '品名', 
    '庫存數量', '平均成本'
]

# 預設選單資料
DEFAULT_SERIES = ["生命數字能量項鍊", "一般款", "客製化", "福利品"]
DEFAULT_CATEGORIES = ["包裝材料", "天然石", "配件", "耗材", "成品"]
DEFAULT_HANDLERS = ["Wen", "店長", "小幫手"]

# ==========================================
# 2. 資料讀寫函式
# ==========================================

def load_data():
    # 讀取庫存
    if os.path.exists(INVENTORY_FILE):
        try:
            inv_df = pd.read_csv(INVENTORY_FILE)
            for col in INVENTORY_COLUMNS:
                if col not in inv_df.columns:
                    inv_df[col] = 0 if '數量' in col or '成本' in col else ""
            inv_df['貨號'] = inv_df['貨號'].astype(str)
        except:
            inv_df = pd.DataFrame(columns=INVENTORY_COLUMNS)
    else:
        inv_df = pd.DataFrame(columns=INVENTORY_COLUMNS)

    # 讀取紀錄
    if os.path.exists(HISTORY_FILE):
        try:
            hist_df = pd.read_csv(HISTORY_FILE)
            # 確保欄位齊全
            for col in HISTORY_COLUMNS:
                if col not in hist_df.columns:
                    hist_df[col] = ""
            hist_df = hist_df[HISTORY_COLUMNS]
        except:
            hist_df = pd.DataFrame(columns=HISTORY_COLUMNS)
    else:
        hist_df = pd.DataFrame(columns=HISTORY_COLUMNS)
        
    return inv_df, hist_df

def save_data():
    if 'inventory' in st.session_state:
        st.session_state['inventory'].to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
    if 'history' in st.session_state:
        st.session_state['history'].to_csv(HISTORY_FILE, index=False, encoding='utf-8-sig')

def generate_sku(category, df):
    prefix_map = {'天然石': 'ST', '配件': 'AC', '耗材': 'OT', '包裝材料': 'PK', '成品': 'PD'}
    prefix = prefix_map.get(category, "XX")
    if df.empty: return f"{prefix}0001"
    
    mask = df['貨號'].astype(str).str.startswith(prefix)
    existing = df.loc[mask, '貨號']
    if existing.empty: return f"{prefix}0001"
    
    try:
        max_num = existing.str.extract(r'(\d+)')[0].astype(float).max()
        return f"{prefix}{int(max_num)+1:04d}"
    except:
        return f"{prefix}{int(time.time())}"

def get_options(df, col, default):
    opts = set(default)
    if not df.empty and col in df.columns:
        exist = df[col].dropna().unique().tolist()
        opts.update([str(x) for x in exist if str(x).strip()])
    return ["➕ 手動輸入"] + sorted(list(opts))

# ==========================================
# 3. 初始化 Session State
# ==========================================

if 'inventory' not in st.session_state:
    inv_data, hist_data = load_data()
    st.session_state['inventory'] = inv_data
    st.session_state['history'] = hist_data

# ==========================================
# 4. Streamlit UI 介面
# ==========================================

st.set_page_config(page_title=PAGE_TITLE, layout="wide", page_icon="📋")
st.title(f"📋 {PAGE_TITLE}")

with st.sidebar:
    st.header("功能導航")
    page = st.radio("前往", ["📝 庫存異動 (輸入資料)", "📦 商品建檔與庫存表", "📜 歷史紀錄 (Excel總表)"])
    
    st.divider()
    st.markdown("### 下載備份")
    if not st.session_state['history'].empty:
        csv_h = st.session_state['history'].to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 下載 Excel 紀錄表", csv_h, f'History_{date.today()}.csv', "text/csv")

# ---------------------------------------------------------
# 頁面 1: 庫存異動 (所有欄位輸入區)
# ---------------------------------------------------------
if page == "📝 庫存異動 (輸入資料)":
    st.subheader("📝 新增異動紀錄")
    
    inv_df = st.session_state['inventory']
    
    # 檢查是否有商品
    if inv_df.empty:
        st.warning("⚠️ 目前還沒有商品資料！")
        st.info("請先點擊左側選單的 **「📦 商品建檔與庫存表」**，建立至少一個商品後，這裡就會出現輸入表格了。")
    else:
        # --- 選擇要操作的商品 ---
        inv_df['label'] = inv_df['貨號'] + " | " + inv_df['品名'] + " | 庫存:" + inv_df['庫存數量'].astype(str)
        
        c_sel, c_act = st.columns([2, 1])
        with c_sel:
            selected_label = st.selectbox("🔍 步驟 1：選擇商品", inv_df['label'].tolist())
            target_row = inv_df[inv_df['label'] == selected_label].iloc[0]
            target_idx = inv_df[inv_df['label'] == selected_label].index[0]
        with c_act:
            action_type = st.radio("步驟 2：動作", ["入庫", "出庫"], horizontal=True)

        st.divider()

        # --- 步驟 3：填寫欄位 (對應 Excel) ---
        st.markdown("#### 步驟 3：填寫詳細資料")
        with st.form("transaction_form"):
            
            # 第一排：基本異動資訊 (對應 A, B, I, J)
            st.markdown("**1. 基本資訊**")
            r1_1, r1_2, r1_3, r1_4 = st.columns(4)
            txn_date = r1_1.date_input("日期 (B)", value=date.today())
            qty = r1_2.number_input("數量 (I)", min_value=1, value=1)
            handler = r1_3.selectbox("經手人 (J)", DEFAULT_HANDLERS)
            # A 欄單號是自動產生的，這裡不顯示
            
            # 顯示目前選到的商品資訊 (對應 C, D, E, F)
            st.info(f"商品資訊：{target_row['系列']} / {target_row['分類']} / {target_row['品名']} ({target_row['貨號']})")

            # 第二排：單據資訊 (對應 G, K, L, M)
            st.markdown("**2. 單據資訊**")
            r2_1, r2_2, r2_3, r2_4 = st.columns(4)
            order_id = r2_1.text_input("訂單單號 (K)", placeholder="例如：蝦皮單號")
            ship_date_val = r2_2.date_input("出貨日期 (L)", value=date.today())
            sku_note = r2_3.text_input("貨號備註 (M)", placeholder="例如：NG品/白色")
            out_id_custom = r2_4.text_input("出庫單號(可複寫) (G)", placeholder="留空則自動產生")

            # 第三排：費用與結算 (對應 N, O, P, Q)
            st.markdown("**3. 費用與結算**")
            r3_1, r3_2, r3_3, r3_4 = st.columns(4)
            shipping_fee = r3_1.text_input("運費 (N)", placeholder="0")
            payment_status = r3_2.selectbox("款項結清 (O)", ["", "是", "否", "部分"], index=0)
            labor_cost = r3_3.text_input("工資 (P)", placeholder="0")
            invoice_no = r3_4.text_input("發票 (Q)", placeholder="發票號碼")

            # 第四排：備註 (R)
            note = st.text_area("備註 (R)", placeholder="其他說明...")

            # 額外：如果是入庫，可以輸入成本來計算平均成本
            cost_input = 0
            if action_type == "入庫":
                cost_input = st.number_input("本次進貨總成本 (系統計算用，不寫入表格)", min_value=0)

            # 送出按鈕
            if st.form_submit_button("✅ 確認送出並寫入紀錄", type="primary"):
                # 1. 產生單號 (A)
                now_str = datetime.now().strftime('%Y%m%d%H%M%S')
                record_id = f"{now_str}" 
                
                # 2. 處理出庫單號 (G)
                final_out_id = out_id_custom
                if action_type == "出庫" and not final_out_id:
                    final_out_id = f"OUT-{datetime.now().strftime('%Y%m%d')}"

                # 3. 處理出入庫欄位 (H) - 格式如圖: "入庫-Wen"
                io_status = f"{action_type}-{handler}"

                # 4. 更新庫存數量
                current_qty = float(target_row['庫存數量'])
                current_avg = float(target_row['平均成本'])
                
                if action_type == "入庫":
                    new_qty = current_qty + qty
                    # 平均成本計算
                    total_val = (current_qty * current_avg) + cost_input
                    new_avg = total_val / new_qty if new_qty > 0 else 0
                    st.session_state['inventory'].at[target_idx, '庫存數量'] = new_qty
                    st.session_state['inventory'].at[target_idx, '平均成本'] = new_avg
                    st.success(f"已入庫 {qty} 個，目前庫存 {new_qty}")
                else:
                    new_qty = current_qty - qty
                    st.session_state['inventory'].at[target_idx, '庫存數量'] = new_qty
                    st.success(f"已出庫 {qty} 個，剩餘庫存 {new_qty}")

                # 5. 寫入歷史紀錄 (18欄位完全對應)
                new_record = {
                    '單號': record_id,
                    '日期': txn_date,
                    '系列': target_row['系列'],
                    '分類': target_row['分類'],
                    '品名': target_row['品名'],
                    '貨號': target_row['貨號'],
                    '出庫單號(可複寫)': final_out_id,
                    '出入庫': io_status,
                    '數量': qty,
                    '經手人': handler,
                    '訂單單號': order_id,
                    '出貨日期': ship_date_val if action_type == '出庫' else None,
                    '貨號備註': sku_note,
                    '運費': shipping_fee,
                    '款項結清': payment_status,
                    '工資': labor_cost,
                    '發票': invoice_no,
                    '備註': note
                }
                
                st.session_state['history'] = pd.concat(
                    [st.session_state['history'], pd.DataFrame([new_record])], 
                    ignore_index=True
                )
                save_data()
                time.sleep(1)
                st.rerun()

# ---------------------------------------------------------
# 頁面 2: 商品建檔
# ---------------------------------------------------------
elif page == "📦 商品建檔與庫存表":
    st.subheader("📦 商品資料庫")
    
    tab_new, tab_list = st.tabs(["✨ 建立新商品", "📋 現有庫存清單"])
    
    with tab_new:
        st.write("第一次使用請先在此建立商品，建立後才能進行入庫/出庫。")
        with st.form("create_item"):
            c1, c2 = st.columns(2)
            cat_opts = get_options(st.session_state['inventory'], '分類', DEFAULT_CATEGORIES)
            cat_sel = c1.selectbox("分類 (D)", cat_opts)
            final_cat = c1.text_input("輸入新分類") if cat_sel == "➕ 手動輸入" else cat_sel
            
            ser_opts = get_options(st.session_state['inventory'], '系列', DEFAULT_SERIES)
            ser_sel = c2.selectbox("系列 (C)", ser_opts)
            final_ser = c2.text_input("輸入新系列") if ser_sel == "➕ 手動輸入" else ser_sel
            
            name = st.text_input("品名 (E)", placeholder="例如：項鍊紙盒/白色")
            auto_sku = generate_sku(final_cat, st.session_state['inventory'])
            sku = st.text_input("貨號 (F) - 預設自動產生", value=auto_sku)
            
            if st.form_submit_button("建立資料"):
                if not name:
                    st.error("品名為必填")
                else:
                    new_row = {
                        '貨號': sku, '系列': final_ser, '分類': final_cat, '品名': name,
                        '庫存數量': 0, '平均成本': 0
                    }
                    st.session_state['inventory'] = pd.concat(
                        [st.session_state['inventory'], pd.DataFrame([new_row])], 
                        ignore_index=True
                    )
                    save_data()
                    st.success(f"成功建立：{name}")
                    st.rerun()

    with tab_list:
        st.dataframe(
            st.session_state['inventory'], 
            use_container_width=True,
            column_config={
                "庫存數量": st.column_config.NumberColumn(help="當前總庫存量"),
                "平均成本": st.column_config.NumberColumn(format="$%.2f")
            }
        )

# ---------------------------------------------------------
# 頁面 3: 歷史紀錄 (Excel 總表)
# ---------------------------------------------------------
elif page == "📜 歷史紀錄 (Excel總表)":
    st.subheader("📜 歷史紀錄總表")
    st.caption("欄位順序已完全對應您的 Excel 截圖。")
    
    df_hist = st.session_state['history']
    
    # 搜尋
    search = st.text_input("🔍 搜尋 (單號/品名/訂單)", "")
    if search:
        mask = df_hist.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)
        df_hist = df_hist[mask]
    
    # 可編輯的表格
    edited_df = st.data_editor(
        df_hist,
        use_container_width=True,
        num_rows="dynamic",
        height=600,
        key="history_editor"
    )
    
    if st.button("💾 儲存修改"):
        st.session_state['history'] = edited_df
        save_data()
        st.success("已更新紀錄！")
