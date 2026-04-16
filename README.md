# SGU25 Data Analytics - Phân Tích Dữ Liệu Đột Quỵ

## Mục Lục

- [Giới Thiệu](#giới-thiệu)
- [Cấu Trúc Dự Án](#cấu-trúc-dự-án)
- [Yêu Cầu Hệ Thống](#yêu-cầu-hệ-thống)
- [Cài Đặt](#cài-đặt)
- [Hướng Dẫn Sử Dụng](#hướng-dẫn-sử-dụng)
- [Tập Dữ Liệu](#tập-dữ-liệu)
- [Công Nghệ Sử Dụng](#công-nghệ-sử-dụng)

## Giới Thiệu

Dự án phân tích dữ liệu y tế toàn diện, tập trung vào việc dự đoán và phân tích các yếu tố liên quan đến bệnh đột quỵ. Dự án sử dụng các kỹ thuật machine learning bao gồm phân cụm (clustering) và phân loại (classification) để khám phá các mô hình trong dữ liệu.

**Mục tiêu chính:**
- Tiền xử lý và làm sạch dữ liệu
- Phân tích khám phá dữ liệu (EDA)
- Phân cụm dữ liệu để xác định nhóm bệnh nhân
- Xây dựng mô hình phân loại để dự đoán đột quỵ
- Trực quan hóa kết quả qua giao diện tương tác

## Cấu Trúc Dự Án

```
sgu25_data_analytics/
├── README.md
├── PhanTichDuLieu_DotQuy/
│   ├── app/
│   │   └── dashboard.py              # Ứng dụng Streamlit thể hiện kết quả
│   ├── data/
│   │   └── raw/
│   │       └── healthcare-dataset-stroke-data.csv
│   ├── notebooks/
│   │   ├── 01_1_data_preprocessing.ipynb  # Tiền xử lý dữ liệu
│   │   ├── 01_2_eda.ipynb                 # Phân tích khám phá
│   │   ├── 02_1_clustering_analysis.ipynb # Phân tích cụm
│   │   ├── 02_2_classification_analysis.ipynb  # Phân tích phân loại
│   │   └── 02_3_visualization.ipynb       # Trực quan hóa
│   └── report/
│       └── report_outline.md         # Dàn ý báo cáo
└── .venv/                            # Môi trường ảo Python

```

### Mô Tả Từng Thư Mục

| Thư Mục | Mục Đích |
|---------|---------|
| `data/raw/` | Lưu trữ dữ liệu gốc, không được chỉnh sửa trực tiếp |
| `notebooks/01_*` | Tiền xử lý dữ liệu và phân tích khám phá (EDA) |
| `notebooks/02_*` | Phân tích cụm, phân loại, và trực quan hóa kết quả |
| `app/` | Ứng dụng Streamlit tương tác để trình bày kết quả |
| `report/` | Dàn ý và nội dung báo cáo cuối kỳ |

## Yêu Cầu Hệ Thống

- **Python:** 3.8 trở lên
- **Quản lý gói:** pip hoặc conda

## Cài Đặt

### 1. Clone hoặc tải về dự án

```bash
cd sgu25_data_analytics
```

### 2. Tạo và kích hoạt môi trường ảo (Khuyến nghị)

**Windows (PowerShell):**
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Cài đặt các thư viện phụ thuộc

```bash
pip install -r requirements.txt
```

## Hướng Dẫn Sử Dụng

### Chạy Jupyter Notebooks

```bash
jupyter notebook
```

Sau đó, mở các file notebook theo thứ tự:
1. `notebooks/01_1_data_preprocessing.ipynb` - Tiền xử lý dữ liệu
2. `notebooks/01_2_eda.ipynb` - Phân tích khám phá
3. `notebooks/02_1_clustering_analysis.ipynb` - Phân cụm
4. `notebooks/02_2_classification_analysis.ipynb` - Phân loại
5. `notebooks/02_3_visualization.ipynb` - Trực quan hóa

### Chạy Dashboard Interactif

**Từ thư mục gốc dự án:**
```bash
streamlit run PhanTichDuLieu_DotQuy/app/dashboard.py
```

Dashboard sẽ mở tại `http://localhost:8501`

## Tập Dữ Liệu

**Tên:** Healthcare Dataset - Stroke Data

**Nguồn:** `data/raw/healthcare-dataset-stroke-data.csv`

**Mô tả:**
- Tập dữ liệu y tế chứa thông tin về bệnh nhân
- Các thuộc tính bao gồm: tuổi, giới tính, bệnh tim, tình trạng huyết áp, BMI, tình trạng hôn nhân, công việc, vùng cư trú, v.v.
- Biến mục tiêu: `stroke` (có/không có đột quỵ)

## Công Nghệ Sử Dụng

| Thư Viện | Mục Đích |
|---------|---------|
| **pandas** | Xử lý và phân tích dữ liệu |
| **numpy** | Tính toán số học |
| **matplotlib, seaborn** | Trực quan hóa dữ liệu |
| **scikit-learn** | Machine learning, clustering, classification |
| **streamlit** | Xây dựng giao diện web tương tác |
| **jupyter** | Phát triển và trình bày code |

## Liên Hệ & Thông Tin Thêm

Cho các câu hỏi hoặc góp ý, vui lòng liên hệ với nhóm dự án.