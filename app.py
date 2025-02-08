import streamlit as st
import math

def main():
    # Page title
    st.title("Net Benefit Calculation App (Excel-Style Formulas)")

    # Intro / disclaimers
    st.markdown(
        """
        <p style='color:red; font-weight:bold;'>
        (No Hardcoded Placeholders Except for Defaults; Excel Logic in Python)
        </p>
        <p>
        <strong>Overview:</strong><br>
        This app replicates the professor's Excel logic for net benefit:
        <ul>
          <li><em>F<sub>k</sub></em> is a fixed sign (+1 or –1) indicating whether an outcome is
              "beneficial" or "harmful" if it goes up.</li>
          <li><em>E<sub>k</sub></em> (Risk Difference) is user-editable, representing the difference
              between intervention and control in absolute risk.</li>
          <li><em>I<sub>k</sub></em> (Importance, 0–100) is also user-editable.</li>
          <li>We normalize importance via <em>J<sub>k</sub> = I<sub>k</sub> / ΣI<sub>k</sub></em>,
              then compute <em>K<sub>k</sub> = E<sub>k</sub> × J<sub>k</sub> × F<sub>k</sub></em>.</li>
          <li>We sum <em>K<sub>k</sub></em> for all outcomes into <em>K17</em>,
              then compute <em>K24 = ROUND(1000 × K17)</em>.</li>
        </ul>
        We also capture <em>Constraints</em> (cost, access, care) and show interpretive messages.
        </p>
        """,
        unsafe_allow_html=True
    )

    # Define up to 5 outcomes with fixed Fk, default E, default I
    # You can expand to 10 outcomes or adjust defaults as needed.
    outcomes = [
        {"label": "Outcome 1: Stroke Prevention",    "f":  1, "default_e":  0.1,  "default_i": 100},
        {"label": "Outcome 2: Heart Failure Prev.",  "f":  1, "default_e": -0.1, "default_i":  29},
        {"label": "Outcome 3: Dizziness",            "f": -1, "default_e":  0.02, "default_i":  5},
        {"label": "Outcome 4: Urination Frequency",  "f": -1, "default_e": -0.01, "default_i":  4},
        {"label": "Outcome 5: Fall Risk",            "f": -1, "default_e": -0.02, "default_i": 13},
    ]

    # PART 1: User Input for E (RD) & I (Importance), with Fk fixed
    st.header("Part 1: Outcome Inputs & Importance")

    user_data = []
    for item in outcomes:
        st.subheader(item["label"])

        # F is fixed — we display it but don't let user edit
        st.write(f"F (fixed) = {item['f']}")

        # E is editable
        e_val = st.number_input(
            f"{item['label']}: E (Risk Difference)",
            value=float(item["default_e"]),
            format="%.3f"
        )

        # I is editable from 0..100
        i_val = st.slider(
            f"{item['label']}: Importance (0..100)",
            min_value=0,
            max_value=100,
            value=item["default_i"],
            step=1
        )

        user_data.append({
            "label": item["label"],
            "f": item["f"],
            "e": e_val,
            "i": i_val
        })

    # PART 2: Constraints
    st.header("Part 2: Constraints")

    st.write("Please specify your level of concern for each constraint:")
    constraint_options = ["No problem", "Moderate concern", "Severe problem"]

    col1, col2, col3 = st.columns(3)
    with col1:
        cost_label = st.radio("Financial / Cost Issues", constraint_options, index=0)
    with col2:
        access_label = st.radio("Access / Transportation Issues", constraint_options, index=0)
    with col3:
        care_label = st.radio("Home Care / Assistance Issues", constraint_options, index=0)

    cost_val = constraint_to_numeric(cost_label)
    access_val = constraint_to_numeric(access_label)
    care_val = constraint_to_numeric(care_label)

    # Button to calculate net benefit
    if st.button("Calculate Net Benefit (K24)"):
        show_results(user_data, cost_val, access_val, care_val)


def show_results(user_data, cost_val, access_val, care_val):
    """
    Implements the Excel-like logic:
      1) total_i = sum(I_k).
      2) For each row, J_k = I_k / total_i, K_k = E_k * J_k * F_k.
      3) K17 = sum(K_k).
      4) K24 = ROUND(1000 * K17, 0).
      Then interpret constraints and show placeholders for advanced expansions.
    """
    st.subheader("A) Net Benefit Calculation Steps")

    # 1) Sum of I
    total_i = sum(row["i"] for row in user_data)
    st.write(f"**Sum of Importance (ΣI)** = {total_i}")

    # Check for zero or near-zero
    if abs(total_i) < 1e-9:
        st.error("All importance values are zero, so we cannot normalize. Please adjust at least one outcome > 0.")
        return

    # 2) Compute each K_k
    k_values = []
    st.markdown("### Row-by-Row Computation of K_k")
    for row in user_data:
        j_k = row["i"] / total_i  # J_k
        k_val = row["e"] * j_k * row["f"]

        k_values.append(k_val)
        # We'll also show star rating and arrow for display
        star_html = star_html_3(row["i"])
        arrow = get_arrow(row["e"] * row["f"])  # interpret sign of E*F
        # If e*f > 0 => "positive RD" arrow, else negative, etc.

        st.markdown(
            f"- **{row['label']}**: F={row['f']}, E={row['e']:.3f}, I={row['i']}, "
            f"J={j_k:.3f}, K={k_val:.4f} {star_html} {arrow}"
        )

    # 3) K17 = sum(K_k)
    k17 = sum(k_values)
    st.markdown(f"**K17** (sum of all K_k) = {k17:.4f}")

    # 4) K24 = ROUND(1000 * K17, 0)
    k24 = round(1000 * k17, 0)
    st.markdown(f"**K24** = round(1000 × K17) = {k24}")

    # Provide interpretive feedback on sign
    if k17 > 0:
        st.warning("Positive K17 => net harmful direction (based on sign conventions).")
    elif abs(k17) < 1e-9:
        st.info("K17 ≈ 0 => net effect is approximately neutral.")
    else:
        st.success("Negative K17 => net beneficial direction (based on sign conventions).")

    # PART B: Constraints Interpretation
    st.subheader("B) Constraints")

    constraint_total = cost_val + access_val + care_val
    if constraint_total == 0:
        st.success("No major constraints identified. Feasibility looks good.")
    elif constraint_total <= 1:
        st.info("Some minor constraints. Possibly manageable with moderate effort.")
    elif constraint_total <= 2:
        st.warning("Multiple constraints likely. Additional support or adjustments needed.")
    else:
        st.error("Severe constraints across multiple dimensions. Careful planning required.")

    st.markdown("### Constraint Breakdown")
    st.write(f"- Financial: **{numeric_to_constraint_label(cost_val)}**")
    st.write(f"- Access: **{numeric_to_constraint_label(access_val)}**")
    st.write(f"- Care: **{numeric_to_constraint_label(care_val)}**")

    # C) Placeholder for advanced expansions
    st.subheader("C) Advanced Methods (Placeholder)")
    st.markdown(
        """
        <p style='color:red; font-weight:bold;'>
        (Not Shown in Production)
        </p>
        <p>
        In a more advanced version:
        <ul>
          <li>Incorporate <strong>correlation matrices</strong> or advanced weighting 
              (AHP, DCE) for better net benefit calculations.</li>
          <li>Handle <strong>confidence intervals</strong> in a probabilistic approach 
              or show intervals for K24.</li>
          <li>Show "per-1000 persons" in a more nuanced way, e.g., 
              <em>K24 = round( 1000 × net_effect )</em> for each scenario.</li>
        </ul>
        </p>
        """,
        unsafe_allow_html=True
    )

# ---------------- HELPER FUNCTIONS ----------------

def get_arrow(value):
    """
    Return arrow based on sign. We consider >0 "harmful", <0 "beneficial", etc.
    Adjust threshold if needed.
    """
    if value > 0.05:
        return "⬆️"
    elif value < -0.05:
        return "⬇️"
    else:
        return "➡️"

def star_html_3(importance_0to100):
    """
    Convert 0..100 => a 1..3 star rating.
    E.g.:
     - 0..33 => 1 star
     - 34..66 => 2 stars
     - 67..100 => 3 stars
    """
    if importance_0to100 <= 33:
        filled = 1
    elif importance_0to100 <= 66:
        filled = 2
    else:
        filled = 3

    stars = ""
    for i in range(3):
        if i < filled:
            stars += "<span style='color:gold;font-size:18px;'>★</span>"
        else:
            stars += "<span style='color:lightgray;font-size:18px;'>★</span>"
    return stars

def constraint_to_numeric(label):
    """
    Convert constraint labels to numeric values for 
    summation or threshold logic.
    """
    if label == "No problem":
        return 0.0
    elif label == "Moderate concern":
        return 0.5
    else:
        return 1.0

def numeric_to_constraint_label(value):
    """
    Reverse mapping for constraint numeric => text.
    """
    if value == 0.0:
        return "No problem"
    elif value == 0.5:
        return "Moderate concern"
    else:
        return "Severe problem"


if __name__ == "__main__":
    main()
