import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# ------------- PAGE CONFIG -------------
st.set_page_config(page_title="Global & Indian Stock Dashboard", layout="wide")

# ------------- CUSTOM CSS -------------
st.markdown("""
<style>
body { background-color: #f7f7f7; }
.big-title { font-size: 36px; font-weight: 700; color: #1a237e; }
.section-header { font-size: 22px; font-weight: 600; margin-top: 20px; }
.card { padding: 15px; background: white; border-radius: 10px; box-shadow: 0px 2px 8px rgba(0,0,0,0.1); }
</style>
""", unsafe_allow_html=True)

# ------------- STOCK INDEX DICTIONARIES -------------

world_indices = {
    "S&P 500 (US)": "^GSPC",
    "NASDAQ (US)": "^IXIC",
    "Dow Jones (US)": "^DJI",
    "FTSE 100 (UK)": "^FTSE",
    "Nikkei 225 (Japan)": "^N225",
    "Hang Seng (Hong Kong)": "^HSI",
    "DAX (Germany)": "^GDAXI",
    "CAC 40 (France)": "^FCHI"
}

indian_indices = {
    "NIFTY 50": "^NSEI",
    "SENSEX": "^BSESN",
    "NIFTY BANK": "^NSEBANK",
}


# ------------ HEADER ---------------
st.markdown("<div class='big-title'>🌍 Global + 🇮🇳 Indian Stock Market Dashboard</div>", unsafe_allow_html=True)
st.write("---")

# ------------ SIDEBAR ---------------
st.sidebar.header("Select Markets")

market_choice = st.sidebar.radio("Choose a Market", ["World Indices", "Indian Indices"])

if market_choice == "World Indices":
    index_dict = world_indices
else:
    index_dict = indian_indices

index_name = st.sidebar.selectbox("Select Index", list(index_dict.keys()))
ticker_symbol = index_dict[index_name]

period = st.sidebar.selectbox("Select Time Period", ["1y", "2y", "5y", "10y", "max"])
st.sidebar.write("Data Powered by Yahoo Finance")

# ------------ DOWNLOAD DATA ---------------
@st.cache_data
def load_data(ticker, period):
    data = yf.download(ticker, period=period)
    data["MA20"] = data["Close"].rolling(20).mean()
    data["MA50"] = data["Close"].rolling(50).mean()
    data["Returns"] = data["Close"].pct_change()
    return data

df = load_data(ticker_symbol, period)

# ------------ PRICE CHART ---------------
st.markdown("<div class='section-header'>📈 Price Chart with Moving Averages</div>", unsafe_allow_html=True)

fig = go.Figure()
fig.add_trace(go.Scatter(x=df.index, y=df["Close"], mode='lines', name="Close Price"))
fig.add_trace(go.Scatter(x=df.index, y=df["MA20"], mode='lines', name="MA20"))
fig.add_trace(go.Scatter(x=df.index, y=df["MA50"], mode='lines', name="MA50"))
fig.update_layout(height=500, template="plotly_white")

st.plotly_chart(fig, use_container_width=True)

# ------------ RSI CALCULATION -----------
def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = -delta.where(delta < 0, 0).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

df["RSI"] = compute_rsi(df["Close"])

st.markdown("<div class='section-header'>📉 RSI (Relative Strength Index)</div>", unsafe_allow_html=True)
fig_rsi = go.Figure()
fig_rsi.add_trace(go.Scatter(x=df.index, y=df["RSI"], mode='lines', name='RSI'))
fig_rsi.update_layout(height=300, template="plotly_white")
st.plotly_chart(fig_rsi, use_container_width=True)

# ------------ DRAWDOWN -----------
st.markdown("<div class='section-header'>📉 Drawdown Analysis</div>", unsafe_allow_html=True)

df["Peak"] = df["Close"].cummax()
df["Drawdown"] = (df["Close"] - df["Peak"]) / df["Peak"] * 100

fig_dd = px.area(df, x=df.index, y="Drawdown")
fig_dd.update_layout(height=300, template="plotly_white")
st.plotly_chart(fig_dd, use_container_width=True)

# ------------ CORRELATION MATRIX -----------
st.markdown("<div class='section-header'>🔗 Correlation Matrix (Daily Returns)</div>", unsafe_allow_html=True)

# Download multiple indexes at once
all_returns = {}

for name, symbol in index_dict.items():
    temp = yf.download(symbol, period="1y")["Close"].pct_change()
    all_returns[name] = temp

corr_df = pd.DataFrame(all_returns).corr()

fig_corr = px.imshow(corr_df, text_auto=True, aspect="auto", color_continuous_scale="Viridis")
st.plotly_chart(fig_corr, use_container_width=True)

# Guidance
st.markdown("""<div class='card'>
<b>How to read this dashboard:</b><br>
- Moving averages help you identify long vs short-term trends.<br>
- RSI shows oversold (<30) and overbought (>70) zones.<br>
- Drawdown reveals historical worst declines.<br>
- Correlation matrix shows how markets move relative to each other.
</div>
""", unsafe_allow_html=True)
