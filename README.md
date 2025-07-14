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