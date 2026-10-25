"""Trang 4: Câu chuyện xây dựng."""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import streamlit as st
from utils import page_header, render_demo_banner, render_footer

st.set_page_config(
    page_title="Tôi Đã Xây Dựng Như Thế Này",
    page_icon="🛠️",
    layout="wide",
)

page_header(
    "Tôi Đã Xây Dựng Như Thế Này",
    "",
)
render_demo_banner()

# ---------- Kiến trúc ----------
st.markdown("### Kiến Trúc")

st.graphviz_chart("""
digraph {
    rankdir=LR;
    node [shape=box, style="rounded,filled", fillcolor="#e3f2fd",
          fontname="Helvetica", fontsize=12];
    edge [fontname="Helvetica", fontsize=10];

    Raw [label="Raw CSV\\n284K transactions", fillcolor="#fff3e0"];
    QG  [label="Quality Gate\\n5 automated checks"];
    Clean [label="Cleaner\\nDedupe + dtypes"];
    EDA [label="EDA Notebook\\n7 sections"];
    FE  [label="Feature Engineering\\n13 new features"];
    FS  [label="Feature Selection\\nVariance + correlation"];
    Train [label="Model Training\\n4 candidates"];
    Tune [label="Optuna Tuning\\n30 trials, 5-fold CV"];
    MLflow [label="MLflow Tracking", fillcolor="#f3e5f5"];
    Model [label="production_model.pkl", fillcolor="#c8e6c9"];
    App [label="Streamlit App", fillcolor="#c8e6c9"];

    Raw -> QG -> Clean -> EDA;
    Clean -> FE -> FS -> Train -> Tune -> Model -> App;
    Train -> MLflow;
    Tune -> MLflow;
}
""")


# ---------- Timeline ----------
st.markdown("---")
st.markdown("### Quá Trình Xây Dựng")

timeline = [
    ("📁", "Thiết lập", "Cấu trúc + Git"),
    ("🔧", "Pipeline", "Quality Gate + Cleaner"),
    ("📊", "EDA", "7 sections notebook"),
    ("⚙️", "Feature Eng", "13 features mới"),
    ("🤖", "Modeling", "4 candidates"),
    ("🎯", "Tuning", "Optuna 30 trials"),
    ("🚀", "Triển khai", "Streamlit App"),
]

cols = st.columns(7)
for i, (icon, title, desc) in enumerate(timeline):
    with cols[i]:
        st.markdown(
            f"""
            <div style='
                text-align: center;
                padding: 1rem;
                background: #f5f5f5;
                border-radius: 8px;
                border: 2px solid #ddd;
            '>
                <div style='font-size: 2em;'>{icon}</div>
                <div style='font-weight: bold; margin-top: 0.5rem;'>{title}</div>
                <div style='font-size: 0.8em; color: #666;'>{desc}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ---------- Quyết định chính ----------
st.markdown("---")
st.markdown("### Quyết Định Chính")

decisions = [
    {"icon": "📊", "title": "PR-AUC", "desc": "Metric cho imbalanced data"},
    {"icon": "🎯", "title": "Stratified", "desc": "Giữ tỷ lệ class"},
    {"icon": "⚖️", "title": "Class Weight", "desc": "Cân bằng loss function"},
    {"icon": "🚀", "title": "XGBoost", "desc": "18× nhanh hơn RF"},
    {"icon": "💡", "title": "Bài học", "desc": "Dùng median thay mean"},
]

cols = st.columns(5)
for i, decision in enumerate(decisions):
    with cols[i]:
        st.markdown(
            f"""
            <div style='
                text-align: center;
                padding: 1rem;
                background: #fff3e0;
                border-radius: 8px;
                border: 2px solid #ff9800;
            '>
                <div style='font-size: 2em;'>{decision['icon']}</div>
                <div style='font-weight: bold; margin-top: 0.5rem;'>{decision['title']}</div>
                <div style='font-size: 0.8em; color: #666;'>{decision['desc']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


render_footer()