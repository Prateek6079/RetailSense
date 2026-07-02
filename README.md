# RetailSense - Intelligent Retail Diagnosis Engine

> A white-box Bayesian Business Intelligence system that identifies the most probable causes of retail profit decline through probabilistic reasoning, statistical analysis, and interpretable business models.

## Overview

Retail businesses often experience declining profits without a clear understanding of the underlying causes. Traditional dashboards provide descriptive statistics but fail to explain **why** performance deteriorates.

RetailSense addresses this problem by combining **Bayesian Belief Networks**, **business domain knowledge**, and **statistical inference** to perform **root cause analysis** on retail operations.

Instead of acting on symptoms, managers receive probabilistic explanations of the underlying operational and market factors affecting profitability.

---

## Features

### Real-Time Business Graph

- Interactive Bayesian Business Graph
- Displays probabilities of underperforming business variables
- Visualizes causal relationships between business factors
- Probabilities improve as evidence accumulates throughout the month using a **Data Maturity Mechanism**

---

### Market State Analysis

Infers the most probable configuration of external market variables such as:

- Competition
- Economy
- Season

allowing businesses to anticipate changing market conditions before reacting to them.

---

### Monthly Diagnosis

Generates an interpretable diagnosis explaining:

- Why profits declined
- Which business components are most likely responsible
- Suggested business interpretation for each identified pathology

---

### Automated Data Labelling

Instead of manually labeling historical data, the project includes an automated labeling pipeline based on:

- Statistical reasoning
- Business principles
- Mathematical rules
- Hypothesis testing

This produces structured training data for Bayesian learning while remaining fully explainable.

---

### Training Configuration

Allows managers to prioritize historical periods during model training, making the Bayesian network adaptable to different business environments.

---

## Architecture

```
Historical Store Data
        │
        ▼
Automatic Data Labelling
        │
        ▼
Conditional Probability Learning
        │
        ▼
 Bayesian Belief Network
        │
        ▼
Real-Time Evidence Injection
        │
        ▼
 Probabilistic Diagnosis
        │
        ▼
Business Insights & Recommendations
```

---

## Bayesian Variables

The model currently reasons over variables including:

- Sales
- Profit
- Pricing
- Costs
- Stocking
- Product Popularity
- Competition
- Operational Efficiency
- Economy
- Season

These relationships were manually designed using real-world business dependencies to produce an interpretable white-box model.

---

## Data Maturity Mechanism

Not every business variable can be inferred reliably on the first day of the month.

RetailSense gradually unlocks evidence as sufficient data becomes available.

Example:

| Variable | Evidence Available After |
|-----------|-------------------------|
| Pricing | Day 1 |
| Season | Day 1 |
| Sales | ~7 Days |
| Product Popularity | ~10 Days |
| Operational Efficiency | Immediately after an incident or after sufficient observation |

This prevents premature inference from insufficient sample sizes.

---

## Technology Stack

- Python
- Flask
- SQLite
- Pandas
- pgmpy
- SciPy
- PyVis
- Matplotlib

---

## Project Structure

```
RetailSense/

│── app.py
│── Detection.py
│── BayesianNetwork.py
│── database.db
│── templates/
│── static/
│── models/
│── data/
│── README.md
```

---

## Future Work

- Decision Simulation Engine
- Automatic Corrective Suggestions
- Temporal Bayesian Networks
- Dynamic Structure Learning
- Integration with live POS systems
- Reinforcement learning for business strategy evaluation

---

## Philosophy

RetailSense was intentionally designed as a **white-box AI system**.

Unlike black-box machine learning models, every inference can be inspected, understood, and verified by managers.

The objective is not merely to predict business outcomes, but to explain **why** they occur.

---

## Disclaimer

This project was developed as a proof of concept for the **Walmart Converge Hackathon**.

The current implementation demonstrates the complete reasoning framework using simulated and statistically generated data. The architecture has been designed to integrate with real retail datasets with minimal modification.
