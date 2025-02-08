import streamlit as st

def main():
    # Title
    st.title("Net Benefit Evaluation Prototype (0–100 Importance Scale)")

    # Disclaimers/Overview in red to highlight placeholders/drafts
    st.markdown(
        """
        <p style='color:red; font-weight:bold;'>
        (No Hardcoded Placeholders)
        </p>
        <p>
        <strong>Overview:</strong><br>
        This prototype lets users (e.g., patients) input 
        <strong>Risk Differences</strong>, 
        <strong>Confidence Intervals</strong>, and 
        <strong>Outcome Importance (0–100)</strong> for a set of outcomes.<br>
        We demonstrate a simple net benefit calculation based on: 
        <code>net_effect = Σ (RD × (importance / 100))</code>.<br>
        You can later integrate the <strong>professor's exact formulas</strong> 
        (including AHP, DCE, Swing Weighting, correlation, etc.).<br>
        Note: The current –0.50 to +0.50 range for RD & CI sliders 
        is a placeholder. Adjust as necessary.
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

        # Risk Difference slider
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

        # Importance on a 0..100 scale
        importance_0to100 = st.sidebar.slider(
            f"{label} – Importance (0 = Not important, 100 = Most important)",
            min_value=0,
            max_value=100,
            value=50,
            step=1
        )

        user_data.append({
            "outcome": label,
            "rd": rd_value,
            "ci_lower": ci_lower,
            "ci_upper": ci_upper,
            "importance_0to100": importance_0to100,
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
    Summarize the net benefit using:
       net_effect = Σ ( RD_k * (importance_k / 100) ).
    Replace or supplement this with the professor's advanced formulas as needed.
    """
    st.subheader("A) Outcome-Level Details")

    net_effect = 0.0
    for row in user_data:
        # Convert the 0..100 scale to a 0..1 multiplier
        importance_factor = row["importance_0to100"] / 100.0
        net_effect += row["rd"] * importance_factor

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
          <li>Use <strong>AHP, Swing Weighting, or DCE</strong> to derive or refine the 0–100 importance weights.</li>
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

    Star rating is derived from the 0..100 importance (similar to the professor's
    approach where the most important outcome might be 100).
    """
    # Convert the 0..100 scale to 1..3 stars
    stars_html = star_html_3(row["importance_0to100"])

    arrow = get_arrow(row["rd"])
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

def star_html_3(importance_0to100):
    """
    Convert the 0..100 importance scale into a 1..3 star display.
    Example thresholds (adjust if desired):
      0..33   => 1 star
      34..66  => 2 stars
      67..100 => 3 stars
    """
    if importance_0to100 <= 33:
        filled = 1
    elif importance_0to100 <= 66:
        filled = 2
    else:
        filled = 3

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
