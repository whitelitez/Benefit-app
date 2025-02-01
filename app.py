import streamlit as st

def main():
    st.title("高血圧治療 オプション評価ツール + 制約 (カラー表示版)")
    st.markdown("""
    このツールでは、5つの治療アウトカムに対する効果（良い/悪い + 重要度 + 変化の大きさ）と、
    3つの制約（費用、アクセス、介助）を入力し、  
    **色付きメッセージ**で全体的な結果を示します。  
    """)

    # -------------------------------------------------------
    # 1) Dictionaries for user-friendly vs numeric
    # -------------------------------------------------------
    importance_map = {"高い": 1.0, "中くらい": 0.5, "低い": 0.0}
    sign_map = {"良い": +1, "悪い": -1}
    constraint_map = {
        "特に問題ない": 0.0,
        "少し問題がある": 0.5,
        "大きな問題": 1.0
    }

    # -------------------------------------------------------
    # 2) Define the 5 outcomes
    # -------------------------------------------------------
    outcome_defs = [
        {"label": "脳卒中を防ぐ",    "default_slider": 50, "default_sign": "良い"},
        {"label": "心不全を防ぐ",   "default_slider": 50, "default_sign": "良い"},
        {"label": "めまいが起こる", "default_slider": 50, "default_sign": "悪い"},
        {"label": "頻尿が増える",   "default_slider": 50, "default_sign": "悪い"},
        {"label": "転倒が起きる",   "default_slider": 50, "default_sign": "悪い"},
    ]

    # -------------------------------------------------------
    # 3) Sidebar: Outcomes
    # -------------------------------------------------------
    st.sidebar.header("① 治療アウトカムの評価")
    user_data = []
    for od in outcome_defs:
        st.sidebar.write(f"### {od['label']}")

        # Slider 0..100 => mapped to -0.2..+0.2
        val = st.sidebar.slider(
            f"{od['label']}：変化の大きさ (目安)",
            min_value=0, max_value=100,
            value=od['default_slider'], step=1
        )
        normalized = (val - 50) / 50.0
        rd_value = 0.2 * normalized  # -0.2..+0.2 range

        # Sign: 良い or 悪い
        chosen_sign_label = st.sidebar.radio(
            f"{od['label']} は良い？悪い？",
            list(sign_map.keys()),
            index=0 if od["default_sign"] == "良い" else 1
        )
        sign_value = sign_map[chosen_sign_label]

        # Importance: 高い / 中くらい / 低い
        chosen_imp_label = st.sidebar.radio(
            f"{od['label']} の重要度は？",
            list(importance_map.keys()),
            index=0  # default "高い"
        )
        imp_value = importance_map[chosen_imp_label]

        user_data.append({
            "outcome": od["label"],
            "rd": rd_value,
            "sign": sign_value,
            "importance": imp_value,
        })

    # -------------------------------------------------------
    # 4) Sidebar: Constraints
    # -------------------------------------------------------
    st.sidebar.header("② 追加の制約を考慮")
    st.sidebar.write("下記の3点について、どの程度問題があるか選んでください。")

    financial_label = st.sidebar.radio(
        "費用面の制約",
        list(constraint_map.keys()),
        index=0
    )
    financial_val = constraint_map[financial_label]

    access_label = st.sidebar.radio(
        "アクセス面の制約（通院など）",
        list(constraint_map.keys()),
        index=0
    )
    access_val = constraint_map[access_label]

    care_label = st.sidebar.radio(
        "介助面の制約（自宅での世話など）",
        list(constraint_map.keys()),
        index=0
    )
    care_val = constraint_map[care_label]

    if st.button("結果を見る"):
        show_results(user_data, financial_val, access_val, care_val)

def show_results(user_data, financial_val, access_val, care_val):
    # -----------------------------
    # A) Calculate net effect
    # -----------------------------
    net_effect = sum(row["rd"] * row["sign"] * row["importance"] for row in user_data)

    # -----------------------------
    # B) Display net effect in a colored box
    # -----------------------------
    st.subheader("A) 治療アウトカムに関するコメント")
    if net_effect > 0.05:
        st.error("全体として、やや悪化する可能性が高いかもしれません。")
    elif net_effect > 0:
        st.warning("どちらかと言うと悪い方向ですが、大きくはないかもしれません。")
    elif abs(net_effect) < 1e-9:
        st.info("良い影響と悪い影響がほぼ釣り合っているか、変化があまりなさそうです。")
    else:
        # net_effect < 0
        if net_effect < -0.05:
            st.success("全体的に改善が期待できるかもしれません。")
        else:
            st.info("多少の改善があるかもしれませんが、大きくはないと思われます。")

    # -----------------------------
    # C) Show bullet list with arrows + stars
    # -----------------------------
    st.markdown("### 各項目の様子")
    for row in user_data:
        # Arrow logic
        if row["rd"] > 0.05:
            arrow = "↑"
        elif row["rd"] < -0.05:
            arrow = "↓"
        else:
            arrow = "→"

        # Star logic
        if row["importance"] == 1.0:
            stars = "⭐⭐"
        elif row["importance"] == 0.5:
            stars = "⭐"
        else:
            stars = ""

        sign_text = "良い" if row["sign"] == +1 else "悪い"
        st.write(f"- **{row['outcome']}**：{stars} {arrow} ({sign_text})")

    # -----------------------------
    # D) Constraints summary
    # -----------------------------
    st.subheader("B) 制約に関するコメント")
    constraint_total = financial_val + access_val + care_val
    if constraint_total <= 0.0:
        st.success("特に大きな問題はなさそうです。治療を進めやすい状況と言えます。")
    elif constraint_total <= 1.0:
        st.info("多少気になる点がありますが、比較的対処しやすい可能性があります。")
    elif constraint_total <= 2.0:
        st.warning("いくつかの面で大きな負担が想定されます。対策が必要でしょう。")
    else:
        st.error("費用や通院・介助など、非常に大きな制約があるようです。慎重な検討が必要です。")

    # Show details of constraints
    st.markdown("### 制約の内訳")
    def label_by_value(val):
        if val == 0.0: return "特に問題ない"
        elif val == 0.5: return "少し問題がある"
        else: return "大きな問題"

    st.write(f"- 費用面: {label_by_value(financial_val)}")
    st.write(f"- アクセス面: {label_by_value(access_val)}")
    st.write(f"- 介助面: {label_by_value(care_val)}")


if __name__ == "__main__":
    main()
