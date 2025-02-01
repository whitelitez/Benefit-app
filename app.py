import streamlit as st

st.title("高血圧治療 オプション評価ツール")
st.markdown("""
このツールでは、以下の5つの項目について、  
①「この治療でどのくらい変化しそうか」をざっくりスライダーで選び、  
② その項目が「体に良い方向か、悪い方向か」、  
③ どの程度「あなたにとって重要」かを選んでください。  
最後に、それらをまとめたコメントを表示します。
**数値は表示せず、全体的な傾向だけ**をお知らせします。
""")

# Define the 5 outcomes
outcome_defs = [
    {"label": "脳卒中を防ぐ", "default_slider": 50,  "default_sign": +1},  # 0-100 scale
    {"label": "心不全を防ぐ", "default_slider": 50,  "default_sign": +1},
    {"label": "めまいが起こる", "default_slider": 50,"default_sign": -1},
    {"label": "頻尿が増える", "default_slider": 50,  "default_sign": -1},
    {"label": "転倒が起きる", "default_slider": 50,  "default_sign": -1},
]

st.sidebar.header("入力：各項目の評価")

user_data = []
for i, od in enumerate(outcome_defs):
    st.sidebar.write(f"### {od['label']}")
    
    # Slider from 0 to 100, mapped to -0.1..+0.1 or any range you want
    #  - We'll interpret <50 as "better" (negative RD) 
    #  - 50 as neutral 
    #  - >50 as "worse" (positive RD)
    val = st.sidebar.slider(
        f"{od['label']}：変化の大きさ (目安)",
        min_value=0, max_value=100, value=od['default_slider'], step=1,
        help="数が低いほど改善（リスク減）かも、数が高いほど悪化（リスク増）かも。"
    )
    
    # Convert slider to a risk difference scale
    # For example, if slider < 50 => negative RD, if slider > 50 => positive RD
    # The maximum we allow is ±0.2 for demonstration. Adjust as needed.
    normalized = (val - 50) / 50.0  # => range -1..+1
    rd = 0.2 * normalized          # => range -0.2..+0.2
    
    # Beneficial or harmful:
    sign_label = st.sidebar.radio(
        f"{od['label']} はプラスかマイナス？",
        options=[
            ("✅ 体に良い（+1）", +1),
            ("⚠️ 体に悪い（−1）", -1),
        ],
        index=0 if od["default_sign"] == +1 else 1,
    )
    
    # Importance: High / Medium / Low
    importance_label = st.sidebar.radio(
        f"{od['label']} の重要度は？",
        [
            ("高い (1.0)", 1.0),
            ("中くらい (0.5)", 0.5),
            ("低い (0.0)", 0.0),
        ],
        index=0,
    )
    
    user_data.append({
        "outcome": od["label"],
        "slider_value": val,
        "rd": rd,  # the numeric interpretation
        "sign": sign_label[1],  # +1 or -1
        "importance": importance_label[1],  # 1.0 / 0.5 / 0.0
    })

if st.button("結果を見る"):
    # Hidden numeric calculation
    net_effect = sum((row["sign"] * row["rd"] * row["importance"]) for row in user_data)
    
    st.subheader("総合コメント")
    if net_effect > 0.05:
        st.write("全体として、**悪化**する項目がやや優勢かもしれません。慎重に検討を。")
    elif net_effect > 0:
        st.write("少し良くない方向かもしれませんが、大きな差はなさそうにも見えます。")
    elif abs(net_effect) < 1e-9:
        st.write("良い影響も悪い影響も特に見られないか、釣り合っている可能性があります。")
    else:
        # net_effect < 0
        if net_effect < -0.05:
            st.write("全体的に**改善**が期待できるかもしれません。")
        else:
            st.write("多少の改善があるかもしれませんが、大きくはなさそうです。")
    
    # Optionally show a mini "visual" for each outcome
    st.markdown("### 各項目のざっくりイメージ")
    for row in user_data:
        # We'll build a short text showing: outcome name + an emoji scale
        # e.g., if sign=+1 but slider_value <50 => "some mismatch," but let's keep it simple
        rd_emoji = "→"  # neutral
        if row["rd"] > 0.05:
            rd_emoji = "↑"
        elif row["rd"] < -0.05:
            rd_emoji = "↓"
        
        importance_emoji = "⭐" * int(row["importance"] * 2)  # 1.0 => 2 stars, 0.5 => 1 star, 0.0 => none

        st.write(f"- **{row['outcome']}** {rd_emoji} {importance_emoji}")
