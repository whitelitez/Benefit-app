import streamlit as st
import pandas as pd

st.title("脳卒中予防の意思決定ツール")
st.write("""
このデモでは、5つのアウトカム（脳卒中予防、心不全予防、めまい、頻尿、転倒）の
Risk Difference (RD) と 95%信頼区間をユーザーが入力できるようにして、
簡易的な正味の益 (Net Benefit) を計算します。
""")

# -------------------------
# 1. Define outcomes & weights
# -------------------------
outcomes_info = [
    {"name_jp": "脳卒中予防", "is_beneficial": True,  "default_rd": 0.10, "default_low": 0.05, "default_high": 0.15, "weight": 100},
    {"name_jp": "心不全予防", "is_beneficial": True,  "default_rd": -0.10,"default_low": -0.16,"default_high": -0.04,"weight": 29},
    {"name_jp": "めまい",    "is_beneficial": False, "default_rd": 0.02, "default_low": 0.011,"default_high": 0.029,"weight": 5},
    {"name_jp": "頻尿",     "is_beneficial": False, "default_rd": -0.01,"default_low": -0.03,"default_high": 0.01, "weight": 4},
    {"name_jp": "転倒",     "is_beneficial": False, "default_rd": -0.02,"default_low": -0.06,"default_high": 0.02, "weight": 13},
]

st.sidebar.header("アウトカムごとの入力 (E_ijk & 95%CI)")
st.sidebar.write("**下の数値を変更して結果を確認してください。**")

# -------------------------
# 2. User Inputs for RD & CIs
# -------------------------
user_data = []
for outcome in outcomes_info:
    name = outcome["name_jp"]
    sign = 1 if outcome["is_beneficial"] else -1
    w = outcome["weight"]  # direct weighting approach

    rd = st.sidebar.number_input(
        f"{name} RD (default={outcome['default_rd']})", 
        value=outcome['default_rd'], 
        step=0.01, 
        format="%.3f"
    )
    lower_ci = st.sidebar.number_input(
        f"{name} Lower CI (default={outcome['default_low']})", 
        value=outcome['default_low'], 
        step=0.01, 
        format="%.3f"
    )
    upper_ci = st.sidebar.number_input(
        f"{name} Upper CI (default={outcome['default_high']})", 
        value=outcome['default_high'], 
        step=0.01, 
        format="%.3f"
    )

    # Store data in a structure for further display/calculation
    user_data.append({
        "アウトカム": name,
        "益/害": "益" if sign == 1 else "害",
        "RD (E_ijk)": rd,
        "95%CI Lower": lower_ci,
        "95%CI Upper": upper_ci,
        "Weight (W_k)": w,
        "Sign (F_k)": sign
    })

# -------------------------
# 3. Compute Net Benefit
# -------------------------
# NetBenefit = sum( F_k * E_k * (W_k/100) )
net_benefit = 0.0
for row in user_data:
    sign = row["Sign (F_k)"]
    e_val = row["RD (E_ijk)"]
    weight = row["Weight (W_k)"]
    net_benefit += sign * e_val * (weight / 100.0)

# Multiply by 1000 for "per 1000 patients" interpretation
net_benefit_per_1000 = net_benefit * 1000

# -------------------------
# 4. Display Results
# -------------------------
st.subheader("入力されたアウトカムデータ")
df_display = pd.DataFrame(user_data)
df_display = df_display[["アウトカム", "益/害", "RD (E_ijk)", "95%CI Lower", "95%CI Upper", "Weight (W_k)"]]
st.table(df_display)

st.subheader("正味の益 (Net Benefit)")
st.write(f"""
- **合計正味の益** (単位なし): `{net_benefit:.4f}`
- **1000人あたりの正味の益**: `{net_benefit_per_1000:.1f}`
""")
st.markdown("""
*注*: これは簡易計算です。実際のバリアンスや相関行列による
厳密な信頼区間計算は含んでいません。
""")

st.success("処理が完了しました。下の数値を変えて正味の益が変化する様子を試してみてください！")

# (Optional) Additional logic or thresholds
# For example, we could classify the result:
if net_benefit_per_1000 > 0:
    st.info("**推定: 治療介入による正味の益はプラスです。**")
else:
    st.warning("**推定: 治療介入による正味の益はマイナスかもしれません。**")
