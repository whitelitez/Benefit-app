import streamlit as st
import pandas as pd

# Initialize Streamlit app
def main():
    st.title("高血圧治療 オプション評価ツール (カラー星バージョン)")
    st.markdown("""
    重要度を3つの星で表しますが、星は同じ形 (★) を使い、
    色によって「埋まっている (金色)」「埋まっていない (灰色)」を区別します。
    """)
    
    # Dictionaries for mappings
    importance_map = {"重要": 1.0, "やや重要": 0.5, "重要でない": 0.0}
    sign_map = {"良い": +1, "悪い": -1}
    constraint_map = {
        "特に問題ない": 0.0,
        "少し問題がある": 0.5,
        "大きな問題": 1.0
    }
    
    # Treatment outcomes
    outcome_defs = [
        {"label": "脳卒中予防", "default_slider": 50, "default_sign": "良い"},
        {"label": "心不全予防", "default_slider": 50, "default_sign": "良い"},
        {"label": "めまい", "default_slider": 50, "default_sign": "悪い"},
        {"label": "頻尿", "default_slider": 50, "default_sign": "悪い"},
        {"label": "転倒", "default_slider": 50, "default_sign": "悪い"},
    ]
    
    st.header("① 高血圧に対する内服薬のアウトカム")
    with st.expander("治療アウトカムを入力する", expanded=True):
        user_data = []
        for od in outcome_defs:
            st.write(f"### {od['label']} ({'益' if od['default_sign'] == '良い' else '害'})")
            val = st.slider(
                f"{od['label']} の変化の大きさ (0=良くなる〜100=悪くなる目安)",
                min_value=0, max_value=100,
                value=od["default_slider"], step=1
            )
            rd_value = slider_to_rd(val)
            chosen_imp_label = st.radio(
                f"{od['label']} の重要度は？",
                list(importance_map.keys()),
                index=0
            )
            imp_value = importance_map[chosen_imp_label]
            user_data.append({
                "outcome": od["label"],
                "rd": rd_value,
                "sign": sign_map[od["default_sign"]],
                "importance": imp_value,
            })
    
    st.header("② あなたの価値観")
    with st.expander("制約を入力する", expanded=True):
        st.write("費用面・アクセス面・介助面などの問題度を選んでください。")
        financial_label = st.radio("費用面の制約", list(constraint_map.keys()), index=0)
        financial_val = constraint_map[financial_label]
        access_label = st.radio("アクセス面の制約（通院など）", list(constraint_map.keys()), index=0)
        access_val = constraint_map[access_label]
        care_label = st.radio("日常生活の制約（介護など）", list(constraint_map.keys()), index=0)
        care_val = constraint_map[care_label]
    
    if st.button("結果を見る"):
        show_results(user_data, financial_val, access_val, care_val)

def show_results(user_data, financial_val, access_val, care_val):
    net_effect = sum(row["rd"] * row["sign"] * row["importance"] for row in user_data)
    st.subheader("A) 治療アウトカムに関するコメント")
    if net_effect > 0.05:
        st.error("全体として、やや悪化する可能性が高いかもしれません。")
    elif net_effect > 0:
        st.warning("どちらかと言うと悪い方向ですが、大きくはないかもしれません。")
    elif abs(net_effect) < 1e-9:
        st.info("良い影響と悪い影響が釣り合っているか、ほぼ変化がないかもしれません。")
    else:
        if net_effect < -0.05:
            st.success("全体的に改善が期待できるかもしれません。")
        else:
            st.info("多少の改善があるかもしれませんが、大きくはないでしょう。")
    
    st.markdown("### 各項目の様子")
    for row in user_data:
        arrow = get_arrow(row["rd"])
        stars_html = star_html_3(row["importance"])
        sign_text = "良い" if row["sign"] == +1 else "悪い"
        st.markdown(f"- **{row['outcome']}**：{stars_html} {arrow} ({sign_text})", unsafe_allow_html=True)

def slider_to_rd(val):
    normalized = (val - 50) / 50.0
    return 0.2 * normalized

def get_arrow(rd):
    if rd > 0.05:
        return "↑"
    elif rd < -0.05:
        return "↓"
    else:
        return "→"

def star_html_3(importance):
    filled = int(importance * 3)
    total = 3
    stars_html = "".join(["<span style='color:gold;font-size:18px;'>★</span>" if i < filled else "<span style='color:lightgray;font-size:18px;'>★</span>" for i in range(total)])
    return stars_html

if __name__ == "__main__":
    main()
