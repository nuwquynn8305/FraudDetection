# Tóm Tắt Dự Án - Phát Hiện Gian Lận Thẻ Tín Dụng

## Dự Án Là Gì?

Đây là một hệ thống **Machine Learning end-to-end** để phát hiện gian lận thẻ tín dụng tự động. Hệ thống nhận dữ liệu giao dịch, phân tích, và dự đoán xem giao dịch đó có phải gian lận hay không.

---

## Vấn Đề Giải Quyết

- **Gian lận thẻ tín dụng:** Gây thiệt hại hàng tỷ USD mỗi năm
- **Thách thức:** Dữ liệu mất cân bằng cực độ (chỉ 0.17% gian lận)
- **Mục tiêu:** Tự động phát hiện gian lận nhanh và chính xác

---

## Giải Pháp

Hệ thống ML với 6 tầng kiến trúc chuẩn Big Data:

```
Raw Data → Ingestion → ETL/ELT → Storage → ML → Visualization
```

---

## 6 Tầng Kiến Trúc

### **Tầng 1: Raw Data (Dữ liệu thô)**
- **Nguồn:** Kaggle Credit Card Fraud Detection
- **Dữ liệu:** 284,807 giao dịch, 492 gian lận
- **Định dạng:** CSV file

### **Tầng 2: Ingestion (Thu thập dữ liệu)**
- **Batch:** Đọc file CSV vào Bronze Layer
- **Synthetic:** Tự sinh data mẫu nếu không có file gốc
- **Streaming:** Giả lập Kafka stream (demo)

### **Tầng 3: ETL/ELT (Xử lý dữ liệu)**
- **Quality Gate:** 5 checks (nulls, duplicates, dtypes, ranges, schema)
- **Cleaning:** Loại 1,081 duplicates, ép kiểu
- **Feature Engineering:** Tạo 13 features mới
  - Domain: hour_of_day, log_amount
  - Statistical: v_magnitude, top_fraud_v_mean
  - Interaction: V14×V17

### **Tầng 4: Storage (Lưu trữ)**
- **Medallion Architecture:**
  - Bronze: Raw data (data/bronze/raw_transactions.csv)
  - Silver: Cleaned data (data/silver/cleaned.csv)
  - Gold: Features (data/gold/features.csv)
- **Data Warehouse:** SQLite database với 3 tables

### **Tầng 5: Machine Learning (Học máy)**
- **Models:**
  - Baseline: Logistic Regression (PR-AUC: 0.673)
  - Candidates: Random Forest, XGBoost
  - Winner: XGBoost Tuned (PR-AUC: 0.810)
- **Tuning:** Optuna (Bayesian optimization)
- **Tracking:** MLflow (params, metrics, artifacts)

### **Tầng 6: Visualization (Trình bày)**
- **Streamlit Dashboard:** 4 trang
  - Home: KPI cards, Pie chart, Confusion Matrix
  - Explore Data: Interactive EDA, Histogram, Heatmap
  - Model Results: Comparison, Feature importance, Live prediction
  - How I Built: Pipeline diagram, Timeline

---

## Kết Quả

| Metric | Giá Trị | Ý Nghĩa |
|--------|---------|---------|
| **PR-AUC** | 0.810 | Khả năng phát hiện gian lận cao |
| **Precision** | 93.6% | Ít báo động sai |
| **Recall** | 76.8% | Bắt được 76.8% gian lận |
| **F1** | 84.4% | Balance giữa precision và recall |
| **False Alarms** | 5 | Giảm từ 1,397 → 5 (99.6%) |

---

## Công Nghệ Sử Dụng

### **Core Stack:**
- **Language:** Python 3.11
- **Data:** Pandas, NumPy
- **ML:** Scikit-learn, XGBoost, Optuna
- **MLOps:** MLflow
- **Visualization:** Streamlit, Plotly
- **Database:** SQLite
- **Testing:** Pytest
- **CI/CD:** GitHub Actions
- **Containerization:** Docker

### **Giải thích công nghệ:**

| Công Nghệ | Là Gì? | Tại Sao Dùng? |
|-----------|--------|---------------|
| **Pandas** | Thư viện xử lý dữ liệu | Đọc/ghi CSV, lọc dữ liệu, tính toán |
| **NumPy** | Thư viện tính toán | Tính toán toán học nhanh, tạo synthetic data |
| **Scikit-learn** | Thư viện ML | Train models, đánh giá metrics |
| **XGBoost** | Algorithm ML mạnh mẽ | Tốt nhất cho classification, nhanh |
| **Optuna** | Tối ưu hóa hyperparameters | Tự động tìm best parameters |
| **MLflow** | Platform MLOps | Track experiments, log params/metrics |
| **Streamlit** | Web framework cho data science | Build dashboard dễ dàng |
| **Plotly** | Thư viện chart | Tạo interactive charts đẹp |
| **SQLite** | Embedded database | Data Warehouse, SQL queries |
| **Pytest** | Testing framework | Unit tests, đảm bảo code quality |
| **GitHub Actions** | CI/CD platform | Tự động chạy tests khi push code |
| **Docker** | Container platform | Đóng gói app, consistent environment |

---

## Cách Sử Dụng

### **1. Chạy Dashboard**
```bash
streamlit run app/streamlit_app.py
```
→ Mở http://localhost:8501

### **2. Chạy Pipeline Đầy Đủ**
```bash
python run_pipeline.py
```
→ Tự động chạy 7 steps:
1. Ingestion → Bronze
2. Quality Gate
3. Cleaning → Silver
4. Feature Engineering → Gold
5. Model Training
6. Export Artifacts
7. Automated Tests

### **3. Chạy với Synthetic Data**
```bash
python run_pipeline.py --synthetic
```
→ Tự sinh data mẫu nếu không có file gốc

---

## Cấu Trúc Thư Mục

```
FraudDetection/
├── app/                          # Streamlit Dashboard
│   ├── streamlit_app.py          # Trang chính
│   ├── pages/                    # Các trang con
│   │   ├── 1_Explore_the_Data.py
│   │   ├── 2_Model_Results.py
│   │   └── 3️_How_I_Built_This.py
│   └── utils.py                 # Utility functions
├── src/                          # Source code
│   ├── data/                     # Data processing
│   │   ├── ingestion.py          # Ingestion module
│   │   ├── quality.py            # Quality gate
│   │   ├── cleaner.py            # Data cleaning
│   │   ├── storage.py            # Data warehouse
│   │   └── loader.py             # Data loader
│   ├── features/                 # Feature engineering
│   │   ├── engineering.py        # Feature creation
│   │   └── run_features.py       # Feature pipeline
│   └── models/                   # ML models
│       ├── run_training.py        # Model training
│       └── export_for_app.py     # Export artifacts
├── data/                         # Data files
│   ├── bronze/                   # Bronze layer
│   ├── silver/                   # Silver layer
│   ├── gold/                     # Gold layer
│   ├── creditcard.csv            # Raw data
│   ├── warehouse.db              # SQLite DWH
│   ├── model_results.json        # ML metrics
│   └── predictions.csv           # Predictions
├── models/                       # Trained models
│   ├── baseline.pkl
│   └── production_model.pkl
├── tests/                        # Unit tests
├── run_pipeline.py               # Pipeline orchestrator
├── Dockerfile                    # Docker config
├── docker-compose.yml            # Docker compose
├── requirements.txt              # Python dependencies
├── README.md                     # Documentation
└── PRESENTATION_PLAN.md          # Presentation plan
```

---

## Key Features

### **1. Data Pipeline Tự Động**
- Ingestion → Quality → Cleaning → Features → Training → Export → Tests
- Tất cả tự động với 1 lệnh

### **2. Feature Engineering**
- 13 features mới từ 31 features gốc
- 3 categories: Domain, Statistical, Interaction

### **3. Model Training**
- 4 models: Logistic Regression, Random Forest, XGBoost, LightGBM
- Hyperparameter tuning với Optuna
- MLflow tracking

### **4. Interactive Dashboard**
- 4 trang với interactive widgets
- Real-time prediction widget
- Visual storytelling

### **5. Production Ready**
- Error handling, logging, type hints
- 22 unit tests
- CI/CD với GitHub Actions
- Docker containerization

---

## Tại Sao Dự Án Này Tốt?

### **1. Full-Stack ML Engineering**
- Không chỉ train model, mà build toàn bộ pipeline
- Từ data ingestion đến visualization

### **2. Production Code Quality**
- Error handling, logging, type hints
- Unit tests, CI/CD, Docker
- Không phải notebook demo

### **3. Architecture Standard**
- 6 tầng kiến trúc Big Data chuẩn
- Medallion Architecture
- Data Warehouse

### **4. MLOps Best Practices**
- MLflow tracking
- Model versioning
- Reproducibility

### **5. User-Friendly**
- Interactive dashboard
- Easy to use
- Visual storytelling

---

## Use Cases

### **Development/Testing**
- Dùng 5K rows synthetic data
- Nhanh, dễ debug

### **Presentation**
- Dùng 284K rows real data
- Chuyên nghiệp, thuyết phục

### **Production**
- BẮT BUỘC 284K rows real data
- Model quality, realistic

---

## Future Work

### **Big Data Extension**
- Migrate sang PySpark
- Kafka cho real-time streaming
- Airflow cho orchestration
- S3 cho Data Lake

### **Production**
- Kubernetes deployment
- Model monitoring (Prometheus/Grafana)
- A/B testing framework

---

## Tóm Tắt Cho Người Mới

**Dự án này là gì?**
→ Hệ thống tự động phát hiện gian lận thẻ tín dụng

**Làm như thế nào?**
→ Dùng Machine Learning để phân tích giao dịch

**Kết quả?**
→ Bắt được 76.8% gian lận, chỉ 5 báo động sai

**Công nghệ?**
→ Python, Pandas, XGBoost, Streamlit, MLflow

**Cách dùng?**
→ Chạy `streamlit run app/streamlit_app.py` để xem dashboard

**Đặc điểm?**
→ Full-stack ML pipeline, production-ready, interactive dashboard

---

## Liên Hệ

- **GitHub:** [Link repo của bạn]
- **Email:** [Email của bạn]
- **Documentation:** README.md, PRESENTATION_PLAN.md

---

## Quick Start

```bash
# 1. Clone repo
git clone [repo-url]
cd FraudDetection

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run pipeline
python run_pipeline.py --synthetic

# 4. Run dashboard
streamlit run app/streamlit_app.py

# 5. Open browser
# http://localhost:8501
```

---

**Dự án đạt 100% chuẩn 6 tầng kiến trúc Big Data Integration!** 🎉
