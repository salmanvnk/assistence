import streamlit as st
from breeze_connect import BreezeConnect
import pandas as pd
import datetime
import numpy as np

# --- PAGE SETUP ---
st.set_page_config(page_title="My Private AI Trader", layout="wide")
st.title("⚡ Personal AI Trading Terminal")

# --- SIDEBAR: CREDENTIALS ---
st.sidebar.header("1. Login to ICICI Direct")
api_key = st.sidebar.text_input("App Key", type="password")
secret_key = st.sidebar.text_input("Secret Key", type="password")
session_token = st.sidebar.text_input("Session Token (from login URL)")

# Initialize Breeze
if 'breeze' not in st.session_state:
    st.session_state.breeze = None

def init_connection():
    try:
        breeze = BreezeConnect(api_key=api_key)
        breeze.generate_session(api_secret=secret_key, session_token=session_token)
        st.session_state.breeze = breeze
        st.sidebar.success("Connected to ICICI Breeze!")
    except Exception as e:
        st.sidebar.error(f"Connection Failed: {e}")

if st.sidebar.button("Connect"):
    init_connection()

# --- THE AI ENGINE (The "Brain") ---
def get_ai_prediction(df):
    """
    This is where your 'Perfect' logic goes.
    Currently uses a Momentum Strategy (Simulated AI).
    """
    # Simple Logic: If short moving average crosses long moving average
    df['SMA_5'] = df['close'].rolling(window=5).mean()
    df['SMA_20'] = df['close'].rolling(window=20).mean()
    
    last_row = df.iloc[-1]
    
    if last_row['SMA_5'] > last_row['SMA_20']:
        return "BUY", 0.85  # 85% confidence
    elif last_row['SMA_5'] < last_row['SMA_20']:
        return "SELL", 0.85
    else:
        return "HOLD", 0.0

# --- MAIN INTERFACE ---
st.header("2. Market Analysis & AI Prediction")

stock_code = st.text_input("Stock Symbol (e.g., NIFTY, RELIAN)", "NIFTY")

if st.button("Analyze & Predict"):
    if st.session_state.breeze:
        # Fetch Historical Data (Last 7 days for analysis)
        try:
            # Note: You must adjust dates dynamically in production
            history = st.session_state.breeze.get_historical_data(
                stock_code=stock_code,
                exchange_code="NSE",
                product_type="cash",
                expiry_date="",
                right="",
                strike_price="",
                from_date="2024-01-01T07:00:00.000Z", # Update this
                to_date="2025-11-15T07:00:00.000Z",   # Update this
                interval="1day"
            )
            
            if 'Success' in history:
                df = pd.DataFrame(history['Success'])
                df['close'] = df['close'].astype(float)
                
                st.line_chart(df['close'])
                
                # Run AI
                signal, confidence = get_ai_prediction(df)
                
                st.metric(label="AI Recommendation", value=signal, delta=f"{confidence*100}% Confidence")
                
                if signal == "BUY":
                    st.success("AI detects bullish momentum. Ready to execute?")
                elif signal == "SELL":
                    st.error("AI detects bearish momentum. Ready to execute?")
            else:
                st.error("Error fetching data. Check Stock Symbol.")
                
        except Exception as e:
            st.error(f"Analysis Error: {e}")
    else:
        st.warning("Please connect to API first.")

# --- EXECUTION WITHOUT RESTRICTIONS ---
st.header("3. Instant Execution")
col1, col2 = st.columns(2)

with col1:
    qty = st.number_input("Quantity", min_value=1, value=10)

with col2:
    action = st.radio("Action", ["Buy", "Sell"])

if st.button("EXECUTE ORDER NOW"):
    if st.session_state.breeze:
        try:
            response = st.session_state.breeze.place_order(
                stock_code=stock_code,
                exchange_code="NSE",
                product="cash",
                action=action.lower(),
                order_type="market",
                stoploss="",
                quantity=str(qty),
                price="",
                validity="day"
            )
            st.json(response) # Shows the raw confirmation from ICICI
        except Exception as e:
            st.error(f"Order Failed: {e}")
    else:
        st.error("Not connected!")