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
Data Tables : Monthly Data, Customer Data
Labelled Data : Data is cleanly labelled


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