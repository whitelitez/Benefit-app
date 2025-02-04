import streamlit as st

def main():
    st.title("Net Benefit Evaluation Prototype")

    st.markdown("""
    **Goal**: Calculate the net benefit of a hypothetical hypertension treatment 
    based on user inputs, including:
    - Risk Difference (RD) for various outcomes
    - Outcome importance (shown with colored stars)
    - Additional constraints (cost, access, care)
    
    This prototype integrates placeholders for advanced weighting or modeling 
    methods (AHP, Swing Weighting, Discrete Choice Experiments).
    """)

    # 1) Define outcomes we want to consider (can be expanded or made dynamic)
    outcome_defs = [
        {"label": "Prevention of stroke (beneficial)", "default_rd": 0.10},
        {"label": "Prevention of heart failure (beneficial)", "default_rd": -0.10},
        {"label": "Increased dizziness (harmful)", "default_rd": 0.02},
        {"label": "Increased urination frequency (harmful)", "default_rd": -0.01},
        {"label": "Increased fall risk (harmful)", "default_rd": -0.02},
    ]

    st.sidebar.header("1) Outcomes and Risk Differences (RD)")
    st.sidebar.write("Specify each outcome’s approximate RD and its importance.")
    
    # Placeholders to store user inputs
    user_data = []
    
    for od in outcome_defs:
        st.sidebar.subheader(od["label"])
        
        # For demonstration: slider range -0.20..+0.20
        # But you can adapt to your typical RD range.
        rd_value = st.sidebar.slider(
            f"{od['label']} (Risk Difference)",
            min_value=-0.20, max_value=0.20,
            value=od["default_rd"], step=0.01
        )
        
        # If beneficial vs harmful is relevant, you could let user pick or
        # store it in the definitions. For example:
        # sign = +1 for beneficial, -1 for harmful, then RD * sign. 
        # For simplicity, assume RD is "signed" already (positive = harmful, negative = beneficial).
        
        # Importance selection
        chosen_importance_label = st.sidebar.radio(
            f"{od['label']} – Importance",
            ["High", "Medium", "Low"],
            index=0
        )
        imp_value = convert_importance(chosen_importance_label)

        user_data.append({
            "outcome": od["label"],
            "rd": rd_value,
            "importance": imp_value,
        })

    # 2) Additional constraints
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
    
    # 3) Action button
    if st.button("Calculate Net Benefit"):
        show_results(user_data, cost_val, access_val, care_val)

def show_results(user_data, cost_val, access_val, care_val):
    """
    Summarize the overall net benefit calculation
    using a simplified approach: sum(RD * importance).
    
    Then factor in constraints by adjusting or
    providing interpretive comments.
    
    This is where you could insert the professor’s 
    more advanced formula for net benefit, correlation, etc.
    """
    st.subheader("A) Outcome-Level Information")

    # 1) Weighted sum using a basic formula
    #    net_effect = Σ (RD_k * weight_k)
    # In real usage, you might incorporate correlation matrices,
    # confidence intervals, or placeholders for AHP, DCE, etc.
    net_effect = 0.0
    for row in user_data:
        net_effect += row["rd"] * row["importance"]

    # 2) Provide interpretive feedback
    #    You can define your own thresholds for “good/bad” effect.
    if net_effect > 0.05:
        st.error("Overall, it seems the net effect may be harmful.")
    elif net_effect > 0:
        st.warning("Somewhat harmful, but relatively small magnitude.")
    elif abs(net_effect) < 1e-9:
        st.info("Overall net effect is approximately neutral.")
    else:  # net_effect < 0
        if net_effect < -0.05:
            st.success("Overall, it seems the net effect may be beneficial!")
        else:
            st.info("Somewhat beneficial, but relatively small magnitude.")
    
    # 3) Show each outcome with an arrow and star rating
    st.markdown("### Outcome Details")
    for row in user_data:
        arrow = get_arrow(row["rd"])
        stars_html = star_html_3(row["importance"])  # star icons
        # sign_text is optional: if RD is negative => beneficial, positive => harmful
        sign_text = "Beneficial" if row["rd"] < 0 else "Harmful" if row["rd"] > 0 else "Neutral"
        
        st.markdown(
            f"- **{row['outcome']}**: {stars_html} {arrow} ({sign_text})", 
            unsafe_allow_html=True
        )

    # 4) Constraints
    st.subheader("B) Constraint Considerations")
    constraint_total = cost_val + access_val + care_val
    
    if constraint_total == 0:
        st.success("No major constraints identified. Feasibility looks good.")
    elif constraint_total <= 1:
        st.info("Some minor constraints. May be addressable with moderate effort.")
    elif constraint_total <= 2:
        st.warning("Multiple constraints likely. Additional support or adjustments needed.")
    else:
        st.error("Severe constraints across cost, access, and care. Careful planning needed.")
    
    st.markdown("### Constraint Breakdown")
    st.write(f"- Financial: **{numeric_to_constraint_label(cost_val)}**")
    st.write(f"- Access: **{numeric_to_constraint_label(access_val)}**")
    st.write(f"- Care: **{numeric_to_constraint_label(care_val)}**")

    # 5) Potential place for advanced suggestions or “best option” logic
    st.subheader("C) Advanced Methods Placeholder")
    st.markdown("""
    - **AHP (Analytic Hierarchy Process)**: We can formalize the pairwise comparisons 
      of outcomes or constraints to get consistent weights.
    - **Swing Weighting**: We can ask the user to assess the “swing” (difference between 
      worst and best) for each outcome to derive more precise weights.
    - **DCE (Discrete Choice Experiments)**: We can gather preference data from multiple 
      choice scenarios to estimate more robust utility weights.
    
    All these methods would feed into the net benefit calculation. 
    For the prototype, we’re just doing a simple additive weighting with the user-specified importance.
    """)

# ---------------- HELPER FUNCTIONS ----------------

def convert_importance(label):
    """
    Convert user-friendly importance labels to numeric values
    for weighting. You can refine this scale.
    """
    if label == "High":
        return 1.0
    elif label == "Medium":
        return 0.5
    else:
        return 0.0  # Low

def constraint_to_numeric(label):
    """
    Convert constraint labels to numeric values.
    0 = No problem
    0.5 = Moderate concern
    1.0 = Severe problem
    """
    if label == "No problem":
        return 0.0
    elif label == "Moderate concern":
        return 0.5
    else:
        return 1.0

def numeric_to_constraint_label(value):
    """Reverse lookup for constraint levels."""
    if value == 0:
        return "No problem"
    elif value == 0.5:
        return "Moderate concern"
    else:
        return "Severe problem"

def get_arrow(rd):
    """Return arrow emoji based on RD threshold."""
    if rd > 0.05:
        return "⬆️"
    elif rd < -0.05:
        return "⬇️"
    else:
        return "➡️"

def star_html_3(importance):
    """
    Return an HTML string with 3 stars in a row:
      - Gold star for 'filled'
      - LightGray star for 'empty'
    
    High (1.0) = 3 gold
    Medium (0.5) = 2 gold, 1 gray
    Low (0.0) = 1 gold, 2 gray
    (Adjust if you want zero gold for Low, etc.)
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
