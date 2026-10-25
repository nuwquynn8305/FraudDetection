"""
Helper chia sẻ cho app Streamlit — tải dữ liệu với fallback demo,
theming, và widget chung.

Loaders kiểm tra file dữ liệu thực trước. Nếu không tồn tại (điều
xảy ra trên clone mới, trước khi pipeline chạy), dữ liệu demo được
tạo tự động để app luôn hoạt động.
"""

import json
import logging
from pathlib import Path

import pandas as pd
import streamlit as st
from demo_data import (
    generate_demo_features,
    generate_demo_predictions,
    generate_demo_results,
    is_demo_mode,
)

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Centralized color scheme used across all pages
COLORS = {
    "primary": "#1f77b4",
    "fraud":   "#d62728",
    "legit":   "#2ca02c",
    "neutral": "#7f7f7f",
    "accent":  "#ff7f0e",
}


# Real data file paths
FEATURES_PATH    = Path("data") / "features.csv"
PREDICTIONS_PATH = Path("data") / "predictions.csv"
RESULTS_PATH     = Path("data") / "model_results.json"


@st.cache_data
def load_features() -> pd.DataFrame:
    """Tải dataset feature, hoặc tạo phiên bản demo nếu thiếu.
    
    Returns:
        pd.DataFrame: Dataset feature
    
    Raises:
        Exception: Nếu cả file thực và demo generation đều thất bại
    """
    try:
        if FEATURES_PATH.exists():
            logger.info(f"Đang tải features từ {FEATURES_PATH}")
            return pd.read_csv(FEATURES_PATH)
        logger.warning("File features không tồn tại, đang dùng demo data")
        return generate_demo_features()
    except Exception as e:
        logger.error(f"Lỗi khi tải features: {e}")
        st.error(f"Không thể tải dữ liệu features: {e!s}")
        raise


@st.cache_data
def load_predictions() -> pd.DataFrame:
    """Tải dự đoán test, hoặc tạo phiên bản demo nếu thiếu.
    
    Returns:
        pd.DataFrame: Dataset dự đoán
    
    Raises:
        Exception: Nếu cả file thực và demo generation đều thất bại
    """
    try:
        if PREDICTIONS_PATH.exists():
            logger.info(f"Đang tải predictions từ {PREDICTIONS_PATH}")
            return pd.read_csv(PREDICTIONS_PATH)
        logger.warning("File predictions không tồn tại, đang dùng demo data")
        features = load_features()
        return generate_demo_predictions(features)
    except Exception as e:
        logger.error(f"Lỗi khi tải predictions: {e}")
        st.error(f"Không thể tải dữ liệu predictions: {e!s}")
        raise


@st.cache_data
def load_model_results() -> dict:
    """Tải metric so sánh model, hoặc tạo kết quả demo nếu thiếu.
    
    Returns:
        Dict: Dictionary chứa metrics của các model
    
    Raises:
        Exception: Nếu cả file thực và demo generation đều thất bại
    """
    try:
        if RESULTS_PATH.exists():
            logger.info(f"Đang tải model results từ {RESULTS_PATH}")
            with open(RESULTS_PATH, encoding='utf-8') as f:
                return json.load(f)
        logger.warning("File model results không tồn tại, đang dùng demo data")
        return generate_demo_results()
    except json.JSONDecodeError as e:
        logger.error(f"Lỗi JSON khi đọc model results: {e}")
        st.error(f"File model results bị hỏng: {e!s}")
        raise
    except Exception as e:
        logger.error(f"Lỗi khi tải model results: {e}")
        st.error(f"Không thể tải model results: {e!s}")
        raise


def render_demo_banner():
    """
    Hiển thị banner cảnh báo ở đầu trang khi chạy trên dữ liệu demo.
    Ẩn khi pipeline thực sự đã chạy.
    """
    if is_demo_mode():
        st.warning(
            "*App được triển khai này chạy trên dataset tổng hợp 10,000 hàng."
            "vì dataset Kaggle gốc 283K hàng "
            "không được bao gồm trong repo này. **Model metrics, bảng "
            "so sánh và widget dự đoán trực tiếp đều sử dụng model "
            "XGBoost đã train thực sự**. Để có trải nghiệm đầy đủ với dữ liệu EDA thực, "
            "clone repo và chạy pipeline (xem README)."
        )


def render_footer():
    """Hiển thị footer nhất quán trên mọi trang."""
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray; font-size: 0.85em;'>"
        "Xây dựng với Python, scikit-learn, XGBoost, MLflow, và Streamlit"
        "</div>",
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str = ""):
    """Header trang nhất quán cho mọi trang."""
    st.markdown(f"# {title}")
    if subtitle:
        st.markdown(
            f"<p style='color: gray; font-size: 1.1em;'>{subtitle}</p>",
            unsafe_allow_html=True,
        )
    st.markdown("---")