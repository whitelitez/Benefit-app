import streamlit as st

def main():
    st.title("Net Benefit Calculation Prototype (Custom Slider Bounds)")

    st.markdown(
        """
        <p style='color:red; font-weight:bold;'>
        (User-Friendly Labels, No Technical Cell References)
        </p>
        <p>
        <strong>Overview:</strong><br>
        This app calculates a "net benefit score" based on each outcome's 
        <em>estimated change in risk</em> and its <em>importance</em>. 
        We've set <strong>custom slider ranges</strong>:
        <ul>
          <li>Stroke Prevention & Heart Failure Prevention: –0.10 to +0.10</li>
          <li>Dizziness, Urination Frequency, Fall Risk: –0.02 to +0.02</li>
        </ul>
        The internal math follows the professor’s Excel approach (K<sub>k</sub>, K17, K24).
        </p>
        """,
        unsafe_allow_html=True
    )

    # Define outcomes with custom slider bounds
    # "f" is fixed, "default_e" is the initial slider value, 
    # "min_e" and "max_e" define the slider bounds for E.
    outcomes = [
        {
            "display_name": "Stroke Prevention",
            "f":  1,
            "default_e":  0.10,
            "default_i": 100,
            "min_e": -0.10,
            "max_e":  0.10
        },
        {
            "display_name": "Heart Failure Prevention",
            "f":  1,
            "default_e": -0.10,
            "default_i": 29,
            "min_e": -0.10,
            "max_e":  0.10
        },
        {
            "display_name": "Dizziness",
            "f": -1,
            "default_e":  0.02,
            "default_i":  5,
            "min_e": -0.02,
            "max_e":  0.02
        },
        {
            "display_name": "Urination Frequency",
            "f": -1,
            "default_e": -0.01,
            "default_i":  4,
            "min_e": -0.02,
            "max_e":  0.02
        },
        {
            "display_name": "Fall Risk",
            "f": -1,
            "default_e": -0.02,
            "default_i": 13,
            "min_e": -0.02,
            "max_e":  0.02
        },
    ]

    # 1) Sidebar for user inputs
    st.sidebar.header("Adjust Outcomes and Their Importance")

    user_data = []
    for item in outcomes:
        st.sidebar.subheader(item["display_name"])

        e_val = st.sidebar.slider(
            f"{item['display_name']} – Estimated Change in Risk",
            min_value=item["min_e"],
            max_value=item["max_e"],
            value=float(item["default_e"]),
            step=0.001  # smaller step for 0.02 range
        )

        i_val = st.sidebar.slider(
            f"{item['display_name']} – Importance (0 = Not important, 100 = Very important)",
            min_value=0,
            max_value=100,
            value=item["default_i"],
            step=1
        )

        user_data.append({
            "label": item["display_name"],
            "f": item["f"],  
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
    st.subheader("Net Benefit Results")

    # 1) Sum of importance
    total_i = sum(row["i"] for row in user_data)
    if abs(total_i) < 1e-9:
        st.error("All importance values are zero. Please adjust at least one outcome above 0.")
        return

    # 2) Compute each outcome's contribution
    st.markdown("### Outcome Breakdown")
    k_values = []
    for row in user_data:
        j_k = row["i"] / total_i  # fraction of total importance
        k_k = row["e"] * j_k * row["f"]
        k_values.append(k_k)

        arrow = get_arrow(row["e"] * row["f"])
        stars = star_html_3(row["i"])

        st.markdown(
            f"- **{row['label']}**: {arrow} {stars} "
            f"(Estimated Change in Risk = {row['e']:.3f}, Importance = {row['i']})",
            unsafe_allow_html=True
        )

    # Net sum
    net_sum = sum(k_values)
    # Convert to "people per 1000"
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
