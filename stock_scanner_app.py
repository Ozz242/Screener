import streamlit as st
import yfinance as yf
from datetime import datetime
import pytz

# --- Config ---
TRADING_MINUTES = 390

# --- Title ---
st.title("📈 Stock Scanner: Relative Volume 100%–300%")
st.write("Scans for stocks with high relative volume and increasing intraday activity.")

# --- Inputs ---
tickers_input = st.text_input(
    "Enter stock tickers (comma-separated):",
    value="AAPL,TSLA,NVDA,AMD,MSFT,AMZN,GOOGL"
)

tickers = [ticker.strip().upper() for ticker in tickers_input.split(",") if ticker.strip()]

# --- Get current time and elapsed trading minutes ---
now = datetime.now(pytz.timezone('US/Eastern'))
if now.hour < 9 or (now.hour == 9 and now.minute < 30):
    st.warning("Market has not opened yet.")
    st.stop()

elapsed_minutes = max(1, (now.hour - 9) * 60 + (now.minute - 30))
if elapsed_minutes > TRADING_MINUTES:
    elapsed_minutes = TRADING_MINUTES  # Cap it at full day length

# --- Process tickers ---
results = []

for ticker in tickers:
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="2d", interval="1d")
        
        if len(hist) < 2:
            continue

        prev_day_vol = hist['Volume'].iloc[-2]
        curr_day_vol = hist['Volume'].iloc[-1]

        if prev_day_vol == 0:
            continue

        rvol = curr_day_vol / prev_day_vol
        intraday_avg_vol = curr_day_vol / elapsed_minutes
        prev_day_avg_vol = prev_day_vol / TRADING_MINUTES

        if 1.0 <= rvol <= 3.0 and intraday_avg_vol > prev_day_avg_vol:
            results.append({
                "Ticker": ticker,
                "Relative Volume": round(rvol, 2),
                "Intraday Avg Volume": int(intraday_avg_vol),
                "Prev Day Avg Volume": int(prev_day_avg_vol)
            })

    except Exception as e:
        st.error(f"Error processing {ticker}: {e}")

# --- Display Results ---
if results:
    st.success(f"Found {len(results)} matching stocks:")
    st.dataframe(results)
else:
    st.info("No matching stocks found.")
