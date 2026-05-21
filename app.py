import os
import json

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv(override=True)

api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

st.set_page_config(
    page_title="AI Delivery Insights Assistant",
    layout="wide"
)

st.title("AI Delivery Insights Assistant")

uploaded_file = st.file_uploader(
    "Upload a project delivery CSV",
    type=["csv"]
)

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.subheader("Data Preview")
    st.dataframe(df)

    df["CostVariance"] = df["ActualCost"] - df["Budget"]
    df["CostVariancePct"] = (df["CostVariance"] / df["Budget"]) * 100

    average_delay = df["DelayDays"].mean()
    high_risk_df = df[
        (df["RiskLevel"] == "High")
        | (df["DelayDays"] > 10)
        | (df["CostVariancePct"] > 10)
    ]

    high_risk_count = len(high_risk_df)
    average_cost_variance_pct = df["CostVariancePct"].mean()
    correlation = df["DelayDays"].corr(df["CostVariancePct"])

    st.subheader("Portfolio Metrics")

    col1, col2, col3 = st.columns(3)

    col1.metric("High-risk projects", high_risk_count)
    col2.metric("Average delay", f"{average_delay:.1f} days")
    col3.metric("Average cost variance", f"{average_cost_variance_pct:.1f}%")

    st.subheader("Project Delays")
    st.bar_chart(
        df.set_index("Project")["DelayDays"]
    )

    st.subheader("Cost Variance")
    st.bar_chart(
        df.set_index("Project")["CostVariancePct"]
    )

    high_risk_records = high_risk_df.to_dict(orient="records")

    analysis_prompt = f"""
You are a senior programme delivery consultant.

Portfolio metrics:

- High-risk projects: {high_risk_count}
- Average delay: {average_delay:.1f} days
- Average cost variance: {average_cost_variance_pct:.1f}%
- Delay/cost variance correlation: {correlation:.2f}

High risk project records:

{json.dumps(high_risk_records, indent=2)}

Return your response in markdown with these sections:

## Executive Summary

## Observations
Clearly distinguish observed facts from inferred risks.

## Key Risks
Include reasonable interpretations, but clearly distinguish them from observed facts.

## Recommended Actions
Provide practical delivery management actions.

Keep the tone concise and professional.
Only reference issues directly supported by the dataset.
"""

    if st.button("Generate AI Analysis"):
        with st.spinner("Generating analysis..."):
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a senior programme delivery consultant "
                            "specialising in software delivery risk."
                        )
                    },
                    {
                        "role": "user",
                        "content": analysis_prompt
                    }
                ]
            )

            analysis = response.choices[0].message.content

        st.subheader("AI Analysis")
        st.markdown(analysis)
else:
    st.info("Upload a CSV file to begin.")