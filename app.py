import streamlit as st

st.title("高血圧治療 オプション評価ツール")
st.markdown("""
このツールでは、以下の5つの項目について、
1. 「この治療でどのくらい変化しそうか」をざっくりスライダーで選び、  
2. その項目が「体に良い方か、悪い方か」、  
3. どの程度「あなたにとって重要」かを選んでください。  

最後に、それらをまとめたコメントを表示します。（**数値は表示しません**）  
""")

# ----------------------------
# 1) Define dictionaries for the radio labels -> numeric values
# ----------------------------
importance_map = {
    "高い": 1.0,
    "中くらい": 0.5,
    "低い": 0.0
}

sign_map = {
    "良い": +1,
    "悪い": -1
}

# ----------------------------
# 2) Define the 5 outcomes and default slider positions
# ----------------------------
outcome_defs = [
    {"label": "脳卒中を防ぐ",     "default_slider": 50, "default_sign": "良い"},
    {"label": "心不全を防ぐ",    "default_slider": 50, "default_sign": "良い"},
    {"label": "めまいが起こる",  "default_slider": 50, "default_sign": "悪い"},
    {"label": "頻尿が増える",    "default_slider": 50, "default_sign": "悪い"},
    {"label": "転倒が起きる",    "default_slider": 50, "default_sign": "悪い"},
]

st.sidebar.header("入力：各項目の評価")

user_data = []
for od in outcome_defs:
    st.sidebar.write(f"### {od['label']}")

    # Slider from 0 to 100
    val = st.sidebar.slider(
        f"{od['label']}：変化の大きさ (目安)",
        min_value=0, max_value=100, value=od['default_slider'], step=1
    )
    
    # Convert slider range to ±0.2 for demonstration
    normalized = (val - 50) / 50.0  # => -1..+1
    rd = 0.2 * normalized          # => -0.2..+0.2

    # Pick sign (beneficial or harmful) from dictionary
    chosen_sign_label = st.sidebar.radio(
        f"{od['label']} は良い？悪い？",
        list(sign_map.keys()),
        index=0 if od["default_sign"] == "良い" else 1,
    )
    sign_value = sign_map[chosen_sign_label]

    # Pick importance from dictionary
    chosen_imp_label = st.sidebar.radio(
        f"{od['label']} の重要度は？",
        list(importance_map.keys()),
        index=0  # default to "高い"
    )
    imp_value = importance_map[chosen_imp_label]

    user_data.append({
        "outcome": od["label"],
        "slider_value": val,
        "rd": rd,            # numeric -0.2..+0.2
        "sign": sign_value,  # +1 or -1
        "importance": imp_value,  # 1.0, 0.5, 0.0
    })

if st.button("結果を見る"):
    # ----------------------------
    # 3) Hidden numeric calculation
    # ----------------------------
    net_effect = sum(row["rd"] * row["sign"] * row["importance"] for row in user_data)

    # ----------------------------
    # 4) Worded output
    # ----------------------------
    st.subheader("総合コメント")
    if net_effect > 0.05:
        st.write("全体的に**悪化**する項目がやや優勢かもしれません。慎重に検討しましょう。")
    elif net_effect > 0:
        st.write("どちらかと言うと悪い方向ですが、大きくはないかもしれません。")
    elif abs(net_effect) < 1e-9:
        st.write("良い影響も悪い影響も特にみられないか、釣り合っているようです。")
    else:
        # net_effect < 0
        if net_effect < -0.05:
            st.write("全体的に**改善**が期待できるかもしれません。")
        else:
            st.write("多少の改善があるかもしれませんが、大きくはないかもしれません。")

    # Show a quick overview
    st.write("### 各項目の状況")
    for row in user_data:
        st.write(f"- {row['outcome']}： 重要度 = {row['importance']}, Sign = {row['sign']}, slider={row['slider_value']}")
