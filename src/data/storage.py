"""
Storage Module (Tầng 4: Storage theo kiến trúc chuẩn Data Lake & Data Warehouse).

Mô hình quản lý lưu trữ:
1. Data Lake (Medallion Architecture):
   - Bronze: Dữ liệu thô vừa ingest (data/bronze/raw_transactions.csv)
   - Silver: Dữ liệu đã làm sạch & validation (data/silver/cleaned_transactions.csv)
   - Gold: Feature Store chuẩn bị cho Model training & Analytics (data/gold/features.csv)

2. Data Warehouse (Embedded SQLite DB - data/warehouse.db):
   - Lưu trữ có cấu trúc các bảng bronze, silver, gold
   - Cho phép chạy SQL queries phân tích nghiệp vụ & trích xuất metrics
"""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path

import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

DB_PATH = Path("data/warehouse.db")


class DataWarehouse:
    """Quản lý kết nối và truy vấn Data Warehouse nội bộ."""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def write_table(
        self,
        df: pd.DataFrame,
        table_name: str,
        if_exists: str = "replace"
    ) -> None:
        """Lưu một DataFrame vào bảng Data Warehouse."""
        with self.get_connection() as conn:
            df.to_sql(table_name, conn, if_exists=if_exists, index=False)
            logger.info(f"Đã lưu {len(df):,} dòng vào bảng DWH: '{table_name}' ({self.db_path})")

    def read_table(self, table_name: str, limit: int | None = None) -> pd.DataFrame:
        """Đọc bảng từ Data Warehouse."""
        query = f"SELECT * FROM {table_name}"
        if limit:
            query += f" LIMIT {limit}"
        with self.get_connection() as conn:
            return pd.read_sql_query(query, conn)

    def execute_query(self, query: str) -> pd.DataFrame:
        """Thực thi câu lệnh SQL tùy biến (Analytical Query)."""
        with self.get_connection() as conn:
            return pd.read_sql_query(query, conn)

    def get_tables_summary(self) -> dict:
        """Tổng kết số lượng dòng và schema các bảng trong Warehouse."""
        summary = {}
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            for tbl in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {tbl};")
                count = cursor.fetchone()[0]
                summary[tbl] = count
        return summary


# Singleton instance tiện dụng
warehouse = DataWarehouse()
