import streamlit as st
import pandas as pd
from datetime import datetime
import os
import csv
import io
import gspread
import gspread_dataframe as gd

# --- Translation Dictionaries (V8 - Text Changes) ---
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
        # "gsheet_info" key removed
        "important_label": "Important",
        "footer_submission_reminder": "Please ensure your meeting notes are submitted by 5:30 PM today. Timely submissions are crucial for accurate feedback and effective project tracking.",
        # Day 1
        "day_1_tab": "🗓️ Day 1 – Kickoff & First Pitch",
        "day_1_value_prop": "Value Proposition", "day_1_value_prop_help": "What insight will this bring? What success will it enable for me (the stakeholder)?", "day_1_value_prop_placeholder": "E.g., 'This project will show us which car features most impact EV range, helping us target our marketing...'",
        "day_1_features_v1": "Proposed V1 Features", "day_1_features_v1_help": "What are the *must-have* features for V1? (Core Req: File Handling, Cleaning, DB Setup, SQL Query, Report).", "day_1_features_v1_placeholder": "E.g., '1. Import EV specs & Population data. 2. Clean 'range' & 'city' columns. 3. Create 'vehicles' & 'locations' tables...'",
        "day_1_features_future": "Future Features", "day_1_features_future_help": "What are your stretch goals or ideas for V2+? (Extension: Advanced SQL, Validation, CLI).", "day_1_features_future_placeholder": "E.g., 'Add sentiment analysis from reviews, predict future EV prices, create an interactive dashboard...'",
        "day_1_planning_readme_link": "Planning/README Link", "day_1_planning_readme_link_help": "Share the link to your plan (Confluence/Jira/GitHub).", "day_1_planning_readme_link_placeholder": "https://github.com/your_team/your_repo/blob/main/README.md",
        "day_1_db_schema_plan": "Database Schema Plan", "day_1_db_schema_plan_help": "Describe or link your ERD/Table plan. Why this structure?", "day_1_db_schema_plan_placeholder": "E.g., 'Vehicles table (PK: VIN) links to Charging_Stations table (FK: Station_ID)... We chose this to easily join on location...'",
        "day_1_git_strategy": "Git Strategy", "day_1_git_strategy_help": "How will you manage code collaboration? Who merges? When?", "day_1_git_strategy_placeholder": "E.g., 'Feature branches, Pull Requests reviewed by 2 members, Scrum Master merges daily...'",
        "day_1_team_roles": "Team Roles & Responsibilities", "day_1_team_roles_help": "Who is Product Owner? Scrum Master? Who does what?", "day_1_team_roles_placeholder": "E.g., 'A: PO, B: Scrum Master, C: Lead Dev (Python), D: DB & SQL Lead...'",
        "day_1_backlog_plan": "Backlog Management", "day_1_backlog_plan_help": "Where is your Product/Sprint backlog? (Jira/Confluence link).", "day_1_backlog_plan_placeholder": "E.g., 'Using Jira board: [link]'",
        "day_1_discussion_points": "Meeting Discussion Points", "day_1_discussion_points_help": "Key topics, decisions, or questions from today.", "day_1_discussion_points_placeholder": "E.g., 'Stakeholder emphasized need for clear 'range' definition. Decided to use 'EPA Est. Range'.'",
        "day_1_instructor_feedback": "Stakeholder Feedback", "day_1_instructor_feedback_help": "Notes from the 'stakeholder'.", "day_1_instructor_feedback_placeholder": "E.g., 'Good start, but push for a more ambitious research question. How does weather affect range?'",
        "day_1_action_items_day2": "Action Items for Day 2", "day_1_action_items_day2_help": "What must be achieved by tomorrow?", "day_1_action_items_day2_placeholder": "E.g., '1. Finalize DB Schema. 2. Implement Python import for 2 datasets. 3. Start cleaning functions.'",
        # Day 2
        "day_2_tab": "🗓️ Day 2 – MVP Build Day",
        "day_2_datasets_imported": "Datasets Imported (>=2)", "day_2_datasets_imported_help": "Which 2+ datasets are imported? Show proof if possible!", "day_2_datasets_imported_placeholder": "E.g., 'EV_Specs.csv and US_Population_2022.csv are now loading via Python scripts.'",
        "day_2_data_cleaning_status": "Data Cleaning Status", "day_2_data_cleaning_status_help": "How is cleaning going? What challenges?", "day_2_data_cleaning_status_placeholder": "E.g., 'Cleaning 'range' (handling 'N/A') and 'price' (removing '$'). Stuck on date formats.'",
        "day_2_sqlite_schema_status": "SQLite Schema Status", "day_2_sqlite_schema_status_help": "Is the DB schema created? Any issues?", "day_2_sqlite_schema_status_placeholder": "E.g., 'Tables created successfully. Added primary/foreign keys. No issues yet.'",
        "day_2_sql_query_ideas": "SQL Query Ideas", "day_2_sql_query_ideas_help": "What specific SQL are you planning?", "day_2_sql_query_ideas_placeholder": "E.g., 'Plan to JOIN vehicles and locations, then GROUP BY state to find AVG range.'",
        "day_2_sprint_backlog_increments": "Sprint 1 Backlog/Increments", "day_2_sprint_backlog_increments_help": "What did you plan and achieve yesterday?", "day_2_sprint_backlog_increments_placeholder": "E.g., 'Achieved DB Schema & Import. Cleaning is 50% done. Backlog updated.'",
        "day_2_blockers_idle": "Blockers / Issues", "day_2_blockers_idle_help": "What's stopping progress?", "day_2_blockers_idle_placeholder": "E.g., 'Member D is blocked waiting for cleaned data. Need to prioritize cleaning script.'",
        "day_2_pipeline_run_status": "End-to-End Pipeline Status", "day_2_pipeline_run_status_help": "Can you run it end-to-end, even with dummy data?", "day_2_pipeline_run_status_placeholder": "E.g., 'Not yet. Aiming for EOD. Can run Import -> Clean currently.'",
        "day_2_logging_documentation": "Logging/Transformation Docs", "day_2_logging_documentation_help": "How are you documenting data changes?", "day_2_logging_documentation_placeholder": "E.g., 'Adding comments in Python functions and logging steps to a text file.'",
        "day_2_discussion_points": "Meeting Discussion Points", "day_2_discussion_points_help": "Key topics from today.", "day_2_discussion_points_placeholder": "E.g., 'Discussed data cleaning strategy. Stakeholder asked about logging.'",
        "day_2_instructor_feedback": "Stakeholder Feedback", "day_2_instructor_feedback_help": "Notes from the 'stakeholder'.", "day_2_instructor_feedback_placeholder": "E.g., 'Good progress, but ensure the E2E pipeline runs soon, even simply. Consider adding more datasets?'",
        "day_2_action_items_day3": "Action Items for Day 3", "day_2_action_items_day3_help": "Goals for tomorrow.", "day_2_action_items_day3_placeholder": "E.g., '1. Complete cleaning. 2. Populate DB. 3. Write first SQL query.'",
        # Day 3
        "day_3_tab": "🗓️ Day 3 – Soft Feature Freeze",
        "day_3_full_pipeline_status": "Full Pipeline Status", "day_3_full_pipeline_status_help": "Is it fully operational? (Import -> Clean -> DB -> SQL).", "day_3_full_pipeline_status_placeholder": "E.g., 'Yes! It runs, imports 2 files, cleans, inserts, and runs one query. Report generation started.'",
        "day_3_sql_query_results": "SQL Query Results", "day_3_sql_query_results_help": "Show the results. Do they make sense? Do they answer the questions?", "day_3_sql_query_results_placeholder": "E.g., 'Query 1 shows CA has highest avg EV range (310 miles). Results seem reasonable.'",
        "day_3_report_gen_status": "Report Generation Status", "day_3_report_gen_status_help": "How is the report script?", "day_3_report_gen_status_placeholder": "E.g., 'Script runs, executes SQL, fetches data. Working on formatting to markdown now.'",
        "day_3_readme_docs": "README Docs (Schema/Query)", "day_3_readme_docs_help": "Is the README updated?", "day_3_readme_docs_placeholder": "E.g., 'Schema added with Crow's Foot. First query documented. Link: ...'",
        "day_3_sprint_backlog_increments": "Sprint 2 Backlog/Increments", "day_3_sprint_backlog_increments_help": "What was planned and achieved yesterday?", "day_3_sprint_backlog_increments_placeholder": "E.g., 'Finished cleaning & DB population. Wrote Q1. Fell behind on Q2.'",
        "day_3_doc_clarity": "Documentation Clarity", "day_3_doc_clarity_help": "Can someone *not* on your team follow it?", "day_3_doc_clarity_placeholder": "E.g., 'We think so. Asked another group for quick feedback - they understood the setup.'",
        "day_3_query_theme_alignment": "Query/Theme Alignment", "day_3_query_theme_alignment_help": "Are we still on track to answer the original questions?", "day_3_query_theme_alignment_placeholder": "E.g., 'Yes, Q1 directly addresses RQ1. RQ2 shifted slightly based on data availability.'",
        "day_3_discussion_points": "Meeting Discussion Points", "day_3_discussion_points_help": "Key topics from today.", "day_3_discussion_points_placeholder": "E.g., 'Reviewed Q1 results. Discussed report format. Stakeholder pushed for query complexity.'",
        "day_3_instructor_feedback": "Stakeholder Feedback", "day_3_instructor_feedback_help": "Notes from the 'stakeholder'.", "day_3_instructor_feedback_placeholder": "E.g., 'Impressive pipeline! Now make the insights clearer in the report. Can you add a JOIN or subquery?'",
        "day_3_action_items_day4": "Action Items for Day 4", "day_3_action_items_day4_help": "Goals for tomorrow.", "day_3_action_items_day4_placeholder": "E.g., '1. Finalize report script. 2. Add 2nd SQL query. 3. Update README completely. 4. Code cleanup & comments.'",
        # Day 4
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
        # "gsheet_info" key removed
        "important_label": "重要",
        "footer_submission_reminder": "本日の午後5時30分までに、必ず会議の記録を提出してください。正確なフィードバックと効果的なプロジェクト進捗管理のため、期限内の提出が不可欠です。",
        # Day 1 (Japanese)
        "day_1_tab": "🗓️ 1日目 – キックオフ＆最初のピッチ",
        "day_1_value_prop": "価値提案", "day_1_value_prop_help": "これはどのような洞察をもたらしますか？私（ステークホルダー）にどのような成功をもたらしますか？", "day_1_value_prop_placeholder": "例: 「このプロジェクトは、どの車の機能がEV航続距離に最も影響するかを示し、マーケティングのターゲット設定に役立ちます...」",
        "day_1_features_v1": "提案 V1 機能", "day_1_features_v1_help": "V1で *必ず* 構築する必要があるコア機能は何ですか？ (コア要件: ファイル処理、クリーニング、DB設定、SQLクエリ、レポート)。", "day_1_features_v1_placeholder": "例: 「1. EV仕様と人口データをインポート。2. '航続距離'と'都市'列をクリーニング。3. 'vehicles'と'locations'テーブルを作成...」",
        "day_1_features_future": "将来の機能", "day_1_features_future_help": "ストレッチゴールやV2+のアイデアは何ですか？ (拡張: 高度なSQL、検証、CLI)。", "day_1_features_future_placeholder": "例: 「レビューからの感情分析を追加、将来のEV価格を予測、インタラクティブなダッシュボードを作成...」",
        "day_1_planning_readme_link": "計画/README リンク", "day_1_planning_readme_link_help": "計画へのリンクを共有してください (Confluence/Jira/GitHub)。", "day_1_planning_readme_link_placeholder": "https://github.com/your_team/your_repo/blob/main/README.md",
        "day_1_db_schema_plan": "データベーススキーマ計画", "day_1_db_schema_plan_help": "ERD/テーブル計画を説明またはリンクしてください。なぜこの構造なのですか？", "day_1_db_schema_plan_placeholder": "例: 「Vehiclesテーブル(PK: VIN)はCharging_Stationsテーブル(FK: Station_ID)にリンク... 場所で簡単に結合できるようにこれを選択...」",
        "day_1_git_strategy": "Git 戦略", "day_1_git_strategy_help": "どのようにコードの共同作業を管理しますか？誰が、いつ、どのようにマージしますか？", "day_1_git_strategy_placeholder": "例: 「機能ブランチ、2人のメンバーによるPRレビュー、スクラムマスターが毎日マージ...」",
        "day_1_team_roles": "チームの役割と責任", "day_1_team_roles_help": "POは誰ですか？SMは？誰が何をしますか？", "day_1_team_roles_placeholder": "例: 「A: PO, B: SM, C: リード開発(Python), D: DB & SQL担当...」",
        "day_1_backlog_plan": "バックログ管理", "day_1_backlog_plan_help": "プロダクト/スプリントバックログはどこですか？ (Jira/Confluenceリンク)。", "day_1_backlog_plan_placeholder": "例: 「Jiraボードを使用: [リンク]」",
        "day_1_discussion_points": "会議の議論点", "day_1_discussion_points_help": "今日の主要なトピック、決定事項、質問。", "day_1_discussion_points_placeholder": "例: 「ステークホルダーが明確な'航続距離'定義の必要性を強調。'EPA推定航続距離'を使用することに決定。」",
        "day_1_instructor_feedback": "ステークホルダーからのフィードバック", "day_1_instructor_feedback_help": "「ステークホルダー」からのメモ。", "day_1_instructor_feedback_placeholder": "例: 「良いスタートだが、より野心的な研究課題を目指してほしい。天候は航続距離にどう影響するか？」",
        "day_1_action_items_day2": "2日目のアクションアイテム", "day_1_action_items_day2_help": "明日までに何を達成する必要がありますか？", "day_1_action_items_day2_placeholder": "例: 「1. DBスキーマを最終化。2. 2つのデータセットのPythonインポートを実装。3. クリーニング関数を開始。」",
        # Day 2 (Japanese)
        "day_2_tab": "🗓️ 2日目 – MVPビルドデイ",
        "day_2_datasets_imported": "インポート済みデータセット (>=2)", "day_2_datasets_imported_help": "どの2つ以上のデータセットがインポートされましたか？可能なら証拠を見せてください！", "day_2_datasets_imported_placeholder": "例: 「EV_Specs.csvとUS_Population_2022.csvがPythonスクリプトでロードされています。」",
        "day_2_data_cleaning_status": "データクリーニング状況", "day_2_data_cleaning_status_help": "クリーニングはどのように進んでいますか？課題は？", "day_2_data_cleaning_status_placeholder": "例: 「'航続距離'（'N/A'処理）と'価格'（'$'削除）をクリーニング中。日付形式で苦戦。」",
        "day_2_sqlite_schema_status": "SQLiteスキーマ状況", "day_2_sqlite_schema_status_help": "DBスキーマは作成されましたか？問題は？", "day_2_sqlite_schema_status_placeholder": "例: 「テーブルは正常に作成。主キー/外部キーを追加。今のところ問題なし。」",
        "day_2_sql_query_ideas": "SQLクエリのアイデア", "day_2_sql_query_ideas_help": "計画している具体的なSQLは何ですか？", "day_2_sql_query_ideas_placeholder": "例: 「vehiclesとlocationsをJOINし、州でGROUP BYして平均航続距離を見つける予定。」",
        "day_2_sprint_backlog_increments": "スプリント1 バックログ/増分", "day_2_sprint_backlog_increments_help": "昨日何を計画し、何を達成しましたか？", "day_2_sprint_backlog_increments_placeholder": "例: 「DBスキーマとインポートを達成。クリーニングは50%完了。バックログ更新済み。」",
        "day_2_blockers_idle": "ブロッカー / 課題", "day_2_blockers_idle_help": "進捗を妨げているものは？", "day_2_blockers_idle_placeholder": "例: 「メンバーDはクリーニング済みデータを待っていてブロック中。クリーニングスクリプトを優先する必要がある。」",
        "day_2_pipeline_run_status": "E2Eパイプライン状況", "day_2_pipeline_run_status_help": "ダミーデータでもE2Eで実行できますか？", "day_2_pipeline_run_status_placeholder": "例: 「まだです。EODを目指しています。現在インポート→クリーンは実行可能。」",
        "day_2_logging_documentation": "ログ/変換ドキュメント", "day_2_logging_documentation_help": "データ変更をどう文書化していますか？", "day_2_logging_documentation_placeholder": "例: 「Python関数にコメントを追加し、ステップをテキストファイルにログ記録しています。」",
        "day_2_discussion_points": "会議の議論点", "day_2_discussion_points_help": "今日の主要なトピック。", "day_2_discussion_points_placeholder": "例: 「データクリーニング戦略を議論。ステークホルダーがログ記録について質問。」",
        "day_2_instructor_feedback": "ステークホルダーからのフィードバック", "day_2_instructor_feedback_help": "「ステークホルダー」からのメモ。", "day_2_instructor_feedback_placeholder": "例: 「良い進捗だが、E2Eパイプラインを早く、たとえ単純でも実行できるようにしてほしい。データセットを追加してみては？」",
        "day_2_action_items_day3": "3日目のアクションアイテム", "day_2_action_items_day3_help": "明日の目標。", "day_2_action_items_day3_placeholder": "例: 「1. クリーニング完了。2. DBにデータ投入。3. 最初のSQLクエリ作成。」",
        # Day 3 (Japanese)
        "day_3_tab": "🗓️ 3日目 – ソフト機能フリーズ",
        "day_3_full_pipeline_status": "完全なパイプライン状況", "day_3_full_pipeline_status_help": "完全に稼働していますか？ (インポート→クリーン→DB→SQL)。", "day_3_full_pipeline_status_placeholder": "例: 「はい！実行され、2つのファイルをインポート、クリーニング、挿入し、1つのクエリを実行します。レポート生成開始。」",
        "day_3_sql_query_results": "SQLクエリ結果", "day_3_sql_query_results_help": "結果を見せてください。意味が通りますか？質問に答えていますか？", "day_3_sql_query_results_placeholder": "例: 「クエリ1はCAが最高の平均EV航続距離(310マイル)であることを示しています。結果は妥当に見えます。」",
        "day_3_report_gen_status": "レポート生成状況", "day_3_report_gen_status_help": "レポートスクリプトはどうですか？", "day_3_report_gen_status_placeholder": "例: 「スクリプト実行、SQL実行、データ取得。現在マークダウンへのフォーマット作業中。」",
        "day_3_readme_docs": "READMEドキュメント (スキーマ/クエリ)", "day_3_readme_docs_help": "READMEは更新されていますか？", "day_3_readme_docs_placeholder": "例: 「スキーマをクロウズフット記法で追加。最初のクエリを文書化。リンク: ...」",
        "day_3_sprint_backlog_increments": "スプリント2 バックログ/増分", "day_3_sprint_backlog_increments_help": "昨日何を計画し、何を達成しましたか？", "day_3_sprint_backlog_increments_placeholder": "例: 「クリーニングとDB投入完了。Q1作成。Q2は遅延。」",
        "day_3_doc_clarity": "ドキュメントの明確さ", "day_3_doc_clarity_help": "チーム外の誰かがそれをフォローできますか？", "day_3_doc_clarity_placeholder": "例: 「そう思います。別のグループに簡単なフィードバックを依頼し、セットアップを理解してもらえました。」",
        "day_3_query_theme_alignment": "クエリ/テーマ整合性", "day_3_query_theme_alignment_help": "元の質問に答えるための軌道に乗っていますか？", "day_3_query_theme_alignment_placeholder": "例: 「はい、Q1はRQ1に直接対応。RQ2はデータ利用可能性に基づきわずかに変更。」",
        "day_3_discussion_points": "会議の議論点", "day_3_discussion_points_help": "今日の主要なトピック。", "day_3_discussion_points_placeholder": "例: 「Q1の結果をレビュー。レポート形式を議論。ステークホルダーがクエリの複雑さを要求。」",
        "day_3_instructor_feedback": "ステークホルダーからのフィードバック", "day_3_instructor_feedback_help": "「ステークホルダー」からのメモ。", "day_3_instructor_feedback_placeholder": "例: 「素晴らしいパイプライン！レポートの洞察をより明確にしてほしい。JOINやサブクエリを追加できるか？」",
        "day_3_action_items_day4": "4日目のアクションアイテム", "day_3_action_items_day4_help": "明日の目標。", "day_3_action_items_day4_placeholder": "例: 「1. レポートスクリプト最終化。2. 2番目のSQLクエリ追加。3. README完全更新。4. コードクリーンアップ＆コメント。」",
        # Day 4 (Japanese)
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

    all_day_form_keys = [k for lang_dict in TRANSLATIONS.values() for k in lang_dict.keys() if k.startswith("day_") and not k.endswith(("_help", "_tab", "_title", "_placeholder"))]
    for key in set(all_day_form_keys):
        if key not in st.session_state:
            if "status" in key or "readme_" in key or key == "day_4_feature_status": # Checkboxes
                st.session_state[key] = False
            else:
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
    # Add all day-specific fields
    all_day_keys_flat = [k for lang_dict in TRANSLATIONS.values() for k in lang_dict.keys() if k.startswith("day_") and not k.endswith(("_help", "_tab", "_title", "_placeholder"))]
    all_day_keys_unique = sorted(list(set(all_day_keys_flat)))
    for key in all_day_keys_unique:
        data[key] = st.session_state.get(key, "") # Ensure default is empty string
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
        day_prefix = active_day_key.split('_tab')[0]
    except Exception:
        day_prefix = "day_1" # Fallback
    content += f"## {get_translation(lang, active_day_key)}\n"
    # Filter keys more carefully to ensure they belong to the current language and are form fields
    day_specific_keys = [k for k in TRANSLATIONS[lang].keys() if k.startswith(day_prefix) and k != active_day_key and not k.endswith(("_help", "_title", "_placeholder"))]
    for key_id in day_specific_keys:
        label = get_translation(lang, key_id)
        value = st.session_state.get(key_id, "")
        if isinstance(value, bool):
            value = ("Yes" if value else "No") if lang == "en" else ("はい" if value else "いいえ")
        content += f"### {label}\n{value}\n\n"
    content += f"## {get_translation(lang, 'current_research_question')}\n"
    content += f"{st.session_state.get('current_research_question', '')}\n"
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

    SHEET_NAME = "All_Submissions"
    # Define the full list of headers based on get_all_form_data structure
    # This order will be used for writing to the sheet
    expected_headers = list(data_dict.keys()) # Use keys from the passed data_dict

    try:
        spreadsheet_id = st.secrets["gcp_spreadsheet"]["key"]
        sh = gc.open_by_key(spreadsheet_id)

        try:
            worksheet = sh.worksheet(SHEET_NAME)
            # Check if sheet is empty or header is missing
            header_row_values = worksheet.row_values(1) if worksheet.row_count > 0 else []
            if not header_row_values or sorted(header_row_values) != sorted(expected_headers):
                # If headers are missing or don't match, it's safer to clear and rewrite
                # This could happen if the form structure changes.
                # For simplicity in this context, we might assume if sheet exists, headers are okay,
                # or, more robustly, recreate if mismatch.
                # Let's go with ensuring headers are there if sheet is new or was empty/mismatched.
                if not header_row_values or worksheet.row_count <= 1: # Add/Rewrite headers if sheet looks empty/new
                    worksheet.clear() # Clears all values but keeps the sheet
                    worksheet.update([expected_headers]) # Write headers as the first row (list of lists)
                    # st.info(f"Headers written/verified in '{SHEET_NAME}'.") # Removed as requested
        except gspread.WorksheetNotFound:
            worksheet = sh.add_worksheet(title=SHEET_NAME, rows="1", cols=len(expected_headers))
            worksheet.update([expected_headers]) # Write headers as the first row
            # st.info(f"Created new sheet '{SHEET_NAME}' and added headers.") # Removed as requested

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
    keys = [k for k in TRANSLATIONS[lang] if k.startswith(day_prefix) and not k.endswith(("_help", "_tab", "_title", "_placeholder"))]
    for key in keys:
        label = get_translation(lang, key)
        help_text = get_help_text(lang, key)
        placeholder = get_placeholder_text(lang, key)

        if key == day_prefix + "title": continue

        if key == "day_4_readme_checklist_title":
            st.markdown(f"**{label}**"); st.caption(f"*{help_text}*"); continue

        if "feature_status" in key or "readme_" in key:
            st.session_state[key] = st.checkbox(label, value=st.session_state.get(key, False), help=help_text, key=f"widget_{key}")
        elif "link" in key:
            st.session_state[key] = st.text_input(label, value=st.session_state.get(key, ""), placeholder=placeholder, help=help_text, key=f"widget_{key}")
        else:
            st.session_state[key] = st.text_area(label, value=st.session_state.get(key, ""), placeholder=placeholder, help=help_text, height=100, key=f"widget_{key}")

def render_buttons(tab_key, lang):
    # st.info(get_translation(lang, "gsheet_info")) # Removed as requested

    group_num = st.session_state.get('group_number', 'GroupX')
    date_str = str(st.session_state.get('date', 'Date'))
    day_num_str = tab_key.split('_')[1]
    download_filename = f"Capstone_Notes_Group{group_num}_Day{day_num_str}_{date_str}.md"
    download_placeholder = st.empty()

    if st.button(get_translation(lang, "submit_and_download"), key=f"submit_b_{tab_key}"):
        st.session_state.submitted_and_download_ready = False
        form_data = get_all_form_data()
        form_data["MeetingDayFocus"] = tab_key # Add which tab was active during submission

        if save_to_gsheets_new_row(form_data):
            st.success(get_translation(lang, "submission_success"))
            st.session_state.current_download_data = {
                "content": get_student_download_content(tab_key, lang),
                "filename": download_filename }
            st.session_state.submitted_and_download_ready = True
        else:
            st.error(get_translation(lang, "submission_gsheets_error"))

    if st.session_state.submitted_and_download_ready:
        download_placeholder.download_button(
            label=get_translation(lang, "download_student_copy"),
            data=st.session_state.current_download_data.get("content", ""),
            file_name=st.session_state.current_download_data.get("filename", "download.md"),
            mime='text/markdown', key=f"download_btn_{tab_key}")

def main():
    initialize_session_state()
    st.set_page_config(layout="wide", page_title=get_translation(st.session_state.lang, "app_title"))
    st.title(get_translation(st.session_state.lang, "app_title"))
    language_options = {"English": "en", "日本語": "ja"}
    current_lang_display = [k for k, v in language_options.items() if v == st.session_state.lang][0]
    selected_language_display = st.sidebar.selectbox(
        get_translation(st.session_state.lang, "language_select"),
        options=list(language_options.keys()),
        index=list(language_options.keys()).index(current_lang_display))
    new_lang = language_options[selected_language_display]
    if new_lang != st.session_state.lang:
        st.session_state.lang = new_lang
        st.rerun()
    lang = st.session_state.lang
    st.sidebar.header(get_translation(lang, "sidebar_title"))
    st.session_state.group_number = st.sidebar.text_input(get_translation(lang, "group_number"), value=st.session_state.get("group_number",""), help=get_help_text(lang, "group_number"))
    st.session_state.time_slot = st.sidebar.text_input(get_translation(lang, "time_slot"), value=st.session_state.get("time_slot",""), help=get_help_text(lang, "time_slot"))
    st.session_state.date = st.sidebar.date_input(get_translation(lang, "date"), value=st.session_state.get("date", datetime.now().date()), help=get_help_text(lang, "date"))
    st.session_state.project_title = st.sidebar.text_input(get_translation(lang, "project_title"), value=st.session_state.get("project_title",""), help=get_help_text(lang, "project_title"))
    st.session_state.note_taker = st.sidebar.text_input(get_translation(lang, "note_taker"), value=st.session_state.get("note_taker",""), help=get_help_text(lang, "note_taker"))

    tab_keys = ["day_1_tab", "day_2_tab", "day_3_tab", "day_4_tab"]
    tab_titles = [get_translation(lang, key) for key in tab_keys]
    tab1, tab2, tab3, tab4 = st.tabs(tab_titles)
    tabs_content = [ (tab1, "day_1_tab", "day_1_"), (tab2, "day_2_tab", "day_2_"), (tab3, "day_3_tab", "day_3_"), (tab4, "day_4_tab", "day_4_"), ]

    for tab, tab_key, day_prefix in tabs_content:
        with tab:
            st.header(get_translation(lang, tab_key))
            st.info(get_translation(lang, "hint_visibility"))
            if tab_key != "day_4_tab":
                render_day_inputs(lang, day_prefix)
            else:
                keys_d4 = [k for k in TRANSLATIONS[lang] if k.startswith("day_4_") and not k.endswith(("_help", "_tab", "_title", "_placeholder")) and not k.startswith("day_4_readme_")]
                for key in keys_d4:
                    label = get_translation(lang, key)
                    help_text = get_help_text(lang, key)
                    placeholder = get_placeholder_text(lang, key)
                    if "feature_status" in key:
                        st.session_state[key] = st.checkbox(label, value=st.session_state.get(key, False), help=help_text, key=f"widget_{key}")
                    else:
                        st.session_state[key] = st.text_area(label, value=st.session_state.get(key, ""), placeholder=placeholder, help=help_text, height=100, key=f"widget_{key}")
                st.markdown(f"**{get_translation(lang, 'day_4_readme_checklist_title')}**")
                st.caption(f"*{get_help_text(lang, 'day_4_readme_checklist_title')}*")
                readme_keys = [k for k in TRANSLATIONS[lang] if k.startswith("day_4_readme_") and not k.endswith(("_help", "_title", "_placeholder"))]
                for key in readme_keys:
                    st.session_state[key] = st.checkbox(get_translation(lang, key), value=st.session_state.get(key, False), key=f"widget_{key}")

            st.markdown("---")
            st.subheader(get_translation(lang, "current_research_question"))
            st.session_state.current_research_question = st.text_area(
                get_translation(lang, "current_research_question"),
                value=st.session_state.get("current_research_question", ""),
                help=get_help_text(lang, "current_research_question"),
                placeholder=get_help_text(lang, "current_research_question"),
                key=f"research_q_{day_prefix}",
                label_visibility="collapsed" )
            st.markdown("---")
            render_buttons(tab_key, lang)

    # Add the footer note at the end of the main app layout
    st.markdown("---")
    st.markdown(f"**{get_translation(lang, 'important_label')}:** {get_translation(lang, 'footer_submission_reminder')}")

if __name__ == "__main__":
    main()