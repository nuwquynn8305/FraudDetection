"""
Feature engineering cho phát hiện gian lận thẻ tín dụng.

Giới hạn: V1-V28 được ẩn danh bằng PCA — chúng ta không biết ý nghĩa gốc,
nên hầu hết engineering theo domain sử dụng 2 feature có thể diễn giải
(Time và Amount). Các feature V được kết hợp thống kê thay vì
theo ngữ nghĩa.

Chạy từ thư mục gốc dự án với: python src/features/engineering.py
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import pandas as pd

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Các feature hàng đầu theo độ tương đối tuyệt đối với Class, được xác định trong EDA
# (tương quan âm: gian lận thường có giá trị thấp hơn trên các feature này)
TOP_FRAUD_V_FEATURES = ["V17", "V14", "V12", "V10", "V16"]


def create_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Tạo các feature mới để phát hiện gian lận.
    
    Args:
        df: DataFrame gốc với các cột Time, Amount, V1-V28, Class
    
    Returns:
        pd.DataFrame: DataFrame mới với các cột gốc cộng thêm các feature được tạo
    
    Raises:
        KeyError: Nếu các cột cần thiết không tồn tại
    """
    required_cols = ['Time', 'Amount', 'Class'] + [f'V{i}' for i in range(1, 29)]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        logger.error(f"Thiếu các cột cần thiết: {missing_cols}")
        raise KeyError(f"Thiếu các cột cần thiết: {missing_cols}")
    
    df = df.copy()  # Tránh thay đổi DataFrame của người gọi
    logger.info(f"Bắt đầu tạo features cho {len(df)} hàng")

    # =================================================================
    # DANH MỤC 1: CÁC FEATURE THEO DOMAIN (Time và Amount)
    # =================================================================
    # Cột Time của dataset là "giây kể từ giao dịch đầu tiên"
    # kéo dài ~2 ngày. Chúng ta có thể trích xuất pattern theo giờ vì
    # gian lận thường xảy ra vào giờ bất thường khi nạn nhân đang ngủ.

    # Feature 1: hour_of_day
    # TẠI SAO: Trích xuất giờ tương đối theo chu kỳ 24 giờ (Time tính từ giao dịch đầu tiên).
    # Feature này giúp model học được nhịp sinh học / chu kỳ hoạt động 24h
    # (các khoảng cao điểm và thấp điểm giao dịch theo ngày).
    df["hour_of_day"] = (df["Time"] // 3600) % 24

    # Feature 2: is_night
    # TẠI SAO: Cờ nhị phân cho các khoảng giờ thấp điểm tương đối (giờ 0 đến 5)
    # theo chu kỳ 24h, giúp model bắt các giao dịch diễn ra trong vùng trũng hoạt động.
    df["is_night"] = ((df["hour_of_day"] >= 0) &
                      (df["hour_of_day"] < 6)).astype(int)

    # Feature 3: log_amount
    # TẠI SAO: EDA cho thấy Amount bị lệch phải cực độ ($0 đến $25,000
    # với hầu hết giá trị dưới $100). Model tuyến tính và thuật toán dựa trên khoảng cách
    # gặp khó khăn với feature bị lệch. log1p(x) = log(1+x)
    # xử lý số 0 một cách êm đẹp.
    df["log_amount"] = np.log1p(df["Amount"])

    # Feature 4: amount_zero_flag
    # TẠI SAO: Một số lượng đáng ngạc nhiên giao dịch có Amount = $0
    # (xác minh thẻ, kiểm tra pre-auth). Các giao dịch này khác nhau cơ bản
    # so với mua hàng $50 và model cần biết.
    df["amount_zero_flag"] = (df["Amount"] == 0).astype(int)

    # Feature 5: amount_bucket
    # TẠI SAO: Phân loại thành các cấp độ rời rạc (nhỏ/trung bình/lớng/rất lớn)
    # cho các model dựa trên cây điểm chia rõ ràng hơn và bắt được
    # pattern gian lận dựa trên ngưỡng (ví dụ, nhiều giao dịch gian lận
    # tập trung trong các phạm vi tiền cụ thể để tránh bị phát hiện).
    df["amount_bucket"] = pd.cut(
        df["Amount"],
        bins=[-0.01, 1, 10, 100, 1000, np.inf],
        labels=[0, 1, 2, 3, 4],
    ).astype(int)

    # =================================================================
    # DANH MỤC 2: CÁC FEATURE THỐNG KÊ / TỔNG HỢP
    # =================================================================
    '''Vì các feature V là thành phần PCA, chúng ta có thể tóm tắt chúng
    theo thống kê. Giao dịch gian lận có xu hướng là "outliers" trên
    nhiều chiều PCA cùng lúc, các tổng hợp này bắt được điều đó
    mà không cần biết ý nghĩa của từng V.'''

    # Feature 6: v_magnitude
    '''TẠI SAO: Chuẩn L2 (Euclidean) của vector V đo khoảng cách
    một giao dịch nằm xa "trung tâm" của không gian PCA bao nhiêu.
    Giao dịch gian lận được xác định trong EDA có giá trị âm cực đoan trên
    nhiều feature V cùng lúc, nên chúng nên có độ lớn tổng thể lớn.'''
    v_cols = [f"V{i}" for i in range(1, 29)]
    df["v_magnitude"] = np.sqrt((df[v_cols] ** 2).sum(axis=1))

    # Feature 7: v_negative_count
    # TẠI SAO: EDA cho thấy các feature tương quan với gian lận hàng đầu (V10, V12, V14, V17)
    # đều có tương quan ÂM với Class, gian lận nằm ở giá trị thấp hơn.
    # Đếm bao nhiêu feature V là âm cho một hàng cho
    # điểm "giống gian lận" đơn giản.
    df["v_negative_count"] = (df[v_cols] < 0).sum(axis=1)

    # Feature 8: top_fraud_v_mean
    # TẠI SAO: Trung bình của các feature V tương quan nhiều với gian lận nhất.
    # Nếu giao dịch là gian lận, tất cả các feature này có xu hướng rất âm,
    # nên trung bình sẽ rất âm. Một feature kết hợp duy nhất
    # dễ hơn cho model tuyến tính so với 5 feature riêng biệt.
    df["top_fraud_v_mean"] = df[TOP_FRAUD_V_FEATURES].mean(axis=1)

    # Feature 9: top_fraud_v_min
    # TẠI SAO: Đối với gian lận, nhiều feature V đạt giá trị âm cực đoan.
    # Giá trị nhỏ nhất bắt được mức độ cực đoan của feature âm nhất,
    # thường là tín hiệu gian lận mạnh hơn trung bình.
    df["top_fraud_v_min"] = df[TOP_FRAUD_V_FEATURES].min(axis=1)

    # =================================================================
    # DANH MỤC 3: CÁC FEATURE TƯƠNG TÁC
    # =================================================================
    # Các trường hợp hai feature cùng nhau mang nhiều thông tin hơn
    # là từng cái một.

    # Feature 10: amount_v17_interaction  (TƯƠNG TÁC 1)
    # TẠI SAO: V17 là bộ dự đoán gian lận đơn lẻ mạnh nhất. Kết hợp nó
    # với số tiền giao dịch bắt được "V17 cực đoan VÀ số tiền lớn" —
    # giao dịch gian lận giá trị cao rủi ro hơn giao dịch giá trị thấp.
    df["amount_v17_interaction"] = df["log_amount"] * df["V17"]

    # Feature 11: night_amount_ratio  (TƯƠNG TÁC 2)
    # TẠI SAO: Giao dịch lớn vào ban đêm đáng ngờ hơn giao dịch lớn
    # vào ban ngày. Nhân log_amount với is_night
    # triệt tiêu giao dịch ban ngày và khuếch đại giao dịch ban đêm.
    df["night_amount_ratio"] = df["log_amount"] * df["is_night"]

    # Feature 12: fraud_score_proxy  (TƯƠNG TÁC 3)
    # TẠI SAO: Kết hợp các tín hiệu gian lận mạnh nhất thành một tổng hợp.
    # top_fraud_v_mean âm * v_magnitude dương bắt được "outlier
    # cực đoan theo hướng gian lận." Đảo ngược kết quả để số lớn hơn
    # có nghĩa là giống gian lận hơn.
    df["fraud_score_proxy"] = -df["top_fraud_v_mean"] * df["v_magnitude"]

    # Feature 13: v14_v17_interaction  (TƯƠNG TÁC 4)
    # TẠI SAO: V14 và V17 là các feature tương quan với gian lận #1 và #2
    # riêng lẻ. Tích của chúng bắt được trường hợp CẢ HAI đều cực đoan,
    # là tín hiệu mạnh hơn nhiều so với việc chỉ một cái cực đoan.
    df["v14_v17_interaction"] = df["V14"] * df["V17"]

    return df
def select_features(
    df: pd.DataFrame,
    target_column: str = "Class",
    correlation_threshold: float = 0.95,
    variance_threshold_ratio: float = 0.01,
) -> tuple[list[str], pd.DataFrame]:
    """
    Chọn feature bằng cách loại bỏ:
      1. Các feature tương quan cao với feature khác (|corr| > 0.95)
      2. Các feature có phương sai rất thấp (< 1% phương sai trung bình tổng thể)

    Cột target được loại trừ khỏi các kiểm tra này (chúng ta không bao giờ loại target).

    Trả về:
        selected_features: danh sách tên feature được giữ lại
        df_reduced: DataFrame chỉ chứa các feature được chọn + target
    """
    # Tách target — chúng ta không bao giờ muốn loại hoặc sửa nó
    if target_column in df.columns:
        target = df[target_column]
        features_df = df.drop(columns=[target_column])
    else:
        target = None
        features_df = df.copy()

    # Chỉ xem xét các feature số cho kiểm tra phương sai/tương quan
    numeric_df = features_df.select_dtypes(include=[np.number])
    original_features = list(numeric_df.columns)

    logger.info(f"Bắt đầu chọn feature với {len(original_features)} features")
    dropped_features = {}  # feature_name -> lý do bị loại

    # ---------- Kiểm tra 1: Cặp tương quan cao ----------
    logger.info(f"Kiểm tra tương quan > {correlation_threshold}...")
    corr_matrix = numeric_df.corr().abs()

    # Chúng ta chỉ muốn xem mỗi cặp một lần. Lấy tam giác trên của
    # ma trận tương quan (trên đường chéo) để không đếm đôi các cặp
    # như (A, B) và (B, A), và không đánh dấu feature với chính nó.
    upper_triangle = corr_matrix.where(
        np.triu(np.ones(corr_matrix.shape), k=1).astype(bool)
    )

    # Đối với mỗi cột trong tam giác trên, nếu bất kỳ giá trị nào vượt quá
    # ngưỡng, cột đó dư thừa với cột trước đó → loại nó.
    # (Các cột trước là "đầu tiên" chúng ta giữ; các cột sau bị loại.)
    cols_to_drop_corr = [
        col for col in upper_triangle.columns
        if any(upper_triangle[col] > correlation_threshold)
    ]

    if cols_to_drop_corr:
        for col in cols_to_drop_corr:
            # Tìm feature trước nào nó tương quan (để ghi log)
            correlated_with = upper_triangle[col][
                upper_triangle[col] > correlation_threshold
            ].idxmax()
            corr_value = upper_triangle.loc[correlated_with, col]
            reason = (f"corr={corr_value:.3f} với '{correlated_with}' "
                      f"(>{correlation_threshold})")
            dropped_features[col] = reason
            print(f"  Loại '{col}' — {reason}")
    else:
        logger.info("Không tìm thấy feature tương quan cao.")

    # Loại bỏ các bị loại do tương quan cao trước khi kiểm tra phương sai,
    # để không tính phương sai trên các feature đã định loại
    remaining = [c for c in original_features if c not in cols_to_drop_corr]
    numeric_df = numeric_df[remaining]

    # ---------- Kiểm tra 2: Feature phương sai thấp ----------
    logger.info("Kiểm tra feature phương sai thấp...")
    variances = numeric_df.var()
    # Dùng trung vị thay vì trung bình — mạnh với feature ngoại lệ như 'Time'
    # có phương sai lớn hơn các cái khác nhiều bậc.
    median_variance = variances.median()
    threshold = variance_threshold_ratio * median_variance
    logger.info(f"Phương sai trung vị trên các feature: {median_variance:.4f}")
    logger.info(f"Ngưỡng phương sai ({variance_threshold_ratio*100:.0f}% "
                f"của trung vị): {threshold:.4f}")

    cols_to_drop_var = variances[variances < threshold].index.tolist()
    if cols_to_drop_var:
        for col in cols_to_drop_var:
            reason = (f"phương sai={variances[col]:.6f} "
                      f"(dưới ngưỡng {threshold:.4f})")
            dropped_features[col] = reason
            print(f"  Loại '{col}' — {reason}")
    else:
        logger.info("Không tìm thấy feature phương sai thấp.")

    # ---------- Xây dựng danh sách cuối cùng và DataFrame giảm ----------
    selected_features = [
        c for c in original_features if c not in dropped_features
    ]

    # DataFrame giảm: feature được chọn + target (nếu có)
    df_reduced = df[selected_features].copy()
    if target is not None:
        df_reduced[target_column] = target

    # Tóm tắt
    logger.info(f"{'=' * 60}")
    logger.info("TÓM TẮT CHỌN FEATURE")
    logger.info(f"{'=' * 60}")
    logger.info(f"Bắt đầu với: {len(original_features)} features")
    logger.info(f"Đã loại:      {len(dropped_features)}")
    logger.info(f"  - Tương quan cao: {len(cols_to_drop_corr)}")
    logger.info(f"  - Phương sai thấp:     {len(cols_to_drop_var)}")
    logger.info(f"Đã giữ:       {len(selected_features)} features")
    logger.info(f"{'=' * 60}")

    return selected_features, df_reduced

if __name__ == "__main__":
    data_folder = Path("data")
    input_path = data_folder / "cleaned.csv"

    if not input_path.exists():
        print(f"Không tìm thấy dữ liệu đã làm sạch tại {input_path}.")
        print("Chạy src/data/cleaner.py trước.")
    else:
        print(f"Đang tải: {input_path}\n")
        df = pd.read_csv(input_path)
        print(f"Trước: {df.shape[0]:,} hàng × {df.shape[1]} cột")

        df_featured = create_features(df)
        print(f"Sau:  {df_featured.shape[0]:,} hàng × "
              f"{df_featured.shape[1]} cột")

        new_columns = [c for c in df_featured.columns if c not in df.columns]
        print(f"\nĐã tạo {len(new_columns)} feature mới:")
        for col in new_columns:
            print(f"  - {col}")

        # Lưu kết quả cho các bước tiếp theo
        output_path = data_folder / "featured.csv"
        df_featured.to_csv(output_path, index=False)
        print(f"\nĐã lưu dữ liệu có feature tại: {output_path}")

        # Kiểm tra nhanh: có null nào được tạo ra không?
        new_nulls = df_featured[new_columns].isnull().sum().sum()
        if new_nulls > 0:
            print(f"\nCẢNH BÁO: {new_nulls} null được tạo ra bởi engineering.")
        else:
            print("\nKhông có null nào được tạo ra. Engineering thành công.")

        # Hiển thị thống kê tóm tắt cho các feature được tạo
        print("\nTóm tắt các feature được tạo:")
        print(df_featured[new_columns].describe().T[
            ["mean", "std", "min", "max"]
        ].round(3))

        # ---- Bước 2: Chọn feature ----
        print("\n" + "=" * 60)
        print("ĐANG CHẠY CHỌN FEATURE")
        print("=" * 60 + "\n")
        selected, df_selected = select_features(df_featured)

        # Lưu phiên bản được chọn
        selected_path = data_folder / "selected.csv"
        df_selected.to_csv(selected_path, index=False)
        print(f"\nĐã lưu dữ liệu được chọn tại: {selected_path}")
        print(f"Kích thước cuối: {df_selected.shape[0]:,} hàng × "
              f"{df_selected.shape[1]} cột")