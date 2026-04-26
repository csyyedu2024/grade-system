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
# ⚠️ 【重要】請把下面這串中文字，替換成你剛剛複製的試算表網址！
# ----------------------------------------------------
SHEET_URL = "https://docs.google.com/spreadsheets/d/1vB-Vqk8t-6CMQGRCGS17JUY8PFNoyUpEcPkfPONO3qc/edit?gid=0#gid=0"

# 建立連線 (讀取保險箱裡的鑰匙)
try:
    creds_dict = json.loads(st.secrets["google_credentials"])
    gc = gspread.service_account_from_dict(creds_dict)
    sh = gc.open_by_url(SHEET_URL)
    worksheet = sh.sheet1
except Exception as e:
    st.error("⚠️ 系統連線設定中。請確認已於 Streamlit Secrets 設定金鑰，或檢查試算表網址是否正確。")
    st.stop()

# 建立輸入表單
with st.form("grade_registration_form", clear_on_submit=True):
    st.subheader("✏️ 新增學生紀錄")
    
    col1, col2 = st.columns(2)
    with col1:
        school = st.text_input("🏫 學校", placeholder="請輸入學校名稱")
        name = st.text_input("👤 學生姓名", placeholder="請輸入姓名")
        
    with col2:
        grade = st.selectbox(
            "🎓 年級", 
            ["小一", "小二", "小三", "小四", "小五", "小六", "國一", "國二", "國三"]
        )
        score = st.text_input("💯 成績 / 表現", placeholder="例如：95 或 表現優異")

    review_unit = st.text_input("📚 複習單元", placeholder="請輸入本次複習的單元名稱")
    
    # 送出按鈕
    submit_button = st.form_submit_button(label="✨ 送出登記")

# 處理表單送出後的邏輯
if submit_button:
    if school and name and review_unit:
        with st.spinner("資料同步中，請稍候..."):
            try:
                # 取得當前台灣時間 (UTC+8)
                current_time = (datetime.utcnow() + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
                
                # 準備要寫入的新資料列 (對應你的試算表欄位)
                new_row = [current_time, school, name, grade, score, review_unit]
                
                # 寫入 Google Sheets 的最下方
                worksheet.append_row(new_row)
                
                st.success(f"✅ 登記成功！已記錄 **{name}** ({school} {grade}) 於「{review_unit}」的表現。")
                st.balloons() # 加上可愛的慶祝氣球
            except Exception as e:
                st.error(f"⚠️ 發生錯誤：{e}")
    else:
        st.error("⚠️ 提醒：請確認「學校」、「姓名」與「複習單元」都已經填寫喔！")
