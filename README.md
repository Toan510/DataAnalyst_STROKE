# sgu25_data_analytics

## Cấu trúc thư mục đề xuất cho báo cáo

```text
DOAN_CUOIKY/
	app/
		dashboard.py
	data/
		raw/
			healthcare-dataset-stroke-data.csv
	notebooks/
		01_data_preprocessing_eda.ipynb
		02_clustering_visualization.ipynb
	report/
		report_outline.md
```

## Ý nghĩa từng phần

- `data/raw`: dữ liệu gốc, không chỉnh sửa trực tiếp.
- `notebooks/01_*`: tiền xử lý và EDA cho phần mô tả dữ liệu.
- `notebooks/02_*`: phân cụm, phân nhóm và trực quan hóa.
- `app/dashboard.py`: dashboard trình bày kết quả tương tác.
- `report/`: dàn ý và nội dung báo cáo cuối kỳ.

## Chạy dashboard

Từ thư mục gốc dự án:

```bash
streamlit run DOAN_CUOIKY/app/dashboard.py
```