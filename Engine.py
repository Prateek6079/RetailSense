from pgmpy.models import DiscreteBayesianNetwork
from pgmpy.estimators import BayesianEstimator
from pgmpy.inference import VariableElimination
from Detection import detect # Assuming Detection.py exists and has a detect function
import pandas as pd
import sqlite3
import pickle
import random # Import random for simulating daily data (if needed by Detection)
import os # Import os to check for file existence

# write a better probability impact function

negative_states = {"profits" : ["stable","low"], "sales" : ["stable","low"], "pricing" : ["high"], 
                   "strategic_levers" : ["moderate","low"], "costs" : ["stable","high"], 
                   "external_factors" : ["moderate","unfavourable"], "operational_efficiency" : ["rough"], 
                   "stocking" : ["abundant", "short"], "product_popularity" : ["declining"], "season" : ["off"], 
                   "economy" : ["bad"], "competition" : ["high"]}


model = DiscreteBayesianNetwork([("sales", "profits"),
                                 ("costs", "profits"),
                                 ("pricing", "profits"),
                                 ("external_factors", "sales"),
                                 ("product_popularity", "sales"),
                                 ("strategic_levers", "sales"),
                                 ("operational_efficiency", "costs"),
                                 ("stocking", "costs"),
                                 ("costs", "pricing"),
                                 ("stocking", "strategic_levers"),
                                 ("pricing", "strategic_levers"),
                                 ("season", "external_factors"),
                                 ("economy", "external_factors"),
                                 ("competition", "external_factors"),
                                 ("product_popularity", "stocking")])


infer = None

def create_dummy_database_and_tables(database_name="Retail_Data.db"):
    """
    Creates a dummy SQLite database and populates it with necessary tables and data
    if the database file does not already exist.
    """
    if os.path.exists(database_name):
        print(f"Database '{database_name}' already exists. Skipping creation.")
        return

    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()

    print(f"Creating dummy database '{database_name}' and tables...")

    # Create real_time_data table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS real_time_data (
            day INTEGER,
            product_name TEXT,
            price REAL,
            units_sold INTEGER,
            accidents INTEGER
        );
    """)
    # Insert dummy data for real_time_data
    real_time_data_entries = [
        (0, 'product_A', 10.0, 50, 0), (0, 'product_B', 20.0, 30, 0),
        (1, 'product_A', 10.0, 52, 0), (1, 'product_B', 20.0, 28, 0), (1, 'operational_accidents', 0.0, 0, 1),
        (2, 'product_A', 10.5, 55, 0), (2, 'product_B', 19.5, 32, 0),
        (5, 'product_A', 10.0, 60, 0), (5, 'product_B', 20.0, 35, 0),
        (7, 'product_A', 11.0, 65, 0), (7, 'product_B', 21.0, 30, 0), (7, 'operational_accidents', 0.0, 0, 1),
        (10, 'product_A', 10.0, 70, 0), (10, 'product_B', 20.0, 40, 0),
        (11, 'product_A', 10.0, 72, 0), (11, 'product_B', 20.0, 41, 0), # Added data for day 11
        (15, 'product_A', 10.0, 75, 0), (15, 'product_B', 20.0, 42, 0), (15, 'operational_accidents', 0.0, 0, 0),
        (20, 'product_A', 10.0, 80, 0), (20, 'product_B', 20.0, 45, 0),
        (25, 'product_A', 10.0, 85, 0), (25, 'product_B', 20.0, 48, 0),
        (30, 'product_A', 10.0, 90, 0), (30, 'product_B', 20.0, 50, 0)
    ]
    cursor.executemany("INSERT INTO real_time_data VALUES (?, ?, ?, ?, ?)", real_time_data_entries)

    # Create product_metrics table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS product_metrics (
            month TEXT,
            product_name TEXT,
            products_sold INTEGER,
            profit_share REAL,
            price REAL
        );
    """)
    # Insert dummy data for product_metrics (for current and previous months)
    product_metrics_entries = [
        ('2024-05', 'product_A', 1500, 0.6, 9.5), ('2024-05', 'product_B', 800, 0.4, 19.0),
        ('2024-06', 'product_A', 1600, 0.62, 10.0), ('2024-06', 'product_B', 850, 0.38, 20.0),
        ('2023-12', 'product_A', 1400, 0.58, 9.0), ('2023-12', 'product_B', 750, 0.42, 18.5),
        ('2024-01', 'product_A', 1450, 0.59, 9.7), ('2024-01', 'product_B', 780, 0.41, 19.2),
        ('2024-02', 'product_A', 1550, 0.61, 10.2), ('2024-02', 'product_B', 810, 0.39, 20.5),
        ('2024-03', 'product_A', 1580, 0.60, 10.1), ('2024-03', 'product_B', 830, 0.40, 19.8),
        ('2024-04', 'product_A', 1590, 0.61, 10.0), ('2024-04', 'product_B', 840, 0.39, 20.1),
    ]
    cursor.executemany("INSERT INTO product_metrics VALUES (?, ?, ?, ?, ?)", product_metrics_entries)

    # Create business_metrics table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS business_metrics (
            operational_accidents INTEGER,
            sales_items INTEGER,
            sales_revenue REAL
        );
    """)
    # Insert dummy data for business_metrics
    business_metrics_entries = [
        (2, 10000, 150000.0), (3, 11000, 160000.0), (1, 9500, 140000.0),
        (2, 10500, 155000.0), (4, 9000, 130000.0), (1, 12000, 170000.0)
    ]
    cursor.executemany("INSERT INTO business_metrics VALUES (?, ?, ?)", business_metrics_entries)

    # Create labelled_data table (for model training)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS labelled_data (
            sales TEXT,
            profits TEXT,
            pricing TEXT,
            external_factors TEXT,
            product_popularity TEXT,
            strategic_levers TEXT,
            operational_efficiency TEXT,
            stocking TEXT,
            costs TEXT,
            season TEXT,
            economy TEXT,
            competition TEXT
        );
    """)
    # Insert dummy data for labelled_data
    labelled_data_entries = [
        ("high", "high", "low", "favourable", "rising", "high", "smooth", "optimal", "low", "festive", "good", "low"),
        ("medium", "stable", "moderate", "moderate", "stable", "moderate", "smooth", "optimal", "stable", "normal", "average", "moderate"),
        ("low", "low", "high", "unfavourable", "declining", "low", "rough", "short", "high", "off", "bad", "high"),
        ("high", "high", "low", "favourable", "rising", "high", "smooth", "optimal", "low", "festive", "good", "low"),
        ("medium", "stable", "moderate", "moderate", "stable", "moderate", "rough", "abundant", "stable", "normal", "average", "moderate"),
        ("low", "low", "high", "unfavourable", "declining", "low", "rough", "short", "high", "off", "bad", "high"),
        ("high", "high", "low", "favourable", "rising", "high", "smooth", "optimal", "low", "festive", "good", "low"),
        ("medium", "stable", "moderate", "moderate", "stable", "moderate", "smooth", "optimal", "stable", "normal", "average", "moderate"),
        ("low", "low", "high", "unfavourable", "declining", "low", "high", "short", "high", "off", "bad", "high"),
        ("high", "high", "low", "favourable", "rising", "high", "smooth", "optimal", "low", "festive", "good", "low"),
    ]
    cursor.executemany(f"INSERT INTO labelled_data VALUES ({','.join(['?']*12)})", labelled_data_entries)


    conn.commit()
    conn.close()
    print("Dummy database and tables created successfully.")


def initialize_engine():
    """Load the engine from older model or create new model"""
    global model
    global infer

    # Ensure the dummy database and tables exist before proceeding
    create_dummy_database_and_tables()

    try:
        model = load_model()
        print("Model loaded from model.pkl.")
    except FileNotFoundError:
        print("Model file not found. Computing and saving a new model.")
        model = compute_new_cpt()
        save_model(model)
    
    infer = get_inference_engine(model)
    return


def get_inference_engine(model):
    return VariableElimination(model)


# compute CPTs ~~ Fit Model
def compute_new_cpt(database="Retail_Data.db", table="labelled_data"):
    """ Bayesian Estimator and BDeu makes sure all that any possible combination that does not show up in data is given a 
    menial probability such that it does not affect the probability values of combination that do appear significantly"""
    conn = sqlite3.connect(f"{database}")
    try:
        data = pd.read_sql_query(f"SELECT * FROM {table}", conn).astype(str)
    except pd.io.sql.DatabaseError as e:
        print(f"Error reading from database: {e}. This should not happen if create_dummy_database_and_tables ran.")
        # Fallback to dummy data if, for some reason, the table is still not found
        data = pd.DataFrame({
            "sales": ["high", "medium", "low", "high", "medium", "low", "high", "medium", "low", "high"],
            "profits": ["high", "stable", "low", "high", "stable", "low", "high", "stable", "low", "high"],
            "pricing": ["low", "moderate", "high", "low", "moderate", "high", "low", "moderate", "high", "low"],
            "external_factors": ["favourable", "moderate", "unfavourable", "favourable", "moderate", "unfavourable", "favourable", "moderate", "unfavourable", "favourable"],
            "product_popularity": ["rising", "stable", "declining", "rising", "stable", "declining", "rising", "stable", "declining", "rising"],
            "strategic_levers": ["high", "moderate", "low", "high", "moderate", "low", "high", "moderate", "low", "high"],
            "operational_efficiency": ["smooth", "rough", "smooth", "rough", "smooth", "rough", "smooth", "rough", "smooth", "rough"],
            "stocking": ["optimal", "abundant", "short", "optimal", "abundant", "short", "optimal", "abundant", "short", "optimal"],
            "costs": ["low", "stable", "high", "low", "stable", "high", "low", "stable", "high", "low"],
            "season": ["festive", "normal", "off", "festive", "normal", "off", "festive", "normal", "off", "festive"],
            "economy": ["good", "average", "bad", "good", "average", "bad", "good", "average", "bad", "good"],
            "competition": ["low", "moderate", "high", "low", "moderate", "high", "low", "moderate", "high", "low"]
        })

    conn.close()

    model.fit(data, estimator=BayesianEstimator, prior_type="BDeu", equivalent_sample_size=1)
    return model


def load_model(file="model.pkl"):
    """Load the old model for faster performance"""
    with open(file, "rb") as f:
        model = pickle.load(f)
    return model


def save_model(model, file="model.pkl"):
    """save model so it does not have to be computed everytime"""
    with open(file, "wb") as f:
        pickle.dump(model, f)

    print("model_saved")
    return


def normalize_by_abs(values):
    total_abs = sum(abs(v) for v in values)
    return [v / total_abs for v in values] if total_abs != 0 else [0 for v in values]


def drift(node, new_evidence_for_query, old_evidence_for_query = dict()):
    """Returns how much the probability of a variable drifts when certain evidence presents itself"""
    states = model.get_cpds(node).state_names[node]
    drift_states = negative_states[node]
    drift = 0
    for state in drift_states:
        if state not in states:
            continue
        old_value = infer.query(variables=[node], evidence=old_evidence_for_query).get_value(**{node : states.index(state)})
        new_value = infer.query(variables=[node], evidence=new_evidence_for_query).get_value(**{node : states.index(state)})
        drift += old_value - new_value
    return drift


def get_parent_impact(node, original_evidence_with_conf):
    """
    Returns the impact of each parent node on the intermediary node post the evidence.
    P(node | evidence) - P(node | evidence ^ parent) likelihood weighted on all states
    P(node | evidence - parent) - P(node | evidence)
    """
    edge_contribution = {}
    
    # Convert original_evidence_with_conf to query-friendly format (just states)
    evidence_for_query = {k: v[0] if isinstance(v, (list, tuple)) else v for k, v in original_evidence_with_conf.items()}
    
    old_evidence_for_query = evidence_for_query.copy()
    new_evidence_for_query = evidence_for_query.copy()
    
    try:
        if node in new_evidence_for_query:
            del new_evidence_for_query[node]
        if node in old_evidence_for_query:
            del old_evidence_for_query[node]
    except KeyError:
        pass

    parents = model.get_parents(node)
    values = []
    for parent in parents:
        contr = 0
        try:
            # If parent is part of the evidence, remove it to see its contribution
            if parent in new_evidence_for_query:
                temp_evidence_val = new_evidence_for_query[parent]
                del new_evidence_for_query[parent]
                contr = drift(node, old_evidence_for_query, new_evidence_for_query) 
                new_evidence_for_query[parent] = temp_evidence_val # Restore for next iteration
            else:
                # If parent is not in evidence, average over its states
                states = model.get_cpds(parent).state_names[parent]
                for label in states:
                    new_evidence_for_query[parent] = label
                    weight = infer.query(variables=[parent]).get_value(**{parent : states.index(label)})
                    contr += drift(node, old_evidence_for_query, new_evidence_for_query) * weight
                    del new_evidence_for_query[parent] # Clean up for next iteration
        except Exception as e:
            print(f"Error calculating parent impact for {parent} on {node}: {e}")
            # Handle cases where query might fail, e.g., if states are missing
            contr = 0 # Default to no contribution on error
        values.append(contr)

    values = normalize_by_abs(values)
    for i in range(len(parents)):
        edge_contribution[parents[i]] = round(values[i], 3)

    return edge_contribution


def get_impact(node, original_evidence_with_conf):
    """returns the drift of the node due to evidence"""
    # Convert original_evidence_with_conf to query-friendly format (just states)
    evidence_for_query = {k: v[0] if isinstance(v, (list, tuple)) else v for k, v in original_evidence_with_conf.items()}

    if node in evidence_for_query.keys():
        print(f"{node} is part of the evidence")
        return 0
    return round(drift(node, evidence_for_query), 3)


def get_probability(variable, states, original_evidence_with_conf):
    """get the probability of a random variable on all of the given states"""
    # Convert original_evidence_with_conf to query-friendly format (just states)
    evidence_for_query = {k: v[0] if isinstance(v, (list, tuple)) else v for k, v in original_evidence_with_conf.items()}

    probability = 0.0
    result = infer.query(variables=[variable], evidence=evidence_for_query)
    state_names = model.get_cpds(variable).state_names[variable]
    for state in states:
        try:
            probability += result.get_value(**{variable : state_names.index(state)})
        except ValueError:
            print(f"Exception occurred in get_probability for {variable} state {state}: State not found.")
            probability += 0

    return round(probability, 3)


def causal_diagnosis(current_day, evidence=None):
    """
    Define a Tree that represents the pathology of losses from the belief graph itself by defining in the root causes
    (leaves) where the root of the tree is profit and the leaves are root causes like bad economy or tough competition.
    
    Parameters:
        current_day (int): The current day for detection.
        evidence (dict, optional): A dictionary of evidence (e.g., from a form submission). 
                                   If provided, it overrides the detection from `detect(current_day)`.
                                   Expected format: {"node_name": "state_string"} for this parameter.
    """
    
    # If evidence is not provided, use the detect module to get daily context
    if evidence is None:
        raw_evidence_from_detect = detect(current_day) # This returns {"node": ["state", confidence]}
    else:
        # If evidence is provided (from monthly form), convert it to the (state, confidence) format
        # For form-submitted evidence, we assume 100% confidence for now.
        raw_evidence_from_detect = {k: [v, 1.0] for k, v in evidence.items()}

    # Validate and process evidence for internal use (remove unseen labels)
    processed_evidence_for_query = {} # This will store {"node": "state_string"}
    final_evidence_for_dashboard = {} # This will store {"node": ["state", confidence]}

    # FIX: Iterate over a copy of the dictionary to prevent "dictionary changed size during iteration"
    for node, value_conf_list in list(raw_evidence_from_detect.items()): 
        if not isinstance(value_conf_list, (list, tuple)) or len(value_conf_list) != 2:
            print(f"Warning: Evidence for {node} is not in (state, confidence) format. Skipping or defaulting confidence.")
            # Attempt to use it as just a state, default confidence to 1.0
            state_val = value_conf_list 
            confidence_val = 1.0
        else:
            state_val = value_conf_list[0]
            confidence_val = value_conf_list[1]

        # Check if the node exists in the model before trying to get its CPDs
        if node not in model.nodes():
            print(f"Skipped: Node '{node}' from evidence is not in the Bayesian Network model.")
            continue

        state_names = model.get_cpds(node).state_names[node]
        if state_val in state_names:
            processed_evidence_for_query[node] = state_val
            final_evidence_for_dashboard[node] = [state_val, confidence_val]
        else:
            print(f"Skipped: Evidence label '{state_val}' for node '{node}' is unseen in model states.")
            # Do not add to processed_evidence_for_query or final_evidence_for_dashboard

    # Return the current state of the business
    state = {"root_causes" : {}, "impact" : {}, "edges" : {}, "evidence" : {}}

    # Store the evidence with confidence for the dashboard
    state["evidence"] = final_evidence_for_dashboard 

    root_causes = {"strategic_levers" : ["low"], "operational_efficiency" : ["rough"], "stocking" : ["short", "abundant"], 
                   "product_popularity" : ["declining"], "competition" : ["high"], "economy" : ["bad"]}

    intermediary_nodes = ["external_factors", "costs", "profits"]

    # root cause analysis
    for cause in root_causes.keys():
        if cause in processed_evidence_for_query.keys(): # If it's already an evidence, don't treat as root cause
            continue
        # Ensure that get_probability is called with processed_evidence_for_query
        prob = get_probability(cause, root_causes[cause], processed_evidence_for_query)
        state["root_causes"][cause] = (root_causes[cause], prob)


    # impact analysis
    for node in intermediary_nodes:
        # Ensure that get_impact is called with processed_evidence_for_query
        state["impact"][node] = get_impact(node, processed_evidence_for_query)

    # edge weight analysis
    for node in model.nodes:
        # Ensure that get_parent_impact is called with processed_evidence_for_query
        state["edges"][node] = get_parent_impact(node, processed_evidence_for_query)

    if not state.get('evidence'): # Check if evidence is empty or None after processing
        print("Problem in ENGINE: No valid evidence processed.")
        # You might want to return None or a default state if no evidence is valid
        # For now, it will return an empty evidence dict, which the dashboard handles.

    # Dummy prediction for profits if not derived from the model
    # This assumes 'profits' is not directly detected but predicted based on causal analysis
    # You might need to refine this logic based on how you want to predict future profits
    # For now, let's just make a simple prediction based on the overall state or a default.
    # This is a placeholder; you'd ideally use a more sophisticated prediction from your model.
    if 'profits' not in state['impact'] and 'profits' not in state['root_causes']:
        # If profits are not directly impacted or a root cause, infer its probability
        try:
            profit_states = model.get_cpds('profits').state_names['profits']
            # Infer the probability of each profit state given the current evidence
            profit_dist = infer.query(variables=['profits'], evidence=processed_evidence_for_query)
            
            # Find the most likely profit state and its probability
            predicted_profit_state, predicted_profit_prob = max(
                zip(profit_states, profit_dist.values), key=lambda x: x[1]
            )
            # Add to state if you want to pass it back, or just use it for future_predictions
            state["predicted_profits"] = (predicted_profit_state, predicted_profit_prob)
        except Exception as e:
            print(f"Could not infer predicted profits: {e}")
            state["predicted_profits"] = ("unknown", 0.0)
    else:
        # If profits are part of impact or root cause, use that information for prediction
        if 'profits' in state['impact']:
            impact_val = state['impact']['profits']
            # Simple heuristic: if impact is negative, predict low; if positive, predict high
            if impact_val < -0.1:
                state["predicted_profits"] = ("low", abs(impact_val)) # Use abs impact as confidence
            elif impact_val > 0.1:
                state["predicted_profits"] = ("high", abs(impact_val))
            else:
                state["predicted_profits"] = ("stable", 1.0 - abs(impact_val)) # Less impact, more stable
        elif 'profits' in state['root_causes']:
            # If profits are a root cause, use its probability
            cause_states, prob = state['root_causes']['profits']
            # Take the first negative state as the prediction
            state["predicted_profits"] = (cause_states[0], prob)
        else:
            state["predicted_profits"] = ("unknown", 0.0)


    return state

initialize_engine()
