# Walmart-Hackathon-2

Problem Statement:
In large-scale, otherwise stable retail businesses, early detection of underlying operational issues becomes increasingly difficult as the organization grows.
Managers often react to surface-level symptoms (like declining profits) without accurate root-cause diagnosis. This reactive decision-making, especially in response to natural market fluctuations or employee/customer anomalies, can trigger a feedback loop of misinformed changes, further destabilizing the business and accelerating decline.

There is a need for a system that can distinguish between normal fluctuations and genuine operational issues, offering explainable diagnostics to guide informed decision-making.


Project Overview:
An AI-powered dashboard driven by a probabilistic reasoning engine, built to assist retail managers in maintaining operational excellence.
The system enables early detection of performance declines and delivers causal diagnoses with probability scores by analyzing internal store data. It also provides real-time business and market insights, along with actionable corrective recommendations to keep the store on track.

By eliminating the need to manually interpret overwhelming volumes of operational and market data, this tool allows managers to focus on what matters most: leading their teams and enhancing the customer experience.



Project Design:

Retail_Data.db:
Data Tables : business_metrics, product_metrics, real_time_data, labelled_data

business_metrics schema : CREAT TABLE business_metrics (month TEXT PRIMARY KEY, -- format: 'YYYY-MM', e.g. '2025-06',
                                                        profits FLOAT,
                                                        costs FLOAT,
                                                        economy FLOAT,
                                                        operational_accidents INTEGER,
                                                        avg_basket_size FLOAT,
                                                        repeat_customers FLOAT CHECK (repeat_customers BETWEEN 0 AND 100),
                                                        new_customers FLOAT CHECK (new_customers BETWEEN 0 AND 100),
                                                        sales_items INTEGER,
                                                        sales_revenue FLOAT);


product_metrics schema : CREATE TABLE product_metrics (
                                                        month TEXT,
                                                        product_name TEXT,
                                                        products_sold INTEGER,
                                                        price FLOAT,
                                                        stock_life INTEGER,
                                                        profit_share FLOAT,
                                                        PRIMARY KEY (month, product_name),
                                                        FOREIGN KEY (month) REFERENCES business_metrics(month)
                                                    );


Labelled Data : Data is cleanly labelled

Labelled Data Schema : CREATE TABLE labelled_data (
                                                    month TEXT PRIMARY KEY,
                                                    profits TEXT CHECK (profits IN ('high', 'low', 'stable')),
                                                    sales TEXT CHECK (sales IN ('high', 'low', 'stable')),
                                                    costs TEXT CHECK (costs IN ('high', 'low', 'stable')),
                                                    competition TEXT CHECK (competition IN ('high', 'low', 'stable')),
                                                    pricing TEXT CHECK (pricing IN ('high', 'low', 'stable')),
                                                    economy TEXT CHECK (economy IN ('good', 'bad', 'neutral')),
                                                    operational_efficiency TEXT CHECK (operational_efficiency IN ('smooth', 'rough', 'expected')),
                                                    stocking TEXT CHECK (stocking IN ('abundant', 'short', 'balanced')),
                                                    product_popularity TEXT CHECK (product_popularity IN ('climbing', 'declining', 'stable')),
                                                    season TEXT CHECK (season IN ('festive', 'off', 'usual')),
                                                    external_factors TEXT CHECK (external_factors IN ('favourable', 'moderate', 'unfavourable')),
                                                    strategic_levers TEXT CHECK (strategic_levers IN ('high', 'moderate', 'low')),
                                                    FOREIGN KEY (month) REFERENCES business_metrics(month)
                                                    );


real_time_data : everyday data of a retail store

real_time_data schema : CREATE TABLE real_time_data (
                            day INTEGER NOT NULL,
                            product_name TEXT NOT NULL,
                            units_sold INTEGER,
                            price FLOAT,
                            revenue FLOAT,
                            accidents INTEGER,
                            PRIMARY KEY (day, product_name)
                        );



Label.py : 
Python Module to label data for the bayesian network to compute CPTs


static/model.pkl : The bayesian network graph is saved for reuse.
static/CPTs.pkl : The conditional probabailty tables are saved for faster access.


Detection.py :
Python Module to crunch real time data and recognize disruptions and other clear signs of market & business state.


Engine.py : 
Computes the probabilities of the queries to run causal diagnoses, market state.


Dashboard.py :
Interface of the application that uses the back engine to give insights to the user.

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
