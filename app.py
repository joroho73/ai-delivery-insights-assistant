import os
import json

import pandas as pd
import streamlit as st
import plotly.express as px
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv(override=True)

try:
    api_key = st.secrets["OPENAI_API_KEY"]
except Exception:
    api_key = os.getenv("OPENAI_API_KEY")

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

    st.subheader("Portfolio Risk Analysis")

    # Define consistent colors for risk levels
    risk_colors={
        "Low": "green",
        "Medium": "orange",
        "High": "red"
    }

    # Project Delays Chart (only showing projects with >10 days delay for clarity)
    df_sorted_by_delays = df[df["DelayDays"] > 10].sort_values(
        by="DelayDays",
        ascending=False
    )

    project_delays_chart = px.bar(
        df_sorted_by_delays,
        x="Project",
        y="DelayDays",
        color="RiskLevel",
        title="Project Delay (Days) by Risk Level (Only Projects > 10 Days Delay)",
        category_orders={"Project": df_sorted_by_delays["Project"].tolist()},
        color_discrete_map=risk_colors,
        hover_data={
            "Budget": ":,.0f",
            "ActualCost": ":,.0f",
            "CostVariancePct": True
        }
    )

    st.plotly_chart(
        project_delays_chart, 
        use_container_width=True
    )

    # Cost Variance Chart
    df_sorted_by_cost_variance = df.sort_values(
        by="CostVariancePct",
        ascending=False
    )

    cost_variance_chart = px.bar(
        df_sorted_by_cost_variance,
        x="Project",
        y="CostVariancePct",
        color="RiskLevel",
        title="Project Cost Variance (%) by Risk Level",
        category_orders={"Project": df_sorted_by_cost_variance["Project"].tolist()},
        color_discrete_map=risk_colors,
        hover_data={
            "Budget": ":,.0f",
            "ActualCost": ":,.0f",
            "DelayDays": True
        }
    )

    st.plotly_chart(
        cost_variance_chart, 
        use_container_width=True
    )

    # Delay vs Cost Variance Scatter Plot
    scatter_chart = px.scatter(
        df,
        x="DelayDays",
        y="CostVariancePct",
        color="RiskLevel",
        hover_name="Project",
        title="Project Delay vs Cost Variance",
        color_discrete_map=risk_colors,
        category_orders={
            "RiskLevel": ["High", "Medium", "Low"]
        },
        hover_data={
            "Budget": ":,.0f",
            "ActualCost": ":,.0f",
            "Status": True
        }
    )

    scatter_chart.update_traces(
        marker=dict(
            size=14,
            line=dict(width=1, color="white")
        )
    )

    scatter_chart.update_layout(
        xaxis_title="Delay (Days)",
        yaxis_title="Cost Variance (%)"
    )

    scatter_chart.add_hline(
    y=0,
    line_dash="dash",
    line_color="gray"
)

    scatter_chart.add_vline(
        x=0,
        line_dash="dash",
        line_color="gray"
    )

    st.plotly_chart(
        scatter_chart,
        use_container_width=True
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