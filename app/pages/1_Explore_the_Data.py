"""Trang 2: Khám phá dữ liệu tương tác."""

import sys
from pathlib import Path

# Add parent folder to path so we can import utils
sys.path.append(str(Path(__file__).parent.parent))

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils import COLORS, load_features, page_header, render_demo_banner, render_footer


st.set_page_config(
    page_title="Khám Phá Dữ Liệu",
    page_icon="📊",
    layout="wide",
)

page_header(
    "Khám Phá Dữ Liệu",
    "",
)
render_demo_banner()
df = load_features()

# ---------- Thống kê nhanh ----------
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Tổng Giao Dịch", f"{len(df):,}")
with col2:
    st.metric("Trường Hợp Gian Lận", f"{int(df['Class'].sum()):,}")
with col3:
    st.metric("Tỷ Lệ Gian Lận", f"{df['Class'].mean() * 100:.3f}%")

st.markdown("---")


# ---------- Phân phối target ----------
st.markdown("### Phân Phối Target")

col1, col2 = st.columns(2)

with col1:
    class_counts = df["Class"].value_counts().sort_index()
    fig = go.Figure(data=[
        go.Bar(
            x=["Hợp pháp", "Gian lận"],
            y=class_counts.values,
            marker_color=[COLORS["legit"], COLORS["fraud"]],
            text=class_counts.values,
            textposition="auto",
        )
    ])
    fig.update_layout(
        title="Phân Phối Class (Tỷ lệ tuyến tính)",
        yaxis_title="Số lượng",
        height=400,
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = go.Figure(data=[
        go.Bar(
            x=["Hợp pháp", "Gian lận"],
            y=class_counts.values,
            marker_color=[COLORS["legit"], COLORS["fraud"]],
            text=class_counts.values,
            textposition="auto",
        )
    ])
    fig.update_layout(
        title="Phân Phối Class (Tỷ lệ log)",
        yaxis_title="Số lượng (log)",
        yaxis_type="log",
        height=400,
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)


# ---------- Khám phá feature tương tác ----------
st.markdown("---")
st.markdown("### Khám Phá Feature")

interesting_features = [
    "Amount", "Time", "log_amount", "hour_of_day", "v_magnitude",
    "top_fraud_v_mean", "fraud_score_proxy",
    "V14", "V17", "V12", "V10", "V11", "V4",
]
interesting_features = [f for f in interesting_features if f in df.columns]

feature = st.selectbox("Chọn một feature:", interesting_features, index=0)

col1, col2 = st.columns(2)
with col1:
    # Histogram colored by class
    fig = px.histogram(
        df, x=feature, color="Class",
        color_discrete_map={0: COLORS["legit"], 1: COLORS["fraud"]},
        nbins=60, barmode="overlay", opacity=0.7,
    )
    fig.update_layout(
        title=f"Phân Phối {feature} Theo Class",
        height=400,
        legend_title_text="",
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Box plot by class
    fig = px.box(
        df, x="Class", y=feature,
        color="Class",
        color_discrete_map={0: COLORS["legit"], 1: COLORS["fraud"]},
    )
    fig.update_layout(
        title=f"So Sánh {feature}: Hợp Pháp vs Gian Lận",
        height=400,
        showlegend=False,
        xaxis_title="Class (0=Hợp pháp, 1=Gian lận)",
    )
    st.plotly_chart(fig, use_container_width=True)


# ---------- Heatmap tương quan hàng đầu ----------
st.markdown("---")
st.markdown("### Heatmap Tương Quan")

# Get the top 15 features by absolute correlation with Class
top_features = (
    df.corr()["Class"]
    .drop("Class")
    .abs()
    .sort_values(ascending=False)
    .head(15)
    .index.tolist()
)
top_features.append("Class")  # Include the target

# Build smaller correlation matrix
top_corr = df[top_features].corr()

fig = px.imshow(
    top_corr,
    color_continuous_scale="RdBu_r",
    aspect="auto",
    zmin=-1, zmax=1,
    text_auto=".2f",   # Show numbers inside each cell
    labels={"color": "Correlation"},
)
fig.update_layout(
    height=600,
    title="Tương Quan Giữa 15 Feature Dự Đoán Gian Lận Hàng Đầu",
)
st.plotly_chart(fig, use_container_width=True)


# ---------- Phát hiện chính ----------
st.markdown("---")
st.markdown("### Phát Hiện Chính")

# Biến info boxes thành visual badges
key_findings = [
    {"label": "Mất cân bằng", "value": "0.17%", "color": COLORS["fraud"]},
    {"label": "Top Features", "value": "V14, V17, V12, V10", "color": COLORS["primary"]},
    {"label": "Amount", "value": "Lệch phải", "color": COLORS["accent"]},
    {"label": "Time", "value": "Bimodal", "color": COLORS["neutral"]},
]

cols = st.columns(4)
for i, finding in enumerate(key_findings):
    with cols[i]:
        st.markdown(
            f"""
            <div style='
                background: {finding["color"]}20;
                padding: 1rem;
                border-radius: 8px;
                text-align: center;
                border: 2px solid {finding["color"]};
            '>
                <div style='font-size: 0.8em; color: #666;'>{finding['label']}</div>
                <div style='font-size: 1.2em; font-weight: bold; color: {finding["color"]};'>{finding['value']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


render_footer()