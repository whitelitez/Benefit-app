import os
import streamlit as st
import pandas as pd
import numpy as np

# Get the absolute path to the Excel file
FILE_PATH = os.path.join(os.path.dirname(__file__), "正味の益計算表.xlsx")

# Load Excel file directly from the app's directory
@st.cache_data
def load_data():
    xls = pd.ExcelFile(FILE_PATH)
    return {sheet: xls.parse(sheet) for sheet in xls.sheet_names}

# Load the data once at startup
data = load_data()

# App UI
st.title("Stroke Prevention Decision Tool")
st.write("Understand your stroke prevention treatment options based on research data.")

st.sidebar.header("Patient Data Input")
age = st.sidebar.slider("Age", 18, 100, 50)
conditions = st.sidebar.multiselect("Existing Health Conditions", ["Hypertension", "Diabetes", "Smoking", "Obesity"])
medications = st.sidebar.text_input("Current Medications")
risk_factors = st.sidebar.multiselect("Other Risk Factors", ["Family History", "High Cholesterol", "Physical Inactivity"])

if st.sidebar.button("Submit"):
    st.subheader("Treatment Options Based on Your Data")
    st.write("The system is calculating your risk and benefit scores...")

    # Dummy placeholder logic, replace with real formulas from the Excel files
    treatment_options = ["Medication A", "Medication B", "Lifestyle Change"]
    effectiveness = np.random.randint(50, 90, size=len(treatment_options))
    risk = np.random.randint(5, 20, size=len(treatment_options))
    confidence_interval = [(eff - 5, eff + 5) for eff in effectiveness]

    df = pd.DataFrame({
        "Treatment": treatment_options,
        "Effectiveness per 1000 Patients": effectiveness,
        "Risk Level": risk,
        "Confidence Interval": confidence_interval
    })

    st.table(df)

    st.subheader("Threshold Analysis")
    st.write("This section will highlight whether treatment benefits are within a confident range.")
    # Placeholder for threshold calculation
    st.write("Threshold status: **Stable** (Within safe benefit range)")

    st.subheader("Final Recommendation")
    st.write("Based on the calculations, you may consider Treatment X. Consult your doctor for final decision.")
    st.button("Start Over")
