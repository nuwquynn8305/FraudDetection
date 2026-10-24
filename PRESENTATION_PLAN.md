# Kế Hoạch Thuyết Trình - Fraud Detection Project

## Tổng Quan

- **Thời lượng:** 15-20 phút
- **Đối tượng:** Giảng viên, sinh viên bộ môn "Tích hợp và phân tích dữ liệu lớn"
- **Mục tiêu:** Chứng minh khả năng xây dựng hệ thống ML end-to-end đạt chuẩn 6 tầng kiến trúc Big Data
- **Format:** Presentation + Live Demo

---

## Cấu Trúc Presentation (15-20 phút)

### **Slide 1: Title Slide (1 phút)**

**Content:**
- Title: "Phát Hiện Gian Lận Thẻ Tín Dụ - End-to-End ML Pipeline"
- Subtitle: "Dự án tích hợp và phân tích dữ liệu lớn"
- Tên sinh viên
- Môn học: Tích hợp và phân tích dữ liệu lớn
- Giảng viên: [Tên GV]

**Visual:**
- Logo trường (nếu có)
- Screenshot dashboard

**Script:**
"Xin chào thầy/cô và các bạn. Hôm nay em sẽ trình bày về dự án Phát Hiện Gian Lận Thẻ Tín Dụ - một hệ thống Machine Learning end-to-end được xây dựng theo kiến trúc chuẩn của bộ môn Tích hợp và phân tích dữ liệu lớn."

---

### **Slide 2: Problem Statement (2 phút)**

**Content:**
- **Bài toán:** Phát hiện gian lận thẻ tín dụng trong thời gian thực
- **Thách thức:**
  - Dữ liệu mất cân bằng cực độ (0.17% gian lận)
  - Dữ liệu ẩn danh (PCA features)
  - Trade-off giữa Precision và Recall
- **Tầm quan trọng:**
  - Thiệt hại kinh tế: Hàng tỷ USD mỗi năm
  - Cần hệ thống tự động, nhanh, chính xác

**Visual:**
- Chart: Phân phối class (pie chart)
- Stat: 284,807 transactions, 492 fraud (0.17%)

**Script:**
"Gian lận thẻ tín dụng là vấn đề nghiêm trọng gây thiệt hại hàng tỷ USD mỗi năm. Bài toán này có 3 thách thức chính: dữ liệu mất cân bằng cực độ với chỉ 0.17% gian lận, dữ liệu được ẩn danh qua PCA, và cần cân bằng giữa việc bắt gian lận (recall) và tránh báo động sai (precision)."

---

### **Slide 3: Solution Overview (2 phút)**

**Content:**
- **Giải pháp:** Hệ thống ML end-to-end với 6 tầng kiến trúc
- **Tech Stack:**
  - Data: Pandas, SQLite
  - ML: Scikit-learn, XGBoost, Optuna
  - MLOps: MLflow, Docker
  - Visualization: Streamlit, Plotly
- **Kết quả:**
  - PR-AUC: 0.810
  - Precision: 93.6%
  - Recall: 76.8%

**Visual:**
- Architecture diagram (6 tầng)
- Tech stack icons

**Script:**
"Em xây dựng hệ thống ML end-to-end với 6 tầng kiến trúc chuẩn: từ Raw Data, Ingestion, ETL/ELT, Storage, Machine Learning đến Visualization. Hệ thống đạt PR-AUC 0.810 với Precision 93.6% và Recall 76.8%."

---

### **Slide 4: Architecture - 6 Tầng (3 phút)**

**Content:**
- **Tầng 1: Raw Data** - CSV file 284K transactions
- **Tầng 2: Ingestion** - Batch + Streaming simulation
- **Tầng 3: ETL/ELT** - Quality Gate → Cleaning → Feature Engineering
- **Tầng 4: Storage** - Medallion Architecture (Bronze/Silver/Gold) + SQLite DWH
- **Tầng 5: ML** - 4 models, Optuna tuning, MLflow tracking
- **Tầng 6: Visualization** - Streamlit Dashboard

**Visual:**
- Diagram 6 tầng với arrows
- Color-coded layers

**Script:**
"Hệ thống được xây dựng theo 6 tầng kiến trúc chuẩn. Tầng 1: Raw Data từ Kaggle. Tầng 2: Ingestion với batch và streaming simulation. Tầng 3: ETL/ELT với Quality Gate, Cleaning và Feature Engineering tạo 13 features mới. Tầng 4: Storage theo Medallion Architecture với Bronze/Silver/Gold layers và SQLite Data Warehouse. Tầng 5: Machine Learning với 4 models, Optuna tuning và MLflow tracking. Tầng 6: Visualization với Streamlit Dashboard."

---

### **Slide 5: Data Pipeline Deep Dive (3 phút)**

**Content:**
- **Ingestion:**
  - Batch: CSV → Bronze Layer
  - Synthetic: Auto-generate data nếu không có file gốc
  - Streaming: Giả lập Kafka stream
- **Quality Gate:**
  - 5 checks: nulls, duplicates, dtypes, ranges, schema
- **Cleaning:**
  - Remove duplicates (1,081 rows)
  - Type casting
- **Feature Engineering:**
  - 13 features: Domain (hour_of_day, log_amount), Statistical (v_magnitude), Interaction (V14×V17)

**Visual:**
- Pipeline flow diagram
- Before/After feature comparison

**Script:**
"Data Pipeline bắt đầu với Ingestion: batch ingestion từ CSV vào Bronze Layer, synthetic data generator nếu không có file gốc, và streaming simulation giả lập Kafka. Quality Gate thực hiện 5 checks để đảm bảo chất lượng. Cleaning loại bỏ 1,081 duplicates và ép kiểu. Feature Engineering tạo 13 features mới theo 3 categories: domain features như hour_of_day và log_amount, statistical features như v_magnitude, và interaction features như V14×V17."

---

### **Slide 6: Storage & Data Warehouse (2 phút)**

**Content:**
- **Medallion Architecture:**
  - Bronze: Raw data (data/bronze/raw_transactions.csv)
  - Silver: Cleaned data (data/silver/cleaned.csv)
  - Gold: Features (data/gold/features.csv)
- **Data Warehouse (SQLite):**
  - 3 tables: bronze_raw_transactions, silver_cleaned_transactions, gold_features
  - SQL query support
  - Analytics & metrics extraction

**Visual:**
- Medallion diagram
- SQLite schema

**Script:**
"Storage được tổ chức theo Medallion Architecture với 3 layers: Bronze lưu raw data, Silver lưu cleaned data, Gold lưu features. Đồng thời, SQLite Data Warehouse lưu trữ có cấu trúc 3 bảng cho phép chạy SQL queries để phân tích và trích xuất metrics."

---

### **Slide 7: Machine Learning (3 phút)**

**Content:**
- **Models:**
  - Baseline: Logistic Regression (PR-AUC: 0.673)
  - Candidates: Random Forest, XGBoost, LightGBM
  - Winner: XGBoost Tuned (PR-AUC: 0.810)
- **Hyperparameter Tuning:**
  - Optuna Bayesian optimization
  - 30 trials, 5-fold CV
- **MLOps:**
  - MLflow tracking (params, metrics, artifacts)
  - Model versioning
  - Reproducibility

**Visual:**
- Model comparison table
- PR-AUC chart
- MLflow UI screenshot

**Script:**
"Machine Learning sử dụng 4 models: Logistic Regression baseline với PR-AUC 0.673, Random Forest, XGBoost, và LightGBM. XGBoost Tuned chiến thắng với PR-AUC 0.810 sau khi được tune với Optuna Bayesian optimization trong 30 trials và 5-fold CV. MLOps với MLflow tracking đảm bảo reproducibility và model versioning."

---

### **Slide 8: Visualization Dashboard (2 phút)**

**Content:**
- **Streamlit Dashboard (4 trang):**
  - Home: KPI cards, Pie chart, Confusion Matrix, Metrics bar chart
  - Explore Data: Interactive EDA, Histogram, Box plot, Heatmap
  - Model Results: Comparison table, Feature importance, Live prediction
  - How I Built: Pipeline diagram, Timeline, Key decisions
- **Features:**
  - Interactive filters
  - Real-time prediction widget
  - Visual storytelling

**Visual:**
- Screenshot 4 trang dashboard
- Highlight interactive features

**Script:**
"Visualization được xây dựng với Streamlit Dashboard có 4 trang. Trang Home hiển thị KPI cards và charts tổng quan. Explore Data cho phép interactive EDA với histograms, box plots và heatmaps. Model Results so sánh các models và có live prediction widget. How I Built trình bày pipeline diagram và timeline. Dashboard tập trung vào visual storytelling thay vì text dài."

---

### **Slide 9: Orchestration & Automation (1 phút)**

**Content:**
- **Pipeline Orchestrator (run_pipeline.py):**
  - 7 steps tự động: Ingestion → Quality → Cleaning → Features → Training → Export → Tests
  - Timing tracking
  - CLI arguments (--synthetic, --samples, --skip-tests)
  - Fallback handling
- **Usage:**
  - `python run_pipeline.py` - Chạy pipeline đầy đủ
  - `python run_pipeline.py --synthetic` - Sinh data mẫu

**Visual:**
- Pipeline flow diagram
- Terminal output screenshot

**Script:**
"Pipeline Orchestrator tự động chạy toàn bộ pipeline trong 7 steps với timing tracking. Hỗ trợ CLI arguments để sinh data mẫu hoặc skip tests. Fallback handling đảm bảo graceful degradation khi dependencies không có."

---

### **Slide 10: Results & Achievements (2 phút)**

**Content:**
- **Kết quả ML:**
  - PR-AUC: 0.810 (21% improvement)
  - Precision: 93.6%
  - Recall: 76.8%
  - F1: 84.4%
- **Kiến trúc:**
  - 100% đạt chuẩn 6 tầng kiến trúc
  - Medallion Architecture
  - Data Warehouse (SQLite)
- **Code Quality:**
  - Error handling, logging, type hints
  - 22 unit tests
  - CI/CD (GitHub Actions)
  - Docker containerization

**Visual:**
- Metrics comparison chart
- Architecture checklist
- Code quality badges

**Script:**
"Kết quả ML đạt PR-AUC 0.810, cải thiện 21% so với baseline. Kiến trúc đạt 100% chuẩn 6 tầng với Medallion Architecture và Data Warehouse. Code quality đạt chuẩn production với error handling, logging, type hints, 22 unit tests, CI/CD và Docker containerization."

---

### **Slide 11: Live Demo (3-5 phút)**

**Content:**
- Demo Streamlit Dashboard
- Thử interactive features
- Live prediction widget

**Visual:**
- Live screen sharing

**Script:**
"Bây giờ em sẽ demo hệ thống thực tế. Em sẽ mở Streamlit Dashboard và chạy qua các trang để các bạn thấy interactive features và live prediction widget."

---

### **Slide 12: Challenges & Lessons Learned (1-2 phút)**

**Content:**
- **Thách thức:**
  - Imbalanced data handling
  - Feature selection based on variance
  - Model selection trade-offs
- **Bài học:**
  - PR-AUC > Accuracy cho imbalanced data
  - Stratified split để giữ tỷ lệ class
  - Class weighting để balance loss function
  - XGBoost: 18× faster than RF

**Visual:**
- Bullet points with icons

**Script:**
"Thách thức chính là xử lý imbalanced data và feature selection. Bài học rút ra: PR-AUC quan trọng hơn Accuracy cho imbalanced data, stratified split để giữ tỷ lệ class, class weighting để balance loss, và XGBoost nhanh hơn 18 lần so với Random Forest."

---

### **Slide 13: Future Work (1 phút)**

**Content:**
- **Big Data Extension:**
  - PySpark cho distributed computing
  - Kafka cho real-time streaming
  - Airflow cho orchestration
  - S3 cho Data Lake
- **Production:**
  - Kubernetes deployment
  - Model monitoring (Prometheus/Grafana)
  - A/B testing framework

**Visual:**
- Future architecture diagram

**Script:**
"Future work bao gồm mở rộng sang Big Data với PySpark, Kafka, Airflow và S3. Production deployment với Kubernetes, model monitoring và A/B testing framework."

---

### **Slide 14: Conclusion (1 phút)**

**Content:**
- **Tóm tắt:**
  - Đã xây dựng hệ thống ML end-to-end hoàn chỉnh
  - Đạt 100% chuẩn 6 tầng kiến trúc
  - PR-AUC 0.810 với XGBoost
  - Dashboard tương tác với Streamlit
- **Key Takeaways:**
  - Full-stack ML Engineering capability
  - Production-ready code quality
  - Data visualization focus
  - Phù hợp bộ môn Big Data Integration

**Visual:**
- Summary checklist
- Thank you message

**Script:**
"Tóm lại, em đã xây dựng hệ thống ML end-to-end hoàn chỉnh đạt 100% chuẩn 6 tầng kiến trúc với PR-AUC 0.810. Dự án chứng minh khả năng full-stack ML Engineering với production-ready code quality và data visualization focus, phù hợp với bộ môn Tích hợp và phân tích dữ liệu lớn. Cảm ơn thầy/cô và các bạn đã lắng nghe."

---

### **Slide 15: Q&A (2-3 phút)**

**Content:**
- Questions?
- Contact info (nếu cần)

**Visual:**
- Q&A icon
- Email/GitHub (nếu muốn)

**Script:**
"Em xin mời thầy/cô và các bạn đặt câu hỏi."

---

## Live Demo Plan (3-5 phút)

### **Preparation (Trước demo):**
1. Mở terminal, chạy `streamlit run app/streamlit_app.py`
2. Đảm bảo app load thành công
3. Chuẩn browser ở localhost:8501
4. Mở terminal thứ 2 để chạy pipeline nếu cần

### **Demo Flow:**

#### **Step 1: Trang Chính (1 phút)**
- Show KPI cards (284K transactions, 13 features, PR-AUC 0.810)
- Show Pie chart phân phối class
- Show Confusion Matrix
- Show Metrics bar chart
- **Comment:** "Đây là trang tổng quan với các KPI quan trọng và charts visual"

#### **Step 2: Explore Data (1 phút)**
- Show thống kê nhanh
- Show phân phối target (linear + log)
- Chọn feature "V14" từ dropdown
- Show histogram và box plot
- Show heatmap tương quan
- Show key findings badges
- **Comment:** "Trang này cho phép interactive exploration với filters và charts"

#### **Step 3: Model Results (1 phút)**
- Show comparison table
- Show bar chart XGBoost vs RF
- Show metrics badges
- Show feature importance
- Show confusion matrix
- **Comment:** "Trang này so sánh các models và hiển thị feature importance"

#### **Step 4: Live Prediction (1 phút)**
- Chọn preset "Giao dịch gian lận ngẫu nhiên"
- Điều chỉnh slider V14
- Xem prediction thay đổi real-time
- Show gauge chart
- **Comment:** "Widget này cho phép thử prediction real-time với interactive sliders"

#### **Step 5: How I Built (30 giây)**
- Show pipeline diagram (Graphviz)
- Show timeline badges
- Show decision badges
- **Comment:** "Trang này trình bày pipeline architecture và timeline xây dựng"

#### **Step 6: Pipeline Orchestrator (Optional, 1 phút)**
- Mở terminal
- Chạy `python run_pipeline.py --synthetic --skip-tests`
- Show pipeline chạy qua 7 steps
- Show timing report
- **Comment:** "Pipeline orchestrator tự động chạy toàn bộ pipeline với timing tracking"

---

## Q&A Preparation

### **Câu hỏi có thể gặp:**

#### **Q1: Tại sao chọn PR-AUC thay vì Accuracy?**
**Answer:**
"Với dataset 99.83% hợp pháp, model dự đoán 'không gian lận' cho mọi thứ đạt 99.83% accuracy nhưng bắt được 0 gian lận. PR-AUC tập trung vào class hiếm và là metric trung thực cho imbalanced data classification."

#### **Q2: Tại sao chia stratified thay vì random?**
**Answer:**
"Với chỉ 492 gian lận trong 284K rows, chia random có thể để lại một phần gần như không có gian lận. Stratification buộc cả hai phần phải bảo tồn tỷ lệ gian lận 0.17%."

#### **Q3: Tại sao chọn XGBoost thay vì Random Forest?**
**Answer:**
"PR-AUC hòa (0.81), nhưng XGBoost bắt được 3 gian lận nhiều hơn chỉ với 4 báo động sai thêm. Train nhanh 18× (2s vs 30s), quan trọng cho hệ thống retrain thường xuyên."

#### **Q4: Feature engineering làm như thế nào?**
**Answer:**
"Tạo 13 features theo 3 categories: Domain features (hour_of_day, log_amount), Statistical features (v_magnitude, top_fraud_v_mean), và Interaction features (V14×V17). Feature selection dựa trên variance threshold và correlation analysis."

#### **Q5: Medallion Architecture là gì?**
**Answer:**
"Medallion Architecture tổ chức data theo 3 layers: Bronze lưu raw data, Silver lưu cleaned và validated data, Gold lưu features và analytics-ready data. Mỗi layer tăng dần chất lượng và giá trị."

#### **Q6: Tại sao dùng SQLite thay vì PostgreSQL?**
**Answer:**
"SQLite phù hợp cho local pipeline và demo. Production có thể migrate sang PostgreSQL hoặc BigQuery cho scalability. SQLite embedded, không cần setup server."

#### **Q7: Làm sao đảm bảo data quality?**
**Answer:**
"Quality Gate với 5 checks: null values, duplicates, data types, value ranges, và schema validation. Nếu fail, pipeline dừng và báo lỗi."

#### **Q8: MLOps được implement như thế nào?**
**Answer:**
"MLflow tracking params, metrics, và artifacts. Model versioning với run IDs. Reproducibility với logged hyperparameters. CI/CD với GitHub Actions. Docker containerization."

#### **Q9: Streaming simulation làm như thế nào?**
**Answer:**
"simulate_transaction_stream() trong ingestion.py giả lập Kafka consumer với batch size và delay. Production có thể migrate sang Kafka thật."

#### **Q10: Future work là gì?**
**Answer:**
"Migrate sang PySpark cho big data, Kafka cho real-time streaming, Airflow cho orchestration, S3 cho Data Lake, Kubernetes deployment, và model monitoring với Prometheus/Grafana."

---

## Tips Để Thuyết Trình Tốt

### **Trước thuyết trình:**
1. **Practice:** Tập thuyết trình ít nhất 3 lần
2. **Timing:** Đảm bảo đúng 15-20 phút
3. **Demo test:** Chạy app và pipeline trước để chắc chắn không lỗi
4. **Backup:** Chuẩn bị screenshots nếu demo fail
5. **Questions:** Dự đoán câu hỏi và chuẩn bị answers

### **Trong thuyết trình:**
1. **Eye contact:** Nhìn khán phòng, không chỉ nhìn slide
2. **Pacing:** Nói chậm, rõ ràng, không quá nhanh
3. **Interactive:** Hỏi khán phòng "Có câu hỏi không?" giữa các phần
4. **Demo:** Giải thích khi demo, không chỉ click
5. **Confidence:** Tin vào project của bạn

### **Sau thuyết trình:**
1. **Q&A:** Lắng nghe kỹ câu hỏi
2. **Honest:** Nếu không biết, nói "Em sẽ tìm hiểu thêm"
3. **Follow-up:** Cung cấp contact nếu cần
4. **Feedback:** Xin feedback để cải thiện

---

## Checklist Trước Thuyết Trình

- [ ] Slide đã hoàn thành
- [ ] Script đã viết và practice
- [ ] Demo đã test và chạy thành công
- [ ] Pipeline đã test và chạy thành công
- [ ] Q&A đã chuẩn bị
- [ ] Laptop đã charge
- [ ] Internet connection ổn định
- [ ] Backup screenshots đã chuẩn bị
- [ ] Timer đã set
- [ ] Water đã chuẩn bị

---

## Backup Plan (Nếu Demo Fail)

### **Scenario 1: App không chạy**
- **Solution:** Show screenshots của dashboard
- **Explanation:** "Do vấn đề mạng, em sẽ show screenshots"

### **Scenario 2: Pipeline không chạy**
- **Solution:** Show terminal output screenshot
- **Explanation:** "Pipeline đã chạy trước, đây là output"

### **Scenario 3: Charts không load**
- **Solution:** Show static images
- **Explanation:** "Do data size, em sẽ show static charts"

### **Scenario 4: Time不足**
- **Solution:** Skip demo, focus on slides
- **Explanation:** "Do thời gian, em sẽ skip demo và tập trung vào slides"

---

## Kết Luận

**Thuyết trình thành công =**
1. **Content:** Rõ ràng, logic, có depth
2. **Delivery:** Tự tin, pacing tốt, eye contact
3. **Demo:** Smooth, interactive, impressive
4. **Q&A:** Chuyên nghiệp, honest, helpful

**Key message:**
"Tôi có thể xây dựng hệ thống ML end-to-end hoàn chỉnh đạt chuẩn production, không chỉ là notebook demo."
