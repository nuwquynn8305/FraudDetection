"""Trang 3: So sánh model và dự đoán trực tiếp."""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import joblib
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from utils import (
    COLORS,
    load_features,
    load_model_results,
    page_header,
    render_demo_banner,
    render_footer,
)

st.set_page_config(
    page_title="Kết Quả Model",
    page_icon="🤖",
    layout="wide",
)

page_header(
    "Kết Quả Model",
    "",
)
render_demo_banner()

# ---------- Comparison table ----------
results = load_model_results()
# Chỉ sử dụng các models có sẵn trong JSON
order = [key for key in ["baseline", "random_forest", "xgboost_untuned", "xgboost_tuned"] if key in results]
rows = []
for key in order:
    r = results[key]
    rows.append({
        "Model": r["name"],
        "PR-AUC": r["pr_auc"],
        "ROC-AUC": r["roc_auc"],
        "Precision": r["precision"],
        "Recall": r["recall"],
        "F1": r["f1"],
        "Fraud Caught": r["tp"],
        "False Alarms": r["fp"],
        "Fraud Missed": r["fn"],
    })
df_results = pd.DataFrame(rows)

st.markdown("### So Sánh Model")
st.dataframe(
    df_results.style.format({
        "PR-AUC": "{:.4f}",
        "ROC-AUC": "{:.4f}",
        "Precision": "{:.4f}",
        "Recall": "{:.4f}",
        "F1": "{:.4f}",
    }).background_gradient(subset=["PR-AUC", "F1"], cmap="Greens"),
    use_container_width=True,
    hide_index=True,
)


# ---------- Tại sao model này chiến thắng ----------
st.markdown("### Tại Sao XGBoost Chiến Thắng")

# Visual comparison of key metrics
winner = results["xgboost_tuned"]
baseline = results["baseline"]

comparison_data = {
    "Metric": ["PR-AUC", "Precision", "Recall", "F1"],
    "XGBoost": [winner["pr_auc"], winner["precision"], winner["recall"], winner["f1"]],
    "Baseline": [baseline["pr_auc"], baseline["precision"], baseline["recall"], baseline["f1"]],
}

fig = go.Figure()
fig.add_trace(go.Bar(
    name="XGBoost",
    x=comparison_data["Metric"],
    y=comparison_data["XGBoost"],
    marker_color=COLORS["primary"],
))
fig.add_trace(go.Bar(
    name="Baseline",
    x=comparison_data["Metric"],
    y=comparison_data["Baseline"],
    marker_color=COLORS["accent"],
))
fig.update_layout(
    barmode="group",
    title="So Sánh XGBoost vs Baseline",
    height=400,
)
st.plotly_chart(fig, use_container_width=True)

# Key advantages as badges
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Bắt Gian Lận", "+3", "+3 so với RF")
with col2:
    st.metric("Train Time", "2s", "18× nhanh hơn")
with col3:
    st.metric("Báo Động Sai", "+4", "Chấp nhận được")


# ---------- Tầm quan trọng feature ----------
st.markdown("---")
st.markdown("### Feature Hàng Đầu")

fi = pd.DataFrame(results["feature_importance"]).head(15)

fig = go.Figure(go.Bar(
    x=fi["importance"],
    y=fi["feature"],
    orientation="h",
    marker_color=COLORS["primary"],
))
fig.update_layout(
    xaxis_title="Tầm Quan Trọng Feature",
    yaxis={"categoryorder": "total ascending"},
    height=500,
)
st.plotly_chart(fig, use_container_width=True)


# ---------- Confusion matrix ----------
st.markdown("---")
st.markdown("### Confusion Matrix")

winner = results["xgboost_tuned"]
z = [[winner["tn"], winner["fp"]],
     [winner["fn"], winner["tp"]]]

fig = go.Figure(data=go.Heatmap(
    z=z,
    x=["Dự đoán Hợp pháp", "Dự đoán Gian lận"],
    y=["Thực tế Hợp pháp", "Thực tế Gian lận"],
    text=[[f"{v:,}" for v in row] for row in z],
    texttemplate="%{text}",
    textfont={"size": 18},
    colorscale="Blues",
    showscale=False,
))
fig.update_layout(height=400)
st.plotly_chart(fig, use_container_width=True)


# ---------- Thử tự mình ----------
st.markdown("---")
st.markdown("### Dự Đoán Trực Tiếp")

@st.cache_resource
def load_production_model():
    """Thử tải model sản xuất. Trả về None nếu không tồn tại."""
    model_path = Path("models/production_model.pkl")
    if not model_path.exists():
        return None
    return joblib.load(model_path)


model = load_production_model()

if model is None:
    st.info(
        "🎮 **Widget dự đoán tương tác bị ẩn trong chế độ demo.** "
        "Train model sản xuất trước để bật nó: "
        "`python src/models/run_training.py`"
    )
    render_footer()
    st.stop()   # Dừng render trang — mọi thứ dưới đây sẽ không thực thi
df_features = load_features()
feature_cols = [c for c in df_features.columns if c != "Class"]

st.markdown("**Chọn điểm bắt đầu:**")
preset = st.radio(
    "Preset",
    ["Giao dịch hợp pháp ngẫu nhiên", "Giao dịch gian lận ngẫu nhiên", "Giá trị trung vị"],
    horizontal=True,
    label_visibility="collapsed",
)

# Xây dựng giá trị ban đầu từ preset
if preset == "Giao dịch hợp pháp ngẫu nhiên":
    sample = df_features[df_features["Class"] == 0].sample(1, random_state=None).iloc[0]
elif preset == "Giao dịch gian lận ngẫu nhiên":
    sample = df_features[df_features["Class"] == 1].sample(1, random_state=None).iloc[0]
else:
    sample = df_features.median()

# Điều khiển có thể điều chỉnh cho các feature quan trọng nhất
top_features = [f["feature"] for f in results["feature_importance"][:5]]

st.markdown("**Điều chỉnh 5 feature hàng đầu:**")
inputs = {}
cols = st.columns(5)
for i, feature in enumerate(top_features):
    with cols[i]:
        col_min = float(df_features[feature].min())
        col_max = float(df_features[feature].max())
        default = float(sample[feature])
        inputs[feature] = st.slider(
            feature,
            min_value=col_min,
            max_value=col_max,
            value=default,
            key=f"slider_{feature}",
        )

# Build prediction input (use sample values for non-slider features)
prediction_input = pd.DataFrame([sample[feature_cols].to_dict()])
for feature, value in inputs.items():
    prediction_input[feature] = value

# QUAN TRỌNG: sắp xếp lại cột để khớp với thứ tự model được train.
# XGBoost nghiêm ngặt về thứ tự cột và sẽ thất bại nếu không khớp.
if hasattr(model, "feature_names_in_"):
    prediction_input = prediction_input[list(model.feature_names_in_)]

# Dự đoán
proba = model.predict_proba(prediction_input)[0, 1]
pred = int(proba >= 0.5)

# Hiển thị kết quả
col1, col2 = st.columns([1, 2])
with col1:
    if pred == 1:
        st.error(f"### GIAN LẬN\nXác suất: {proba:.2%}")
    else:
        st.success(f"### HỢP PHÁP\nXác suất gian lận: {proba:.2%}")

with col2:
    # Đồng hồ xác suất
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=proba * 100,
        title={"text": "Xác Suất Gian Lận"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": COLORS["fraud"] if pred == 1 else COLORS["legit"]},
            "steps": [
                {"range": [0, 50], "color": "#e8f5e9"},
                {"range": [50, 100], "color": "#ffebee"},
            ],
            "threshold": {
                "line": {"color": "black", "width": 4},
                "thickness": 0.75,
                "value": 50,
            },
        },
        number={"suffix": "%"},
    ))
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)


render_footer()