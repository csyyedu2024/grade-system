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
# 🧠 V3.0 全自動記憶魔法：建立「姓名-密碼」對照表
# ==========================================
try:
    all_records = worksheet.get_all_records()
    df = pd.DataFrame(all_records)
    
    df['學生姓名'] = df['學生姓名'].astype(str).str.strip()
    df['專屬密碼'] = df['專屬密碼'].astype(str).str.strip()
    
    has_pwd_df = df[df['專屬密碼'] != '']
    pwd_dict = dict(zip(has_pwd_df['學生姓名'], has_pwd_df['專屬密碼']))
    
    unique_names = sorted(list(set([n for n in df['學生姓名'] if n != "" and n != "學生姓名"])))
except Exception as e:
    pwd_dict = {}
    unique_names = [] 

# 建立輸入表單
with st.form("grade_registration_form", clear_on_submit=True):
    st.subheader("✏️ 新增學生紀錄")
    
    # 🌟 修改點：改用「橫向區塊」分層設計，完美解決手機版堆疊順序！
    
    # --- 區塊一：基本資料 ---
    col1, col2 = st.columns(2)
    with col1:
        school = st.selectbox("🏫 學校", options=["土城國中", "海山國中", "江翠國中", "重慶國中", "新莊國中", "板橋國小", "廣福國小", "後埔國小"], index=None, placeholder="請選擇學校")
    with col2:
        grade = st.selectbox("🎓 年級", ["小一", "小二", "小三", "小四", "小五", "小六", "七年級（國一）", "八年級（國二）", "九年級（國三）"])

    # --- 區塊二：學生身分與密碼 ---
    col3, col4 = st.columns(2)
    with col3:
        known_name = st.selectbox("👤 選擇已建檔學生", options=["➕ 建立新學生"] + unique_names)
    with col4:
        new_name = st.text_input("👉 或手動輸入新學生", placeholder="若為新生請填此欄，例如：小創")
        
    # 將密碼獨立橫跨一整行，視覺更舒爽，也不會被擠到下面
    parent_password = st.text_input("🔑 專屬密碼 (家長登入用)", placeholder="新生必填，舊生系統將自動帶入")

    # --- 區塊三：學習表現 ---
    col5, col6 = st.columns(2)
    with col5:
        review_unit = st.text_input("📚 複習單元", placeholder="請輸入本次複習的單元名稱")
    with col6:
        score = st.text_input("💯 成績 / 表現", placeholder="例如：95 或 表現優異")

    # 送出按鈕
    submit_button = st.form_submit_button(label="✨ 送出登記")

# 處理表單送出後的邏輯
if submit_button:
    actual_name = new_name.strip() if new_name.strip() else known_name

    if actual_name and actual_name != "➕ 建立新學生" and review_unit: 
        with st.spinner("資料同步中，請稍候..."):
            try:
                final_password = parent_password.strip()
                
                if not final_password and actual_name in pwd_dict:
                    final_password = pwd_dict[actual_name]

                current_time = (datetime.utcnow() + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
                new_row = [current_time, school, grade, actual_name, review_unit, score, final_password]
                worksheet.append_row(new_row)
                
                st.success(f"✅ 登記成功！已記錄 **{actual_name}** ({school} {grade}) 於「{review_unit}」的表現。")
                if final_password:
                    st.info(f"🔑 系統已綁定密碼：{final_password}")
                else:
                    st.warning(f"⚠️ 提醒：{actual_name} 目前尚未設定專屬密碼喔！")
                    
                st.balloons()
            except Exception as e:
                st.error(f"⚠️ 發生錯誤：{e}")
    else:
        st.error("⚠️ 提醒：請確認「姓名」與「複習單元」都已經正確填寫喔！")
