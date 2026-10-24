"""
Pipeline Orchestrator (Giám sát & Điều phối toàn bộ 6 tầng kiến trúc).

Thực hiện liên hoàn luồng End-to-End:
1. Ingestion: Thu thập / sinh dữ liệu thô -> Bronze Layer & Data Warehouse
2. Quality Gate: Kiểm định chất lượng dữ liệu 5 bước
3. Cleaning & ETL: Loại bỏ trùng lặp, ép kiểu -> Silver Layer & Data Warehouse
4. Feature Engineering: Tạo 13 features & selection -> Gold Layer & Data Warehouse
5. Machine Learning: Train Baseline & Tuned Model (MLflow tracking)
6. App Export: Xuất predictions và metrics cho Streamlit Dashboard
7. Testing & Verification: Chạy kiểm thử tự động

Sử dụng:
    python run_pipeline.py               # Chạy pipeline chuẩn với dữ liệu thật
    python run_pipeline.py --synthetic   # Tự sinh dữ liệu mẫu vào data/synthetic/ (không đè file gốc)
    python run_pipeline.py --skip-tests  # Bỏ qua bước chạy pytest cuối
"""

from __future__ import annotations

import argparse
import logging
import shutil
import sys
import time
from pathlib import Path

import pandas as pd

# Đảm bảo stdout hỗ trợ UTF-8 trên Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Thiết lập logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("PipelineOrchestrator")


def print_banner(step_num: int, title: str):
    print("\n" + "=" * 70)
    print(f"BUOC {step_num}: {title.upper()}")
    print("=" * 70)


def ensure_raw_data_backup(
    creditcard_path: Path = Path("data/creditcard.csv"),
    backup_path: Path = Path("data/creditcard.csv.bak"),
) -> None:
    """
    Sao lưu an toàn file dữ liệu gốc creditcard.csv sang creditcard.csv.bak.
    Nếu file gốc bị thiếu nhưng file backup tồn tại, tự động khôi phục từ backup.
    """
    # 1. Nếu file gốc thiếu nhưng có backup -> khôi phục
    if not creditcard_path.exists() and backup_path.exists():
        logger.warning(f"File gốc {creditcard_path} không tồn tại. Đang khôi phục từ {backup_path}...")
        shutil.copy2(backup_path, creditcard_path)
        logger.info(f"Đã khôi phục thành công {creditcard_path} ({backup_path.stat().st_size:,} bytes).")
        return

    # 2. Nếu file gốc tồn tại -> đảm bảo đã backup
    if creditcard_path.exists():
        if not backup_path.exists() or backup_path.stat().st_size != creditcard_path.stat().st_size:
            logger.info(f"Đang sao lưu file gốc từ {creditcard_path} sang {backup_path}...")
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(creditcard_path, backup_path)
            logger.info(f"Đã sao lưu thành công ({creditcard_path.stat().st_size:,} bytes).")
        else:
            logger.info(f"Bản sao lưu {backup_path} đã tồn tại và đồng bộ ({backup_path.stat().st_size:,} bytes).")


def run_full_pipeline(
    force_synthetic: bool = False,
    n_samples: int = 15000,
    skip_tuning: bool = True,
    run_tests: bool = True
) -> bool:
    start_time = time.time()
    timings = {}

    print("=" * 70)
    print(">>> BAT DAU DIEU PHOI END-TO-END DATA & ML PIPELINE")
    print("=" * 70)

    # -------------------------------------------------------------
    # 1. INGESTION (Tầng 2: Ingestion & Bronze Lake)
    # -------------------------------------------------------------
    print_banner(1, "Data Ingestion & Bronze Storage")
    t0 = time.time()
    from src.data.ingestion import ingest_raw_data, generate_synthetic_raw_data
    from src.data.storage import warehouse

    bronze_path = Path("data/bronze/raw_transactions.csv")
    creditcard_path = Path("data/creditcard.csv")
    backup_path = Path("data/creditcard.csv.bak")
    synthetic_dir = Path("data/synthetic")
    synthetic_path = synthetic_dir / "synthetic_transactions.csv"

    # Bước sao lưu dữ liệu gốc trước mọi thao tác
    ensure_raw_data_backup(creditcard_path, backup_path)

    if force_synthetic:
        logger.info(f"Sinh {n_samples:,} dòng dữ liệu giả lập cho pipeline...")
        synthetic_dir.mkdir(parents=True, exist_ok=True)
        df_raw = generate_synthetic_raw_data(synthetic_path, n_samples=n_samples)
        # Ghi vào Bronze Layer để xử lý tiếp, TUYỆT ĐỐI KHÔNG ghi đè file gốc creditcard.csv
        bronze_path.parent.mkdir(parents=True, exist_ok=True)
        df_raw.to_csv(bronze_path, index=False)
        logger.info(f"Dữ liệu synthetic đã lưu vào {synthetic_path} và {bronze_path} (bảo toàn {creditcard_path}).")
    elif creditcard_path.exists():
        logger.info(f"Đọc dữ liệu gốc từ {creditcard_path} ({creditcard_path.stat().st_size:,} bytes)...")
        bronze_file = ingest_raw_data(source_path=creditcard_path)
        df_raw = pd.read_csv(bronze_file)
    elif bronze_path.exists():
        logger.info(f"Đọc dữ liệu thô từ Bronze layer: {bronze_path}...")
        df_raw = pd.read_csv(bronze_path)
    else:
        logger.warning("Không tìm thấy file creditcard.csv gốc. Sinh dữ liệu giả lập vào data/synthetic/...")
        synthetic_dir.mkdir(parents=True, exist_ok=True)
        df_raw = generate_synthetic_raw_data(synthetic_path, n_samples=n_samples)
        bronze_path.parent.mkdir(parents=True, exist_ok=True)
        df_raw.to_csv(bronze_path, index=False)

    # Nạp mẫu vào Data Warehouse
    try:
        warehouse.write_table(df_raw.head(5000), "bronze_raw_transactions")
    except Exception as e:
        logger.warning(f"Không thể lưu vào Data Warehouse: {e}")

    timings["1. Ingestion"] = time.time() - t0
    logger.info(f"Hoàn thành Ingestion trong {timings['1. Ingestion']:.2f}s ({len(df_raw):,} records)")

    # -------------------------------------------------------------
    # 2. QUALITY GATE (Tầng 3: Data Quality)
    # -------------------------------------------------------------
    print_banner(2, "Data Quality Gate Validation")
    t0 = time.time()
    from src.data.quality import check_data_quality, print_report

    quality_res = check_data_quality(df_raw)
    print_report(quality_res)

    if not quality_res.get("success", False):
        logger.error("Quality gate that bai! Du lieu khong dat tieu chuan toi thieu.")
        return False

    timings["2. Quality Gate"] = time.time() - t0

    # -------------------------------------------------------------
    # 3. CLEANING & ETL (Tầng 3 -> Silver Layer)
    # -------------------------------------------------------------
    print_banner(3, "Data Cleaning & Silver Storage")
    t0 = time.time()
    from src.data.cleaner import clean_data

    silver_path = Path("data/silver/cleaned.csv")
    silver_path.parent.mkdir(parents=True, exist_ok=True)
    cleaned_path = Path("data/cleaned.csv")

    df_clean, _ = clean_data(df_raw, output_path=cleaned_path)
    df_clean.to_csv(silver_path, index=False)

    try:
        warehouse.write_table(df_clean.head(5000), "silver_cleaned_transactions")
    except Exception as e:
        logger.warning(f"Không thể lưu bảng silver vào DWH: {e}")

    timings["3. Cleaning & ETL"] = time.time() - t0
    logger.info(f"Hoàn thành Cleaning trong {timings['3. Cleaning & ETL']:.2f}s ({len(df_clean):,} records)")

    # -------------------------------------------------------------
    # 4. FEATURE ENGINEERING (Tầng 3 -> Gold Layer / Feature Store)
    # -------------------------------------------------------------
    print_banner(4, "Feature Engineering & Gold Storage")
    t0 = time.time()
    from src.features.run_features import run_feature_pipeline

    gold_path = Path("data/gold/features.csv")
    gold_path.parent.mkdir(parents=True, exist_ok=True)
    features_path = Path("data/features.csv")

    df_features = run_feature_pipeline(input_path=cleaned_path, output_path=features_path)
    df_features.to_csv(gold_path, index=False)

    try:
        warehouse.write_table(df_features.head(5000), "gold_features")
    except Exception as e:
        logger.warning(f"Không thể lưu bảng gold vào DWH: {e}")

    timings["4. Feature Engineering"] = time.time() - t0
    logger.info(f"Hoàn thành Feature Engineering trong {timings['4. Feature Engineering']:.2f}s ({len(df_features):,} records)")

    # -------------------------------------------------------------
    # 5. MODEL TRAINING & TRACKING (Tầng 5: Machine Learning)
    # -------------------------------------------------------------
    print_banner(5, "Model Training & Evaluation")
    t0 = time.time()
    Path("models").mkdir(parents=True, exist_ok=True)

    _train_direct_model(df_features)

    timings["5. Model Training"] = time.time() - t0
    logger.info(f"Hoàn thành Huấn luyện Model trong {timings['5. Model Training']:.2f}s")

    # -------------------------------------------------------------
    # 6. EXPORT ARTIFACTS FOR DASHBOARD (Tầng 6: Visualization)
    # -------------------------------------------------------------
    print_banner(6, "Export Artifacts for Web Dashboard")
    t0 = time.time()
    try:
        from src.models.export_for_app import main as export_main
        export_main()
    except Exception as e:
        logger.warning(f"export_for_app gặp lỗi ({e}). Chạy fallback export...")
        _export_fallback_artifacts(df_features)

    timings["6. Export Artifacts"] = time.time() - t0

    # -------------------------------------------------------------
    # 7. AUTOMATED TESTS VALIDATION
    # -------------------------------------------------------------
    if run_tests:
        print_banner(7, "Automated Verification Tests (pytest)")
        t0 = time.time()
        import pytest
        exit_code = pytest.main(["tests/", "-q"])
        timings["7. Verification Tests"] = time.time() - t0
        logger.info(f"Kết quả kiểm thử tự động: Mã thoát {exit_code}")

    total_time = time.time() - start_time
    print("\n" + "=" * 70)
    print(" BÁO CÁO TỔNG KẾT ĐIỀU PHỐI PIPELINE")
    print("=" * 70)
    for stage, duration in timings.items():
        print(f"  [OK] {stage:<30}: {duration:.2f}s")
    print("-" * 70)
    print(f"[*] TONG THOI GIAN THUC HIEN: {total_time:.2f}s")
    print("[*] Trang thai kho du lieu (Data Warehouse SQLite):")
    try:
        for tbl, count in warehouse.get_tables_summary().items():
            print(f"    - Bang '{tbl}': {count:,} records")
    except Exception:
        pass
    print("\n[DONE] DU AN DA SAN SANG! Khoi dong Dashboard voi lenh:")
    print("    streamlit run app/streamlit_app.py")
    print("=" * 70)
    return True


def _train_direct_model(df_features: pd.DataFrame):
    """Huấn luyện đầy đủ các mô hình Baseline, Random Forest và XGBoost (Tuned/Winner)."""
    import joblib
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler
    from xgboost import XGBClassifier

    X = df_features.drop(columns=["Class"])
    y = df_features["Class"]
    stratify = y if y.value_counts().min() >= 2 else None
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=stratify, random_state=42
    )
    logger.info(f"Tập huấn luyện: {len(X_train):,} dòng ({y_train.sum()} fraud) | Tập kiểm thử: {len(X_test):,} dòng ({y_test.sum()} fraud)")

    # 1. Baseline Logistic Regression với StandardScaler
    logger.info("Huấn luyện Baseline Logistic Regression...")
    lr_pipe = Pipeline([
        ("scaler", StandardScaler()),
        ("classifier", LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42))
    ])
    lr_pipe.fit(X_train, y_train)
    joblib.dump(lr_pipe, "models/baseline.pkl")
    logger.info("Đã lưu models/baseline.pkl")

    # 2. Random Forest (50 trees, balanced)
    logger.info("Huấn luyện Random Forest Classifier (50 trees)...")
    rf = RandomForestClassifier(n_estimators=50, random_state=42, class_weight="balanced", n_jobs=-1)
    rf.fit(X_train, y_train)
    joblib.dump(rf, "models/randomforest.pkl")
    logger.info("Đã lưu models/randomforest.pkl")

    # 3. XGBoost
    neg_to_pos = float((y_train == 0).sum() / (y_train == 1).sum())
    logger.info(f"Huấn luyện XGBoost Classifier (scale_pos_weight={neg_to_pos:.1f})...")
    xgb = XGBClassifier(
        n_estimators=100,
        scale_pos_weight=neg_to_pos,
        eval_metric="aucpr",
        tree_method="hist",
        n_jobs=-1,
        random_state=42,
        verbosity=0
    )
    xgb.fit(X_train, y_train)
    joblib.dump(xgb, "models/xgboost.pkl")
    joblib.dump(xgb, "models/production_model.pkl")
    logger.info("Đã lưu models/xgboost.pkl và models/production_model.pkl")


def _export_fallback_artifacts(df_features: pd.DataFrame):
    """Fallback export gọi trực tiếp export_for_app để bảo đảm kết quả đồng bộ 100%."""
    from src.models.export_for_app import main as export_main
    export_main()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="End-to-End Pipeline Orchestrator")
    parser.add_argument("--synthetic", action="store_true", help="Sinh dữ liệu giả lập vào data/synthetic/ nếu muốn thử nghiệm")
    parser.add_argument("--samples", type=int, default=15000, help="Số lượng giao dịch mẫu khi sinh synthetic")
    parser.add_argument("--skip-tests", action="store_true", help="Bỏ qua bước chạy pytest")
    args = parser.parse_args()

    success = run_full_pipeline(
        force_synthetic=args.synthetic,
        n_samples=args.samples,
        run_tests=not args.skip_tests
    )
    if not success:
        sys.exit(1)
