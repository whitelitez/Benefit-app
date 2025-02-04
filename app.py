import streamlit as st
import pandas as pd
import os

# ------------------------------------------
# Constants and Configuration
# ------------------------------------------
FILE_PATH = "正味の益計算表.xlsx"
SHEET_NAME = "効果推定値s"

# Maps for user-friendly inputs
IMPORTANCE_MAP = {"★★★ (高)": 1.0, "★★☆ (中)": 0.5, "★☆☆ (低)": 0.0}
SIGN_MAP = {"有益 (+1)": +1, "有害 (-1)": -1}
CONSTRAINT_MAP = {
    "特に問題ない": 0.0,
    "少し問題がある": 0.5,
    "大きな問題": 1.0
}

# ------------------------------------------
# Helper Functions
# ------------------------------------------
def load_data(file_path, sheet_name):
    """Load data from the Excel file."""
    if not os.path.exists(file_path):
        st.error(f"ローカルに '{file_path}' がありません。パスを確認してください。")
        return None

    xls = pd.ExcelFile(file_path)
    if sheet_name not in xls.sheet_names:
        st.error(f"'{file_path}' に '{sheet_name}' シートが見つかりません。")
        return None

    # Read the sheet with header=3 (row 4 as column names)
    df = pd.read_excel(xls, sheet_name=sheet_name, header=3)
    df = df.dropna(subset=["アウトカムk"])  # Drop rows where "Outcome" is empty

    # Rename columns
    rename_map = {
        "Eijk: 介入群の絶対リスク-対照群の絶対リスク": "E_ijk",
        "95%信頼区間下限値": "CI_lower",
        "95%信頼区間上限値": "CI_upper",
        "アウトカムk": "Outcome",
        "Fk": "Fk",
    }
    df = df.rename(columns=rename_map)

    # Convert numeric columns
    numeric_columns = ["E_ijk", "CI_lower", "CI_upper", "Fk"]
    df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors="coerce")

    return df

def star_html(importance):
    """Return HTML string for color-coded stars."""
    if importance == 1.0:
        return "<span style='color:gold;font-size:18px;'>★★★</span>"
    elif importance == 0.5:
        return "<span style='color:gold;font-size:18px;'>★★</span><span style='color:lightgray;font-size:18px;'>☆</span>"
    else:
        return "<span style='color:gold;font-size:18px;'>★</span><span style='color:lightgray;font-size:18px;'>☆☆</span>"

# ------------------------------------------
# Main Function
# ------------------------------------------
def main():
    st.title("正味の益計算表: 効果推定値s ローカル版")
    st.markdown("""
    このツールでは、治療アウトカムの効果推定値と制約を入力し、正味の益を計算します。
    """)

    # Load data
    df = load_data(FILE_PATH, SHEET_NAME)
    if df is None:
        return

    # Display raw data for debugging
    st.subheader("シートデータ (先頭10行)")
    st.dataframe(df.head(10))

    # ------------------------------------------
    # Part 1: User Inputs for Outcomes
    # ------------------------------------------
    st.header("① 治療アウトカムの編集")
    user_data = []
    for i, row in df.iterrows():
        outcome_name = str(row.get("Outcome", f"Row{i}"))

        with st.expander(f"{outcome_name} の設定", expanded=(i == 0)):
            # E_ijk
            e_val = st.number_input(
                f"{outcome_name}: E_ijk",
                value=float(row["E_ijk"]) if pd.notnull(row.get("E_ijk")) else 0.0,
                step=0.01,
                format="%.3f",
                key=f"eijk_{i}"
            )

            # CI lower / upper
            ci_low = st.number_input(
                f"{outcome_name}: 95%CI 下限",
                value=float(row["CI_lower"]) if pd.notnull(row.get("CI_lower")) else 0.0,
                step=0.01,
                format="%.3f",
                key=f"cilow_{i}"
            )
            ci_high = st.number_input(
                f"{outcome_name}: 95%CI 上限",
                value=float(row["CI_upper"]) if pd.notnull(row.get("CI_upper")) else 0.0,
                step=0.01,
                format="%.3f",
                key=f"cihigh_{i}"
            )

            # Sign (有益/有害)
            sign_choice = st.radio(
                f"{outcome_name}: 有益(+1) or 有害(-1)?",
                list(SIGN_MAP.keys()),
                index=0 if row.get("Fk", +1) == +1 else 1,
                key=f"sign_{i}"
            )
            sign_val = SIGN_MAP[sign_choice]

            # Importance (3-star)
            imp_label = st.radio(
                f"{outcome_name} の重要度 (★)",
                list(IMPORTANCE_MAP.keys()),
                index=0,
                key=f"imp_{i}"
            )
            imp_val = IMPORTANCE_MAP[imp_label]

            # Store user data
            user_data.append({
                "outcome": outcome_name,
                "E_ijk": e_val,
                "CI_lower": ci_low,
                "CI_upper": ci_high,
                "Fk": sign_val,
                "importance": imp_val,
            })

    # ------------------------------------------
    # Part 2: User Inputs for Constraints
    # ------------------------------------------
    st.header("② 制約の編集")
    with st.expander("制約を入力する", expanded=True):
        financial_label = st.radio("費用面の制約", list(CONSTRAINT_MAP.keys()), index=0)
        financial_val = CONSTRAINT_MAP[financial_label]

        access_label = st.radio("アクセス面の制約", list(CONSTRAINT_MAP.keys()), index=0)
        access_val = CONSTRAINT_MAP[access_label]

        care_label = st.radio("介助面の制約", list(CONSTRAINT_MAP.keys()), index=0)
        care_val = CONSTRAINT_MAP[care_label]

    # ------------------------------------------
    # Part 3: Calculate and Display Results
    # ------------------------------------------
    if st.button("結果を計算"):
        net_effect = sum(r["Fk"] * r["E_ijk"] * r["importance"] for r in user_data)
        constraint_total = financial_val + access_val + care_val

        st.subheader("A) 治療アウトカムのコメント")
        if net_effect > 0.05:
            st.error("全体的にやや悪化傾向かもしれません。")
        elif net_effect > 0:
            st.warning("少し悪い方向ですが大差はないかも。")
        elif abs(net_effect) < 1e-9:
            st.info("良い影響と悪い影響が拮抗しているか、ほぼ変化なし。")
        else:
            st.success("全体的に改善が期待できそうです。")

        st.write(f"（内部計算 net_effect = {net_effect:.4f}）")

        st.subheader("B) 制約のコメント")
        if constraint_total <= 0.0:
            st.success("特に大きな問題はなさそうです。")
        elif constraint_total <= 1.0:
            st.info("多少気になる点はあるものの、対処可能かもしれません。")
        elif constraint_total <= 2.0:
            st.warning("いくつかの面で大きな負担が想定されます。検討要。")
        else:
            st.error("非常に大きな制約があり、慎重な対応が必要。")

        st.markdown("### 制約の内訳")
        st.write(f"- 費用面: {financial_label}")
        st.write(f"- アクセス面: {access_label}")
        st.write(f"- 介助面: {care_label}")

if __name__ == "__main__":
    main()
