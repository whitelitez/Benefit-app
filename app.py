import streamlit as st

st.title("高血圧治療の簡易評価ツール（5アウトカム + 3段階重要度）")

st.markdown("""
このツールでは、脳卒中予防・心不全予防・めまい・頻尿・転倒の5つのアウトカムそれぞれに対して、
以下の情報を入力できます：
- **リスク差 (RD)**：介入群の絶対リスク - 対照群の絶対リスク  
- **有益 (+1) / 有害 (−1)**：そのアウトカムが全体にプラスかマイナスか  
- **重要度 (1.0 / 0.5 / 0.0)**：非常に重要、重要、または重要でない  
入力内容に基づいて、総合的な影響に対するコメントを表示します。
（数値の結果は一切表示しません）
""")

# ----------------------------------------------------------------------------------
# Define the five outcomes with default RD and default sign
# (Users can override these in the UI)
# ----------------------------------------------------------------------------------
outcomes_info = [
    {
        "name_jp": "脳卒中予防", 
        "default_rd": 0.10,
        "default_sign": +1,  # Typically beneficial
    },
    {
        "name_jp": "心不全予防",
        "default_rd": 0.10,
        "default_sign": +1,  # Typically beneficial
    },
    {
        "name_jp": "めまい",
        "default_rd": 0.02,
        "default_sign": -1,  # Typically harmful
    },
    {
        "name_jp": "頻尿",
        "default_rd": -0.01,
        "default_sign": -1,  # Typically harmful
    },
    {
        "name_jp": "転倒",
        "default_rd": -0.02,
        "default_sign": -1,  # Typically harmful
    },
]

st.sidebar.header("アウトカム設定")

user_data = []
for outcome in outcomes_info:
    name_jp = outcome["name_jp"]
    default_rd = outcome["default_rd"]
    default_sign = outcome["default_sign"]

    st.sidebar.write(f"### {name_jp}")
    
    # User sets RD
    rd_val = st.sidebar.number_input(
        f"{name_jp} のリスク差 (RD)",
        value=default_rd,
        step=0.01,
        format="%.3f",
        key=f"rd_{name_jp}"
    )
    
    # User picks sign: beneficial or harmful
    sign_choice = st.sidebar.radio(
        f"{name_jp} は有益か有害か？",
        options=[("有益 (+1)", +1), ("有害 (−1)", -1)],
        index=0 if default_sign == +1 else 1,
        key=f"sign_{name_jp}"
    )
    
    # User picks importance: 1.0, 0.5, or 0.0
    imp_choice = st.sidebar.radio(
        f"{name_jp} の重要度",
        options=[("非常に重要 (1.0)", 1.0),
                 ("重要 (0.5)", 0.5),
                 ("重要でない (0.0)", 0.0)],
        index=0,  # default to very important (you can adjust)
        key=f"imp_{name_jp}"
    )

    user_data.append({
        "アウトカム": name_jp,
        "RD": rd_val,
        "Sign": sign_choice[1],  # numeric +1 or -1
        "Importance": imp_choice[1],  # numeric 1.0, 0.5, or 0.0
    })

if st.button("評価結果を表示"):
    # -----------------------
    # Calculate net effect behind the scenes
    # net_effect = SUM(sign * rd * importance)
    # -----------------------
    net_effect = 0.0
    for row in user_data:
        net_effect += row["Sign"] * row["RD"] * row["Importance"]
    
    st.subheader("総合コメント")
    # Example threshold-based statements (tweak as needed):
    if net_effect > 0.05:
        st.write("""
        全体的に、**プラスの影響**が得られる可能性がやや高いように見えます。
        さらなる検討や医療専門家の意見を踏まえて、最適な治療を選択してください。
        """)
    elif net_effect > 0:
        st.write("""
        わずかながらプラスの影響が期待できるかもしれません。
        ただし、状況により異なるため、慎重に判断してください。
        """)
    elif abs(net_effect) < 1e-9:
        st.write("""
        入力された値の範囲では、全体的にプラスともマイナスとも言えない状況です。
        個人差や他の因子を合わせて考慮する必要があります。
        """)
    else:
        st.write("""
        全体として、**注意が必要な可能性**がうかがえます。
        副作用やリスクが上回る恐れもありますので、担当医とよくご相談ください。
        """)

    # (Optional) Show a table of user inputs if you like:
    st.write("### 参考：入力データ")
    st.table(user_data)
