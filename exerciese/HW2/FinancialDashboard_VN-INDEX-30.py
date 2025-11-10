import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ============================
# VN30 Financial Dashboard
# - Giữ các tab chính: Summary, Chart, Statistics, Financials, Analysis,
#   Monte Carlo Simulation, Your Portfolio's Trend
# - Hỗ trợ: upload danh sách mã VN30 (txt/csv) hoặc dùng danh sách mặc định
# - Sử dụng yfinance với hậu tố .VN (nếu cần). Data VN có thể bị thiếu trên Yahoo.
# ============================

# Danh sách VN30 mẫu (cập nhật theo thực tế nếu bạn có file chính xác)
DEFAULT_VN30 = [
    "VIC","VHM","VNM","MWG","VCB","VPB","CTG","BID","TPB","HDB",
    "MSN","FPT","PNJ","SSI","VRE","GAS","PLX","BVH","NVL","KDH",
    "SAB","VJC","MWG","TPB","TCH","PNJ","HSG","VIB","STB","MWG"
]

# ============================
# Lấy danh sách tickers (VN30) — có thể upload file txt/csv 1 mã/1 dòng
# ============================
@st.cache_data(ttl=3600)
def load_ticker_list_from_file(uploaded):
    try:
        # thử đọc csv đơn giản
        df = pd.read_csv(uploaded, header=None)
        lst = df[0].astype(str).str.strip().tolist()
        return ['-'] + [x for x in lst if x]
    except Exception:
        txt = uploaded.getvalue().decode('utf-8').splitlines()
        lst = [t.strip() for t in txt if t.strip()]
        return ['-'] + lst

# ============================
# Hỗ trợ đọc CSV lịch sử từ ./data/<TICKER>.csv (nếu bạn đặt dữ liệu cục bộ)
# ============================
@st.cache_data(ttl=3600)
def load_local_csv(ticker):
    path = f"./data/{ticker}.csv"
    try:
        df = pd.read_csv(path)
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
            # loại timezone nếu có
            if hasattr(df['Date'].dt, 'tz'):
                df['Date'] = df['Date'].dt.tz_localize(None)
        return df.sort_values('Date')
    except Exception:
        return pd.DataFrame()

# ============================
# Sidebar: cài đặt chung + chọn ticker + upload danh sách mã
# ============================
st.sidebar.title("Cài đặt VN30 Dashboard")

# upload danh sách mã VN30 (tùy chọn)
upload_tick_list = st.sidebar.file_uploader("Tải lên danh sách mã VN30 (txt/csv, mỗi dòng 1 mã)", type=['txt','csv'])
if upload_tick_list is not None:
    ticker_list = load_ticker_list_from_file(upload_tick_list)
else:
    ticker_list = ['-'] + DEFAULT_VN30

# chọn ticker chung cho các tab
ticker = st.sidebar.selectbox("Select Ticker", ticker_list, index=0)

# bật/tắt đọc dữ liệu local ./data/
use_local_data = st.sidebar.checkbox("Dùng dữ liệu trong ./data/ nếu có", value=True)

# Navigation tabs (giữ các tab chính)
tabs = st.sidebar.radio("Navigation", [
    'Summary', 'Chart', 'Statistics', 'Financials',
    'Analysis', 'Monte Carlo Simulation', "Your Portfolio's Trend"
])

# ============================
# Hàm lấy dữ liệu lịch sử theo ticker (ưu tiên local upload -> ./data -> yfinance)
# ============================
def get_history(ticker_symbol, start=None, end=None, period=None, interval='1d'):
    # cố gắng đọc local CSV nếu bật
    if use_local_data:
        df_local = load_local_csv(ticker_symbol)
        if not df_local.empty:
            return df_local

    # fallback: dùng yfinance, thêm .VN nếu cần
    yf_sym = ticker_symbol if ticker_symbol.endswith('.VN') else f"{ticker_symbol}.VN"
    try:
        if period is not None and period != '-':
            hist = yf.Ticker(yf_sym).history(period=period, interval=interval, auto_adjust=False)
        else:
            hist = yf.Ticker(yf_sym).history(start=start, end=end, interval=interval, auto_adjust=False)
        if not hist.empty:
            hist = hist.reset_index()
            # chuẩn hóa cột Date, bỏ timezone nếu có
            hist['Date'] = pd.to_datetime(hist['Date'])
            if hasattr(hist['Date'].dt, 'tz'):
                hist['Date'] = hist['Date'].dt.tz_localize(None)
            return hist
    except Exception:
        # thử dùng ticker không .VN (nếu user chọn đã có hậu tố)
        try:
            hist = yf.Ticker(ticker_symbol).history(start=start, end=end, interval=interval, auto_adjust=False)
            if not hist.empty:
                hist = hist.reset_index()
                hist['Date'] = pd.to_datetime(hist['Date'])
                if hasattr(hist['Date'].dt, 'tz'):
                    hist['Date'] = hist['Date'].dt.tz_localize(None)
                return hist
        except Exception:
            pass
    return pd.DataFrame()

# ============================
# Tab 1: Summary
# ============================
def tab_summary():
    st.title("Summary")
    st.write(f"Ticker: **{ticker}**")
    if ticker in ['-', '']:
        st.info("Vui lòng chọn mã cổ phiếu.")
        return

    # Thử load thông tin cơ bản từ yfinance
    yf_sym = ticker if ticker.endswith('.VN') else f"{ticker}.VN"
    try:
        stock = yf.Ticker(yf_sym)
        info = stock.info
    except Exception:
        info = {}

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Thông tin cơ bản")
        summary_data = {
            "Previous Close": info.get("previousClose", "N/A"),
            "Open": info.get("open", "N/A"),
            "Day's Range": f"{info.get('dayLow', 'N/A')} - {info.get('dayHigh', 'N/A')}",
            "52 Week Range": f"{info.get('fiftyTwoWeekLow', 'N/A')} - {info.get('fiftyTwoWeekHigh', 'N/A')}",
            "Volume": info.get("volume", "N/A"),
            "Market Cap": info.get("marketCap", "N/A"),
        }
        df1 = pd.DataFrame(list(summary_data.items()), columns=["Attribute", "Value"])
        st.table(df1)

    with c2:
        st.subheader("Tóm tắt phân tích")
        rec = info.get("recommendationKey", "N/A")
        st.write(f"Recommendation: **{rec}**")
        st.write("Các thông số khác (nếu có):")
        df2 = pd.DataFrame(list(info.items())[:10], columns=["K", "V"])
        st.dataframe(df2)

    # Biểu đồ giá ngắn
    with st.spinner("Đang tải dữ liệu lịch sử..."):
        hist = get_history(ticker, period='1y', interval='1d')
        if hist.empty:
            st.warning("Không có dữ liệu lịch sử (upload CSV hoặc kiểm tra ./data/).")
        else:
            hist['SMA50'] = hist['Close'].rolling(window=50).mean()
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.add_trace(go.Scatter(x=hist['Date'], y=hist['Close'], name='Close'), secondary_y=False)
            fig.add_trace(go.Scatter(x=hist['Date'], y=hist['SMA50'], name='SMA50', line=dict(dash='dash')), secondary_y=False)
            if 'Volume' in hist.columns:
                fig.add_trace(go.Bar(x=hist['Date'], y=hist['Volume'], name='Volume', opacity=0.3), secondary_y=True)
            fig.update_layout(title=f"{ticker} - Giá lịch sử (1y)", xaxis_rangeslider_visible=False, height=500)
            st.plotly_chart(fig, use_container_width=True)

# ============================
# Tab 2: Chart
# ============================
def tab_chart():
    st.title("Chart")
    st.write(f"Ticker: **{ticker}**")
    if ticker in ['-', '']:
        st.info("Vui lòng chọn mã.")
        return

    # controls
    c1, c2, c3 = st.columns([1,1,1])
    with c1:
        start = st.date_input("Start date", datetime.today().date() - timedelta(days=180))
    with c2:
        end = st.date_input("End date", datetime.today().date())
    with c3:
        period = st.selectbox("Period (tùy chọn)", ['-', '1mo', '3mo', '6mo', '1y', '3y', '5y', 'max'], index=0)

    interval = st.selectbox("Interval", ['1d','1wk','1mo'], index=0)
    plot_type = st.selectbox("Plot type", ['Line','Candle'], index=0)

    df = get_history(ticker, start=start, end=end, period=(None if period=='-' else period), interval=interval)
    if df.empty:
        st.warning("Không có dữ liệu cho khoảng chọn.")
        return

    df['SMA50'] = df['Close'].rolling(50).mean()

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    if plot_type == 'Line':
        fig.add_trace(go.Scatter(x=df['Date'], y=df['Close'], name='Close'), secondary_y=False)
    else:
        fig.add_trace(go.Candlestick(x=df['Date'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='OHLC'), secondary_y=False)
    fig.add_trace(go.Scatter(x=df['Date'], y=df['SMA50'], name='SMA50', line=dict(dash='dash')), secondary_y=False)
    if 'Volume' in df.columns:
        fig.add_trace(go.Bar(x=df['Date'], y=df['Volume'], name='Volume', opacity=0.3), secondary_y=True)

    fig.update_layout(title=f"{ticker} - Chart", xaxis_rangeslider_visible=False, height=600)
    st.plotly_chart(fig, use_container_width=True)

# ============================
# Tab 3: Statistics
# ============================
def tab_statistics():
    st.title("Statistics")
    st.write(f"Ticker: **{ticker}**")
    if ticker in ['-', '']:
        st.info("Chọn mã để xem thống kê.")
        return

    df = get_history(ticker, period='1y', interval='1d')
    if df.empty:
        st.warning("Không có dữ liệu lịch sử.")
        return

    # chuẩn hóa Date
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)

    returns = df['Close'].pct_change().dropna()
    total_return = (df['Close'].iloc[-1] / df['Close'].iloc[0] - 1) if len(df)>1 else np.nan
    ann_return = (1 + total_return) ** (252 / len(returns)) - 1 if len(returns)>0 else np.nan
    vol = returns.std() * np.sqrt(252)
    max_dd = (df['Close'] / df['Close'].cummax() - 1).min()

    st.metric("Total Return", f"{total_return:.2%}" if not pd.isna(total_return) else "N/A")
    st.metric("Annualized Return (est)", f"{ann_return:.2%}" if not pd.isna(ann_return) else "N/A")
    st.metric("Annualized Vol", f"{vol:.2%}" if not pd.isna(vol) else "N/A")
    st.metric("Max Drawdown", f"{max_dd:.2%}" if not pd.isna(max_dd) else "N/A")

    st.subheader("Return distribution")
    st.histbar(returns.dropna(), bins=30) if hasattr(st, 'histbar') else st.write(returns.describe())

# ============================
# Tab 4: Financials
# ============================
def tab_financials():
    st.title("Financials")
    st.write(f"Ticker: **{ticker}**")
    if ticker in ['-', '']:
        st.info("Chọn mã để xem báo cáo tài chính.")
        return

    yf_sym = ticker if ticker.endswith('.VN') else f"{ticker}.VN"
    stock = yf.Ticker(yf_sym)
    statement = st.selectbox("Statement", ['Income Statement','Balance Sheet','Cash Flow'])
    period = st.selectbox("Period", ['Yearly','Quarterly'])
    try:
        if statement == 'Income Statement':
            df = stock.financials if period=='Yearly' else stock.quarterly_financials
        elif statement == 'Balance Sheet':
            df = stock.balance_sheet if period=='Yearly' else stock.quarterly_balance_sheet
        else:
            df = stock.cashflow if period=='Yearly' else stock.quarterly_cashflow

        if df is None or df.empty:
            st.warning("No financial data available for this ticker (VN data often missing on yfinance).")
        else:
            st.dataframe(df)
    except Exception as e:
        st.error(f"Lỗi khi tải financials: {e}")

# ============================
# Tab 5: Analysis (ví dụ: recommendations / correlation placeholder)
# ============================
def tab_analysis():
    st.title("Analysis")
    st.write(f"Ticker: **{ticker}**")
    if ticker in ['-', '']:
        st.info("Chọn mã để phân tích.")
        return

    # Thử lấy recommendations (nếu yfinance có)
    try:
        yf_sym = ticker if ticker.endswith('.VN') else f"{ticker}.VN"
        recs = yf.Ticker(yf_sym).recommendations
        if recs is None or recs.empty:
            st.info("Không có dữ liệu khuyến nghị từ yfinance.")
        else:
            st.dataframe(recs.tail(20))
    except Exception:
        st.info("Không có dữ liệu phân tích (yfinance không hỗ trợ cho nhiều mã VN).")

# ============================
# Tab 6: Monte Carlo Simulation
# ============================
def tab_monte_carlo():
    st.title("Monte Carlo Simulation")
    st.write(f"Ticker: **{ticker}**")
    if ticker in ['-', '']:
        st.info("Chọn mã để chạy mô phỏng.")
        return

    sims = st.selectbox("Simulations", [100, 500, 1000], index=0)
    days = st.selectbox("Days ahead", [30, 60, 90], index=0)

    if st.button("Run Simulation"):
        hist = get_history(ticker, period='90d', interval='1d')
        if hist.empty or 'Close' not in hist.columns:
            st.error("Không đủ dữ liệu để chạy mô phỏng.")
            return

        returns = hist['Close'].pct_change().dropna()
        vol = returns.std()
        last_price = hist['Close'].iloc[-1]

        sim_matrix = np.zeros((days, sims))
        for i in range(sims):
            price = last_price
            for d in range(days):
                shock = np.random.normal(0, vol)
                price = price * (1 + shock)
                sim_matrix[d, i] = price

        sim_df = pd.DataFrame(sim_matrix)
        fig, ax = plt.subplots(figsize=(10,5))
        ax.plot(sim_df, linewidth=0.6, alpha=0.6)
        ax.axhline(last_price, color='red', label='Current')
        ax.set_title(f"Monte Carlo ({ticker})")
        ax.set_xlabel("Days")
        ax.set_ylabel("Price")
        ax.legend()
        st.pyplot(fig)

# ============================
# Tab 7: Your Portfolio's Trend (chuẩn hóa 100%)
# ============================
def tab_portfolio_trend():
    st.title("Your Portfolio's Trend")
    st.write(f"Ticker: **{ticker}**")
    if ticker in ['-', '']:
        st.info("Chọn mã để xem xu hướng.")
        return

    period = st.selectbox("Period", ['1Y','3Y','5Y','MAX'], index=0)
    try:
        if period == '1Y':
            start = datetime.now() - timedelta(days=365)
        elif period == '3Y':
            start = datetime.now() - timedelta(days=365*3)
        elif period == '5Y':
            start = datetime.now() - timedelta(days=365*5)
        else:
            start = None

        df = get_history(ticker, start=start, end=datetime.now(), period=None, interval='1d')
        if df.empty or 'Close' not in df.columns:
            st.error("Không tải được dữ liệu.")
            return

        close = df['Close'].dropna()
        df_norm = close / close.iloc[0] * 100
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['Date'], y=df_norm, mode='lines', name=ticker))
        fig.update_layout(title=f"Xu hướng {ticker} (chuẩn hóa 100%)", height=600)
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Lỗi: {e}")

# ============================
# Main runner
# ============================
def run_app():
    st.set_page_config(page_title="VN30 Financial Dashboard", layout="wide")
    st.title("VN30 Financial Dashboard - Các tab chính")

    if tabs == 'Summary':
        tab_summary()
    elif tabs == 'Chart':
        tab_chart()
    elif tabs == 'Statistics':
        tab_statistics()
    elif tabs == 'Financials':
        tab_financials()
    elif tabs == 'Analysis':
        tab_analysis()
    elif tabs == 'Monte Carlo Simulation':
        tab_monte_carlo()
    elif tabs == "Your Portfolio's Trend":
        tab_portfolio_trend()

if __name__ == "__main__":
    run_app()
