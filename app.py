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
    
    # Drop rows where "Outcome" is empty
    df_s = df_s.dropna(subset=["アウトカムk"])

    # Rename columns
    rename_map = {
        "Eijk: 介入群の絶対リスク-対照群の絶対リスク": "E_ijk",
        "95%信頼区間下限値": "CI_lower",
        "95%信頼区間上限値": "CI_upper",
        "アウトカムk": "Outcome",
        "Fk": "Fk",
    }
    df_s = df_s.rename(columns=rename_map)

    # Convert numeric columns
    numeric_columns = ["E_ijk", "CI_lower", "CI_upper", "Fk"]
    df_s[numeric_columns] = df_s[numeric_columns].apply(pd.to_numeric, errors="coerce")

    # Debugging output
    st.subheader("シート効果推定値s: 先頭10行 (ヘッダー=3 で読込)")
    st.write("**Columns found**:", df_s.columns.tolist())
    st.write("**Column Data Types**:", df_s.dtypes)
    st.dataframe(df_s.head(10))

    # Rest of the code remains the same...
    # ...

if __name__ == "__main__":
    main()
