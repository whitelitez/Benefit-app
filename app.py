import streamlit as st
import pandas as pd
import os

def main():
    st.title("正味の益計算表: 効果推定値s ローカル版 (フルデモ)")

    st.markdown("""
    このデモでは、ローカルファイル「正味の益計算表.xlsx」を読み込み、
    「効果推定値s」シートからデータを取得します。

    - 重要カラム: 'Fk', 'E_ijk', '95%信頼区間下限値', '95%信頼区間上限値', 'アウトカムk' 等
    - ユーザーは E_ijk や信頼区間、sign(有益/有害)、重要度(3つ星) をUIで上書き
    - 最終的に簡易的な正味の益 (net_effect) を計算 & 制約(費用・アクセス・介助)も考慮
    """)

    # 1) Set the local file path
    FILE_PATH = "正味の益計算表.xlsx"

    # 2) Verify the file exists locally
    if not os.path.exists(FILE_PATH):
        st.error(f"ローカルに '{FILE_PATH}' が見つかりません。")
        return

    # 3) Load the Excel, check if "効果推定値s" exists
    xls = pd.ExcelFile(FILE_PATH)
    if "効果推定値s" not in xls.sheet_names:
        st.error(f"'{FILE_PATH}' 内に '効果推定値s' シートが見つかりません。シート名を確認してください。")
        return

    # 4) Read the sheet
    df_s = pd.read_excel(xls, sheet_name="効果推定値s")

    st.subheader("効果推定値s: 原データプレビュー (先頭10行)")
    st.dataframe(df_s.head(10))

    # 5) Rename columns (adjust as needed to match your actual sheet):
    df_s = df_s.rename(columns={
        "アウトカムk": "Outcome",
        "Eijk: 介入群の絶対リスク-対照群の絶対リスク": "E_ijk",
        "95%信頼区間下限値": "CI_lower",
        "95%信頼区間上限値": "CI_upper"
    })

    # Keep only the first 5 rows for demonstration (assuming 5 main outcomes)
    df_s = df_s.head(5).copy()

    st.markdown("---")
    st.write("## アウトカム編集")

    # 6) Build user-editable forms in the sidebar
    user_data = []
    st.sidebar.header("① 各アウトカムの編集 (効果推定値s)")
    for i, row in df_s.iterrows():
        outcome_name = str(row.get("Outcome", f"Row{i}"))
        
        # Default values from the sheet
        default_e = float(row["E_ijk"]) if pd.notnull(row["E_ijk"]) else 0.0
        default_low = float(row["CI_lower"]) if pd.notnull(row["CI_lower"]) else 0.0
        default_high = float(row["CI_upper"]) if pd.notnull(row["CI_upper"]) else 0.0
        default_fk = row["Fk"] if "Fk" in df_s.columns and pd.notnull(row["Fk"]) else +1

        with st.sidebar.expander(f"{outcome_name} の設定", expanded=(i==0)):
            e_val = st.number_input(
                f"{outcome_name}: E_ijk (介入群-対照群)",
                value=default_e,
                step=0.01,
                format="%.3f",
                key=f"eijk_{i}"
            )

            ci_low = st.number_input(
                f"{outcome_name}: 95%CI 下限",
                value=default_low,
                step=0.01,
                format="%.3f",
                key=f"cilow_{i}"
            )

            ci_high = st.number_input(
                f"{outcome_name}: 95%CI 上限",
                value=default_high,
                step=0.01,
                format="%.3f",
                key=f"cihigh_{i}"
            )

            # Sign radio
            sign_choice = st.radio(
                f"{outcome_name}: 有益(＋1) or 有害(−1)？",
                ("有益 (+1)", "有害 (−1)"),
                index=0 if default_fk == +1 else 1,
                key=f"sign_{i}"
            )
            sign_val = +1 if "有益" in sign_choice else -1

            # 3-star approach for importance
            imp_label = st.radio(
                f"{outcome_name} の重要度(3つ星)",
                ("★★★ (高)", "★★☆ (中)", "★☆☆ (低)"),
                index=0,
                key=f"imp_{i}"
            )
            if "★★★" in imp_label:
                imp_val = 1.0
            elif "★★☆" in imp_label:
                imp_val = 0.5
            else:
                imp_val = 0.0

        user_data.append({
            "outcome": outcome_name,
            "E_ijk": e_val,
            "CI_lower": ci_low,
            "CI_upper": ci_high,
            "Fk": sign_val,
            "importance": imp_val
        })

    # 7) Constraints Section
    st.sidebar.header("② 追加の制約を考慮")
    st.sidebar.write("以下3点の問題度を選択してください。")
    constraint_map = {
        "特に問題ない": 0.0,
        "少し問題がある": 0.5,
        "大きな問題": 1.0
    }
    financial_label = st.sidebar.radio("費用面の制約", list(constraint_map.keys()), index=0)
    financial_val = constraint_map[financial_label]

    access_label = st.sidebar.radio("アクセス面の制約(通院など)", list(constraint_map.keys()), index=0)
    access_val = constraint_map[access_label]

    care_label = st.sidebar.radio("介助面(自宅での世話など)", list(constraint_map.keys()), index=0)
    care_val = constraint_map[care_label]

    if st.button("結果を計算"):
        show_results(user_data, financial_val, access_val, care_val)

def show_results(user_data, financial_val, access_val, care_val):
    """
    - Displays user-entered data for each outcome
    - Computes a simple net effect = sum(Fk * E_ijk * importance)
    - Provides color-coded commentary
    - Also sums constraints
    """

    st.subheader("A) 入力されたアウトカムと数値")
    for row in user_data:
        st.write(f"- **{row['outcome']}**: "
                 f"E_ijk={row['E_ijk']:.3f}, "
                 f"CI=[{row['CI_lower']:.3f}, {row['CI_upper']:.3f}], "
                 f"Fk={row['Fk']}, importance={row['importance']:.1f}")

    # 1) Net Effect
    net_effect = sum(r["Fk"] * r["E_ijk"] * r["importance"] for r in user_data)

    st.subheader("B) 治療アウトカムのコメント")
    if net_effect > 0.05:
        st.error("全体として、やや悪化する可能性が高いかもしれません。")
    elif net_effect > 0:
        st.warning("どちらかと言うと悪い方向ですが、大きくはないかもしれません。")
    elif abs(net_effect) < 1e-9:
        st.info("良い影響と悪い影響が釣り合っているか、変化があまりない可能性があります。")
    else:
        # net_effect < 0
        if net_effect < -0.05:
            st.success("全体的に改善が期待できるかもしれません。")
        else:
            st.info("多少の改善があるかもしれませんが、大きくはないでしょう。")

    st.write(f"（内部計算 net_effect = {net_effect:.4f}）")

    # 2) Constraints
    st.subheader("C) 制約に関するコメント")
    constraint_total = financial_val + access_val + care_val
    if constraint_total <= 0.0:
        st.success("特に大きな問題はなさそうです。")
    elif constraint_total <= 1.0:
        st.info("多少気になる点がありますが、比較的対処しやすい可能性があります。")
    elif constraint_total <= 2.0:
        st.warning("いくつかの面で大きな負担が想定されます。対策が必要でしょう。")
    else:
        st.error("費用や通院・介助など、非常に大きな制約があるようです。慎重な検討が必要です。")

    st.markdown("### 制約の内訳")
    def label_con(val):
        if val == 0.0: return "特に問題ない"
        elif val == 0.5: return "少し問題がある"
        else: return "大きな問題"

    st.write(f"- 費用面: {label_con(financial_val)}")
    st.write(f"- アクセス面: {label_con(access_val)}")
    st.write(f"- 介助面: {label_con(care_val)}")

if __name__ == "__main__":
    main()
