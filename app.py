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
    data = {sheet: xls.parse(sheet, header=2) for sheet in xls.sheet_names}  # Adjusted header row
    return data

# Load the data once at startup
data = load_data()

def get_treatment_data():
    df = data['RD_信頼区間_相関係数から_比']
    
    # Print actual column names for debugging
    st.write("### データセットの実際のカラム名:")
    st.write(df.columns.tolist())
    
    # Dynamically find matching columns to avoid KeyErrors
    expected_cols = ['アウトカムk', 'RDijkまたはMDijk 介入群の絶対リスク-対照群の絶対リスク=Eijk', '95%信頼区間下限値', '95%信頼区間上限値', 'Estimate']
    actual_cols = df.columns.tolist()
    col_mapping = {col: next((actual for actual in actual_cols if col in actual), None) for col in expected_cols}
    
    # Ensure all expected columns exist
    missing_cols = [col for col in expected_cols if col_mapping[col] is None]
    if missing_cols:
        st.error(f"以下のカラムが見つかりません: {missing_cols}")
        return pd.DataFrame()  # Return an empty DataFrame to prevent crash
    
    # Extract relevant columns
    df = df[[col_mapping[col] for col in expected_cols]]
    df.columns = ['Outcome', 'Risk Difference', 'Lower CI', 'Upper CI', 'Net Benefit']
    df.dropna(subset=['Outcome'], inplace=True)
    
    # Convert numeric columns
    numeric_cols = ['Risk Difference', 'Lower CI', 'Upper CI', 'Net Benefit']
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')
    
    # Normalize Net Benefit values
    max_benefit = df['Net Benefit'].max()
    min_benefit = df['Net Benefit'].min()
    if max_benefit != min_benefit:
        df['Normalized Net Benefit'] = (df['Net Benefit'] - min_benefit) / (max_benefit - min_benefit)
    else:
        df['Normalized Net Benefit'] = 1

    # Categorize Benefit Levels
    def classify_benefit(value):
        if value >= 0.07:
            return "高い利益 (High Benefit)"
        elif value >= 0.03:
            return "中程度の利益 (Moderate Benefit)"
        elif value >= 0.00:
            return "低い利益 (Low Benefit)"
        else:
            return "利益なし (No Benefit)"
    
    df['Benefit Category'] = df['Net Benefit'].apply(classify_benefit)
    return df

# App UI
st.title("脳卒中予防の意思決定ツール")
st.write("研究データに基づいた脳卒中予防治療の選択肢を理解しましょう。")

st.sidebar.header("患者情報入力")
age = st.sidebar.slider("年齢", 18, 100, 50)
conditions = st.sidebar.multiselect("既存の健康状態", ["高血圧", "糖尿病", "喫煙", "肥満"])
medications = st.sidebar.text_input("現在の服用薬")
risk_factors = st.sidebar.multiselect("その他のリスク要因", ["家族歴", "高コレステロール", "運動不足"])

# User-friendly input fields
st.sidebar.subheader("カスタムデータ入力")
custom_risk_difference = st.sidebar.select_slider("リスク差のカスタム値", options=[-0.1, -0.05, 0.0, 0.05, 0.1, 0.15, 0.2], value=0.0)
custom_lower_ci = st.sidebar.select_slider("信頼区間下限のカスタム値", options=[-0.1, -0.05, 0.0, 0.05, 0.1], value=0.0)
custom_upper_ci = st.sidebar.select_slider("信頼区間上限のカスタム値", options=[0.0, 0.05, 0.1, 0.15, 0.2], value=0.1)
custom_net_benefit = st.sidebar.select_slider("ネットベネフィットのカスタム値", options=[-0.1, 0.0, 0.05, 0.1, 0.2], value=0.0)

if st.sidebar.button("送信"):
    st.subheader("あなたのデータに基づく治療オプション")
    st.write("システムがリスクとベネフィットスコアを計算しています...")
    
    treatment_df = get_treatment_data()
    
    if treatment_df.empty:
        st.write("データの読み込みに失敗しました。適切なデータセットを確認してください。")
    else:
        # Apply custom user inputs
        treatment_df.at[0, 'Risk Difference'] = custom_risk_difference
        treatment_df.at[0, 'Lower CI'] = custom_lower_ci
        treatment_df.at[0, 'Upper CI'] = custom_upper_ci
        treatment_df.at[0, 'Net Benefit'] = custom_net_benefit
    
        st.write("### 治療の有効性")
        st.dataframe(treatment_df[['Outcome', 'Risk Difference', 'Lower CI', 'Upper CI', 'Benefit Category']])
    
        # Pie Chart Visualization
        st.subheader("治療の有効性（1000人あたり）")
        if treatment_df['Normalized Net Benefit'].sum() > 0:
            fig, ax = plt.subplots()
            ax.pie(treatment_df['Normalized Net Benefit'], labels=treatment_df['Outcome'], autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
            st.pyplot(fig)
        else:
            st.write("データが不足しているため、円グラフを表示できません。")
    
    st.button("最初からやり直す")
