import streamlit as st
import pandas as pd
import numpy as np

# ---------- Functions ----------
@st.cache_data
def load_csv(file):
    df = pd.read_csv(file)
    return df['multiplier'].tolist()

def compute_advanced_confidence(data, threshold=2.0, trend_window=5):
    if not data:
        return 0.5, 0.5, "Neutral"

    data = np.array(data)
    # Base frequency
    above = np.sum(data > threshold)
    under = np.sum(data <= threshold)
    total = above + under
    base_above = above / total

    # Recent trend
    recent = data[-trend_window:] if len(data) >= trend_window else data
    recent_above = np.sum(recent > threshold)
    recent_under = np.sum(recent <= threshold)

    trend_bias = 0
    if recent_under > recent_above:
        trend_bias = 0.05
    elif recent_above > recent_under:
        trend_bias = -0.05

    # Streak adjustment
    streak_bias = 0
    streak = 1
    for i in range(len(data)-2, -1, -1):
        if (data[i] > threshold and data[i+1] > threshold) or (data[i] <= threshold and data[i+1] <= threshold):
            streak += 1
        else:
            break
    if streak >= 3:
        if data[-1] <= threshold:
            streak_bias = 0.08
        else:
            streak_bias = -0.08

    above_conf = min(max(base_above + trend_bias + streak_bias, 0), 1)
    under_conf = 1 - above_conf

    return above_conf, under_conf

def main():
    st.title("Crash Game Predictor (Simplified)")

    st.write("Upload a CSV or enter values manually. Uses frequency, trends, and streaks.")

    # Upload CSV
    uploaded_file = st.file_uploader("Upload multipliers CSV", type=["csv"])
    data = []
    if uploaded_file:
        data = load_csv(uploaded_file)
        st.success(f"Loaded {len(data)} multipliers from file.")

    # Manual input
    st.subheader("Manual Input")
    new_val = st.text_input("Enter a new multiplier (e.g., 1.87)")
    if st.button("Add to history"):
        try:
            val = float(new_val)
            data.append(val)
            st.success(f"Added {val} to history")
        except:
            st.error("Invalid number.")

    # Compute confidence and make prediction
    if data:
        above_conf, under_conf = compute_advanced_confidence(data)
        st.subheader("Prediction Result")
        if above_conf > under_conf:
            st.write(f"Prediction: **Above 200%** ({above_conf:.1%} confidence)")
        else:
            st.write(f"Prediction: **Under 200%** ({under_conf:.1%} confidence)")
    else:
        st.write("Add data to see prediction.")

if __name__ == "__main__":
    main()
