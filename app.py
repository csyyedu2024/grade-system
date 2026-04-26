import streamlit as st
import pandas as pd
import json
import gspread
from datetime import datetime, timedelta

# 設定網頁標題與視覺風格
st.set_page_config(page_title="創思優語 - 登記系統", page_icon="🌱")
st.title("🌱 創思優語學習紀錄")
st.markdown("##### 簡約、高效的成績與複習進度管理")
st.divider()

# ----------------------------------------------------
# ⚠️ 【重要】請確保這裡維持你原本的試算表網址
# ----------------------------------------------------
SHEET_URL = "https://docs.google.com/spreadsheets/d/1vB-Vqk8t-6CMQGRCGS17JUY8PFNoyUpEcPkfPONO3qc/edit?gid=0#gid=0"

# 建立連線 (讀取保險箱裡的鑰匙)
try:
    creds_dict = json.loads(st.secrets["google_credentials"])
    gc = gspread.service_account_from_dict(creds_dict)
    sh = gc.open_by_url(SHEET_URL)
    worksheet = sh.sheet1
except Exception as e:
    st.error("⚠️ 系統連線錯誤詳細說明：" + str(e))
    st.stop()

# ==========================================
# 🧠 V2.0 雙向記憶魔法：讀取試算表中的舊生名單
# ==========================================
try:
    # 抓取第 3 欄 (C欄) 的所有資料
    all_names = worksheet.col_values(3)
    # 過濾掉空白、排除標題，並自動移除重複的名字
    unique_names = sorted(list(set([n for n in all_names if n.strip() != "" and n != "學生姓名"])))
except Exception as e:
    unique_names = [] # 如果剛好抓不到，就先給空名單

# 建立輸入表單
with st.form("grade_registration_form", clear_on_submit=True):
    st.subheader("✏️ 新增學生紀錄")
    
    col1, col2 = st.columns(2)
    with col1:
        school = st.selectbox(
            "🏫 學校", 
            options=["土城國中", "海山國中", "江翠國中", "重慶國中", "新莊國中"],
            index=None,
            placeholder="請選擇學校"
        )
        
        # --- 雙軌制姓名輸入設計 ---
        known_name = st.selectbox("👤 選擇已建檔學生", options=["➕ 建立新學生"] + unique_names)
        new_name = st.text_input("👉 或手動輸入新學生", placeholder="若為新生請填此欄，例如：彧安")
        
    with col2:
        grade = st.selectbox(
            "🎓 年級", 
            ["小一", "小二", "小三", "小四", "小五", "小六", "七年級（國一）", "八年級（國二）", "九年級（國三）"]
        )
        score = st.text_input("💯 成績 / 表現", placeholder="例如：95 或 表現優異")

    review_unit = st.text_input("📚 複習單元", placeholder="請輸入本次複習的單元名稱")
    
    # 送出按鈕
    submit_button = st.form_submit_button(label="✨ 送出登記")

# 處理表單送出後的邏輯
if submit_button:
    # 邏輯判斷：如果手打欄位有字，優先用手打的；沒字的話才用選單裡的
    actual_name = new_name.strip() if new_name.strip() else known_name

    # 確保名字不是空值，且不是那個「➕ 建立新學生」的選項
    if actual_name and actual_name != "➕ 建立新學生" and review_unit: 
        with st.spinner("資料同步中，請稍候..."):
            try:
                # 取得當前台灣時間 (UTC+8)
                current_time = (datetime.utcnow() + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
                
                # 準備要寫入的新資料列
                new_row = [current_time, school, actual_name, grade, score, review_unit]
                
                # 寫入 Google Sheets
                worksheet.append_row(new_row)
                
                st.success(f"✅ 登記成功！已記錄 **{actual_name}** ({school} {grade}) 於「{review_unit}」的表現。")
                st.balloons()
            except Exception as e:
                st.error(f"⚠️ 發生錯誤：{e}")
    else:
        st.error("⚠️ 提醒：請確認「姓名」與「複習單元」都已經正確填寫喔！")
