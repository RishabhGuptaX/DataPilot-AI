import os
import sys

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
import streamlit as st
import pandas as pd

from app.data.loader import (
    load_dataset,
    validate_dataset,
)

from app.data.profiler import (
    get_dataset_overview,
    get_column_profile,
    get_numeric_statistics,
)

from app.data.cleaner import (
    generate_cleaning_report,
    clean_dataset,
)

from app.agents.cleaning_agent import (
    generate_cleaning_recommendations,
)

from app.agents.analyst_agent import (
    generate_analysis_plan,
)

from app.analysis.statistics import (
    execute_analysis_plan,
)

from app.analysis.visualization import (
    create_visualization,
)

from app.data.validator import (
    validate_analysis_plan,
)

from app.core.conversation import (
    initialize_conversation,
    add_message,
    clear_conversation,
    save_last_analysis,
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="DataPilot AI",
    page_icon="📊",
    layout="wide",
)


# ============================================================
# INITIALIZE CONVERSATION
# ============================================================

initialize_conversation(
    st.session_state
)


# ============================================================
# HEADER
# ============================================================

st.title(
    "📊 DataPilot AI"
)

st.subheader(
    "AI-Powered Data Analysis & Cleaning Copilot"
)

st.write(
    "Upload a dataset, clean it, analyze it "
    "and ask follow-up questions naturally."
)

st.divider()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header(
        "💬 Conversation"
    )

    conversation_count = len(
        st.session_state.conversation
    )

    st.metric(
        "Messages",
        conversation_count,
    )


    if st.button(
        "🗑️ Clear Conversation",
        use_container_width=True,
    ):

        clear_conversation(
            st.session_state
        )

        st.rerun()


    st.divider()


    st.caption(
        "DataPilot remembers recent questions "
        "and analysis context during this session."
    )


# ============================================================
# FILE UPLOAD
# ============================================================

uploaded_file = st.file_uploader(
    "📂 Upload your dataset",
    type=[
        "csv",
        "xlsx",
        "xls",
    ],
)


# ============================================================
# MAIN APPLICATION
# ============================================================

if uploaded_file:

    try:

        # ====================================================
        # LOAD DATASET
        # ====================================================

        df = load_dataset(
            uploaded_file
        )

        validate_dataset(
            df
        )


        st.success(
            f"✅ Successfully loaded: "
            f"{uploaded_file.name}"
        )


        st.divider()


        # ====================================================
        # DATASET OVERVIEW
        # ====================================================

        st.header(
            "📋 Dataset Overview"
        )


        overview = (
            get_dataset_overview(
                df
            )
        )


        col1, col2, col3, col4 = (
            st.columns(4)
        )


        with col1:

            st.metric(
                "Rows",
                f"{overview['rows']:,}",
            )


        with col2:

            st.metric(
                "Columns",
                overview["columns"],
            )


        with col3:

            st.metric(
                "Missing %",
                f"{overview['missing_percentage']}%",
            )


        with col4:

            st.metric(
                "Duplicate Rows",
                f"{overview['duplicate_rows']:,}",
            )


        st.divider()


        # ====================================================
        # DATA PREVIEW
        # ====================================================

        st.header(
            "👀 Dataset Preview"
        )


        st.dataframe(
            df.head(100),
            use_container_width=True,
            hide_index=True,
        )


        st.divider()


        # ====================================================
        # COLUMN PROFILE
        # ====================================================

        st.header(
            "🔍 Column Profile"
        )


        column_profile = (
            get_column_profile(
                df
            )
        )


        st.dataframe(
            column_profile,
            use_container_width=True,
            hide_index=True,
        )


        st.divider()


        # ====================================================
        # NUMERICAL STATISTICS
        # ====================================================

        st.header(
            "📈 Numerical Statistics"
        )


        numeric_stats = (
            get_numeric_statistics(
                df
            )
        )


        if numeric_stats.empty:

            st.info(
                "No numerical columns found."
            )

        else:

            st.dataframe(
                numeric_stats,
                use_container_width=True,
                hide_index=True,
            )


        st.divider()


        # ====================================================
        # DATA QUALITY
        # ====================================================

        st.header(
            "🧹 Data Quality"
        )


        cleaning_report = (
            generate_cleaning_report(
                df
            )
        )


        # ====================================================
        # MISSING VALUES
        # ====================================================

        st.subheader(
            "⚠️ Missing Values"
        )


        missing_values = (
            cleaning_report[
                "missing_values"
            ]
        )


        if missing_values.empty:

            st.success(
                "✅ No missing values detected."
            )

        else:

            st.warning(
                f"⚠️ Missing values found in "
                f"{len(missing_values)} column(s)."
            )

            st.dataframe(
                missing_values,
                use_container_width=True,
                hide_index=True,
            )


        # ====================================================
        # DUPLICATES
        # ====================================================

        st.subheader(
            "🔁 Duplicate Rows"
        )


        duplicate_rows = (
            cleaning_report[
                "duplicate_rows"
            ]
        )


        if duplicate_rows == 0:

            st.success(
                "✅ No duplicate rows detected."
            )

        else:

            st.warning(
                f"⚠️ {duplicate_rows:,} "
                f"duplicate rows detected."
            )


        # ====================================================
        # OUTLIERS
        # ====================================================

        st.subheader(
            "📊 Potential Numerical Outliers"
        )


        outliers = (
            cleaning_report[
                "outliers"
            ]
        )


        if outliers.empty:

            st.success(
                "✅ No potential numerical "
                "outliers detected."
            )

        else:

            st.warning(
                "⚠️ Potential numerical "
                "outliers detected."
            )

            st.dataframe(
                outliers,
                use_container_width=True,
                hide_index=True,
            )


        st.divider()


        # ====================================================
        # AI CLEANING RECOMMENDATIONS
        # ====================================================

        st.header(
            "🤖 AI Cleaning Recommendations"
        )


        if st.button(
            "✨ Generate Cleaning Recommendations",
            type="primary",
        ):

            with st.spinner(
                "🤖 AI is analyzing dataset quality..."
            ):

                try:

                    recommendations = (
                        generate_cleaning_recommendations(
                            cleaning_report
                        )
                    )

                    st.success(
                        "✅ AI analysis completed."
                    )

                    st.markdown(
                        recommendations
                    )

                except Exception as error:

                    st.error(
                        "❌ AI analysis failed."
                    )

                    st.exception(
                        error
                    )


        st.divider()


        # ====================================================
        # DATA CLEANING
        # ====================================================

        st.header(
            "🛠️ Clean Dataset"
        )


        remove_duplicates_option = (
            st.checkbox(
                "🔁 Remove duplicate rows",
                value=(
                    duplicate_rows > 0
                ),
            )
        )


        fill_missing_option = (
            st.checkbox(
                "⚠️ Fill missing values",
                value=(
                    not missing_values.empty
                ),
            )
        )


        remove_outliers_option = (
            st.checkbox(
                "📊 Remove numerical outliers",
                value=False,
            )
        )


        st.info(
            "Numerical missing values use the median. "
            "Categorical missing values use the mode."
        )


        if st.button(
            "🔍 Preview Cleaning"
        ):

            preview_df = clean_dataset(
                df,
                remove_duplicates=(
                    remove_duplicates_option
                ),
                fill_missing=(
                    fill_missing_option
                ),
                remove_outlier_rows=(
                    remove_outliers_option
                ),
            )


            st.subheader(
                "📋 Cleaning Preview"
            )


            preview_col1, preview_col2, preview_col3 = (
                st.columns(3)
            )


            with preview_col1:

                st.metric(
                    "Original Rows",
                    f"{len(df):,}",
                )


            with preview_col2:

                st.metric(
                    "Cleaned Rows",
                    f"{len(preview_df):,}",
                )


            with preview_col3:

                st.metric(
                    "Rows Removed",
                    f"{len(df) - len(preview_df):,}",
                )


            st.dataframe(
                preview_df.head(100),
                use_container_width=True,
                hide_index=True,
            )


        if st.button(
            "🧹 Apply Cleaning",
            type="primary",
        ):

            cleaned_df = clean_dataset(
                df,
                remove_duplicates=(
                    remove_duplicates_option
                ),
                fill_missing=(
                    fill_missing_option
                ),
                remove_outlier_rows=(
                    remove_outliers_option
                ),
            )


            st.success(
                "✅ Dataset cleaned successfully!"
            )


            st.metric(
                "Rows Removed",
                f"{len(df) - len(cleaned_df):,}",
            )


            st.dataframe(
                cleaned_df.head(100),
                use_container_width=True,
                hide_index=True,
            )


            csv_data = (
                cleaned_df
                .to_csv(
                    index=False
                )
                .encode("utf-8")
            )


            st.download_button(
                "⬇️ Download Cleaned CSV",
                data=csv_data,
                file_name="datapilot_cleaned.csv",
                mime="text/csv",
            )


        st.divider()


        # ====================================================
        # ASK DATAPILOT
        # ====================================================

        st.header(
            "🤖 Ask DataPilot"
        )


        st.write(
            "Ask questions naturally. "
            "DataPilot remembers the recent conversation."
        )


        # ====================================================
        # SHOW CONVERSATION
        # ====================================================

        if st.session_state.conversation:

            st.subheader(
                "💬 Conversation"
            )


            for message in (
                st.session_state.conversation
            ):

                role = message[
                    "role"
                ]

                content = message[
                    "content"
                ]


                if role == "user":

                    with st.chat_message(
                        "user"
                    ):

                        st.write(
                            content
                        )


                else:

                    with st.chat_message(
                        "assistant"
                    ):

                        st.write(
                            content
                        )


        # ====================================================
        # QUESTION INPUT
        # ====================================================

        question = st.text_input(
            "💬 Ask a question",
            placeholder=(
                "Example: Which companies "
                "have the most jobs?"
            ),
        )


        if st.button(
            "🔎 Analyze Dataset",
            type="primary",
        ):

            if not question.strip():

                st.warning(
                    "⚠️ Please enter a question."
                )

            else:

                with st.spinner(
                    "🤖 DataPilot is thinking..."
                ):

                    try:

                        # ------------------------------------
                        # SAVE USER MESSAGE
                        # ------------------------------------

                        add_message(
                            st.session_state,
                            "user",
                            question,
                        )


                        # ------------------------------------
                        # GENERATE CONTEXT-AWARE PLAN
                        # ------------------------------------

                        plan = (
                            generate_analysis_plan(
                                df,
                                question,
                                conversation=(
                                    st.session_state
                                    .conversation
                                ),
                                last_plan=(
                                    st.session_state
                                    .last_plan
                                ),
                            )
                        )


                        # ------------------------------------
                        # VALIDATE
                        # ------------------------------------

                        is_valid, validation_message = (
                            validate_analysis_plan(
                                plan,
                                df,
                            )
                        )


                        if not is_valid:

                            st.error(
                                f"❌ {validation_message}"
                            )

                        else:

                            # --------------------------------
                            # EXECUTE
                            # --------------------------------

                            result = (
                                execute_analysis_plan(
                                    df,
                                    plan,
                                )
                            )


                            # --------------------------------
                            # SAVE CONTEXT
                            # --------------------------------

                            save_last_analysis(
                                st.session_state,
                                question,
                                plan,
                                result,
                            )


                            # --------------------------------
                            # ASSISTANT MESSAGE
                            # --------------------------------

                            if isinstance(
                                result,
                                pd.DataFrame,
                            ):

                                assistant_text = (
                                    "I analyzed the dataset "
                                    "and generated the result "
                                    "shown below."
                                )

                            elif isinstance(
                                result,
                                pd.Series,
                            ):

                                assistant_text = (
                                    "I analyzed the dataset "
                                    "and generated the "
                                    "requested summary."
                                )

                            else:

                                assistant_text = (
                                    f"The answer is "
                                    f"{result}."
                                )


                            add_message(
                                st.session_state,
                                "assistant",
                                assistant_text,
                                plan=plan,
                            )


                            st.success(
                                "✅ Analysis completed."
                            )


                            # --------------------------------
                            # RESULT
                            # --------------------------------

                            st.subheader(
                                "💡 Result"
                            )


                            if isinstance(
                                result,
                                pd.DataFrame,
                            ):

                                st.dataframe(
                                    result,
                                    use_container_width=True,
                                    hide_index=True,
                                )


                            elif isinstance(
                                result,
                                pd.Series,
                            ):

                                st.dataframe(
                                    result.to_frame(),
                                    use_container_width=True,
                                    hide_index=True,
                                )


                            else:

                                st.metric(
                                    "Answer",
                                    str(result),
                                )


                            # --------------------------------
                            # CHART
                            # --------------------------------

                            if plan.get(
                                "chart"
                            ):

                                st.subheader(
                                    "📊 Visualization"
                                )


                                try:

                                    figure = (
                                        create_visualization(
                                            result,
                                            plan,
                                        )
                                    )


                                    if figure is not None:

                                        st.plotly_chart(
                                            figure,
                                            use_container_width=True,
                                        )

                                    else:

                                        st.info(
                                            "No suitable "
                                            "visualization "
                                            "was generated."
                                        )


                                except Exception as chart_error:

                                    st.warning(
                                        "⚠️ Chart generation "
                                        "failed."
                                    )

                                    st.caption(
                                        str(
                                            chart_error
                                        )
                                    )


                            # --------------------------------
                            # ANALYSIS PLAN
                            # --------------------------------

                            with st.expander(
                                "🔧 View Analysis Plan"
                            ):

                                st.json(
                                    plan
                                )


                    except Exception as error:

                        st.error(
                            "❌ Analysis failed."
                        )

                        st.exception(
                            error
                        )


        st.divider()


        # ====================================================
        # DATASET SUMMARY
        # ====================================================

        st.header(
            "📊 Dataset Summary"
        )


        numerical_count = len(
            df.select_dtypes(
                include=["number"]
            ).columns
        )


        categorical_count = len(
            df.select_dtypes(
                include=[
                    "object",
                    "category",
                    "bool",
                ]
            ).columns
        )


        summary_col1, summary_col2 = (
            st.columns(2)
        )


        with summary_col1:

            st.subheader(
                "Dataset"
            )

            st.write(
                f"**Rows:** "
                f"{df.shape[0]:,}"
            )

            st.write(
                f"**Columns:** "
                f"{df.shape[1]:,}"
            )

            st.write(
                f"**Numerical Columns:** "
                f"{numerical_count}"
            )

            st.write(
                f"**Categorical Columns:** "
                f"{categorical_count}"
            )


        with summary_col2:

            st.subheader(
                "Data Quality"
            )

            st.write(
                f"**Missing Cells:** "
                f"{overview['missing_cells']:,}"
            )

            st.write(
                f"**Duplicate Rows:** "
                f"{overview['duplicate_rows']:,}"
            )

            st.write(
                f"**Missing Percentage:** "
                f"{overview['missing_percentage']}%"
            )


    except Exception as error:

        st.error(
            "❌ Unable to process the dataset."
        )

        st.exception(
            error
        )


# ============================================================
# NO DATASET
# ============================================================

else:

    st.info(
        "👆 Upload a CSV or Excel dataset "
        "above to get started."
    )


    st.markdown(
        """
        ## 🚀 DataPilot AI

        ### 📊 Dataset Profiling
        - Dataset dimensions
        - Data types
        - Unique values
        - Missing values
        - Numerical statistics

        ### 🧹 Data Cleaning
        - Missing-value detection
        - Duplicate detection
        - Outlier detection
        - Automated cleaning
        - Cleaned CSV download

        ### 🤖 AI Cleaning Copilot
        - Data-quality explanations
        - Cleaning recommendations

        ### 💬 Conversational Data Analyst
        - Natural-language questions
        - Structured AI analysis plans
        - Pandas analysis
        - Interactive visualizations
        - Follow-up questions
        - Conversation memory
        """
    )
