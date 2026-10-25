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


# ---------- Phân phối Thời Gian (Time & Bimodal Pattern) ----------
st.markdown("---")
st.markdown("### Phân Phối Thời Gian (Time & Chu Kỳ 24 Giờ)")

col_time1, col_time2 = st.columns(2)

with col_time1:
    fig_time = px.histogram(
        df,
        x="Time",
        nbins=96,
        color="Class",
        color_discrete_map={0: COLORS["legit"], 1: COLORS["fraud"]},
        title="Phân Phối Time: Bimodal (2 đỉnh tương ứng 2 ngày)",
        labels={"Time": "Time (giây từ giao dịch đầu tiên)", "count": "Số giao dịch"},
        opacity=0.75,
        barmode="overlay",
    )
    fig_time.update_layout(
        height=400,
        legend_title_text="Class",
    )
    st.plotly_chart(fig_time, use_container_width=True)
    st.caption(
        "💡 **Time là số giây tính từ giao dịch đầu tiên của bộ dữ liệu** (~48 giờ / 2 ngày). "
        "Biểu đồ thể hiện rõ dạng **Bimodal (hai đỉnh)**: Giao dịch tập trung nhiều vào ban ngày "
        "(tạo thành 2 đỉnh của 2 ngày) và giảm rõ rệt vào ban đêm (vùng trũng ở giữa)."
    )

with col_time2:
    if "hour_of_day" in df.columns:
        fig_hour = px.histogram(
            df,
            x="hour_of_day",
            nbins=24,
            color="Class",
            color_discrete_map={0: COLORS["legit"], 1: COLORS["fraud"]},
            title="Phân Phối Theo Chu Kỳ 24 Giờ (hour_of_day)",
            labels={"hour_of_day": "Giờ tương đối (0 - 23)", "count": "Số giao dịch"},
            opacity=0.75,
            barmode="overlay",
        )
        fig_hour.update_layout(
            height=400,
            legend_title_text="Class",
        )
        st.plotly_chart(fig_hour, use_container_width=True)
        st.caption(
            "💡 **Về `hour_of_day`:** Do `Time` bắt đầu từ giao dịch đầu tiên (không nhất thiết là 0h sáng), "
            "`hour_of_day` là giờ tương đối trong chu kỳ 24 giờ. Feature này giúp mô hình "
            "**học được nhịp sinh học / chu kỳ 24 giờ** của người dùng thay vì khẳng định giờ thực tế."
        )


# ---------- Khám phá feature tương tác ----------
st.markdown("---")
st.markdown("### Khám Phá Chi Tiết Từng Feature")

interesting_features = [
    "Amount", "Time", "log_amount", "hour_of_day", "v_magnitude",
    "top_fraud_v_mean", "fraud_score_proxy",
    "V14", "V17", "V12", "V10", "V11", "V4",
]
interesting_features = [f for f in interesting_features if f in df.columns]

feature = st.selectbox("Chọn một feature để phân tích chi tiết:", interesting_features, index=0)

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
        legend_title_text="Class",
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


# ---------- Phát hiện chính (Tính toán động từ dữ liệu) ----------
st.markdown("---")
st.markdown("### Phát Hiện Chính (Được tính trực tiếp từ dữ liệu)")

# Tính toán các chỉ số động từ DataFrame thực tế
fraud_rate = df["Class"].mean() * 100 if "Class" in df.columns else 0.17
fraud_count = int(df["Class"].sum()) if "Class" in df.columns else 0
total_count = len(df)
amount_skew = float(df["Amount"].skew()) if "Amount" in df.columns else 0.0
median_amount = float(df["Amount"].median()) if "Amount" in df.columns else 0.0
max_amount = float(df["Amount"].max()) if "Amount" in df.columns else 0.0
time_hours = float(df["Time"].max() / 3600) if "Time" in df.columns else 48.0

# Lấy top PCA features tương quan âm mạnh nhất với Class
v_cols = [f"V{i}" for i in range(1, 29) if f"V{i}" in df.columns]
if v_cols and "Class" in df.columns:
    top_v_features = (
        df[v_cols + ["Class"]]
        .corr()["Class"]
        .drop("Class")
        .abs()
        .sort_values(ascending=False)
        .head(4)
        .index.tolist()
    )
else:
    top_v_features = ["V17", "V14", "V12", "V10"]

key_findings = [
    {
        "label": "Mất cân bằng",
        "value": f"{fraud_rate:.3f}%",
        "subtext": f"{fraud_count:,} / {total_count:,} ca",
        "color": COLORS["fraud"],
    },
    {
        "label": "Top Features PCA",
        "value": ", ".join(top_v_features),
        "subtext": "Tương quan âm mạnh nhất",
        "color": COLORS["primary"],
    },
    {
        "label": "Amount (Số tiền)",
        "value": f"Lệch phải ({amount_skew:+.1f})",
        "subtext": f"Median ${median_amount:.0f} | Max ${max_amount:,.0f}",
        "color": COLORS["accent"],
    },
    {
        "label": "Time (Thời gian)",
        "value": "Bimodal (2 đỉnh)",
        "subtext": f"2 chu kỳ (~{time_hours:.0f} giờ)",
        "color": COLORS["neutral"],
    },
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
                <div style='font-size: 0.85em; color: #555; font-weight: 500;'>{finding['label']}</div>
                <div style='font-size: 1.2em; font-weight: bold; color: {finding["color"]}; margin: 4px 0;'>{finding['value']}</div>
                <div style='font-size: 0.78em; color: #666;'>{finding['subtext']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


render_footer()
