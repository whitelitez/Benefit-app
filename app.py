import streamlit as st
import pandas as pd

def main():
    st.title("正味の益計算表: 効果推定値s フルデモ")

    st.markdown("""
    このデモでは:
    1. **正味の益計算表.xlsx** をアップロードし、「効果推定値s」シートを読み込みます。
    2. シートから得たアウトカム情報 (E_ijk, Fkなど) を表示し、ユーザーが E_ijk や信頼区間、sign (有益/有害) を上書き可能。
    3. 重要度は**3つ星表記**で (★の色) を使い「高い/中/低」を指定。
    4. 簡易的に **Net Effect = Σ ( Fk × E_ijk × importance )** を計算して色付きで表示。
    5. **制約 (費用/アクセス/介助)** も入力し、合計で色付きコメントを表示。
    ---
    """)

    uploaded_file = st.file_uploader("正味の益計算表.xlsx をアップロードしてください", type=["xlsx"])
    if uploaded_file is not None:
        xls = pd.ExcelFile(uploaded_file)
        if "効果推定値s" not in xls.sheet_names:
            st.warning("アップロードされたファイルに『効果推定値s』シートが見つかりません。")
            return
        
        # 1) Load 効果推定値s
        df_s = pd.read_excel(xls, sheet_name="効果推定値s")
        st.subheader("効果推定値s: 原データ(先頭10行プレビュー)")
        st.dataframe(df_s.head(10))

        st.markdown("---")

        # 2) Basic column rename (if needed). Adjust if your actual columns differ:
        #    We assume some typical column names: 'アウトカムk' -> 'Outcome',
        #    'Fk' -> 'Fk' (sign), 'Eijk: 介入群の絶対リスク-対照群の絶対リスク' -> 'E_ijk',
        #    and lower/upper CI columns, etc.
        df_s = df_s.rename(columns={
            "アウトカムk": "Outcome",
            "Eijk: 介入群の絶対リスク-対照群の絶対リスク": "E_ijk",
            "95%信頼区間下限値": "CI_lower",
            "95%信頼区間上限値": "CI_upper"
            # If "Fk" is already "Fk", no rename needed
            # If your sheet has different exact column names, adjust accordingly
        })

        # 3) Filter down to relevant rows (e.g., first 5 if that's your standard),
        #    or you might do a .dropna to ignore blank rows, etc.
        #    We'll just assume the top 5 are your main outcomes:
        df_s = df_s.head(5).copy()

        st.sidebar.header("① 各アウトカムの編集")

        # 4) We create a structure to store user edits
        user_data = []
        for i, row in df_s.iterrows():
            outcome_name = str(row.get("Outcome", f"Row{i}"))
            
            # default values
            default_e = float(row["E_ijk"]) if pd.notnull(row["E_ijk"]) else 0.0
            default_low = float(row["CI_lower"]) if pd.notnull(row["CI_lower"]) else 0.0
            default_high = float(row["CI_upper"]) if pd.notnull(row["CI_upper"]) else 0.0
            default_fk = row["Fk"] if "Fk" in df_s.columns and pd.notnull(row["Fk"]) else +1
            
            with st.sidebar.expander(f"{outcome_name} の編集", expanded=(i==0)):
                e_val = st.number_input(
                    f"{outcome_name}: E_ijk",
                    value=default_e,
                    step=0.01,
                    format="%.3f"
                )
                ci_low = st.number_input(
                    f"{outcome_name}: 95%CI 下限",
                    value=default_low,
                    step=0.01,
                    format="%.3f"
                )
                ci_high = st.number_input(
                    f"{outcome_name}: 95%CI 上限",
                    value=default_high,
                    step=0.01,
                    format="%.3f"
                )

                # Sign radio
                sign_choice = st.radio(
                    f"{outcome_name} は有益(＋1) or 有害(−1)？",
                    ("有益 (+1)", "有害 (−1)"),
                    index=0 if default_fk == +1 else 1
                )
                sign_val = +1 if "有益" in sign_choice else -1

                # 3-star importance approach
                imp_label = st.radio(
                    f"{outcome_name} の重要度",
                    ("★★★ (高い)", "★★☆ (中くらい)", "★☆☆ (低い)"),
                    index=0
                )
                # interpret into numeric: 3=1.0, 2=0.5, 1=0.0 ( or you can do your own mapping)
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

        # 5) Constraints
        st.sidebar.header("② 追加の制約を考慮")
        st.sidebar.write("以下の3点について、問題度を選択してください。")
        constraint_map = {
            "特に問題ない": 0.0,
            "少し問題がある": 0.5,
            "大きな問題": 1.0
        }
        financial_label = st.sidebar.radio("費用面の制約", list(constraint_map.keys()), index=0)
        financial_val = constraint_map[financial_label]
        access_label = st.sidebar.radio("アクセス面の制約（通院など）", list(constraint_map.keys()), index=0)
        access_val = constraint_map[access_label]
        care_label = st.sidebar.radio("介助面の制約（自宅での世話など）", list(constraint_map.keys()), index=0)
        care_val = constraint_map[care_label]

        if st.button("結果を計算"):
            show_results(user_data, financial_val, access_val, care_val)
    else:
        st.write("ファイルがアップロードされていません。")

def show_results(user_data, financial_val, access_val, care_val):
    st.subheader("A) 入力されたアウトカムと数値")
    for row in user_data:
        st.write(f"- **{row['outcome']}**: "
                 f"E_ijk={row['E_ijk']:.3f}, "
                 f"CI=[{row['CI_lower']:.3f}, {row['CI_upper']:.3f}], "
                 f"Fk={row['Fk']}, importance={row['importance']}")

    # Simple net effect
    net_effect = sum(r["Fk"] * r["E_ijk"] * r["importance"] for r in user_data)

    st.subheader("B) 治療アウトカムのコメント")
    if net_effect > 0.05:
        st.error("全体として、やや悪化の恐れが高いかもしれません。")
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

    st.write(f"（内部計算上の net_effect = {net_effect:.4f}）")

    st.subheader("C) 制約に関するコメント")
    constraint_total = financial_val + access_val + care_val
    if constraint_total <= 0.0:
        st.success("特に大きな問題はなさそうです。")
    elif constraint_total <= 1.0:
        st.info("多少気になる点はありますが、比較的対処しやすいかもしれません。")
    elif constraint_total <= 2.0:
        st.warning("いくつかの面で大きな負担が想定されます。対策が必要でしょう。")
    else:
        st.error("費用や通院・介助など非常に大きな制約があるようです。慎重な検討が必要です。")

    st.markdown("### 制約の内訳")
    def to_label(val):
        if val == 0.0: return "特に問題ない"
        elif val == 0.5: return "少し問題がある"
        else: return "大きな問題"

    st.write(f"- 費用面: {to_label(financial_val)}")
    st.write(f"- アクセス面: {to_label(access_val)}")
    st.write(f"- 介助面: {to_label(care_val)}")

if __name__ == "__main__":
    main()
