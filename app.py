import os
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Get the absolute path to the Excel file
FILE_PATH = os.path.join(os.path.dirname(__file__), "net_benefit_rd_md_v0.97.xlsx")

# Load Excel file directly from the app's directory
@st.cache_data
def load_data():
    xls = pd.ExcelFile(FILE_PATH)
    data = {sheet: xls.parse(sheet) for sheet in xls.sheet_names}
    return data

# Load the data once at startup
data = load_data()

def get_treatment_data():
    df = data['RD_信頼区間_相関係数から_比']
    df = df.iloc[3:, [2, 5, 6, 7, 8, 9, 37, 38, 39, 40]]  # Extract relevant columns
    df.columns = ['Outcome', 'Risk Difference', 'Lower CI', 'Upper CI', 'Relative Importance', 'Standardized Importance', 'Threshold Low', 'Threshold High', 'Estimate', 'Net Benefit']
    df.dropna(inplace=True)
    return df

# App UI
st.title("Stroke Prevention Decision Tool")
st.write("Understand your stroke prevention treatment options based on research data.")

st.sidebar.header("Patient Information Input")
age = st.sidebar.slider("Age", 18, 100, 50)
conditions = st.sidebar.multiselect("Existing Health Conditions", ["Hypertension", "Diabetes", "Smoking", "Obesity"])
medications = st.sidebar.text_input("Current Medications")
risk_factors = st.sidebar.multiselect("Other Risk Factors", ["Family History", "High Cholesterol", "Physical Inactivity"])

if st.sidebar.button("Submit"):
    st.subheader("Treatment Options Based on Your Data")
    st.write("The system is calculating your risk and benefit scores...")
    
    treatment_df = get_treatment_data()
    
    st.write("### Treatment Effectiveness")
    st.dataframe(treatment_df[['Outcome', 'Risk Difference', 'Lower CI', 'Upper CI', 'Net Benefit']])

    # Pie Chart Visualization of Treatment Effectiveness
    st.subheader("Treatment Effectiveness (Per 1000 Patients)")
    fig, ax = plt.subplots()
    ax.pie(treatment_df['Net Benefit'], labels=treatment_df['Outcome'], autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    st.pyplot(fig)
    
    st.subheader("Threshold Analysis")
    st.write("This section highlights whether treatment benefits are within a reliable range.")
    st.dataframe(treatment_df[['Outcome', 'Threshold Low', 'Threshold High']])

    st.subheader("Final Recommendation")
    best_treatment = treatment_df.sort_values(by='Net Benefit', ascending=False).iloc[0]
    st.write(f"Based on the calculations, the most recommended treatment is **{best_treatment['Outcome']}**. Please consult your doctor before making a final decision.")
    st.button("Start Over")
