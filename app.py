import streamlit as st

st.title("高血圧治療 オプション評価ツール (星マーク＆矢印付き)")

st.markdown("""
このツールでは、次の5つの項目に対して、
1. 「この治療でどのくらい変化しそうか」をスライダーで選ぶ  
2. 「その項目は体に良いのか、悪いのか」  
3. 「その項目がどのくらいあなたにとって重要か」を選択  
の3ステップを行い、最後に総合的な傾向をコメントします。  

また、**最終表示**では数値の代わりに「星」や「矢印」で
おおまかなイメージを示します。
""")

# ----------------------------
# 1) Define dictionaries for radio labels -> numeric values
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
# 2) Define the 5 outcomes
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

    # Slider: 0..100
    val = st.sidebar.slider(
        f"{od['label']}：変化の大きさ (目安)",
        min_value=0, max_value=100,
        value=od['default_slider'],
        step=1
    )
    
    # Convert slider 0..100 => -0.2..+0.2 for demonstration
    normalized = (val - 50) / 50.0  # => -1..+1
    rd_value = 0.2 * normalized    # => -0.2..+0.2

    # Sign radio
    chosen_sign_label = st.sidebar.radio(
        f"{od['label']} は良い？悪い？",
        list(sign_map.keys()),
        index=0 if od["default_sign"] == "良い" else 1
    )
    sign_num = sign_map[chosen_sign_label]  # +1 or -1

    # Importance radio
    chosen_imp_label = st.sidebar.radio(
        f"{od['label']} の重要度は？",
        list(importance_map.keys()),
        index=0  # default "高い"
    )
    imp_num = importance_map[chosen_imp_label]  # 1.0, 0.5, or 0.0

    user_data.append({
        "outcome": od["label"],
        "slider_raw": val,   # 0..100
        "rd": rd_value,      # numeric -0.2..+0.2
        "sign": sign_num,    # +1 or -1
        "importance": imp_num,  
    })

if st.button("結果を見る"):
    # ----------------------------
    # 3) Hidden numeric calculation
    # ----------------------------
    net_effect = sum(row["rd"] * row["sign"] * row["importance"] for row in user_data)

    st.subheader("総合コメント")
    if net_effect > 0.05:
        st.write("全体として、悪い方向に進む可能性がやや強いように見えます。")
    elif net_effect > 0:
        st.write("どちらかと言うと悪化するかもしれませんが、大きな差はなさそうです。")
    elif abs(net_effect) < 1e-9:
        st.write("良い影響と悪い影響がおおむね釣り合っているか、ほぼ変化なしと見えます。")
    else:
        # net_effect < 0
        if net_effect < -0.05:
            st.write("全体的には改善が期待できるかもしれません。")
        else:
            st.write("多少の改善があるかもしれませんが、大きくはない可能性もあります。")

    st.markdown("### 各項目の状況")
    # ----------------------------
    # 4) Show star & arrow visuals
    # ----------------------------
    for row in user_data:
        # Determine arrow based on RD
        if row["rd"] > 0.05:
            arrow = "↑"
        elif row["rd"] < -0.05:
            arrow = "↓"
        else:
            arrow = "→"

        # Determine number of stars based on importance
        if row["importance"] == 1.0:
            stars = "⭐⭐"
        elif row["importance"] == 0.5:
            stars = "⭐"
        else:
            stars = ""

        # Build display string
        # Example: "脳卒中を防ぐ：⭐⭐ ↑ (良い)"
        # or "めまいが起こる：⭐ ↓ (悪い)"
        # If sign=+1, show "良い"; if −1, "悪い"
        sign_text = "良い" if row["sign"] == +1 else "悪い"

        st.write(f"- **{row['outcome']}**：{stars} {arrow} ({sign_text})")

