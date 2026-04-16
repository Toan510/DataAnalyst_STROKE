import pandas as pd
import numpy as np
import streamlit as st
from pathlib import Path
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
import plotly.express as px
import io


st.set_page_config(page_title="Phân tích Nguy cơ Đột quỵ", layout="wide", initial_sidebar_state="expanded")
st.title("Phân tích Nguy cơ Đột quỵ – Dashboard Hoàn chỉnh")

@st.cache_data
def load_data():
    data_path = Path(__file__).resolve().parents[1] / 'data' / 'raw' / 'healthcare-dataset-stroke-data.csv'
    try:
        df = pd.read_csv(data_path)
        return df
    except:
        st.error(f"Không tìm thấy file dữ liệu tại: {data_path}")
        st.stop()

df = load_data()

st.sidebar.title("Điều hướng")
page = st.sidebar.radio("Chọn phần", [
    "Tổng quan dữ liệu",
    "Tiền xử lý dữ liệu",
    "Phân tích khám phá (EDA)",
    "Phân cụm bệnh nhân",
    "Trực quan hóa nâng cao",
    "Bảng tóm tắt nguy cơ"
])


if page == "Tổng quan dữ liệu":
    st.header("1. Tổng quan dữ liệu")
    st.dataframe(df.head(10), use_container_width=True)
    st.write(f"**Kích thước**: {df.shape[0]:,} dòng × {df.shape[1]} cột")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Kiểu dữ liệu")
        st.code(df.dtypes.to_string())
    with col2:
        st.subheader("Giá trị thiếu")
        missing = df.isnull().sum()
        missing = missing[missing > 0]
        if missing.empty:
            st.success("Không có giá trị thiếu!")
        else:
            st.dataframe(missing.reset_index().rename(columns={0:"Số lượng thiếu"}), use_container_width=True)

    st.subheader("Thống kê mô tả")
    st.dataframe(df.describe().round(2), use_container_width=True)
    
elif page == "Tiền xử lý dữ liệu":
    st.header("2. Tiền xử lý dữ liệu")
    df_clean = df.copy()
    bmi_median = df_clean['bmi'].median()
    df_clean['bmi'] = df_clean['bmi'].fillna(bmi_median)
    st.success(f"Đã điền {df['bmi'].isnull().sum()} giá trị thiếu ở BMI → trung vị = {bmi_median:.1f}")

    st.dataframe(df_clean.head(), use_container_width=True)
    csv = df_clean.to_csv(index=False).encode()
    st.download_button("Tải file CSV đã làm sạch", data=csv, file_name="stroke_cleaned.csv", mime="text/csv")

elif page == "Phân tích khám phá (EDA)":
    st.header("3. Phân tích khám phá dữ liệu (EDA)")

    num_cols = ['age', 'avg_glucose_level', 'bmi']
    cat_cols = ['gender', 'hypertension', 'heart_disease', 'ever_married', 'work_type', 'Residence_type', 'smoking_status']

    # Số liệu
    st.subheader("Phân phối các đặc trưng số")
    for col in num_cols:
        fig = px.histogram(df, x=col, color='stroke', marginal='box', nbins=50,
                           title=f"Phân phối {col.replace('_', ' ')} theo Đột quỵ",
                           color_discrete_sequence=['#636EFA', '#EF553B'])
        st.plotly_chart(fig, use_container_width=True)

    # Phân loại – ĐÃ SỬA HOÀN TOÀN
    st.subheader("Phân bố các đặc trưng phân loại")
    for col in cat_cols:
        fig = px.histogram(df.astype({col: str}), x=col, color='stroke', barmode='group',
                           text_auto=True,
                           title=f"{col.replace('_', ' ').title()} theo Đột quỵ",
                           color_discrete_sequence=['#636EFA', '#EF553B'])
        fig.update_xaxes(type='category')
        fig.update_layout(yaxis_title="Số lượng bệnh nhân")
        st.plotly_chart(fig, use_container_width=True)

    # Tương quan
    st.subheader("Ma trận tương quan")
    corr = df.select_dtypes('number').corr()
    fig = px.imshow(corr.round(2), text_auto=True, color_continuous_scale='RdBu_r',
                    title="Tương quan giữa các biến")
    st.plotly_chart(fig, use_container_width=True)

elif page == "Phân cụm bệnh nhân":
    st.header("4. Phân cụm bệnh nhân (K-Means)")

    # Tiền xử lý an toàn
    df_cluster = df.copy()
    df_cluster['bmi'] = df_cluster['bmi'].fillna(df_cluster['bmi'].median())

    features = ['age', 'hypertension', 'heart_disease', 'avg_glucose_level', 'bmi',
                'gender', 'ever_married', 'work_type', 'Residence_type', 'smoking_status']
    X = df_cluster[features]

    num_features = ['age', 'avg_glucose_level', 'bmi']
    cat_features = ['gender', 'ever_married', 'work_type', 'Residence_type', 'smoking_status']

    preprocessor = ColumnTransformer([
        ('num', Pipeline([('scaler', StandardScaler())]), num_features),
        ('cat', Pipeline([('onehot', OneHotEncoder(handle_unknown='ignore'))]), cat_features),
        ('bin', 'passthrough', ['hypertension', 'heart_disease'])
    ])

    X_processed = preprocessor.fit_transform(X)

    n_clusters = st.slider("Chọn số cụm", 2, 8, 4, key="n_clusters")
    
    with st.spinner("Đang phân cụm..."):
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(X_processed)
        df_cluster['Cụm'] = clusters.astype(str)  # Ép thành string để tránh lỗi

    # Biểu đồ phân bố cụm
    fig1 = px.histogram(df_cluster, x='Cụm', color='stroke', barmode='group',
                        title="Phân bố cụm theo tình trạng Đột quỵ",
                        color_discrete_sequence=['#636EFA', '#EF553B'])
    st.plotly_chart(fig1, use_container_width=True)

    # Hồ sơ cụm
    st.subheader("Hồ sơ trung bình từng cụm")
    profile = df_cluster.groupby('Cụm').agg({
        'age': 'mean', 'avg_glucose_level': 'mean', 'bmi': 'mean',
        'hypertension': 'mean', 'heart_disease': 'mean', 'stroke': 'mean'
    }).round(2)
    profile.rename(columns={
        'age': 'Tuổi TB', 'avg_glucose_level': 'Đường huyết TB', 'bmi': 'BMI TB',
        'hypertension': 'Tăng HA (%)', 'heart_disease': 'Bệnh tim (%)', 'stroke': 'Đột quỵ (%)'
    }, inplace=True)
    profile[['Tăng HA (%)', 'Bệnh tim (%)', 'Đột quỵ (%)']] *= 100
    st.dataframe(profile.style.background_gradient(cmap='Reds'), use_container_width=True)

    # Biểu đồ scatter – ĐÃ SỬA LỖI HOÀN TOÀN
    st.subheader("Phân cụm: Tuổi vs Đường huyết")
    fig2 = px.scatter(df_cluster, x='age', y='avg_glucose_level',
                      color='Cụm', size='bmi', symbol='stroke',
                      hover_data=['gender', 'smoking_status', 'work_type'],
                      title="Cụm bệnh nhân: Tuổi vs Đường huyết (kích thước = BMI)",
                      color_discrete_sequence=px.colors.qualitative.Set1)
    st.plotly_chart(fig2, use_container_width=True)

elif page == "Trực quan hóa nâng cao":
    st.header("5. Trực quan hóa nâng cao")

    # Pie chart
    stroke_counts = df['stroke'].value_counts()
    fig = px.pie(values=stroke_counts.values,
                 names=['Không đột quỵ', 'Có đột quỵ'],
                 title="Tỷ lệ đột quỵ trong tập dữ liệu",
                 hole=0.4, color_discrete_sequence=['#636EFA', '#EF553B'])
    st.plotly_chart(fig, use_container_width=True)

    # Box plot
    for col in ['age', 'avg_glucose_level', 'bmi']:
        fig = px.box(df, x='stroke', y=col, color='stroke',
                     title=f"{col.replace('_', ' ')} theo Đột quỵ")
        st.plotly_chart(fig, use_container_width=True)

elif page == "Bảng tóm tắt nguy cơ":
    st.header("6. Bảng tóm tắt nguy cơ đột quỵ")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Theo nhóm tuổi")
        df['Nhóm tuổi'] = pd.cut(df['age'], [0,18,35,50,65,120],
                                 labels=['0-18','19-35','36-50','51-65','66+'])
        tbl = df.groupby('Nhóm tuổi', observed=False)['stroke'].agg(['count','mean','sum'])
        tbl['mean'] = (tbl['mean']*100).round(2)
        tbl.rename(columns={'count':'Tổng','mean':'Tỷ lệ (%)','sum':'Số ca'}, inplace=True)
        st.dataframe(tbl, use_container_width=True)

    with col2:
        st.subheader("Theo hút thuốc")
        tbl2 = df.groupby('smoking_status')['stroke'].agg(['count','mean','sum'])
        tbl2['mean'] = (tbl2['mean']*100).round(2)
        tbl2.rename(columns={'count':'Tổng','mean':'Tỷ lệ (%)','sum':'Số ca'}, inplace=True)
        st.dataframe(tbl2, use_container_width=True)

st.caption("Dashboard đã được sửa hoàn chỉnh – Không còn lỗi NaN, không còn biểu đồ kẻ ngang!")