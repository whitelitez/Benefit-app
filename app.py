import streamlit as st
import pandas as pd
import os

def main():
    st.title("正味の益計算表: 効果推定値s ローカル版 (ヘッダー調整)")

    st.markdown("""
    このスクリプトでは:
    - `正味の益計算表.xlsx` をローカルから読み込み
    - `sheet_name="効果推定値s"`, `header=3` を指定して、エクセルの4行目を列名とする
    - 列名を確認し、`Eijk: 介入群の絶対リスク-対照群の絶対リスク` を `E_ijk` にリネーム
    - ユーザーが E_ijk, CI下限/上限, sign, 3スター重要度を編集
    - 簡易的な net_effect (Fk * E_ijk * importanceの合計) を表示
    - 制約(費用,アクセス,介助)の合計も表示
    """)

    # 1) Local Excel path
    FILE_PATH = "正味の益計算表.xlsx"
    if not os.path.exists(FILE_PATH):
        st.error(f"ローカルに '{FILE_PATH}' がありません。パスを確認してください。")
        return

    xls = pd.ExcelFile(FILE_PATH)
    if "効果推定値s" not in xls.sheet_names:
        st.error(f"'{FILE_PATH}' に '効果推定値s' シートが見つかりません。")
        return

    # 2) Read the sheet, with header=3 => means row 4 is the column names
    df_s = pd.read_excel(xls, sheet_name="効果推定値s", header=3)
    st.subheader("シート効果推定値s: 先頭10行 (ヘッダー=3 で読込)")
    st.write("**Columns found**:", df_s.columns.tolist())
    st.dataframe(df_s.head(10))

    # 3) Rename columns as needed
    rename_map = {
        # e.g., "Eijk: 介入群の絶対リスク-対照群の絶対リスク" => "E_ijk"
        "Eijk: 介入群の絶対リスク-対照群の絶対リスク": "E_ijk",
        "Fk": "Fk",  # if your file actually has a column spelled "Fk"
        "アウトカムk": "Outcome",
        "95%信頼区間下限値": "CI_lower",
        "95%信頼区間上限値": "CI_upper",
    }
    df_s = df_s.rename(columns=rename_map)

    st.write("**リネーム後のカラム**:", df_s.columns.tolist())

    # 4) Possibly keep only first 5 rows if you have exactly 5 outcomes
    df_s = df_s.head(5).copy()

    st.markdown("---")
    st.write("## ユーザー編集")

    # Build user editable forms
    user_data = []
    st.sidebar.header("① 各アウトカム編集 (効果推定値s)")

    # If your sheet definitely has "Fk", "E_ijk" columns now, proceed:
    for i, row in df_s.iterrows():
        outcome_name = str(row.get("Outcome", f"Row{i}"))

        # Attempt to parse or default to 0.0
        default_e = float(row["E_ijk"]) if pd.notnull(row.get("E_ijk")) else 0.0
        default_low = float(row["CI_lower"]) if pd.notnull(row.get("CI_lower")) else 0.0
        default_high = float(row["CI_upper"]) if pd.notnull(row.get("CI_upper")) else 0.0
        default_fk = row["Fk"] if "Fk" in df_s.columns and pd.notnull(row.get("Fk")) else +1

        with st.sidebar.expander(f"{outcome_name} の設定", expanded=(i == 0)):
            # E_ijk
            e_val = st.number_input(
                f"{outcome_name}: E_ijk",
                value=default_e,
                step=0.01,
                format="%.3f",
                key=f"eijk_{i}"
            )
            # CI lower / upper
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
            # sign
            sign_choice = st.radio(
                f"{outcome_name}: 有益(+1) or 有害(-1)?",
                ("有益 (+1)", "有害 (-1)"),
                index=0 if default_fk == +1 else 1,
                key=f"sign_{i}"
            )
            sign_val = +1 if "有益" in sign_choice else -1

            # 3-star importance
            imp_label = st.radio(
                f"{outcome_name} の重要度 (★)",
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

    # Constraints
    st.sidebar.header("② 追加の制約")
    constraint_map = {
        "特に問題ない": 0.0,
        "少し問題がある": 0.5,
        "大きな問題": 1.0
    }
    financial_label = st.sidebar.radio("費用面の制約", list(constraint_map.keys()), index=0)
    financial_val = constraint_map[financial_label]
    access_label = st.sidebar.radio("アクセス面 (通院等)", list(constraint_map.keys()), index=0)
    access_val = constraint_map[access_label]
    care_label = st.sidebar.radio("介助面 (世話等)", list(constraint_map.keys()), index=0)
    care_val = constraint_map[care_label]

    if st.button("結果を計算"):
        show_results(user_data, financial_val, access_val, care_val)

def show_results(user_data, financial_val, access_val, care_val):
    st.subheader("A) 入力されたアウトカム")
    for row in user_data:
        st.write(f"- **{row['outcome']}**: E_ijk={row['E_ijk']}, "
                 f"CI=[{row['CI_lower']}, {row['CI_upper']}], "
                 f"Fk={row['Fk']}, importance={row['importance']}")

    # net effect
    net_effect = sum(r["Fk"] * r["E_ijk"] * r["importance"] for r in user_data)

    st.subheader("B) 治療アウトカムのコメント")
    if net_effect > 0.05:
        st.error("全体的にやや悪化傾向かもしれません。")
    elif net_effect > 0:
        st.warning("少し悪い方向ですが大差はないかも。")
    elif abs(net_effect) < 1e-9:
        st.info("良い影響と悪い影響が拮抗しているか、ほぼ変化なし。")
    else:
        # net_effect < 0
        if net_effect < -0.05:
            st.success("全体的に改善が期待できそうです。")
        else:
            st.info("わずかながら改善があるかもしれませんが大きくはないでしょう。")

    st.write(f"（内部計算 net_effect = {net_effect:.4f}）")

    st.subheader("C) 制約コメント")
    constraint_total = financial_val + access_val + care_val
    if constraint_total <= 0.0:
        st.success("特に大きな問題はなさそうです。")
    elif constraint_total <= 1.0:
        st.info("多少気になる点はあるものの、対処可能かもしれません。")
    elif constraint_total <= 2.0:
        st.warning("いくつかの面で大きな負担が想定されます。検討要。")
    else:
        st.error("非常に大きな制約があり、慎重な対応が必要。")

    st.markdown("### 制約の内訳")
    def label_con(val):
        if val == 0.0: return "特に問題ない"
        elif val == 0.5: return "少し問題がある"
        else: return "大きな問題"
    st.write(f"- 費用面: {label_con(financial_val)}")
    st.write(f"- アクセス: {label_con(access_val)}")
    st.write(f"- 介助面: {label_con(care_val)}")

if __name__ == "__main__":
    main()
