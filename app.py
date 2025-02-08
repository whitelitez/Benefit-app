import streamlit as st

def main():
    # Page title
    st.title("Net Benefit Calculation Prototype")

    # Intro / disclaimers
    st.markdown(
        """
        <p style='color:red; font-weight:bold;'>
        (User-Friendly Labels, No Technical Cell References)
        </p>
        <p>
        <strong>Overview:</strong><br>
        This app calculates a "net benefit score" based on how each outcome's 
        effect (positive or negative) interacts with its importance, then sums them 
        up to give a final value "per 1000 people." The technical details (e.g., F=1, E, K24) 
        are hidden, but the internal math follows the professor’s Excel approach.
        </p>
        """,
        unsafe_allow_html=True
    )

    # We define outcomes with an internal "f" (fixed) but don't show it
    outcomes = [
        {"display_name": "Stroke Prevention",      "f":  1, "default_e":  0.10, "default_i": 100},
        {"display_name": "Heart Failure Prevention","f": 1, "default_e": -0.10, "default_i":  29},
        {"display_name": "Dizziness",             "f": -1, "default_e":  0.02, "default_i":   5},
        {"display_name": "Urination Frequency",    "f": -1, "default_e": -0.01, "default_i":   4},
        {"display_name": "Fall Risk",             "f": -1, "default_e": -0.02, "default_i":  13},
    ]

    # 1) Sidebar for outcome inputs
    st.sidebar.header("Adjust Outcomes and Their Importance")

    user_data = []
    for item in outcomes:
        st.sidebar.subheader(item["display_name"])

        # We hide the mention of "F (fixed)"
        # We only let the user set the "Change in Risk" (E) and "Importance"
        e_val = st.sidebar.number_input(
            f"{item['display_name']} – Estimated Change in Risk",
            value=float(item["default_e"]),
            format="%.3f"
        )

        i_val = st.sidebar.slider(
            f"{item['display_name']} – Importance (0 = Not important, 100 = Very important)",
            min_value=0,
            max_value=100,
            value=item["default_i"],
            step=1
        )

        # Store everything internally
        user_data.append({
            "label": item["display_name"],
            "f": item["f"],      # hidden from user
            "e": e_val,
            "i": i_val
        })

    # 2) Constraints
    st.sidebar.header("Constraints")
    constraint_options = ["No problem", "Moderate concern", "Severe problem"]

    cost_label = st.sidebar.radio("Financial / Cost Issues", constraint_options, index=0)
    access_label = st.sidebar.radio("Access / Transportation Issues", constraint_options, index=0)
    care_label = st.sidebar.radio("Home Care / Assistance Issues", constraint_options, index=0)

    cost_val = constraint_to_numeric(cost_label)
    access_val = constraint_to_numeric(access_label)
    care_val = constraint_to_numeric(care_label)

    # Button
    if st.sidebar.button("Calculate Net Benefit"):
        show_results(user_data, cost_val, access_val, care_val)


def show_results(user_data, cost_val, access_val, care_val):
    """
    Performs the internal math:
      - sum of I => total_i
      - j_k = i_k / total_i
      - k_k = e_k * j_k * f_k
      - net_sum = sum(k_k)
      - "Score per 1000" = round( 1000 * net_sum )
    We rename them to simpler terms for display.
    """
    st.subheader("Net Benefit Results")

    # Calculate total importance
    total_i = sum(row["i"] for row in user_data)
    if abs(total_i) < 1e-9:
        st.error("All importance values are zero. Please adjust at least one outcome above 0.")
        return

    # Calculate each outcome's contribution
    st.markdown("### Outcome Breakdown")
    k_values = []
    for row in user_data:
        # j_k is the fraction of total importance
        j_k = row["i"] / total_i
        # k_k is e * j_k * f
        k_k = row["e"] * j_k * row["f"]
        k_values.append(k_k)

        # For display, show a simpler label
        arrow = get_arrow(row["e"] * row["f"])
        stars = star_html_3(row["i"])  # 0..100 => star rating
        st.markdown(
            f"- **{row['label']}**: {arrow} {stars}  "
            f"(Estimated Change in Risk = {row['e']:.3f}, Importance = {row['i']})"
        )

    net_sum = sum(k_values)

    # "Score per 1000" = round(1000 * net_sum)
    score_1000 = round(1000 * net_sum, 0)

    # Interpret net_sum
    if net_sum > 0:
        st.warning("Overall direction suggests possible net harm.")
    elif abs(net_sum) < 1e-9:
        st.info("Overall effect appears neutral.")
    else:
        st.success("Overall direction suggests possible net benefit.")

    st.markdown(
        f"**Net Benefit Score** (summed effect): {net_sum:.4f}  \n"
        f"**Estimated 'people per 1000'**: {score_1000:.0f}"
    )

    # Constraints
    st.subheader("Constraints")
    constraint_total = cost_val + access_val + care_val
    if constraint_total == 0:
        st.success("No major constraints identified.")
    elif constraint_total <= 1:
        st.info("Some minor constraints. Potentially manageable.")
    elif constraint_total <= 2:
        st.warning("Multiple constraints likely. Additional support or adjustments needed.")
    else:
        st.error("Severe constraints across multiple dimensions. Careful planning required.")

    st.write(f"- Financial: **{numeric_to_constraint_label(cost_val)}**")
    st.write(f"- Access: **{numeric_to_constraint_label(access_val)}**")
    st.write(f"- Care: **{numeric_to_constraint_label(care_val)}**")

    # Placeholder
    st.subheader("Further Analysis (Placeholder)")
    st.markdown(
        """
        <p style='color:red; font-weight:bold;'>
        (Advanced Methods Not Shown in Production)
        </p>
        <ul>
          <li>Incorporate correlation or advanced weighting (AHP, DCE)</li>
          <li>Handle confidence intervals probabilistically</li>
          <li>Refine interpretation for beneficial vs. harmful outcomes</li>
        </ul>
        """,
        unsafe_allow_html=True
    )


# ---------------- HELPER FUNCTIONS ----------------

def constraint_to_numeric(label):
    if label == "No problem":
        return 0.0
    elif label == "Moderate concern":
        return 0.5
    else:
        return 1.0

def numeric_to_constraint_label(value):
    if value == 0.0:
        return "No problem"
    elif value == 0.5:
        return "Moderate concern"
    else:
        return "Severe problem"

def get_arrow(value):
    if value > 0.05:
        return "⬆️"
    elif value < -0.05:
        return "⬇️"
    else:
        return "➡️"

def star_html_3(importance_0to100):
    """
    Convert 0..100 => 1..3 stars
    e.g., 0..33 => 1 star, 34..66 => 2 stars, 67..100 => 3 stars
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


if __name__ == "__main__":
    main()
