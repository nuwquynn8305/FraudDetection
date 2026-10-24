"""
Data Ingestion Module (Tầng 2: Ingestion theo kiến trúc chuẩn).

Chức năng:
1. Batch Ingestion: Đọc và xác thực nguồn dữ liệu thô (CSV, API, Local file) chuyển vào Bronze Layer.
2. Streaming Simulation: Giả lập nguồn stream giao dịch (như Kafka / Event Stream) để test luồng real-time fraud detection.
3. Synthetic Data Generator: Tự động sinh dữ liệu mẫu chuẩn cấu trúc nếu chưa có file creditcard.csv gốc.
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Generator, Optional

import numpy as np
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def generate_synthetic_raw_data(
    output_path: Path,
    n_samples: int = 10000,
    fraud_rate: float = 0.0017,
    random_state: int = 42
) -> pd.DataFrame:
    """
    Tạo dữ liệu giao dịch giả lập chuẩn cấu trúc (Time, V1-V28, Amount, Class)
    với tỉ lệ gian lận sát thực tế (~0.17%).
    """
    logger.info(f"Đang sinh {n_samples:,} dòng dữ liệu giả lập (fraud_rate={fraud_rate:.2%})...")
    np.random.seed(random_state)
    
    n_fraud = max(2, int(n_samples * fraud_rate))
    n_legit = n_samples - n_fraud
    
    # 1. Legit transactions (Class 0)
    legit_v = np.random.normal(loc=0.0, scale=1.0, size=(n_legit, 28))
    legit_time = np.sort(np.random.uniform(0, 172800, size=n_legit)) # 2 ngày
    legit_amount = np.random.exponential(scale=88.0, size=n_legit)
    
    # 2. Fraud transactions (Class 1) - skew trên V10, V12, V14, V16, V17
    fraud_v = np.random.normal(loc=0.0, scale=1.5, size=(n_fraud, 28))
    # Điều chỉnh các feature tương quan gian lận âm
    fraud_v[:, 13] -= 4.0  # V14
    fraud_v[:, 16] -= 3.5  # V17
    fraud_v[:, 11] -= 3.0  # V12
    fraud_v[:, 9] -= 2.5   # V10
    fraud_time = np.random.uniform(0, 172800, size=n_fraud)
    fraud_amount = np.random.exponential(scale=122.0, size=n_fraud)
    
    # Ghép dữ liệu
    v_cols = [f"V{i}" for i in range(1, 29)]
    df_legit = pd.DataFrame(legit_v, columns=v_cols)
    df_legit["Time"] = legit_time
    df_legit["Amount"] = np.round(legit_amount, 2)
    df_legit["Class"] = 0
    
    df_fraud = pd.DataFrame(fraud_v, columns=v_cols)
    df_fraud["Time"] = fraud_time
    df_fraud["Amount"] = np.round(fraud_amount, 2)
    df_fraud["Class"] = 1
    
    df = pd.concat([df_legit, df_fraud], ignore_index=True)
    # Sắp xếp theo Time
    df = df.sort_values("Time").reset_index(drop=True)
    
    # Đảm bảo thứ tự cột chuẩn
    cols_order = ["Time"] + v_cols + ["Amount", "Class"]
    df = df[cols_order]
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    logger.info(f"Đã lưu dữ liệu thô tại: {output_path} (Gian lận: {n_fraud}/{n_samples})")
    return df


def ingest_raw_data(
    source_path: Optional[Path] = None,
    bronze_dir: Path = Path("data/bronze"),
    fallback_n_samples: int = 15000
) -> Path:
    """
    Ingestion Pipeline:
    - Tìm kiếm file data thô ở thư mục gốc / nguồn chỉ định.
    - Chuyển vào Bronze Layer (Data Lake lưu trữ dữ liệu thô).
    - Tự sinh dữ liệu nếu chưa có file nào.
    """
    bronze_dir.mkdir(parents=True, exist_ok=True)
    bronze_output = bronze_dir / "raw_transactions.csv"
    
    # 1. Kiểm tra nguồn đầu vào
    candidate_paths = []
    if source_path and Path(source_path).exists():
        candidate_paths.append(Path(source_path))
    candidate_paths.extend([
        Path("data/creditcard.csv"),
        Path("data/raw_transactions.csv"),
        Path("creditcard.csv")
    ])
    
    existing_file = next((p for p in candidate_paths if p.exists() and p.is_file()), None)
    
    if existing_file:
        logger.info(f"Phát hiện file dữ liệu thô tại: {existing_file}")
        df = pd.read_csv(existing_file)
        df.to_csv(bronze_output, index=False)
        logger.info(f"Đã nạp {len(df):,} giao dịch vào Bronze Layer: {bronze_output}")
    else:
        logger.warning("Không tìm thấy file creditcard.csv gốc. Kích hoạt Synthetic Ingestion Generator...")
        generate_synthetic_raw_data(bronze_output, n_samples=fallback_n_samples)
        
    return bronze_output


def simulate_transaction_stream(
    data_path: Path,
    batch_size: int = 5,
    delay_seconds: float = 0.5,
    max_batches: int = 10
) -> Generator[pd.DataFrame, None, None]:
    """
    Giả lập Streaming Ingestion (như Kafka Consumer nhận stream giao dịch liên tục).
    """
    logger.info(f"Khởi động Streaming Ingestion (batch={batch_size}, interval={delay_seconds}s)...")
    df = pd.read_csv(data_path)
    total_rows = len(df)
    
    for i in range(0, min(total_rows, batch_size * max_batches), batch_size):
        chunk = df.iloc[i : i + batch_size]
        logger.info(f"[STREAM EVENT] Ingested batch {i // batch_size + 1}: {len(chunk)} giao dịch")
        yield chunk
        time.sleep(delay_seconds)
