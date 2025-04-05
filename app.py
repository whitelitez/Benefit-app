import streamlit as st
import openai

# Set your OpenAI API key.
# For Streamlit Cloud, store your key in the secrets file as:
# [OPENAI]
# API_KEY = "your_openai_api_key"
openai.api_key = st.secrets["OPENAI_API_KEY"]

def generate_forecast(pair: str) -> str:
    """
    Uses the OpenAI ChatCompletion API to generate a forecast for the given forex pair.
    The prompt instructs the model to perform a deep research analysis and forecast for various timeframes.
    """
    prompt = (
        f"Please conduct a deep research and analysis for the forex pair {pair}. "
        "Include macroeconomic factors, technical analysis, and geopolitical considerations. "
        "Then, provide a detailed forecast and analysis for the next 2 weeks, 1 month, 3 months, 6 months, and 1 year. "
        "Present your output in a structured report format with clear headers for each timeframe and include key technical levels, "
        "trading signals, and supporting commentary as appropriate. Use credible language and analysis similar to a financial research report."
    )
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # or your preferred model
            messages=[
                {"role": "system", "content": "You are a knowledgeable financial research assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        forecast = response.choices[0].message.content.strip()
        return forecast
    except Exception as e:
        return f"Error generating forecast: {e}"

def main():
    st.title("Forex Pair Forecast App")
    st.write("Enter a forex pair (e.g., XAUUSD, USDJPY) to generate a detailed forecast report.")

    pair_input = st.text_input("Enter Forex Pair(s):", value="XAUUSD")
    
    if st.button("Generate Forecast"):
        if pair_input:
            st.info("Generating forecast... This may take a few moments.")
            with st.spinner("Please wait, generating forecast..."):
                forecast_result = generate_forecast(pair_input)
            st.subheader("Forecast Analysis")
            st.text_area("Output", forecast_result, height=600)
        else:
            st.error("Please enter a valid forex pair.")

if __name__ == "__main__":
    main()
