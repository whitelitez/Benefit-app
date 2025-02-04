import streamlit as st

def main():
    st.title("Net Benefit Evaluation Prototype (No Hardcoded Placeholders)")

    st.markdown("""
    **Overview**:
    - This prototype lets users (e.g., patients) input **Risk Differences** (RD),
      **Confidence Intervals**, and **Outcome Importance** for a set of outcomes.
    - No hard-coded RD defaults — the user explicitly enters all values.
    - We demonstrate a simple net benefit calculation based on (RD * importance).
    - You can later integrate advanced formulas (AHP, Swing Weighting, etc.).
    """)

    # Define the outcomes we want to evaluate.
    # We'll just name them here; the user sets the numeric values.
    outcome_labels = [
        "Prevention of stroke",
        "Prevention of heart failure",
        "Dizziness",
        "Urination frequency",
        "Fall risk"
    ]

    st.sidebar.header("1) Outcomes, Risk Differences, and Confidence Intervals")

    # We'll store user-input data for each outcome in a list
    user_data = []

    for label in outcome_labels:
        st.sidebar.subheader(label)

        # Let user input numeric RD, CI lower, CI upper from scratch
        rd_value = st.sidebar.number_input(
            f"{label} – Risk Difference (E_ijk)",
            value=0.0,  # default to 0.0 for demonstration
            format="%.4f"
        )
        ci_lower = st.sidebar.number_input(
            f"{label} – 95% CI (Lower)",
            value=0.0,
            format="%.4f"
        )
        ci_upper = st.sidebar.number_input(
            f"{label} – 95% CI (Upper)",
            value=0.0,
            format="%.4f"
        )

        # Importance selection
        chosen_importance_label = st.sidebar.radio(
            f"{label} – Importance",
            ["High", "Medium", "Low"],
            index=1  # "Medium" as the default
        )
        imp_value = convert_importance(chosen_importance_label)

        # Save all info in a dictionary
        user_data.append({
            "outcome": label,
            "rd": rd_value,
            "ci_lower": ci_lower,
            "ci_upper": ci_upper,
            "importance": imp_value,
        })

    st.sidebar.header("2) Additional Constraints")
    st.sidebar.write("Specify the level of concern for each constraint.")

    constraint_options = ["No problem", "Moderate concern", "Severe problem"]

    cost_label = st.sidebar.radio("Financial / Cost Issues", constraint_options, index=0)
    access_label = st.sidebar.radio("Access / Transportation Issues", constraint_options, index=0)
    care_label = st.sidebar.radio("Home Care / Assistance Issues", constraint_options, index=0)

    # Convert these labels to numeric values for the logic
    cost_val = constraint_to_numeric(cost_label)
    access_val = constraint_to_numeric(access_label)
    care_val = constraint_to_numeric(care_label)

    # Button to calculate
    if st.button("Calculate Net Benefit"):
        show_results(user_data, cost_val, access_val, care_val)


def show_results(user_data, cost_val, access_val, care_val):
    """
    Summarize the net benefit calculation using a simple approach:
       net_effect = sum(RD_k * importance_k).

    We'll also show the CI that the user entered, but not necessarily do
    anything fancy with it unless you want to incorporate it in the logic.
    """
    st.subheader("A) Outcome-Level Details")

    net_effect = 0.0

    for row in user_data:
        # Basic additive model: net_effect += (rd * importance)
        # In an advanced approach, you might incorporate correlation or 
        # more sophisticated weighting. This is just the simplest approach.
        net_effect += row["rd"] * row["importance"]

    # Provide interpretive feedback
    if net_effect > 0.05:
        st.error("Overall net effect may be harmful (positive direction).")
    elif net_effect > 0:
        st.warning("Somewhat harmful, but of smaller magnitude.")
    elif abs(net_effect) < 1e-9:
        st.info("Overall effect is approximately neutral.")
    else:  # net_effect < 0
        if net_effect < -0.05:
            st.success("Overall net effect may be beneficial (negative direction).")
        else:
            st.info("Somewhat beneficial, but of smaller magnitude.")

    st.markdown("### Individual Outcomes")
    for row in user_data:
        arrow = get_arrow(row["rd"])
        stars_html = star_html_3(row["importance"])

        # If RD > 0, you might label it harmful or improved risk
        # but we simply note the sign in parentheses
        sign_text = "Positive RD" if row["rd"] > 0 else "Negative RD" if row["rd"] < 0 else "Zero"

        st.markdown(
            f"- **{row['outcome']}**: {stars_html} {arrow} ({sign_text}) "
            f"[95% CI: {row['ci_lower']}, {row['ci_upper']}]",
            unsafe_allow_html=True
        )

    # Constraints
    st.subheader("B) Constraints")
    constraint_total = cost_val + access_val + care_val

    if constraint_total == 0:
        st.success("No major constraints identified. Feasibility looks good.")
    elif constraint_total <= 1:
        st.info("Some minor constraints. Possibly manageable with moderate effort.")
    elif constraint_total <= 2:
        st.warning("Several constraints likely. Additional support or adjustments may be required.")
    else:
        st.error("Severe constraints across multiple dimensions. Careful planning needed.")

    st.markdown("### Constraint Breakdown")
    st.write(f"- Financial: **{numeric_to_constraint_label(cost_val)}**")
    st.write(f"- Access: **{numeric_to_constraint_label(access_val)}**")
    st.write(f"- Care: **{numeric_to_constraint_label(care_val)}**")

    # Placeholder for advanced methods
    st.subheader("C) Advanced Methods (Placeholder)")
    st.markdown("""
    In a more advanced version:
    - **Incorporate confidence intervals** into a probabilistic net benefit approach.
    - Use **AHP, Swing Weighting, or Discrete Choice Experiments** to derive or refine the 
      'importance' weighting for each outcome.
    - Combine multiple outcomes with correlation or other advanced modeling from 
      the professor's formulas.
    """)


# ---------------- HELPER FUNCTIONS ----------------

def convert_importance(label):
    """
    Convert user-friendly importance labels to numeric weighting values.
    """
    if label == "High":
        return 1.0
    elif label == "Medium":
        return 0.5
    else:
        # "Low"
        return 0.0

def constraint_to_numeric(label):
    """
    Convert constraint labels to numeric values for summation.
    """
    if label == "No problem":
        return 0.0
    elif label == "Moderate concern":
        return 0.5
    else:
        return 1.0

def numeric_to_constraint_label(value):
    """
    Inverse mapping for constraint values.
    """
    if value == 0.0:
        return "No problem"
    elif value == 0.5:
        return "Moderate concern"
    else:
        return "Severe problem"

def get_arrow(rd):
    """
    Return arrow based on Risk Difference sign and threshold.
    """
    if rd > 0.05:
        return "⬆️"
    elif rd < -0.05:
        return "⬇️"
    else:
        return "➡️"

def star_html_3(importance):
    """
    Return an HTML string with 3 stars, colored gold or gray based on importance.
    High (1.0): 3 gold
    Medium (0.5): 2 gold, 1 gray
    Low (0.0): 1 gold, 2 gray (adjust if you'd prefer 0 gold for Low).
    """
    if importance == 1.0:
        filled = 3
    elif importance == 0.5:
        filled = 2
    else:
        filled = 1

    total = 3
    stars_html = ""
    for i in range(total):
        if i < filled:
            stars_html += "<span style='color:gold;font-size:18px;'>★</span>"
        else:
            stars_html += "<span style='color:lightgray;font-size:18px;'>★</span>"

    return stars_html


if __name__ == "__main__":
    main()
