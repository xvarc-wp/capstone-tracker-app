import streamlit as st
import pandas as pd
from datetime import datetime
import os
import csv
import io
import gspread
import gspread_dataframe as gd

# --- Translation Dictionaries (V9 - User Revised Questions for Day 1, 2, 3) ---
TRANSLATIONS = {
    "en": {
        "app_title": "Capstone Meeting Tracker",
        "language_select": "Select Language / 言語",
        "sidebar_title": "Meeting Information",
        "group_number": "Group Number", "group_number_help": "Which group is presenting?",
        "time_slot": "Time Slot (e.g., 10:30)", "time_slot_help": "Enter the scheduled meeting time manually (e.g., 10:30, 14:00).",
        "date": "Date", "date_help": "Date of the meeting.",
        "project_title": "Project Title", "project_title_help": "Official name of your Automotive Data Pipeline project.",
        "current_research_question": "Current Research Question(s)", "current_research_question_help": "What specific questions are you trying to answer? This might evolve each day!",
        "note_taker": "Note Taker", "note_taker_help": "Who is responsible for documenting this meeting?",
        "download_student_copy": "Click Here to Download Your Copy",
        "submit_and_download": "Submit to Instructor & Download",
        "submission_success": "Data submitted to Instructor (Google Sheets) successfully!",
        "submission_gsheets_error": "Failed to submit to Google Sheets. Please contact instructor. Your data was NOT saved.",
        "submission_error": "Error in form data. Please ensure required fields are filled.",
        "file_will_be_named": "File will be named:",
        "hint_visibility": "ℹ️ Need guidance? Hover over '❓' next to each field for stakeholder prompts!",
        "important_label": "Important",
        "footer_submission_reminder": "Please ensure your meeting notes are submitted by 5:30 PM today. Timely submissions are crucial for accurate feedback and effective project tracking.",

        # Day 1
        "day_1_tab": "🗓️ Day 1 – Kickoff & First Pitch",
        "day_1_value_prop": "Value Proposition", "day_1_value_prop_help": "What insight will this bring? What success will it enable for me (the stakeholder)?", "day_1_value_prop_placeholder": "E.g., 'This project will show us which car features most impact EV range, helping us target our marketing...'",
        "day_1_proposed_features_investigation": "Proposed Features/Investigation", "day_1_proposed_features_investigation_help": "What are the core features you plan to build or areas you will investigate initially?", "day_1_proposed_features_investigation_placeholder": "E.g., 'Investigate impact of X on Y, Develop data import for Z dataset, Core user authentication...'",
        "day_1_team_roles": "Team Roles & Responsibilities", "day_1_team_roles_help": "Who is Product Owner? Scrum Master? Who does what?", "day_1_team_roles_placeholder": "E.g., 'A: PO, B: Scrum Master, C: Lead Dev (Python), D: DB & SQL Lead...'",
        "day_1_action_items_day2": "Action Items for Day 2", "day_1_action_items_day2_help": "What must be achieved by tomorrow?", "day_1_action_items_day2_placeholder": "E.g., '1. Finalize DB Schema. 2. Implement Python import for 2 datasets. 3. Start cleaning functions.'",
        "day_1_meeting_feedback": "Meeting Notes/Feedback", "day_1_meeting_feedback_help": "Key discussion points, decisions, stakeholder input, or instructor feedback from today's meeting.", "day_1_meeting_feedback_placeholder": "E.g., 'Stakeholder emphasized need for clear 'range' definition. Decided to use 'EPA Est. Range'. Instructor suggested focusing on research question X.'",

        # Day 2
        "day_2_tab": "🗓️ Day 2 – MVP Build Day",
        "day_2_datasets_imported": "Datasets Imported (>=2)", "day_2_datasets_imported_help": "Which 2+ datasets are imported? Show proof if possible!", "day_2_datasets_imported_placeholder": "E.g., 'EV_Specs.csv and US_Population_2022.csv are now loading via Python scripts.'",
        "day_2_data_transformations": "Data Transformations", "day_2_data_transformations_help": "Describe the data cleaning, preprocessing, or transformation steps applied. What challenges?", "day_2_data_transformations_placeholder": "E.g., 'Cleaned 'range' (handling 'N/A') and 'price' (removing '$'). Stuck on date formats. Transformed feature X using Y.'",
        "day_2_sqlite_tables_queries": "SQLite Tables and Queries", "day_2_sqlite_tables_queries_help": "Describe the database tables created and any key SQL queries planned or executed. Any issues?", "day_2_sqlite_tables_queries_placeholder": "E.g., ''vehicles' & 'locations' tables created. Planning to JOIN them. Query for AVG range by state drafted.'",
        "day_2_blockers_idle": "Blockers / Issues", "day_2_blockers_idle_help": "What's stopping progress?", "day_2_blockers_idle_placeholder": "E.g., 'Member D is blocked waiting for cleaned data. Need to prioritize cleaning script.'",
        "day_2_backlog": "Backlog", "day_2_backlog_help": "What was planned for this iteration and what was achieved? Update on backlog items.", "day_2_backlog_placeholder": "E.g., 'Planned: DB Schema & Import. Achieved: Both. Cleaning is 50% done. Backlog updated.'",
        "day_2_action_items_day3": "Action Items for Day 3", "day_2_action_items_day3_help": "Goals for tomorrow.", "day_2_action_items_day3_placeholder": "E.g., '1. Complete cleaning. 2. Populate DB. 3. Write first SQL query.'",
        "day_2_meeting_feedback": "Meeting Notes/Feedback", "day_2_meeting_feedback_help": "Key discussion points, decisions, stakeholder input, or instructor feedback from today's meeting.", "day_2_meeting_feedback_placeholder": "E.g., 'Discussed data cleaning strategy. Stakeholder asked about logging. Instructor: ensure E2E pipeline runs soon.'",

        # Day 3
        "day_3_tab": "🗓️ Day 3 – Soft Feature Freeze",
        "day_3_research_question_status": "Research Question Status", "day_3_research_question_status_help": "Update on your progress towards answering the main research question(s). Are your findings aligning?", "day_3_research_question_status_placeholder": "E.g., 'Initial analysis of dataset X suggests Y. This aligns with RQ1. Need further query Z for RQ2.'",
        "day_3_features_reports": "Features and Reports", "day_3_features_reports_help": "Status of key features developed and reports generated. Is the pipeline fully operational (Import -> Clean -> DB -> SQL -> Report)?", "day_3_features_reports_placeholder": "E.g., 'Pipeline is operational! Report script generates findings for Q1. Feature X is complete.'",
        "day_3_readme_documentation": "README and Documentations", "day_3_readme_documentation_help": "Is the README updated with necessary information (setup, schema, findings, query explanations)? Other documentation status. Can someone *not* on your team follow it?", "day_3_readme_documentation_placeholder": "E.g., 'README updated with schema and first query. Setup instructions are clear. Another group confirmed understanding.'",
        "day_3_action_items_day4": "Action Items for Day 4", "day_3_action_items_day4_help": "Goals for tomorrow.", "day_3_action_items_day4_placeholder": "E.g., '1. Finalize report script. 2. Add 2nd SQL query. 3. Update README completely. 4. Code cleanup & comments.'",
        "day_3_meeting_feedback": "Meeting Notes/Feedback", "day_3_meeting_feedback_help": "Key discussion points, decisions, stakeholder input, or instructor feedback from today's meeting.", "day_3_meeting_feedback_placeholder": "E.g., 'Reviewed Q1 results. Discussed report format. Stakeholder pushed for query complexity. Instructor: Impressive pipeline! Make insights clearer.'",

        # Day 4 (Unchanged as per request to modify Day 1-3)
        "day_4_tab": "🗓️ Day 4 – Final Prep & Feature Freeze",
        "day_4_feature_status": "Feature Freeze Confirmed", "day_4_feature_status_help": "Confirm: Only bug fixes and polish now.", "day_4_feature_status_placeholder": "",
        "day_4_sql_queries_report": "SQL Queries in Report", "day_4_sql_queries_report_help": "List the >=2 key queries and their purpose.", "day_4_sql_queries_report_placeholder": "E.g., '1. AVG_Range_by_State (JOIN, GROUP BY). 2. Top_5_EVs_by_Count (COUNT, ORDER BY, LIMIT).'",
        "day_4_report_readability": "Report Readability/Relevance", "day_4_report_readability_help": "Is the report clear? Can I understand it?", "day_4_report_readability_placeholder": "E.g., 'Report includes intro, query explanations, results, and summary. Formatted with markdown.'",
        "day_4_readme_checklist_title": "README Final Checklist", "day_4_readme_checklist_title_help": "Is the final documentation 100% complete?", "day_4_readme_checklist_title_placeholder": "",
        "day_4_readme_theme_summary": "Theme Summary Included", "day_4_readme_theme_summary_help": "", "day_4_readme_theme_summary_placeholder": "",
        "day_4_readme_setup_instructions": "Setup & Run Instructions Included", "day_4_readme_setup_instructions_help": "", "day_4_readme_setup_instructions_placeholder": "",
        "day_4_readme_final_schema": "Final Schema Design Included", "day_4_readme_final_schema_help": "", "day_4_readme_final_schema_placeholder": "",
        "day_4_readme_sql_queries_explanation": "SQL Queries & Output Explanation Included", "day_4_readme_sql_queries_explanation_help": "", "day_4_readme_sql_queries_explanation_placeholder": "",
        "day_4_readme_summary_findings": "Summary of Findings Included", "day_4_readme_summary_findings_help": "", "day_4_readme_summary_findings_placeholder": "",
        "day_4_code_quality": "Code Quality Check", "day_4_code_quality_help": "Is it modular, commented, readable?", "day_4_code_quality_placeholder": "E.g., 'Refactored into functions. Added docstrings. Ran linter. Followed PEP8.'",
        "day_4_sprint_records": "Sprint Records Link/Location", "day_4_sprint_records_help": "Where can I see the journey?", "day_4_sprint_records_placeholder": "E.g., 'Jira board link / Confluence page with sprint summaries.'",
        "day_4_output_insightfulness": "Output Insightfulness", "day_4_output_insightfulness_help": "Is this genuinely useful? What's the 'so what'?", "day_4_output_insightfulness_placeholder": "E.g., 'Our key finding is X, which suggests the business should focus on Y...'",
        "day_4_presentation_confidence": "Non-Technical Presentation Readiness", "day_4_presentation_confidence_help": "Are you ready to present clearly to non-tech people?", "day_4_presentation_confidence_placeholder": "E.g., 'We have practiced the flow, focusing on the 'why' and the results, not just the code.'",
        "day_4_final_questions_issues": "Final Questions / Issues", "day_4_final_questions_issues_help": "Any last-minute concerns?", "day_4_final_questions_issues_placeholder": "E.g., 'Concerned about running live - will use pre-generated report as backup.'",
        "day_4_instructor_feedback": "Stakeholder Feedback", "day_4_instructor_feedback_help": "Final notes from the 'stakeholder'.", "day_4_instructor_feedback_placeholder": "E.g., 'Looks great! Ready for the presentation. Focus on clarity.'",
    },
    "ja": {
        "app_title": "キャップストーン会議トラッカー",
        "language_select": "言語を選択 / Select Language",
        "sidebar_title": "会議情報",
        "group_number": "グループ番号", "group_number_help": "どのグループが発表していますか？",
        "time_slot": "時間枠 (例: 10:30)", "time_slot_help": "予定されている会議の時間を手動で入力してください (例: 10:30, 14:00)。",
        "date": "日付", "date_help": "会議の日付です。",
        "project_title": "プロジェクトタイトル", "project_title_help": "あなたの自動車データパイプラインプロジェクトの正式名称です。",
        "current_research_question": "現在の研究課題", "current_research_question_help": "どのような具体的な質問に答えようとしていますか？ これは日々変化する可能性があります！",
        "note_taker": "ノートテイカー", "note_taker_help": "この会議の記録担当者は誰ですか？",
        "download_student_copy": "ここをクリックしてコピーをダウンロード",
        "submit_and_download": "教員に提出＆ダウンロード",
        "submission_success": "データが教員(Google Sheets)に正常に送信されました！",
        "submission_gsheets_error": "Google Sheetsへの送信に失敗しました。教員に連絡してください。データは保存されていません。",
        "submission_error": "フォームデータのエラー。必須項目がすべて入力されていることを確認してください。",
        "file_will_be_named": "ファイル名:",
        "hint_visibility": "ℹ️ ガイダンスが必要ですか？各項目隣の '❓' にカーソルを合わせると、ステークホルダーからのプロンプトが表示されます！",
        "important_label": "重要",
        "footer_submission_reminder": "本日の午後5時30分までに、必ず会議の記録を提出してください。正確なフィードバックと効果的なプロジェクト進捗管理のため、期限内の提出が不可欠です。",

        # Day 1 (Japanese)
        "day_1_tab": "🗓️ 1日目 – キックオフ＆最初のピッチ",
        "day_1_value_prop": "価値提案", "day_1_value_prop_help": "これはどのような洞察をもたらしますか？私（ステークホルダー）にどのような成功をもたらしますか？", "day_1_value_prop_placeholder": "例: 「このプロジェクトは、どの車の機能がEV航続距離に最も影響するかを示し、マーケティングのターゲット設定に役立ちます...」",
        "day_1_proposed_features_investigation": "提案機能/調査内容", "day_1_proposed_features_investigation_help": "初期に構築予定のコア機能や調査する分野は何ですか？", "day_1_proposed_features_investigation_placeholder": "例: 「XのYへの影響調査、Zデータセットのデータインポート開発、コアユーザー認証...」",
        "day_1_team_roles": "チームの役割と責任", "day_1_team_roles_help": "POは誰ですか？SMは？誰が何をしますか？", "day_1_team_roles_placeholder": "例: 「A: PO, B: SM, C: リード開発(Python), D: DB & SQL担当...」",
        "day_1_action_items_day2": "2日目のアクションアイテム", "day_1_action_items_day2_help": "明日までに何を達成する必要がありますか？", "day_1_action_items_day2_placeholder": "例: 「1. DBスキーマを最終化。2. 2つのデータセットのPythonインポートを実装。3. クリーニング関数を開始。」",
        "day_1_meeting_feedback": "会議メモ/フィードバック", "day_1_meeting_feedback_help": "今日の会議での主要な議論点、決定事項、ステークホルダーからの意見、または教員からのフィードバック。", "day_1_meeting_feedback_placeholder": "例: 「ステークホルダーが明確な'航続距離'定義の必要性を強調。'EPA推定航続距離'を使用することに決定。教員は研究課題Xに焦点を当てるよう提案。」",

        # Day 2 (Japanese)
        "day_2_tab": "🗓️ 2日目 – MVPビルドデイ",
        "day_2_datasets_imported": "インポート済みデータセット (>=2)", "day_2_datasets_imported_help": "どの2つ以上のデータセットがインポートされましたか？可能なら証拠を見せてください！", "day_2_datasets_imported_placeholder": "例: 「EV_Specs.csvとUS_Population_2022.csvがPythonスクリプトでロードされています。」",
        "day_2_data_transformations": "データ変換", "day_2_data_transformations_help": "適用したデータクリーニング、前処理、または変換のステップを記述してください。課題は？", "day_2_data_transformations_placeholder": "例: 「'航続距離'（'N/A'処理）と'価格'（'$'削除）をクリーニング。日付形式で苦戦。特徴量XをYを用いて変換。」",
        "day_2_sqlite_tables_queries": "SQLiteテーブルとクエリ", "day_2_sqlite_tables_queries_help": "作成したデータベーステーブルと、計画または実行した主要なSQLクエリを記述してください。問題は？", "day_2_sqlite_tables_queries_placeholder": "例: 「'vehicles'と'locations'テーブルを作成。それらをJOINする計画。州別の平均航続距離のクエリを作成済み。」",
        "day_2_blockers_idle": "ブロッカー / 課題", "day_2_blockers_idle_help": "進捗を妨げているものは？", "day_2_blockers_idle_placeholder": "例: 「メンバーDはクリーニング済みデータを待っていてブロック中。クリーニングスクリプトを優先する必要がある。」",
        "day_2_backlog": "バックログ", "day_2_backlog_help": "このイテレーションで何を計画し、何を達成しましたか？バックログ項目の更新。", "day_2_backlog_placeholder": "例: 「計画: DBスキーマとインポート。達成: 両方。クリーニングは50%完了。バックログ更新済み。」",
        "day_2_action_items_day3": "3日目のアクションアイテム", "day_2_action_items_day3_help": "明日の目標。", "day_2_action_items_day3_placeholder": "例: 「1. クリーニング完了。2. DBにデータ投入。3. 最初のSQLクエリ作成。」",
        "day_2_meeting_feedback": "会議メモ/フィードバック", "day_2_meeting_feedback_help": "今日の会議での主要な議論点、決定事項、ステークホルダーからの意見、または教員からのフィードバック。", "day_2_meeting_feedback_placeholder": "例: 「データクリーニング戦略を議論。ステークホルダーがログ記録について質問。教員: E2Eパイプラインを早く実行できるように。」",

        # Day 3 (Japanese)
        "day_3_tab": "🗓️ 3日目 – ソフト機能フリーズ",
        "day_3_research_question_status": "研究課題の状況", "day_3_research_question_status_help": "主要な研究課題への回答に向けた進捗状況を更新してください。調査結果は整合していますか？", "day_3_research_question_status_placeholder": "例: 「データセットXの初期分析はYを示唆。これはRQ1と整合。RQ2のためにはさらなるクエリZが必要。」",
        "day_3_features_reports": "機能とレポート", "day_3_features_reports_help": "開発した主要機能と生成されたレポートの状況。パイプラインは完全に稼働していますか（インポート→クリーン→DB→SQL→レポート）？", "day_3_features_reports_placeholder": "例: 「パイプラインは稼働中！レポートスクリプトはQ1の調査結果を生成。機能Xは完了。」",
        "day_3_readme_documentation": "READMEとドキュメント", "day_3_readme_documentation_help": "READMEは必要な情報（セットアップ、スキーマ、調査結果、クエリ説明）で更新されていますか？その他のドキュメントの状況。チーム外の誰かがそれをフォローできますか？", "day_3_readme_documentation_placeholder": "例: 「READMEにスキーマと最初のクエリを更新。セットアップ手順は明確。別のグループが理解を確認。」",
        "day_3_action_items_day4": "4日目のアクションアイテム", "day_3_action_items_day4_help": "明日の目標。", "day_3_action_items_day4_placeholder": "例: 「1. レポートスクリプト最終化。2. 2番目のSQLクエリ追加。3. README完全更新。4. コードクリーンアップ＆コメント。」",
        "day_3_meeting_feedback": "会議メモ/フィードバック", "day_3_meeting_feedback_help": "今日の会議での主要な議論点、決定事項、ステークホルダーからの意見、または教員からのフィードバック。", "day_3_meeting_feedback_placeholder": "例: 「Q1の結果をレビュー。レポート形式を議論。ステークホルダーがクエリの複雑さを要求。教員: 素晴らしいパイプライン！洞察をより明確に。」",

        # Day 4 (Japanese - Unchanged as per request to modify Day 1-3)
        "day_4_tab": "🗓️ 4日目 – 最終準備＆機能フリーズ",
        "day_4_feature_status": "機能フリーズ確認", "day_4_feature_status_help": "確認：今はバグ修正と磨き上げのみ。", "day_4_feature_status_placeholder": "",
        "day_4_sql_queries_report": "レポート内のSQLクエリ", "day_4_sql_queries_report_help": "レポート内の2つ以上の主要なクエリとその目的をリストアップしてください。", "day_4_sql_queries_report_placeholder": "例: 「1. 州別平均航続距離 (JOIN, GROUP BY)。2. 台数別トップ5 EV (COUNT, ORDER BY, LIMIT)。」",
        "day_4_report_readability": "レポートの可読性/関連性", "day_4_report_readability_help": "レポートは明確ですか？私が理解できますか？", "day_4_report_readability_placeholder": "例: 「レポートには序論、クエリ説明、結果、要約が含まれています。マークダウンでフォーマット済み。」",
        "day_4_readme_checklist_title": "README 最終チェックリスト", "day_4_readme_checklist_title_help": "最終ドキュメントは100%完成していますか？", "day_4_readme_checklist_title_placeholder": "",
        "day_4_readme_theme_summary": "テーマ概要を含む", "day_4_readme_theme_summary_help": "", "day_4_readme_theme_summary_placeholder": "",
        "day_4_readme_setup_instructions": "セットアップと実行手順を含む", "day_4_readme_setup_instructions_help": "", "day_4_readme_setup_instructions_placeholder": "",
        "day_4_readme_final_schema": "最終スキーマ設計を含む", "day_4_readme_final_schema_help": "", "day_4_readme_final_schema_placeholder": "",
        "day_4_readme_sql_queries_explanation": "SQLクエリと出力の説明を含む", "day_4_readme_sql_queries_explanation_help": "", "day_4_readme_sql_queries_explanation_placeholder": "",
        "day_4_readme_summary_findings": "調査結果の概要を含む", "day_4_readme_summary_findings_help": "", "day_4_readme_summary_findings_placeholder": "",
        "day_4_code_quality": "コード品質チェック", "day_4_code_quality_help": "モジュール化され、コメントがあり、読みやすいですか？", "day_4_code_quality_placeholder": "例: 「関数にリファクタリング。ドックストリング追加。リンター実行。PEP8準拠。」",
        "day_4_sprint_records": "スプリント記録リンク/場所", "day_4_sprint_records_help": "その道のりはどこで見られますか？", "day_4_sprint_records_placeholder": "例: 「Jiraボードリンク / スプリントサマリー付きConfluenceページ。」",
        "day_4_output_insightfulness": "出力の洞察力", "day_4_output_insightfulness_help": "これは本当に役立ちますか？「だから何？」という点は？", "day_4_output_insightfulness_placeholder": "例: 「主要な発見はXであり、これはビジネスがYに集中すべきことを示唆しています...」",
        "day_4_presentation_confidence": "非技術者向けプレゼン準備", "day_4_presentation_confidence_help": "これを非技術的な聴衆に明確に説明する準備はできていますか？", "day_4_presentation_confidence_placeholder": "例: 「コードだけでなく、『なぜ』と結果に焦点を当てて流れを練習しました。」",
        "day_4_final_questions_issues": "最終的な質問 / 課題", "day_4_final_questions_issues_help": "最終プレゼンテーション前の最後の懸念事項はありますか？", "day_4_final_questions_issues_placeholder": "例: 「ライブ実行に懸念あり - バックアップとして事前生成レポートを使用します。」",
        "day_4_instructor_feedback": "ステークホルダーからのフィードバック", "day_4_instructor_feedback_help": "「ステークホルダー」からの最終メモ。", "day_4_instructor_feedback_placeholder": "例: 「素晴らしい出来栄え！プレゼンテーションの準備は万端。明瞭さを重視してください。」",
    }
}

# --- Helper Functions ---
def get_translation(lang_code, key):
    return TRANSLATIONS.get(lang_code, TRANSLATIONS["en"]).get(key, key)

def get_help_text(lang_code, key):
    help_key = f"{key}_help"
    return TRANSLATIONS.get(lang_code, TRANSLATIONS["en"]).get(help_key, "")

def get_placeholder_text(lang_code, key):
    placeholder_key = f"{key}_placeholder"
    return TRANSLATIONS.get(lang_code, TRANSLATIONS["en"]).get(placeholder_key, "")

def initialize_session_state():
    if "lang" not in st.session_state:
        st.session_state.lang = "en"
    base_keys = ["group_number", "time_slot", "project_title", "current_research_question", "note_taker"]
    for key in base_keys:
        if key not in st.session_state:
            st.session_state[key] = ""
    if "date" not in st.session_state:
        st.session_state.date = datetime.now().date()

    # Dynamically get all form field keys from the TRANSLATIONS dictionary
    # These are keys that start with "day_" and do not end with common suffixes for non-input elements
    all_day_form_keys = []
    for lang_code in TRANSLATIONS: # Iterate through each language dictionary
        for key in TRANSLATIONS[lang_code]:
            if key.startswith("day_") and not key.endswith(("_help", "_tab", "_title", "_placeholder")):
                all_day_form_keys.append(key)
    all_day_form_keys = sorted(list(set(all_day_form_keys))) # Get unique keys and sort

    for key in all_day_form_keys:
        if key not in st.session_state:
            if "status" in key or "readme_" in key or key == "day_4_feature_status": # Checkboxes
                st.session_state[key] = False
            else: # Text inputs/areas
                st.session_state[key] = ""
    if "submitted_and_download_ready" not in st.session_state:
        st.session_state.submitted_and_download_ready = False
    if "current_download_data" not in st.session_state:
        st.session_state.current_download_data = {}

def get_all_form_data():
    data = {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Language": st.session_state.lang,
        "GroupNumber": st.session_state.get("group_number", ""),
        "MeetingTimeSlot": str(st.session_state.get("time_slot", "")),
        "MeetingDate": str(st.session_state.get("date", "")),
        "ProjectTitle": st.session_state.get("project_title", ""),
        "CurrentResearchQuestion": st.session_state.get("current_research_question", ""),
        "NoteTaker": st.session_state.get("note_taker", ""),
        "MeetingDayFocus": "" # Will be filled in render_buttons before saving
    }
    # Add all day-specific fields dynamically from session state based on TRANSLATIONS keys
    all_day_keys_flat = []
    for lang_code in TRANSLATIONS:
        for k in TRANSLATIONS[lang_code]:
            if k.startswith("day_") and not k.endswith(("_help", "_tab", "_title", "_placeholder")):
                all_day_keys_flat.append(k)
    all_day_keys_unique = sorted(list(set(all_day_keys_flat)))

    for key in all_day_keys_unique:
        data[key] = st.session_state.get(key, False if "status" in key or "readme_" in key else "") # Handle booleans for checkboxes
    return data

def get_student_download_content(active_day_key, lang):
    content = f"# {get_translation(lang, 'app_title')}\n\n"
    content += f"## {get_translation(lang, 'sidebar_title')}\n"
    content += f"- **{get_translation(lang, 'group_number')}**: {st.session_state.get('group_number', '')}\n"
    content += f"- **{get_translation(lang, 'time_slot')}**: {st.session_state.get('time_slot', '')}\n"
    content += f"- **{get_translation(lang, 'date')}**: {st.session_state.get('date', '')}\n"
    content += f"- **{get_translation(lang, 'project_title')}**: {st.session_state.get('project_title', '')}\n"
    content += f"- **{get_translation(lang, 'note_taker')}**: {st.session_state.get('note_taker', '')}\n\n"
    try:
        day_prefix = active_day_key.split('_tab')[0] + "_" # e.g., "day_1_"
    except Exception:
        day_prefix = "day_1_" # Fallback
    content += f"## {get_translation(lang, active_day_key)}\n"

    # Filter keys more carefully: must exist in the CURRENT language's dictionary for that day
    day_specific_keys = [
        k for k in TRANSLATIONS[lang].keys()
        if k.startswith(day_prefix) and
           k != active_day_key and
           not k.endswith(("_help", "_title", "_placeholder", "_tab"))
    ]
    # Also add the common "current_research_question" if it's not already listed by prefix
    # However, it's handled separately below.

    for key_id in day_specific_keys:
        label = get_translation(lang, key_id)
        value = st.session_state.get(key_id, "") # Get value from session state
        if isinstance(st.session_state.get(key_id), bool): # Check original type from session_state for checkboxes
            value = ("Yes" if value else "No") if lang == "en" else ("はい" if value else "いいえ")
        content += f"### {label}\n{value}\n\n"

    # Add Current Research Question separately as it's common to all tabs but tied to session state
    content += f"### {get_translation(lang, 'current_research_question')}\n" # Label for the section
    content += f"{st.session_state.get('current_research_question', '')}\n\n" # The actual content

    return content

@st.cache_resource # Cache the gspread connection
def connect_gsheets():
    try:
        creds_dict = st.secrets["gcp_service_account"]
        gc = gspread.service_account_from_dict(creds_dict)
        return gc
    except Exception as e:
        st.error(f"GSheets Connect Error (check st.secrets configuration): {e}")
        return None

def save_to_gsheets_new_row(data_dict):
    gc = connect_gsheets()
    if not gc:
        return False

    SHEET_NAME = "All_Submissions_V2" # Consider a new sheet name if schema changes significantly
    # Define the full list of headers based on get_all_form_data structure
    expected_headers = list(data_dict.keys())

    try:
        spreadsheet_id = st.secrets["gcp_spreadsheet"]["key"]
        sh = gc.open_by_key(spreadsheet_id)

        try:
            worksheet = sh.worksheet(SHEET_NAME)
            header_row_values = worksheet.row_values(1) if worksheet.row_count > 0 else []
            # If headers are missing, mismatched, or only placeholder headers exist, rewrite them
            if not header_row_values or sorted(header_row_values) != sorted(expected_headers):
                # Check if the sheet is practically empty or headers are truly different
                if worksheet.row_count <= 1 or not header_row_values : # If empty or just a placeholder row
                    worksheet.clear() # Clears all values but keeps the sheet
                    worksheet.update([expected_headers]) # Write headers as the first row
                    # st.toast(f"Headers updated/written in '{SHEET_NAME}'.") # Optional: for debugging
                # If headers exist but don't match, and sheet has data, it's a more complex migration.
                # For now, we assume new data will be appended, and columns might not align perfectly with old data.
                # GSpread append_row handles this by adding new columns if necessary at the end of the sheet,
                # or filling existing columns. This might lead to sparse rows if old data had more columns.
        except gspread.WorksheetNotFound:
            worksheet = sh.add_worksheet(title=SHEET_NAME, rows="1", cols=len(expected_headers))
            worksheet.update([expected_headers]) # Write headers as the first row
            # st.toast(f"Created new sheet '{SHEET_NAME}' and added headers.") # Optional: for debugging

        # Prepare data row in the order of expected_headers
        data_row = [data_dict.get(header, "") for header in expected_headers]
        worksheet.append_row(data_row, value_input_option='USER_ENTERED')
        return True
    except gspread.exceptions.APIError as e:
        st.error(f"GSheets API Error: {e}. Check Google Sheet Sharing settings or API quotas.")
        return False
    except Exception as e:
        st.error(f"GSheets Write Error: {e}")
        return False

def render_day_inputs(lang, day_prefix):
    # Get keys relevant for the current day and language from TRANSLATIONS
    keys = [k for k in TRANSLATIONS[lang] if k.startswith(day_prefix) and not k.endswith(("_help", "_tab", "_title", "_placeholder"))]

    for key in keys:
        label = get_translation(lang, key)
        help_text = get_help_text(lang, key)
        placeholder = get_placeholder_text(lang, key)

        # Skip any key that accidentally gets here if it's a title-like key (though filtered above)
        if key == day_prefix + "title": continue

        # Specific handling for Day 4 README checklist title (if it were part of this generic function)
        if key == "day_4_readme_checklist_title": # This specific key is handled in main() for Day 4
            st.markdown(f"**{label}**"); st.caption(f"*{help_text}*"); continue

        # Determine widget type based on key name conventions or explicitly
        if "feature_status" in key or "readme_" in key: # Checkboxes
             # Ensure boolean default from session_state if key exists, otherwise False
            default_value = st.session_state.get(key, False)
            if not isinstance(default_value, bool): # Correct if somehow not a bool
                default_value = False
            st.session_state[key] = st.checkbox(label, value=default_value, help=help_text, key=f"widget_{key}")
        elif "link" in key: # Text input for links
            st.session_state[key] = st.text_input(label, value=st.session_state.get(key, ""), placeholder=placeholder, help=help_text, key=f"widget_{key}")
        else: # Default to text_area for other fields
            st.session_state[key] = st.text_area(label, value=st.session_state.get(key, ""), placeholder=placeholder, help=help_text, height=100, key=f"widget_{key}")


def render_buttons(tab_key, lang):
    group_num = st.session_state.get('group_number', 'GroupX')
    date_str = str(st.session_state.get('date', 'Date'))

    # Extract day number from tab_key (e.g., "day_1_tab" -> "1")
    try:
        day_num_str = tab_key.split('_')[1]
    except IndexError:
        day_num_str = "UnknownDay" # Fallback

    download_filename = f"Capstone_Notes_Group{group_num}_Day{day_num_str}_{date_str}.md"
    # download_placeholder = st.empty() # Not used here, button directly placed

    if st.button(get_translation(lang, "submit_and_download"), key=f"submit_b_{tab_key}"):
        st.session_state.submitted_and_download_ready = False # Reset flag
        form_data = get_all_form_data()
        form_data["MeetingDayFocus"] = get_translation(lang, tab_key) # Store the translated tab name as focus

        # Basic validation for common fields
        required_sidebar_fields = ["group_number", "time_slot", "project_title", "note_taker"]
        missing_fields = [get_translation(lang, f) for f in required_sidebar_fields if not st.session_state.get(f)]
        if missing_fields:
            st.error(f"{get_translation(lang, 'submission_error')} {get_translation(lang, 'Please fill these common fields')}: {', '.join(missing_fields)}")
            return # Stop submission

        if save_to_gsheets_new_row(form_data):
            st.success(get_translation(lang, "submission_success"))
            st.session_state.current_download_data = {
                "content": get_student_download_content(tab_key, lang), # Pass active tab_key
                "filename": download_filename
            }
            st.session_state.submitted_and_download_ready = True
            # Rerun to make download button available immediately below
            st.rerun()
        else:
            st.error(get_translation(lang, "submission_gsheets_error"))
            st.session_state.submitted_and_download_ready = False


    if st.session_state.submitted_and_download_ready:
        # Ensure the active tab for download matches the one submitted
        # This check might be redundant if rerun clears other states, but good for safety
        # For simplicity, we assume if submitted_and_download_ready is true, current_download_data is set.
        st.download_button(
            label=get_translation(lang, "download_student_copy"),
            data=st.session_state.current_download_data.get("content", "Error: No content generated."),
            file_name=st.session_state.current_download_data.get("filename", "error_filename.md"),
            mime='text/markdown',
            key=f"download_btn_active_{tab_key}" # Make key unique if needed, or general
        )
        # Optionally reset flag after download button is shown to prevent it from staying across tabs if not desired
        # However, current logic with rerun might handle this. If download button persists unwantedly:
        # st.session_state.submitted_and_download_ready = False


def main():
    initialize_session_state() # Initialize first
    st.set_page_config(layout="wide", page_title=get_translation(st.session_state.lang, "app_title"))
    st.title(get_translation(st.session_state.lang, "app_title"))

    language_options = {"English": "en", "日本語": "ja"}
    # Ensure current_lang_display is found, default to English if somehow lang is not in options
    current_lang_key = st.session_state.get("lang", "en")
    current_lang_display = [k for k, v in language_options.items() if v == current_lang_key]
    current_lang_display = current_lang_display[0] if current_lang_display else "English"


    selected_language_display = st.sidebar.selectbox(
        get_translation(st.session_state.lang, "language_select"), # Label uses current lang
        options=list(language_options.keys()),
        index=list(language_options.keys()).index(current_lang_display)
    )
    new_lang = language_options[selected_language_display]

    if new_lang != st.session_state.lang:
        st.session_state.lang = new_lang
        # Clear submission ready flag on language change to avoid showing download for wrong language/content
        st.session_state.submitted_and_download_ready = False
        st.session_state.current_download_data = {}
        st.rerun()

    lang = st.session_state.lang # Set lang after potential rerun

    st.sidebar.header(get_translation(lang, "sidebar_title"))
    st.session_state.group_number = st.sidebar.text_input(get_translation(lang, "group_number"), value=st.session_state.get("group_number",""), help=get_help_text(lang, "group_number"))
    st.session_state.time_slot = st.sidebar.text_input(get_translation(lang, "time_slot"), value=st.session_state.get("time_slot",""), help=get_help_text(lang, "time_slot"))
    st.session_state.date = st.sidebar.date_input(get_translation(lang, "date"), value=st.session_state.get("date", datetime.now().date()), help=get_help_text(lang, "date"))
    st.session_state.project_title = st.sidebar.text_input(get_translation(lang, "project_title"), value=st.session_state.get("project_title",""), help=get_help_text(lang, "project_title"))
    st.session_state.note_taker = st.sidebar.text_input(get_translation(lang, "note_taker"), value=st.session_state.get("note_taker",""), help=get_help_text(lang, "note_taker"))

    # Define tab keys and their corresponding prefixes for filtering questions
    tab_definitions = [
        ("day_1_tab", "day_1_"),
        ("day_2_tab", "day_2_"),
        ("day_3_tab", "day_3_"),
        ("day_4_tab", "day_4_")
    ]

    tab_titles = [get_translation(lang, tab_key) for tab_key, _ in tab_definitions]
    created_tabs = st.tabs(tab_titles)

    # Store which tab was last submitted to manage download button visibility correctly
    if 'last_submitted_tab_key' not in st.session_state:
        st.session_state.last_submitted_tab_key = None


    for i, (tab_key, day_prefix) in enumerate(tab_definitions):
        with created_tabs[i]:
            st.header(get_translation(lang, tab_key)) # Display translated tab header
            st.info(get_translation(lang, "hint_visibility"))

            # Special handling for Day 4's unique structure (README checklist)
            if tab_key == "day_4_tab":
                # Render non-README fields for Day 4
                day_4_non_readme_keys = [
                    k for k in TRANSLATIONS[lang]
                    if k.startswith(day_prefix) and
                       not k.endswith(("_help", "_tab", "_title", "_placeholder")) and
                       not k.startswith(day_prefix + "readme_") and # Exclude general readme title itself
                       k != day_prefix + "readme_checklist_title" # Explicitly exclude this meta-key
                ]
                for key_d4 in day_4_non_readme_keys:
                    label = get_translation(lang, key_d4)
                    help_text = get_help_text(lang, key_d4)
                    placeholder = get_placeholder_text(lang, key_d4)
                    if "feature_status" in key_d4: # Checkbox
                        default_val_d4_cb = st.session_state.get(key_d4, False)
                        if not isinstance(default_val_d4_cb, bool): default_val_d4_cb = False
                        st.session_state[key_d4] = st.checkbox(label, value=default_val_d4_cb, help=help_text, key=f"widget_{key_d4}")
                    else: # Text Area
                        st.session_state[key_d4] = st.text_area(label, value=st.session_state.get(key_d4, ""), placeholder=placeholder, help=help_text, height=100, key=f"widget_{key_d4}")

                # Render Day 4 README Checklist Title
                readme_title_key = day_prefix + "readme_checklist_title"
                if readme_title_key in TRANSLATIONS[lang]:
                    st.markdown(f"**{get_translation(lang, readme_title_key)}**")
                    st.caption(f"*{get_help_text(lang, readme_title_key)}*")

                # Render Day 4 README checklist items (checkboxes)
                day_4_readme_item_keys = [
                    k for k in TRANSLATIONS[lang]
                    if k.startswith(day_prefix + "readme_") and
                       not k.endswith(("_help", "_title", "_placeholder")) and # Standard exclusions
                       k != readme_title_key # Exclude the title itself from being a checkbox
                ]
                for key_d4_readme in day_4_readme_item_keys:
                    default_val_d4_cb_readme = st.session_state.get(key_d4_readme, False)
                    if not isinstance(default_val_d4_cb_readme, bool): default_val_d4_cb_readme = False
                    st.session_state[key_d4_readme] = st.checkbox(get_translation(lang, key_d4_readme), value=default_val_d4_cb_readme, help=get_help_text(lang, key_d4_readme), key=f"widget_{key_d4_readme}")
            else:
                # Generic rendering for Day 1, 2, 3
                render_day_inputs(lang, day_prefix)

            st.markdown("---")
            # Current Research Question - Common to all tabs
            # The label for the text_area itself is a bit redundant due to the subheader, so can be collapsed
            st.subheader(get_translation(lang, "current_research_question"))
            st.session_state.current_research_question = st.text_area(
                label=get_translation(lang, "current_research_question"), # Technically the label for the box
                value=st.session_state.get("current_research_question", ""),
                help=get_help_text(lang, "current_research_question"),
                placeholder=get_placeholder_text(lang, "current_research_question") or "Enter your research questions here...", # Fallback placeholder
                key=f"research_q_input_{day_prefix}", # Unique key for the text_area widget on each tab
                label_visibility="collapsed" # Hide the direct label as subheader is used
            )
            st.markdown("---")

            # --- Submit and Download Buttons Logic ---
            group_num = st.session_state.get('group_number', 'GroupX')
            date_str = str(st.session_state.get('date', datetime.now().strftime('%Y-%m-%d')))
            try:
                day_num_str = tab_key.split('_')[1]
            except IndexError:
                day_num_str = "CurrentDay"

            download_filename = f"Capstone_Notes_Group{group_num}_Day{day_num_str}_{date_str}.md"

            # Submit Button
            if st.button(get_translation(lang, "submit_and_download"), key=f"submit_btn_{tab_key}"):
                st.session_state.submitted_and_download_ready = False # Reset for this submission attempt
                st.session_state.last_submitted_tab_key = tab_key # Mark this tab as the source of submission

                form_data = get_all_form_data()
                form_data["MeetingDayFocus"] = get_translation(lang, tab_key) # Set focus to current tab's name

                required_sidebar_fields = ["group_number", "time_slot", "project_title", "note_taker"]
                missing_fields = [get_translation(lang, f) for f in required_sidebar_fields if not st.session_state.get(f)]

                if missing_fields:
                    missing_fields_str = ", ".join(missing_fields)
                    # Try to get a translated "Please fill common fields" or use a default
                    common_fields_prompt_key = "please_fill_common_fields" # Add this key to TRANSLATIONS if needed
                    common_fields_prompt = get_translation(lang, common_fields_prompt_key)
                    if common_fields_prompt == common_fields_prompt_key: # If no translation, use English
                        common_fields_prompt = "Please fill these common fields"
                    st.error(f"{get_translation(lang, 'submission_error')} {common_fields_prompt}: {missing_fields_str}")
                elif save_to_gsheets_new_row(form_data):
                    st.success(get_translation(lang, "submission_success"))
                    st.session_state.current_download_data = {
                        "content": get_student_download_content(tab_key, lang),
                        "filename": download_filename
                    }
                    st.session_state.submitted_and_download_ready = True
                    # No rerun here, let download button appear on the same interaction
                else:
                    st.error(get_translation(lang, "submission_gsheets_error"))
                    st.session_state.submitted_and_download_ready = False # Explicitly set on failure

            # Download Button - Show only if submission was successful AND this is the tab that was submitted
            if st.session_state.get("submitted_and_download_ready") and st.session_state.get("last_submitted_tab_key") == tab_key:
                st.download_button(
                    label=get_translation(lang, "download_student_copy"),
                    data=st.session_state.current_download_data.get("content", "Error: No content generated."),
                    file_name=st.session_state.current_download_data.get("filename", "error_filename.md"),
                    mime='text/markdown',
                    key=f"download_btn_for_{tab_key}" # Unique key for download button
                )

    st.markdown("---")
    st.markdown(f"**{get_translation(lang, 'important_label')}:** {get_translation(lang, 'footer_submission_reminder')}")

if __name__ == "__main__":
    main()