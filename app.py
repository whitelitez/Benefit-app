import streamlit as st

def main():
    st.title("治療アウトカム E_ijk + 95%CI 入力デモ")

    st.markdown("""
    ここでは、5つのアウトカムに対して、  
    - **E_ijk** (介入群の絶対リスク - 対照群の絶対リスク),
    - **95%信頼区間の下限**・**上限**,  
    - **有益/有害** (＋1 or −1),
    - **重要度** (高い/中くらい/低い),  
    をユーザーが入力できるようにしています。  
    """)

    # 1) Define 5 outcomes in a list (with initial defaults)
    outcomes_info = [
        {"label": "脳卒中予防",  "default_eijk": 0.1,  "default_lower": 0.05, "default_upper": 0.15, "default_sign": +1},
        {"label": "心不全予防","default_eijk": -0.1, "default_lower": -0.16,"default_upper": -0.04,"default_sign": +1},
        {"label": "めまい",    "default_eijk": 0.02,"default_lower": 0.011,"default_upper": 0.029,"default_sign": -1},
        {"label": "頻尿",      "default_eijk": -0.01,"default_lower": -0.03,"default_upper": 0.01, "default_sign": -1},
        {"label": "転倒",      "default_eijk": -0.02,"default_lower": -0.06,"default_upper": 0.02, "default_sign": -1},
    ]

    sign_map = { "有益 (+1)": +1, "有害 (−1)": -1 }
    importance_map = { "高い (1.0)": 1.0, "中くらい (0.5)": 0.5, "低い (0.0)": 0.0 }

    st.sidebar.header("アウトカム別の入力欄")
    user_data = []
    for i, od in enumerate(outcomes_info):
        st.sidebar.write(f"### {od['label']}")

        # E_ijk input
        eijk = st.sidebar.number_input(
            f"{od['label']}: E_ijk (介入群 - 対照群)",
            value=od["default_eijk"],
            step=0.01,
            format="%.3f",
            key=f"eijk_{i}"
        )

        # 95% CI lower
        lower_ci = st.sidebar.number_input(
            f"{od['label']}: 95%CI 下限",
            value=od["default_lower"],
            step=0.01,
            format="%.3f",
            key=f"lower_{i}"
        )

        # 95% CI upper
        upper_ci = st.sidebar.number_input(
            f"{od['label']}: 95%CI 上限",
            value=od["default_upper"],
            step=0.01,
            format="%.3f",
            key=f"upper_{i}"
        )

        # Sign: +1 or -1
        sign_choice = st.sidebar.radio(
            f"{od['label']} は？",
            list(sign_map.keys()),
            index=0 if od["default_sign"] == +1 else 1,
            key=f"sign_{i}"
        )
        sign_val = sign_map[sign_choice]

        # Importance: 1.0, 0.5, or 0.0
        imp_choice = st.sidebar.radio(
            f"{od['label']} の重要度",
            list(importance_map.keys()),
            index=0,  # default = "高い (1.0)"
            key=f"imp_{i}"
        )
        imp_val = importance_map[imp_choice]

        user_data.append({
            "label": od["label"],
            "E_ijk": eijk,
            "CI_lower": lower_ci,
            "CI_upper": upper_ci,
            "Fk": sign_val,
            "Importance": imp_val
        })

    if st.button("結果を計算"):
        show_results(user_data)

def show_results(user_data):
    """
    Example of calculating a simple net effect:
       sum( Fk * E_ijk * Importance )
    Then we display the user inputs.
    """
    st.subheader("入力内容")
    for row in user_data:
        st.write(f"- {row['label']} (E_ijk={row['E_ijk']}, "
                 f"95%CI=[{row['CI_lower']}, {row['CI_upper']}], "
                 f"Fk={row['Fk']}, 重要度={row['Importance']})")

    # Calculate a simple net effect
    net_effect = 0.0
    for row in user_data:
        net_effect += row["Fk"] * row["E_ijk"] * row["Importance"]

    st.subheader("簡易計算の結果")
    if net_effect > 0:
        st.write("正味の益は正の値 → ややプラスの影響かもしれません。")
    elif abs(net_effect) < 1e-9:
        st.write("正味の益はほぼ0 → プラスとマイナスが釣り合っている可能性があります。")
    else:
        st.write("正味の益は負の値 → マイナスの影響が大きいかもしれません。")

    st.write(f"（内部計算値： net_effect={net_effect:.4f}）")

if __name__ == "__main__":
    main()
