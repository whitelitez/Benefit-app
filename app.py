import streamlit as st

def main():
    # Title
    st.title("Net Benefit Evaluation Prototype")

    # Disclaimers/Overview in red to highlight placeholders/drafts
    st.markdown(
        """
        <p style='color:red; font-weight:bold;'>
        (No Hardcoded Placeholders)
        </p>
        <p>
        <strong>Overview:</strong><br>
        This prototype lets users (e.g., patients) input <strong>Risk Differences</strong>, 
        Confidence Intervals, and Outcome Importance for a set of outcomes.<br>
        <em>No hard-coded RD defaults</em> — the user explicitly enters all values via sliders (for RD & CI).<br>
        We demonstrate a simple net benefit calculation based on (RD × importance).<br>
        Later, integrate the <strong>professor’s exact formulas</strong> 
        (including <em>AHP, DCE, Swing Weighting</em>, etc.) for the final product.<br>
        Note: The current min/max range for the RD & CI sliders (–0.50 to +0.50) 
        is just a placeholder. Adjust as necessary.
        </p>
        """,
        unsafe_allow_html=True
    )

    # Define the outcomes we want to evaluate
    outcome_labels = [
        "Prevention of stroke",
        "Prevention of heart failure",
        "Dizziness",
        "Urination frequency",
        "Fall risk"
    ]

    # Sidebar inputs for RD, CI, and importance
    st.sidebar.header("1) Outcomes, Risk Differences, and Confidence Intervals")

    user_data = []
    for label in outcome_labels:
        st.sidebar.subheader(label)

        # Risk Difference slider (example range: -0.5 to +0.5)
        rd_value = st.sidebar.slider(
            f"{label} – Risk Difference",
            min_value=-0.50,
            max_value=0.50,
            value=0.0,
            step=0.01
        )

        # 95% CI Lower slider
        ci_lower = st.sidebar.slider(
            f"{label} – 95% CI (Lower)",
            min_value=-0.50,
            max_value=0.50,
            value=0.0,
            step=0.01
        )

        # 95% CI Upper slider
        ci_upper = st.sidebar.slider(
            f"{label} – 95% CI (Upper)",
            min_value=-0.50,
            max_value=0.50,
            value=0.0,
            step=0.01
        )

        # Radio buttons for Importance (High, Medium, Low)
        chosen_importance_label = st.sidebar.radio(
            f"{label} – Importance",
            ["High", "Medium", "Low"],
            index=1  # default "Medium"
        )
        imp_value = convert_importance(chosen_importance_label)

        user_data.append({
            "outcome": label,
            "rd": rd_value,
            "ci_lower": ci_lower,
            "ci_upper": ci_upper,
            "importance": imp_value,
        })

    # Additional constraints
    st.sidebar.header("2) Additional Constraints")
    st.sidebar.write("Specify the level of concern for each constraint.")

    constraint_options = ["No problem", "Moderate concern", "Severe problem"]

    cost_label = st.sidebar.radio("Financial / Cost Issues", constraint_options, index=0)
    access_label = st.sidebar.radio("Access / Transportation Issues", constraint_options, index=0)
    care_label = st.sidebar.radio("Home Care / Assistance Issues", constraint_options, index=0)

    cost_val = constraint_to_numeric(cost_label)
    access_val = constraint_to_numeric(access_label)
    care_val = constraint_to_numeric(care_label)

    if st.button("Calculate Net Benefit"):
        show_results(user_data, cost_val, access_val, care_val)


def show_results(user_data, cost_val, access_val, care_val):
    """
    Summarize the net benefit using a simple approach:
       net_effect = sum(RD_k * importance_k).

    Replace this with the professor's formulas (RD, AHP, DCE, correlation, etc.) as needed.
    """
    st.subheader("A) Outcome-Level Details")

    net_effect = 0.0
    for row in user_data:
        net_effect += row["rd"] * row["importance"]

    # Provide interpretive feedback
    if net_effect > 0.05:
        st.error("Overall net effect seems harmful (positive direction).")
    elif net_effect > 0:
        st.warning("Slightly harmful, but smaller magnitude.")
    elif abs(net_effect) < 1e-9:
        st.info("Overall effect is approximately neutral.")
    else:  # net_effect < 0
        if net_effect < -0.05:
            st.success("Overall net effect seems beneficial (negative direction).")
        else:
            st.info("Slightly beneficial, but smaller magnitude.")

    # Show individual outcome details
    st.markdown("### Individual Outcomes")
    for row in user_data:
        display_outcome_line(row)

    # Constraints
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

    # Red disclaimer for placeholders
    st.subheader("C) Advanced Methods")
    st.markdown(
        """
        <p style='color:red; font-weight:bold;'>
        (Placeholder Section - Not Shown in Production)
        </p>
        <p>
        In a more advanced version:
        <ul>
          <li><strong>Incorporate confidence intervals</strong> into a probabilistic net benefit approach.</li>
          <li>Use <strong>AHP, Swing Weighting, or DCE</strong> to derive or refine importance weights.</li>
          <li>Combine multiple outcomes with correlation and the full logic from the professor's formulas.</li>
        </ul>
        </p>
        """,
        unsafe_allow_html=True
    )


def display_outcome_line(row):
    """
    Constructs a user-friendly outcome line, omitting "Zero" and
    "[95% CI: 0.0, 0.0]" if those values are all default or near zero.
    """
    arrow = get_arrow(row["rd"])
    stars_html = star_html_3(row["importance"])

    if abs(row["rd"]) < 1e-9:
        sign_text = ""
    else:
        sign_text = "Positive RD" if row["rd"] > 0 else "Negative RD"

    show_ci = not (abs(row["ci_lower"]) < 1e-9 and abs(row["ci_upper"]) < 1e-9)
    ci_text = f"[95% CI: {row['ci_lower']}, {row['ci_upper']}]" if show_ci else ""

    display_line = f"- **{row['outcome']}**: {stars_html} {arrow}"
    if sign_text:
        display_line += f" ({sign_text})"
    if ci_text:
        display_line += f" {ci_text}"

    st.markdown(display_line, unsafe_allow_html=True)


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
        return 0.0

def constraint_to_numeric(label):
    """Convert constraint labels to numeric values for summation."""
    if label == "No problem":
        return 0.0
    elif label == "Moderate concern":
        return 0.5
    else:
        return 1.0

def numeric_to_constraint_label(value):
    """Inverse mapping for constraint values."""
    if value == 0.0:
        return "No problem"
    elif value == 0.5:
        return "Moderate concern"
    else:
        return "Severe problem"

def get_arrow(rd):
    """Return an arrow based on RD sign and threshold."""
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
    Low (0.0): 1 gold, 2 gray
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
