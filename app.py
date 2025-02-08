import streamlit as st
import math

def main():
    # Page title
    st.title("Net Benefit Calculation App (Excel-Style Formulas, Inputs on Sidebar)")

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
          <li><em>F<sub>k</sub></em> is fixed (+1 or –1).</li>
          <li><em>E<sub>k</sub></em> (Risk Difference) is user-editable.</li>
          <li><em>I<sub>k</sub></em> (Importance, 0–100) is user-editable.</li>
          <li><em>J<sub>k</sub> = I<sub>k</sub> / ΣI<sub>k</sub></em>, 
              <em>K<sub>k</sub> = E<sub>k</sub> × J<sub>k</sub> × F<sub>k</sub></em>.</li>
          <li>Sum K<sub>k</sub> → K17, then <em>K24 = ROUND(1000 × K17)</em>.</li>
        </ul>
        All input fields are on the <strong>sidebar</strong>. 
        See below for final results and interpretation.
        </p>
        """,
        unsafe_allow_html=True
    )

    # Define up to 5 outcomes with fixed Fk, default E, default I
    outcomes = [
        {"label": "Outcome 1: Stroke Prevention",    "f":  1, "default_e":  0.1,  "default_i": 100},
        {"label": "Outcome 2: Heart Failure Prev.",  "f":  1, "default_e": -0.1, "default_i":  29},
        {"label": "Outcome 3: Dizziness",            "f": -1, "default_e":  0.02, "default_i":  5},
        {"label": "Outcome 4: Urination Frequency",  "f": -1, "default_e": -0.01,"default_i":  4},
        {"label": "Outcome 5: Fall Risk",            "f": -1, "default_e": -0.02,"default_i": 13},
    ]

    # --------------------------
    # PART 1: Outcome Inputs
    # --------------------------
    st.sidebar.header("1) Outcome Inputs & Importance")

    user_data = []
    for item in outcomes:
        st.sidebar.subheader(item["label"])

        # F is fixed; just display
        st.sidebar.write(f"F (fixed) = {item['f']}")

        # E is editable
        e_val = st.sidebar.number_input(
            f"{item['label']}: E (Risk Diff)",
            value=float(item["default_e"]),
            format="%.3f"
        )

        # I is editable from 0..100
        i_val = st.sidebar.slider(
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

    # --------------------------
    # PART 2: Constraints
    # --------------------------
    st.sidebar.header("2) Constraints")
    st.sidebar.write("Specify your level of concern for each constraint:")

    constraint_options = ["No problem", "Moderate concern", "Severe problem"]

    cost_label = st.sidebar.radio("Financial / Cost Issues", constraint_options, index=0)
    access_label = st.sidebar.radio("Access / Transportation Issues", constraint_options, index=0)
    care_label = st.sidebar.radio("Home Care / Assistance Issues", constraint_options, index=0)

    cost_val = constraint_to_numeric(cost_label)
    access_val = constraint_to_numeric(access_label)
    care_val = constraint_to_numeric(care_label)

    # Button to calculate net benefit
    if st.sidebar.button("Calculate Net Benefit (K24)"):
        # We move to the results section
        show_results(user_data, cost_val, access_val, care_val)


def show_results(user_data, cost_val, access_val, care_val):
    """
    Implements the Excel-like logic:
      1) total_i = sum(I_k).
      2) J_k = I_k / total_i
      3) K_k = E_k * J_k * F_k
      4) K17 = sum(K_k)
      5) K24 = round(1000 * K17)
    Then interpret constraints, show star ratings, etc.
    """
    st.subheader("A) Net Benefit Calculation Steps")

    # 1) Sum of I
    total_i = sum(row["i"] for row in user_data)
    st.write(f"**Sum of Importance (ΣI)** = {total_i}")

    if abs(total_i) < 1e-9:
        st.error("All importance values are zero. Cannot normalize. Please set at least one outcome > 0.")
        return

    # 2) Compute each K_k
    k_values = []
    st.markdown("### Row-by-Row Computation of K_k (E×(I/ΣI)×F)")
    for row in user_data:
        j_k = row["i"] / total_i
        k_val = row["e"] * j_k * row["f"]
        k_values.append(k_val)

        stars = star_html_3(row["i"])
        arrow = get_arrow(row["e"] * row["f"])

        st.markdown(
            f"- **{row['label']}**: "
            f"F={row['f']}, E={row['e']:.3f}, I={row['i']}, J={j_k:.3f}, "
            f"K={k_val:.4f} &nbsp;&nbsp;{stars} {arrow}",
            unsafe_allow_html=True
        )

    # 3) K17 = sum(K_k)
    k17 = sum(k_values)
    st.markdown(f"**K17** (sum of K_k) = {k17:.4f}")

    # 4) K24 = round(1000 * K17)
    k24 = round(1000 * k17, 0)
    st.markdown(f"**K24** = round(1000 × K17, 0) = {k24}")

    # Provide interpretive feedback on sign
    if k17 > 0:
        st.warning("Positive K17 => net harmful direction (assuming F=+1 => beneficial?).")
    elif abs(k17) < 1e-9:
        st.info("K17 ≈ 0 => net effect is approximately neutral.")
    else:
        st.success("Negative K17 => net beneficial direction (based on sign conventions).")

    # PART B: Constraints
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
          <li>Show "per-1000 persons" in a more nuanced way, 
              e.g., separate net effects for beneficial vs. harmful outcomes.</li>
        </ul>
        </p>
        """,
        unsafe_allow_html=True
    )


# ---------------- HELPER FUNCTIONS ----------------

def get_arrow(value):
    """
    Return arrow based on sign. 
    > 0 => up arrow, < 0 => down arrow, else => right arrow.
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
    For example:
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
    Convert constraint labels to numeric values for summation logic.
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
