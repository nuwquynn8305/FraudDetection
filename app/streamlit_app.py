"""
Portfolio Phát Hiện Gian Lận Thẻ Tín Dụng
Trang chính (Tổng quan dự án).
"""

import streamlit as st
from utils import (
    COLORS,
    load_features,
    load_model_results,
    render_demo_banner,
    render_footer,
)

# ---------- Cấu hình trang ----------
st.set_page_config(
    page_title="Portfolio Phát Hiện Gian Lận",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------- Thương hiệu sidebar ----------
with st.sidebar:
    st.markdown("# Phát Hiện Gian Lận")
    st.markdown("*Dự án portfolio ML end-to-end*")
    st.markdown("---")
    st.markdown(
        "**Stack:** Python, scikit-learn, XGBoost, MLflow, Streamlit"
    )

render_demo_banner()
# ---------- Phần hero ----------
st.markdown(
    """
    <div style="
        padding: 1rem 0 0.5rem 0;
        text-align: center;
    ">
        <h1 style="font-size: 2.5em; margin-bottom: 0.1em;">
            💳 Phát Hiện Gian Lận
        </h1>
    </div>
    """,
    unsafe_allow_html=True,
)




# ---------- Thẻ KPI ----------
results = load_model_results()
features_df = load_features()

baseline_pr = results["baseline"]["pr_auc"]
winner_pr = results["xgboost_tuned"]["pr_auc"]
improvement = ((winner_pr - baseline_pr) / baseline_pr) * 100

# KPI cards
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(
        label="Giao Dịch",
        value=f"{len(features_df):,}",
    )
with col2:
    n_engineered = sum(1 for c in features_df.columns if c not in [
        "Time", "Amount", "Class"
    ] and not c.startswith("V"))
    st.metric(
        label="Feature",
        value=f"{n_engineered}",
    )
with col3:
    st.metric(
        label="PR-AUC",
        value=f"{winner_pr:.3f}",
    )
with col4:
    st.metric(
        label="Cải Thiện",
        value=f"+{improvement:.0f}%",
    )

# Thêm chart cho class distribution
import plotly.graph_objects as go

class_counts = features_df["Class"].value_counts()
fig_pie = go.Figure(data=[go.Pie(
    labels=['Hợp pháp', 'Gian lận'],
    values=[class_counts[0], class_counts[1]],
    hole=0.4,
    marker={"colors": [COLORS["legit"], COLORS["fraud"]]}
)])
fig_pie.update_layout(
    title="Phân Phối Giao Dịch",
    height=300,
    margin={"l": 0, "r": 0, "t": 30, "b": 0}
)

st.plotly_chart(fig_pie, use_container_width=True)


# ---------- Model Performance Chart ----------
winner = results["xgboost_tuned"]

# Confusion Matrix visualization
cm_data = [[winner["tn"], winner["fp"]], [winner["fn"], winner["tp"]]]
fig_cm = go.Figure(data=go.Heatmap(
    z=cm_data,
    x=['Dự đoán Hợp pháp', 'Dự đoán Gian lận'],
    y=['Thực tế Hợp pháp', 'Thực tế Gian lận'],
    colorscale='RdYlGn',
    text=[[f"{winner['tn']:,}", f"{winner['fp']:,}"], 
          [f"{winner['fn']:,}", f"{winner['tp']:,}"]],
    texttemplate="%{text}",
    textfont={"size": 14},
    colorbar={"title": "Số lượng"}
))
fig_cm.update_layout(
    title="Confusion Matrix",
    height=350,
    margin={"l": 80, "r": 20, "t": 40, "b": 20}
)
st.plotly_chart(fig_cm, use_container_width=True)

# Metrics bar chart
metrics = ['Precision', 'Recall', 'F1', 'PR-AUC']
values = [winner['precision'], winner['recall'], winner['f1'], winner['pr_auc']]

fig_metrics = go.Figure(data=[go.Bar(
    x=metrics,
    y=values,
    marker_color=[COLORS['primary'], COLORS['accent'], COLORS['fraud'], COLORS['legit']],
    text=[f"{v:.2%}" if v < 1 else f"{v:.3f}" for v in values],
    textposition='outside',
)])
fig_metrics.update_layout(
    title="Metrics Model",
    yaxis={"range": [0, 1.1]},
    height=300,
    margin={"l": 0, "r": 0, "t": 30, "b": 0}
)
st.plotly_chart(fig_metrics, use_container_width=True)






render_footer()