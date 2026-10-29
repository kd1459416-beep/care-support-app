import streamlit as st
import pandas as pd
import re
from datetime import datetime, date

st.title("介護支援記録＆申し送り・スケジュール管理システム")

# 簡易データベース代わりのセッション状態の初期化
if "records" not in st.session_state:
    st.session_state["records"] = []
if "schedules" not in st.session_state:
    st.session_state["schedules"] = []

# --- タブによる画面切り替え ---
tab1, tab2, tab3 = st.tabs(["支援記録入力", "申し送り作成", "スケジュール確認"])

# ==========================================
# 1. 支援記録入力
# ==========================================
with tab1:
    st.header("支援記録の入力")
    
    col1, col2 = st.columns(2)
    with col1:
        record_date = st.date_input("記録日", date.today())
        user_name = st.text_input("利用者名", placeholder="例: 山田 太郎様")
    
    note = st.text_area(
        "記録本文（特記事項は●を付けてください）",
        placeholder="朝食完食。●14時に37.5℃の発熱あり。水分補給実施。\n【次回予定】2026/11/05 10:00 通院（〇〇病院）",
        height=150
    )
    
    if st.button("記録を保存"):
        if user_name and note:
            # 支援記録の保存
            st.session_state["records"].append({
                "date": record_date.strftime("%Y-%m-%d"),
                "user_name": user_name,
                "note": note
            })
            
            # 本文から【次回予定】を抽出してスケジュールに自動登録
            schedule_pattern = r"【次回予定】\s*(\d{4}/\d{2}/\d{2})\s*(\d{2}:\d{2})\s*(.+)"
            matches = re.findall(schedule_pattern, note)
            for s_date, s_time, s_subject in matches:
                st.session_state["schedules"].append({
                    "date": s_date,
                    "time": s_time,
                    "user_name": user_name,
                    "subject": s_subject.strip()
                })
            
            st.success("支援記録を保存しました！")
        else:
            st.warning("利用者名と記録本文を入力してください。")

# ==========================================
# 2. 申し送り自動作成
# ==========================================
with tab2:
    st.header("申し送り事項の自動作成")
    
    target_date = st.date_input("申し送りを抽出する日付", date.today())
    target_date_str = target_date.strftime("%Y-%m-%d")
    
    if st.button("申し送りを生成"):
        handover_text = f"=== 申し送り事項一覧 ({target_date_str}) ===\n\n"
        found = False
        
        # 特記事項（●）を抽出するパターン
        pattern = r"●(.*?)(?=(?:●|【次回予定】|$))"
        
        for r in st.session_state["records"]:
            if r["date"] == target_date_str:
                # 改行をスペースに置換
                cleaned_note = r["note"].replace("\n", " ")
                matches = re.findall(pattern, cleaned_note)
                
                if matches:
                    found = True
                    handover_text += f"【{r['user_name']}】\n"
                    for m in matches:
                        handover_text += f"  ・{m.strip()}\n"
                    handover_text += "\n"
        
        if found:
            st.text_area("生成された申し送り（コピーしてご利用ください）", handover_text, height=250)
        else:
            st.info("該当日に●付きの特記事項はありませんでした。")

# ==========================================
# 3. スケジュール確認（面会・通院などの漏れ防止）
# ==========================================
with tab3:
    st.header("予定一覧（通院・面会など）")
    
    if st.session_state["schedules"]:
        df_sch = pd.DataFrame(st.session_state["schedules"])
        df_sch = df_sch.sort_values(by=["date", "time"])
        st.dataframe(df_sch, use_container_width=True)
    else:
        st.info("登録されている予定はありません。")