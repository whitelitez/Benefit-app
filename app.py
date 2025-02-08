import streamlit as st
import math

def main():
    st.title("Net Benefit (K24) Calculation – Fk Static, Eijk Editable")

    st.markdown("""
    This app replicates the Excel logic, with:
    - F<sub>k</sub> (beneficial/harmful flags) set to fixed values (non-editable).
    - E<sub>k</sub> (Risk Difference) is user-editable.
    - I<sub>k</sub> (Importance, 0–100) is user-editable.
    
    Formula references (Excel-like):
    - F<sub>k</sub> in column E is static.
    - E<sub>k</sub> in column F is user input.
    - I<sub>k</sub> in column I is user input (0–100).
    - J<sub>k</sub> = I<sub>k</sub> / Σ I<sub>k</sub>.
    - K<sub>k</sub> = E<sub>k</sub> × J<sub>k</sub> × F<sub>k</sub>.
    - SUM(K<sub>k</sub>) => K17.
    - K24 = ROUND(1000 × K17, 0).
    """)

    # Define 5 outcomes with Fk fixed
    # These F values correspond to your example:
    #  1, 1, -1, -1, -1
    # with default E values from your screenshot (0.1, -0.1, 0.02, -0.01, -0.02).
    # The user can edit E if they like.
    # The user can also edit I (0..100).
    outcomes = [
        {"label": "Outcome 1", "f": 1,  "default_e": 0.1,   "default_i": 100},
        {"label": "Outcome 2", "f": 1,  "default_e": -0.1, "default_i": 29},
        {"label": "Outcome 3", "f": -1, "default_e": 0.02, "default_i": 5},
        {"label": "Outcome 4", "f": -1, "default_e": -0.01,"default_i": 4},
        {"label": "Outcome 5", "f": -1, "default_e": -0.02,"default_i": 13},
    ]

    st.sidebar.header("E (Risk Difference) & I (Importance)")

    user_data = []
    for item in outcomes:
        st.sidebar.subheader(item["label"])

        # F is static, so we don't show an input for it; we only display it:
        st.sidebar.write(f"F (fixed) = {item['f']}")

        e_val = st.sidebar.number_input(
            f"{item['label']}: E (Risk Diff)",
            value=float(item["default_e"]),
            format="%.3f"
        )

        i_val = st.sidebar.slider(
            f"{item['label']}: I (Importance 0–100)",
            min_value=0,
            max_value=100,
            value=item["default_i"],
            step=1
        )

        user_data.append({
            "label": item["label"],
            "f": item["f"],       # static
            "e": e_val,           # user editable
            "i": i_val            # user editable
        })

    if st.button("Compute K24"):
        show_results(user_data)

def show_results(user_data):
    """
    Reproduce the Excel logic:
      K_k = E_k * (I_k / sum(I_k)) * F_k
      K17 = sum(K_k)
      K24 = round(1000 * K17)
    """

    st.subheader("Step 1: Summation of I (ΣI)")
    total_i = sum(row["i"] for row in user_data)
    st.write(f"ΣI = {total_i} (sum of importance values)")

    if abs(total_i) < 1e-9:
        st.error("All importance values are zero. Cannot normalize. Please set at least one outcome > 0.")
        return

    # Compute K for each outcome
    st.subheader("Step 2: Compute K_k = E_k × (I_k / ΣI) × F_k")
    k_values = []
    for row in user_data:
        j_k = row["i"] / total_i  # J_k
        k_val = row["e"] * j_k * row["f"]
        k_values.append(k_val)

        st.markdown(
            f"- **{row['label']}**: F={row['f']}, E={row['e']:.3f}, I={row['i']}, "
            f"J={j_k:.3f}, **K={k_val:.4f}**"
        )

    # Sum of K_k => K17
    k17 = sum(k_values)
    st.subheader("Step 3: K17 = SUM(K_k)")
    st.write(f"K17 = {k17:.4f}")

    # K24 = ROUND(1000 × K17, 0)
    k24 = round(1000 * k17, 0)
    st.subheader("Step 4: K24 = ROUND(1000 × K17, 0)")
    st.write(f"K24 = {k24}")

    st.markdown("""
    The sign of K24 indicates harmful (+) vs. beneficial (–), 
    depending on how F and E are assigned.
    """)

if __name__ == "__main__":
    main()
