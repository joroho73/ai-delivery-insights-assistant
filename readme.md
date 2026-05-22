# AI Project Delivery Insights Assistant

A Streamlit web app that helps programme and delivery managers analyse project portfolio performance, identify at-risk projects, visualise delivery issues, and generate an AI-assisted delivery risk summary.

Live app: https://ai-delivery-insights-assistant.streamlit.app/

## Features

- Upload a project delivery CSV
- Validate required columns
- Calculate portfolio metrics
- Identify at-risk projects
- Visualise delivery performance using interactive Plotly charts
- Generate an AI-assisted portfolio analysis using the OpenAI API
- Download at-risk projects as CSV
- Download an HTML report including metrics, AI analysis, and interactive charts

## Required CSV Columns

The uploaded CSV must include:

- `Project`
- `Status`
- `Budget`
- `ActualCost`
- `DelayDays`
- `RiskLevel`

## At-Risk Definition

A project is considered at risk if it meets any of the following criteria:

- `RiskLevel` is `High`
- `DelayDays` is greater than `10`
- `CostVariancePct` is greater than `10%`

`CostVariancePct` is calculated by the app from `Budget` and `ActualCost`.

## Portfolio Metrics

The app calculates:

- Total projects
- At-risk project count
- Average delay
- Average cost variance percentage
- Correlation between delay and cost variance

## Visualisations

The dashboard includes:

- Project delays by risk level
- Cost variance by risk level
- Delay vs cost variance scatter plot

Charts are interactive and include hover data for project-level inspection.

## AI Analysis

The app sends portfolio metrics and at-risk project records to the OpenAI API and returns a structured markdown report with:

- Executive summary
- Observations
- Key risks
- Recommended actions

The AI is instructed to distinguish observed facts from inferred risks and only reference issues supported by the dataset.

## Tech Stack

- Python
- Streamlit
- pandas
- Plotly
- OpenAI API
- python-dotenv
- Markdown

## Local Setup

Clone the repository:

```bash
git clone https://github.com/joroho73/ai-delivery-insights-assistant.git
cd ai-delivery-insights-assistant
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Create a .env file:

```bash
OPENAI_API_KEY=your_api_key_here
```

Run the app:

```bash
streamlit run app.py
```

## Deployment

The app is deployed using Streamlit Community Cloud.
For deployment, the OpenAI API key should be added through Streamlit Secrets:

```toml
OPENAI_API_KEY = "your_api_key_here"
```

Do not commit .env or API keys to GitHub.

## Project Purpose

This project demonstrates an end-to-end AI-assisted analytics workflow:

CSV upload
→ data validation
→ pandas transformation
→ risk classification
→ Plotly visualisation
→ OpenAI-generated analysis
→ downloadable HTML report

It was built as a portfolio project to demonstrate practical AI integration in a project delivery / technical programme management context.

Future Improvements

Possible future enhancements:

Add configurable at-risk thresholds
Add support for Excel uploads
Add cached AI analysis to avoid repeat API calls
Add richer data validation and friendly error messages
Add PDF export
Add trend analysis across reporting periods
Move reusable logic into helper modules
Add automated tests
