import streamlit as st
import pandas as pd

# Initialize Streamlit app
def main():
    st.title("正味の益計算ツール (教授版)")
    st.markdown("""
    **リスク差 (Risk Difference, RD) に基づく治療評価**
    
    介入群と対照群の絶対リスクの差 (E_ijk) と 95% 信頼区間の値を入力できます。
    計算結果として、正味の益の推定値が表示されます。
    """)
    
    # User-editable data
    data = {
        "Outcome": ["脳卒中予防", "心不全予防", "めまい", "頻尿", "転倒"],
        "E_ijk": [0.1, -0.1, 0.02, -0.01, -0.02],  # Risk difference
        "CI_lower": [0.05, -0.16, 0.011, -0.03, -0.06],  # 95% CI lower
        "CI_upper": [0.15, -0.04, 0.029, 0.01, 0.02]  # 95% CI upper
    }
    
    df = pd.DataFrame(data)
    
    # Sidebar Inputs
    st.sidebar.header("ユーザー入力")
    for i in range(len(df)):
        df.loc[i, "E_ijk"] = st.sidebar.number_input(
            f"{df.loc[i, 'Outcome']} の E_ijk", value=df.loc[i, "E_ijk"], step=0.01
        )
        df.loc[i, "CI_lower"] = st.sidebar.number_input(
            f"{df.loc[i, 'Outcome']} の 95%信頼区間下限", value=df.loc[i, "CI_lower"], step=0.01
        )
        df.loc[i, "CI_upper"] = st.sidebar.number_input(
            f"{df.loc[i, 'Outcome']} の 95%信頼区間上限", value=df.loc[i, "CI_upper"], step=0.01
        )
    
    # Display Data
    st.subheader("効果推定値の入力")
    st.dataframe(df)
    
    # Compute Net Benefit Estimate (Simplified)
    df["Net Benefit"] = df["E_ijk"]  # Placeholder formula, update with correct calculations
    
    st.subheader("計算結果: 正味の益")
    st.write("各アウトカムの正味の益を表示します。")
    st.dataframe(df[["Outcome", "E_ijk", "Net Benefit"]])
    
if __name__ == "__main__":
    main()
