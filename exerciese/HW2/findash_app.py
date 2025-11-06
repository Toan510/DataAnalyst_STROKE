import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests

# ==============================================================================
# Lấy danh sách S&P 500 (cache 1 ngày)
# ==============================================================================
@st.cache_data(ttl=86400)
def get_sp500_tickers():
    try:
        df = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies", header=0)[0]
        symbols = df['Symbol'].str.replace('.', '-').tolist()
        return ['-'] + sorted(symbols)
    except:
        # Không hiện st.warning ở đây → chỉ trả về mặc định
        return ['-', 'AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA', 'META', 'AMD', 'NFLX']

# ==============================================================================
# Tab 1: Summary
# ==============================================================================
def tab1():
    st.title("Summary")
    st.write("Select ticker on the left to begin")
    st.write(f"**{ticker}**")

    if ticker == '-' or ticker == '':
        st.info("Please select a valid ticker.")
        return

    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        c1, c2 = st.columns(2)

        with c1:
            summary_data = {
                "Previous Close": info.get("previousClose", "N/A"),
                "Open": info.get("open", "N/A"),
                "Day's Range": f"{info.get('dayLow', 'N/A')} - {info.get('dayHigh', 'N/A')}",
                "52 Week Range": f"{info.get('fiftyTwoWeekLow', 'N/A')} - {info.get('fiftyTwoWeekHigh', 'N/A')}",
                "Volume": info.get("volume", "N/A"),
                "Avg. Volume": info.get("averageVolume", "N/A"),
                "Market Cap": info.get("marketCap", "N/A"),
                "P/E Ratio": info.get("trailingPE", "N/A"),
            }
            df1 = pd.DataFrame(list(summary_data.items()), columns=["Attribute", "Value"])
            st.dataframe(df1, use_container_width=True)

        with c2:
            summary_data2 = {
                "Beta": info.get("beta", "N/A"),
                "EPS (TTM)": info.get("trailingEps", "N/A"),
                "Forward P/E": info.get("forwardPE", "N/A"),
                "Dividend Yield": info.get("dividendYield", "N/A"),
                "Ex-Dividend Date": info.get("exDividendDate", "N/A"),
                "Target Mean Price": info.get("targetMeanPrice", "N/A"),
                "Recommendation": info.get("recommendationKey", "N/A").title(),
                "Number of Analysts": info.get("numberOfAnalystOpinions", "N/A"),
            }
            df2 = pd.DataFrame(list(summary_data2.items()), columns=["Attribute", "Value"])
            st.dataframe(df2, use_container_width=True)

        # Chart lịch sử giá
        with st.spinner("Loading price chart..."):
            data = stock.history(period="max")
            if not data.empty:
                fig = px.area(data, x=data.index, y="Close", title=f"{ticker} - Historical Close Price")
                fig.update_xaxes(
                    rangeselector=dict(
                        buttons=list([
                            dict(count=1, label="1M", step="month", stepmode="backward"),
                            dict(count=3, label="3M", step="month", stepmode="backward"),
                            dict(count=6, label="6M", step="month", stepmode="backward"),
                            dict(count=1, label="YTD", step="year", stepmode="todate"),
                            dict(count=1, label="1Y", step="year", stepmode="backward"),
                            dict(count=5, label="5Y", step="year", stepmode="backward"),
                            dict(step="all", label="MAX")
                        ])
                    )
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No historical data available.")
    except Exception as e:
        st.error(f"Error loading summary: {e}")

# ==============================================================================
# Tab 2: Chart
# ==============================================================================
def tab2():
    st.title("Chart")
    st.write(f"**{ticker}**")
    if ticker in ['-', '']:
        st.info("Select a ticker.")
        return

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        start_date = st.date_input("Start date", datetime.today().date() - timedelta(days=30))
    with c2:
        end_date = st.date_input("End date", datetime.today().date())
    with c3:
        duration = st.selectbox("Duration", ['-', '1Mo', '3Mo', '6Mo', 'YTD', '1Y', '3Y', '5Y', 'MAX'])
    with c4:
        interval = st.selectbox("Interval", ['1d', '1wk', '1mo'])
    with c5:
        plot_type = st.selectbox("Plot", ['Line', 'Candle'])

    @st.cache_data
    def get_chart_data(ticker, start, end, period, interval):
        stock = yf.Ticker(ticker)
        if duration != '-':
            hist = stock.history(period=period.replace('Mo', 'mo'), interval=interval)
        else:
            hist = stock.history(start=start, end=end, interval=interval)
        hist = hist.reset_index()
        hist['SMA50'] = hist['Close'].rolling(window=50).mean()
        return hist

    try:
        data = get_chart_data(ticker, start_date, end_date, duration, interval)
        if data.empty:
            st.warning("No data for selected range.")
            return

        fig = make_subplots(specs=[[{"secondary_y": True}]])

        if plot_type == 'Line':
            fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name='Close'), secondary_y=False)
        else:
            fig.add_trace(go.Candlestick(x=data['Date'],
                                         open=data['Open'], high=data['High'],
                                         low=data['Low'], close=data['Close'], name='OHLC'), secondary_y=False)

        fig.add_trace(go.Scatter(x=data['Date'], y=data['SMA50'], name='50-day SMA', line=dict(dash='dash')), secondary_y=False)
        fig.add_trace(go.Bar(x=data['Date'], y=data['Volume'], name='Volume', opacity=0.3), secondary_y=True)

        fig.update_yaxes(title_text="Price", secondary_y=False)
        fig.update_yaxes(title_text="Volume", secondary_y=True, showticklabels=False)
        fig.update_layout(title=f"{ticker} - {plot_type} Chart", xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error: {e}")

# ==============================================================================
# Tab 3: Statistics
# ==============================================================================
def tab3():
    st.title("Statistics")
    st.write(f"**{ticker}**")
    if ticker in ['-', '']:
        return

    stock = yf.Ticker(ticker)
    info = stock.info

    c1, c2 = st.columns(2)

    with c1:
        st.header("Valuation & Financial Highlights")
        valuation = {
            "Market Cap": info.get("marketCap"),
            "Enterprise Value": info.get("enterpriseValue"),
            "P/E Ratio": info.get("trailingPE"),
            "Forward P/E": info.get("forwardPE"),
            "PEG Ratio": info.get("pegRatio"),
            "Price/Sales": info.get("priceToSalesTrailing12Months"),
            "Price/Book": info.get("priceToBook"),
            "EV/EBITDA": info.get("enterpriseToEbitda"),
        }
        df_val = pd.DataFrame([(k, v) for k, v in valuation.items() if v is not None], columns=["Metric", "Value"])
        st.table(df_val)

        st.subheader("Profitability")
        profit = {
            "Profit Margin": info.get("profitMargins"),
            "Operating Margin": info.get("operatingMargins"),
            "Return on Assets": info.get("returnOnAssets"),
            "Return on Equity": info.get("returnOnEquity"),
        }
        df_profit = pd.DataFrame([(k, f"{v:.2%}" if isinstance(v, float) else v) for k, v in profit.items() if v is not None], columns=["Metric", "Value"])
        st.table(df_profit)

    with c2:
        st.header("Trading Information")
        trading = {
            "52 Week High": info.get("fiftyTwoWeekHigh"),
            "52 Week Low": info.get("fiftyTwoWeekLow"),
            "50 Day Avg": info.get("fiftyDayAverage"),
            "200 Day Avg": info.get("twoHundredDayAverage"),
            "Volume": info.get("volume"),
            "Avg Volume": info.get("averageVolume"),
            "Shares Outstanding": info.get("sharesOutstanding"),
            "Float": info.get("floatShares"),
        }
        df_trading = pd.DataFrame([(k, v) for k, v in trading.items() if v is not None], columns=["Metric", "Value"])
        st.table(df_trading)

        st.subheader("Dividends")
        div = {
            "Forward Dividend": info.get("dividendRate"),
            "Dividend Yield": info.get("dividendYield"),
            "Payout Ratio": info.get("payoutRatio"),
            "Ex-Dividend Date": info.get("exDividendDate"),
        }
        df_div = pd.DataFrame([(k, f"{v:.2%}" if isinstance(v, (int, float)) and 'Yield' in k and v else v) for k, v in div.items() if v is not None], columns=["Metric", "Value"])
        st.table(df_div)

# ==============================================================================
# Tab 4: Financials
# ==============================================================================
def tab4():
    st.title("Financials")
    st.write(f"**{ticker}**")
    if ticker in ['-', '']:
        return

    statement = st.selectbox("Statement", ['Income Statement', 'Balance Sheet', 'Cash Flow'])
    period = st.selectbox("Period", ['Yearly', 'Quarterly'])

    stock = yf.Ticker(ticker)

    try:
        if statement == 'Income Statement':
            df = stock.income_stmt if period == 'Yearly' else stock.quarterly_income_stmt
        elif statement == 'Balance Sheet':
            df = stock.balance_sheet if period == 'Yearly' else stock.quarterly_balance_sheet
        else:
            df = stock.cashflow if period == 'Yearly' else stock.quarterly_cashflow

        if df is not None and not df.empty:
            st.dataframe(df.style.format("{:,.0f}"), use_container_width=True)
        else:
            st.warning("No financial data available.")
    except Exception as e:
        st.error(f"Error: {e}")

# ==============================================================================
# Tab 5: Analysis
# ==============================================================================

def tab5(ticker):
    st.title("Analyst Recommendations Summary")
    st.write(f"**{ticker}**")

    if ticker in ['-', '']:
        st.info("Please enter a valid ticker.")
        return

    try:
        stock = yf.Ticker(ticker)
        recs = stock.recommendations_summary  # 🟢 Lấy dữ liệu tổng hợp khuyến nghị

        if recs is not None and not recs.empty:
            # Hiển thị bảng và biểu đồ
            st.subheader("Analyst Recommendation Summary Table")
            st.dataframe(recs)

            # Nếu có các cột phổ biến thì vẽ biểu đồ
            cols = ['strongBuy', 'buy', 'hold', 'sell', 'strongSell']
            available_cols = [c for c in cols if c in recs.columns]

            if available_cols:
                st.subheader("Recommendation Summary Chart")
                st.bar_chart(recs[available_cols].T)
            else:
                st.info("No standard recommendation columns found for this ticker.")
        else:
            st.info("No analyst summary data available for this stock.")

    except Exception as e:
        st.warning(f"Analyst data not available: {e}")


# ==============================================================================
# Tab 6: Monte Carlo Simulation
# ==============================================================================
def tab6():
    st.title("Monte Carlo Simulation")
    st.write(f"**{ticker}**")
    if ticker in ['-', '']:
        return

    col1, col2 = st.columns(2)
    with col1:
        simulations = st.selectbox("Simulations", [100, 500, 1000], index=1)
    with col2:
        days = st.selectbox("Days Ahead", [30, 60, 90], index=0)

    if st.button("Run Simulation"):
        with st.spinner("Running simulation..."):
            stock = yf.Ticker(ticker)
            hist = stock.history(period="60d")
            if hist.empty:
                st.error("Not enough data.")
                return

            close = hist['Close']
            returns = close.pct_change().dropna()
            vol = returns.std()

            last_price = close.iloc[-1]
            sim_prices = np.zeros((days, simulations))

            for i in range(simulations):
                price = last_price
                for d in range(days):
                    shock = np.random.normal(0, vol)
                    price = price * (1 + shock)
                    sim_prices[d, i] = price

            sim_df = pd.DataFrame(sim_prices)

            fig1, ax1 = plt.subplots(figsize=(12, 6))
            ax1.plot(sim_df, linewidth=0.6, alpha=0.6)
            ax1.axhline(last_price, color='red', linewidth=2, label=f"Current: ${last_price:.2f}")
            ax1.set_title(f"Monte Carlo - {ticker} ({days} days, {simulations} sims)")
            ax1.set_xlabel("Days")
            ax1.set_ylabel("Price ($)")
            ax1.legend()
            st.pyplot(fig1)

            ending = sim_df.iloc[-1]
            var_95 = np.percentile(ending, 5)
            st.write(f"**VaR (95%):** ${last_price - var_95:.2f}")
            st.write(f"**5th Percentile Price:** ${var_95:.2f}")

            fig2, ax2 = plt.subplots(figsize=(10, 5))
            ax2.hist(ending, bins=50, alpha=0.7, color='skyblue', edgecolor='black')
            ax2.axvline(var_95, color='red', linestyle='--', label=f"5th % = ${var_95:.2f}")
            ax2.set_title("Distribution of Ending Prices")
            ax2.legend()
            st.pyplot(fig2)

# ==============================================================================
# Tab 7: Your Portfolio's Trend → Dùng ticker từ sidebar (bỏ multiselect)
# ==============================================================================
def tab7():
    st.title("Your Portfolio's Trend")
    
    if ticker in ['-', ''] or not ticker:
        st.info("Vui lòng chọn một mã chứng khoán từ sidebar.")
        return

    period = st.selectbox("Time Period", ['1Y', '3Y', '5Y', 'MAX'], index=2)

    with st.spinner(f"Đang tải dữ liệu {ticker}..."):
        try:
            # Tính start_date theo period
            end_date = datetime.now()
            if period == '1Y':
                start_date = end_date - timedelta(days=365)
            elif period == '3Y':
                start_date = end_date - timedelta(days=365*3)
            elif period == '5Y':
                start_date = end_date - timedelta(days=365*5)
            else:
                start_date = None  # MAX

            df = yf.download(
                tickers=ticker,
                start=start_date,
                end=end_date,
                progress=False,
                auto_adjust=True
            )

            if df.empty or 'Close' not in df.columns:
                st.error("Không tải được dữ liệu.")
                return

            close = df['Close'].dropna()
            if len(close) < 2:
                st.error("Không đủ dữ liệu để vẽ biểu đồ.")
                return

        except Exception as e:
            st.error("Lỗi khi tải dữ liệu.")
            return

    # Chuẩn hóa về 100%
    df_norm = pd.DataFrame({ticker: close.squeeze()}, index=close.index)
    df_norm_normalized = df_norm.div(df_norm.iloc[0]) * 100

    # Vẽ biểu đồ
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_norm_normalized.index,
        y=df_norm_normalized[ticker],
        mode='lines',
        name=ticker,
        line=dict(width=3, color='#00D9FF'),
        hovertemplate=f"<b>{ticker}</b><br>Ngày: %{{x|%Y-%m-%d}}<br>Giá: $%{{y:.2f}}<extra></extra>"
    ))

    fig.update_layout(
        title=f"Xu hướng giá {ticker} (Chuẩn hóa 100%)",
        xaxis_title="Ngày",
        yaxis_title="Tăng trưởng (%)",
        hovermode="x unified",
        template="plotly_dark",
        height=600
    )

    st.plotly_chart(fig, use_container_width=True)

    # Bảng giá gần đây
    with st.expander("Giá đóng cửa gần đây"):
        st.dataframe(df_norm.tail(10).round(2))
        
# ==============================================================================
# Main App
# ==============================================================================
def run():
    st.set_page_config(page_title="Stock Analyzer", layout="wide")
    global ticker
    ticker_list = get_sp500_tickers()
    ticker = st.sidebar.selectbox("Select Ticker", ticker_list, index=0)

    tabs = st.sidebar.radio("Navigation", [
        'Summary', 'Chart', 'Statistics', 'Financials',
        'Analysis', 'Monte Carlo Simulation', "Your Portfolio's Trend"
    ])

    if tabs == 'Summary': tab1()
    elif tabs == 'Chart': tab2()
    elif tabs == 'Statistics': tab3()
    elif tabs == 'Financials': tab4()
    elif tabs == 'Analysis': tab5(ticker)
    elif tabs == 'Monte Carlo Simulation': tab6()
    elif tabs == "Your Portfolio's Trend": tab7()

if __name__ == "__main__":
    run()