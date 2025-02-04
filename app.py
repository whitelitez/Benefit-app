import streamlit as st
import pandas as pd
import os

def load_and_process_sheet(file_path, sheet_name, rename_map, numeric_columns):
    """Load and process a sheet from the Excel file."""
    if not os.path.exists(file_path):
        st.error(f"ローカルに '{file_path}' がありません。パスを確認してください。")
        return None

    xls = pd.ExcelFile(file_path)
    if sheet_name not in xls.sheet_names:
        st.error(f"'{file_path}' に '{sheet_name}' シートが見つかりません。")
        return None

    # Read the sheet with header=3 (row 4 as column names)
    df = pd.read_excel(xls, sheet_name=sheet_name, header=3)

    # Drop rows where "アウトカムk" is empty
    df = df.dropna(subset=["アウトカムk"])

    # Rename columns
    df = df.rename(columns=rename_map)

    # Convert numeric columns
    df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors="coerce")

    return df

def main():
    st.title("正味の益計算表: 効果推定値s と 効果推定値r ローカル版")

    # File path
    FILE_PATH = "正味の益計算表.xlsx"

    # Define sheet-specific parameters
    sheets = {
        "効果推定値s": {
            "rename_map": {
                "Eijk: 介入群の絶対リスク-対照群の絶対リスク": "E_ijk",
                "95%信頼区間下限値": "CI_lower",
                "95%信頼区間上限値": "CI_upper",
                "アウトカムk": "Outcome",
                "Fk": "Fk",
            },
            "numeric_columns": ["E_ijk", "CI_lower", "CI_upper", "Fk"],
        },
        "効果推定値r": {
            "rename_map": {
                "Eijk: 介入群の絶対リスク-対照群の絶対リスク": "E_ijk",
                "95%信頼区間下限値": "CI_lower",
                "95%信頼区間上限値": "CI_upper",
                "アウトカムk": "Outcome",
                "Fk": "Fk",
                "最重要との比 重要度wrk": "importance",
            },
            "numeric_columns": ["E_ijk", "CI_lower", "CI_upper", "Fk", "importance"],
        },
    }

    # Load and process each sheet
    for sheet_name, params in sheets.items():
        st.subheader(f"シート: {sheet_name}")
        df = load_and_process_sheet(FILE_PATH, sheet_name, params["rename_map"], params["numeric_columns"])

        if df is not None:
            st.write("**Columns found**:", df.columns.tolist())
            st.write("**Column Data Types**:", df.dtypes)
            st.dataframe(df.head(10))

            # Add additional processing or visualization here
            # ...

if __name__ == "__main__":
    main()
