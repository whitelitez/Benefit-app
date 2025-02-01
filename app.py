import streamlit as st

st.title("高血圧治療 オプション評価ツール + 追加の制約")

st.markdown("""
このツールでは、
- **5つの治療アウトカム**（脳卒中予防、心不全予防など）を評価  
- **3つの制約**（費用面、アクセス面、介助面）を入力  
し、全体的な治療の傾向と制約の大きさをコメントします。
（数値は表示せず、全体的なイメージのみお伝えします。）
""")

# ----------------------------
# 1) Dictionaries for radio labels -> numeric
# ----------------------------
importance_map = {"高い": 1.0, "中くらい": 0.5, "低い": 0.0}
sign_map = {"良い": +1, "悪い": -1}

# For constraints, 0.0 = no issue, 0.5 = some issue, 1.0 = major issue
constraint_map = {
    "特に問題ない": 0.0,
    "少し問題がある": 0.5,
    "大きな問題": 1.0
}

# ----------------------------
# 2) Five outcomes
# ----------------------------
outcome_defs = [
    {"label": "脳卒中を防ぐ",    "default_slider": 50, "default_sign": "良い"},
    {"label": "心不全を防ぐ",   "default_slider": 50, "default_sign": "良い"},
    {"label": "めまいが起こる", "default_slider": 50, "default_sign": "悪い"},
    {"label": "頻尿が増える",   "default_slider": 50, "default_sign": "悪い"},
    {"label": "転倒が起きる",   "default_slider": 50, "default_sign": "悪い"},
]

# Sidebars
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
    rd_value = 0.2 * normalized

    chosen_sign_label = st.sidebar.radio(
        f"{od['label']} は良い？悪い？",
        list(sign_map.keys()),
        index=0 if od["default_sign"] == "良い" else 1
    )
    sign_value = sign_map[chosen_sign_label]

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

# ----------------------------
# 3) Constraints
# ----------------------------
st.sidebar.header("② 追加の制約を考慮")
st.sidebar.write("以下の3点について、どの程度問題があるか選んでください。")

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
    # 1) Compute net effect
    net_effect = sum(row["rd"] * row["sign"] * row["importance"] for row in user_data)

    st.subheader("A) 治療アウトカムのコメント")
    if net_effect > 0.05:
        st.write("全体として、やや**悪化**する可能性が高いかもしれません。")
    elif net_effect > 0:
        st.write("どちらかと言うと**悪い方向**ですが、大きくはないかもしれません。")
    elif abs(net_effect) < 1e-9:
        st.write("**良い影響と悪い影響が釣り合っている**可能性があります。")
    else:
        # net_effect < 0
        if net_effect < -0.05:
            st.write("全体的に**改善**が期待できるかもしれません。")
        else:
            st.write("多少の**改善**があるかもしれませんが、大きくはないでしょう。")

    st.markdown("### 各項目のざっくりイメージ")
    for row in user_data:
        # Arrows for RD
        if row["rd"] > 0.05:
            arrow = "↑"
        elif row["rd"] < -0.05:
            arrow = "↓"
        else:
            arrow = "→"
        # Stars for importance
        if row["importance"] == 1.0:
            stars = "⭐⭐"
        elif row["importance"] == 0.5:
            stars = "⭐"
        else:
            stars = ""
        sign_text = "良い" if row["sign"] == +1 else "悪い"
        st.write(f"- **{row['outcome']}**：{stars} {arrow} ({sign_text})")

    # 2) Constraints total
    constraint_total = financial_val + access_val + care_val

    st.subheader("B) 制約の大きさに関するコメント")
    if constraint_total <= 0.0:
        st.write("特に問題はなさそうです。治療を進めやすい状況と言えます。")
    elif constraint_total <= 1.0:
        st.write("多少気になる点はありますが、比較的対処しやすい可能性があります。")
    elif constraint_total <= 2.0:
        st.write("いくつかの面で**大きな負担**が想定されます。対策が必要でしょう。")
    else:
        st.write("費用や通院・介助など、**非常に大きな制約**があるようです。慎重な検討が必要です。")

    st.markdown("### 制約の内訳")
    st.write(f"- 費用面: {financial_label}")
    st.write(f"- アクセス面: {access_label}")
    st.write(f"- 介助面: {care_label}")
