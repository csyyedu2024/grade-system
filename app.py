import streamlit as st

# 設定網頁標題與視覺風格
st.set_page_config(page_title="創思優語 - 登記系統", page_icon="🌱")

# 主標題與簡介
st.title("🌱 創思優語學習紀錄")
st.markdown("##### 簡約、高效的成績與複習進度管理")
st.divider()

# 建立輸入表單
with st.form("grade_registration_form", clear_on_submit=True):
    st.subheader("✏️ 新增學生紀錄")
    
    # 橫向排列輸入欄位，讓版面更緊湊好看
    col1, col2 = st.columns(2)
    
    with col1:
        school = st.text_input("🏫 學校", placeholder="請輸入學校名稱")
        name = st.text_input("👤 學生姓名", placeholder="請輸入姓名")
        
    with col2:
        # 針對主要授課對象設定下拉式選單
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
        # 這裡未來可以串接 Google Sheets 或資料庫儲存資料
        st.success(f"✅ 登記成功！已記錄 **{name}** ({school} {grade}) 於「{review_unit}」的表現。")
    else:
        st.error("⚠️ 提醒：請確認「學校」、「姓名」與「複習單元」都已經填寫喔！")
