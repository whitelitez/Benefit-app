import streamlit as st
import pandas as pd

# Initialize Streamlit app
def main():
    st.title("高血圧治療 オプション評価ツール (簡易版)")
    st.markdown("""
    **簡単な治療評価**
    
    各治療オプションについて、どの程度有益またはリスクがあると感じるかをスライダーで調整してください。
    
    計算結果として、治療の総合評価が表示されます。
    """)
    
    # User-friendly outcomes
    outcome_defs = [
        {"label": "脳卒中予防", "default": 50},
        {"label": "心不全予防", "default": 50},
        {"label": "めまい", "default": 50},
        {"label": "頻尿", "default": 50},
        {"label": "転倒", "default": 50},
    ]
    
    st.sidebar.header("治療の評価")
    user_data = []
    for od in outcome_defs:
        val = st.sidebar.slider(
            f"{od['label']} の影響度 (0=悪影響〜100=良い影響)",
            min_value=0, max_value=100,
            value=od["default"], step=1
        )
        user_data.append({"Outcome": od["label"], "Score": val})
    
    df = pd.DataFrame(user_data)
    
    # Display Data
    st.subheader("治療オプションの評価")
    st.dataframe(df)
    
    # Compute Net Benefit Estimate (simplified)
    df["Net Benefit"] = (df["Score"] - 50) / 50  # Normalize between -1 and +1
    
    # Compute Button
    if st.button("結果を見る"):
        st.subheader("治療の総合評価")
        for index, row in df.iterrows():
            if row["Net Benefit"] > 0.2:
                st.success(f"✅ {row['Outcome']} は有益です。")
            elif row["Net Benefit"] < -0.2:
                st.error(f"❌ {row['Outcome']} はリスクが高い可能性があります。")
            else:
                st.warning(f"⚠️ {row['Outcome']} は中立的です。")
    
if __name__ == "__main__":
    main()
