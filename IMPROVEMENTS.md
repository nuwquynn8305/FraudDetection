# Tài Liệu Cải Thiện Code

## Tổng Quan
Tài liệu này mô tả các cải thiện đã thực hiện trên dự án Fraud Detection để nâng cao chất lượng code, stability và maintainability.

---

## Bước 1: Error Handling & Validation

### File: `app/utils.py`

**Thay đổi:**
- Thêm try-catch blocks cho tất cả các hàm load data
- Xử lý cụ thể cho JSON decode errors
- Thêm thông báo lỗi thân thiện cho người dùng qua Streamlit UI
- Validate input parameters

**Lợi ích:**
- App không crash khi file data bị hỏng hoặc thiếu
- Người dùng nhận được thông báo lỗi rõ ràng
- Dễ debug với detailed error messages

**Code mẫu:**
```python
try:
    if FEATURES_PATH.exists():
        logger.info(f"Đang tải features từ {FEATURES_PATH}")
        return pd.read_csv(FEATURES_PATH)
    logger.warning("File features không tồn tại, đang dùng demo data")
    return generate_demo_features()
except Exception as e:
    logger.error(f"Lỗi khi tải features: {e}")
    st.error(f"Không thể tải dữ liệu features: {str(e)}")
    raise
```

---

## Bước 2: Type Hints

### Files: `app/utils.py`, `src/features/engineering.py`

**Thay đổi:**
- Thêm type hints cho tất cả các hàm
- Import typing module (Dict, List, Tuple, Optional)
- Cải thiện docstrings với Args, Returns, Raises sections

**Lợi ích:**
- IDE support tốt hơn (autocomplete, type checking)
- Code dễ đọc và hiểu hơn
- Giảm bugs do type mismatch
- Tự động documentation generation

**Code mẫu:**
```python
def load_model_results() -> Dict:
    """Tải metric so sánh model, hoặc tạo kết quả demo nếu thiếu.
    
    Returns:
        Dict: Dictionary chứa metrics của các model
    
    Raises:
        Exception: Nếu cả file thực và demo generation đều thất bại
    """
```

---

## Bước 3: Logging thay vì Print

### File: `src/features/engineering.py`

**Thay đổi:**
- Thêm logging module với cấu hình chuẩn
- Thay thế print statements bằng logger calls
- Các mức logging: INFO, WARNING, ERROR

**Lợi ích:**
- Có thể cấu hình log level (DEBUG, INFO, WARNING, ERROR)
- Log ra file cho production monitoring
- Timestamp và module name tự động
- Tắt/bật logging dễ dàng

**Cấu hình logging:**
```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
```

**Ví dụ sử dụng:**
```python
logger.info(f"Bắt đầu tạo features cho {len(df)} hàng")
logger.warning("File features không tồn tại, đang dùng demo data")
logger.error(f"Thiếu các cột cần thiết: {missing_cols}")
```

---

## Bước 4: Input Validation

### File: `src/features/engineering.py`

**Thay đổi:**
- Validate các cột cần thiết trước khi processing
- Raise KeyError với thông báo rõ ràng khi thiếu columns
- Log error trước khi raise exception

**Lợi ích:**
- Fail fast với thông báo rõ ràng
- Tránh errors khó hiểu ở downstream
- Dễ debug khi data không đúng format

**Code mẫu:**
```python
required_cols = ['Time', 'Amount', 'Class'] + [f'V{i}' for i in range(1, 29)]
missing_cols = [col for col in required_cols if col not in df.columns]
if missing_cols:
    logger.error(f"Thiếu các cột cần thiết: {missing_cols}")
    raise KeyError(f"Thiếu các cột cần thiết: {missing_cols}")
```

---

## Bước 5: UTF-8 Encoding

### File: `app/utils.py`

**Thay đổi:**
- Thêm encoding='utf-8' khi đọc JSON file

**Lợi ích:**
- Hỗ trợ tiếng Việt và các ký tự Unicode
- Tránh encoding errors trên các hệ thống khác nhau

---

## Quy Trình Sử Dụng

### 1. Chạy App với Logging
```bash
streamlit run app/streamlit_app.py
```

Logs sẽ hiển thị trong terminal với format:
```
2026-10-12 10:30:00 - app.utils - INFO - Đang tải features từ data/features.csv
2026-10-12 10:30:01 - app.utils - WARNING - File features không tồn tại, đang dùng demo data
```

### 2. Debug với Log Level DEBUG
```python
logging.basicConfig(
    level=logging.DEBUG,  # Thay INFO thành DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### 3. Log ra File (Production)
```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

---

## Các Cải Tiến Tương Lai (Đề Xuất)

### 1. Constants File
- Tạo `src/constants.py` để tập trung tất cả constants
- Di chuyển COLORS, thresholds, feature names vào constants

### 2. Configuration Management
- Sử dụng `.env` file cho environment variables
- Thay thế hardcoded paths với config

### 3. Unit Tests
- Thêm tests cho error handling
- Test edge cases (empty data, missing columns)

### 4. Data Validation Schema
- Sử dụng pydantic hoặc pandera cho data validation
- Validate data types, ranges, null values

### 5. Async Operations
- Async data loading cho large datasets
- Progress bars cho long-running operations

---

## Checklist Review

- ✅ Error handling cho data loading
- ✅ Type hints cho các hàm chính
- ✅ Logging thay vì print
- ✅ Input validation
- ✅ UTF-8 encoding
- ⏳ Constants file (chưa thực hiện)
- ⏳ Unit tests (chưa thực hiện)
- ⏳ Configuration management (chưa thực hiện)

---

## Tài Liệu Tham Khảo

- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [Python Logging](https://docs.python.org/3/library/logging.html)
- [PEP 8 Style Guide](https://peps.python.org/pep-0008/)
- [Error Handling Best Practices](https://docs.python.org/3/tutorial/errors.html)
