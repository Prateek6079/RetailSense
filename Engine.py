# bayesian network engine to compute all the probabilities, simulate the network, compute CPTs

from pgmpy.models import DiscreteBayesianNetwork
from pgmpy.estimators import BayesianEstimator
from pgmpy.inference import VariableElimination
import pandas as pd
import sqlite3
import pickle

# write a better probability impact function

negative_states = {"profits" : ["low"], "sales" : ["low"], "pricing" : ["high"], "strategic_levers" : ["low"], 
                   "costs" : ["high"], "external_factors" : ["unfavourable"], "operational_efficiency" : ["rough"], 
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
                         ("competition", "external_factors")])


infer = None


def initialize_engine():
    """Load the engine from older model or create new model"""
    global model
    model = compute_new_cpt()
    save_model(model)
    global infer
    infer = get_inference_engine(model)
    return


def get_inference_engine(model):
    return VariableElimination(model)


# compute CPTs ~~ Fit Model
def compute_new_cpt(database="Retail_Data.db", table="labelled_data"):
    """ Bayesian Estimator and BDeu makes sure all that any possible combination that does not show up in data is given a 
    menial probability such that it does not affect the probability values of combination that do appear significantly"""
    conn = sqlite3.connect(f"{database}")
    data = pd.read_sql_query(f"SELECT * FROM {table}", conn).astype(str)
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


def get_parent_impact(node, evidence):
    """return the impace of each parent node on the intermediary node post the evidence"""
    edge_contribution = {}
    new_evidence = evidence.copy()
    parents = model.get_parents(node)
    state_names = model.get_cpds(node).state_names[node]
    neg_state = negative_states[node]
    # testing
    print("node : ", node)

    for parent in parents:
        edge_contribution[parent] = 0
        print(f"{parent} : {negative_states[parent]}")
        for label in negative_states[parent]:
            new_evidence[parent] = label
            try:
                old_val = infer.query(variables=[node]).get_value(**{node : state_names.index(neg_state)})
                new_val = infer.query(variables=[node], evidence=new_evidence).get_value(**{node : state_names.index(neg_state)})
            except ValueError:
                print("exception at get_parent_impact")
                old_val = 0
                new_val = 0
            edge_contribution[parent] += round(old_val - new_val, 3)
            del new_evidence[parent]

    return edge_contribution


def get_impact(node, n_label, evidence):
    """returns the deviance of the node due to evidence"""
    state_names = model.get_cpds(node).state_names[node]
    print(f"{node} : {n_label}")
    try:
        old_value = infer.query(variables=[node]).get_value(**{node : state_names.index(n_label)})
        new_value = infer.query(variables=[node], evidence=evidence).get_value(**{node : state_names.index(n_label)})
    except ValueError:
        print("exception at get_impact")
        old_value = 0
        new_value = 0
    return round(old_value - new_value, 3)


def get_probability(variable, states, evidence):
    """get the probability of a random variable on all of the given states"""
    probability = 0.0
    result = infer.query(variables=[variable], evidence=evidence)
    state_names = model.get_cpds(variable).state_names[variable]
    for state in states:
        try:
            probability += result.get_value(**{variable : state_names.index(state)})
        except ValueError:
            probability += 0

    return round(probability, 3)


def causal_diagnosis(evidence):
    """Define a Tree that represents the pathology of losses from the belief graph itself by definingin the root causes
    (leaves) where the root of the tree is profit and the leaves are root causes like bad economy or tough competition"""
    # check for proper evidence
    for node in evidence.keys():
        state_names = model.get_cpds(node).state_names[node]
        try:
            index = state_names.index(evidence[node])
        except ValueError:
            print("Evidence Label is unseen in data")
            return

    # return the current state of the business
    state = {"root_causes" : {}, "impact" : {}, "edges" : {}}

    root_causes = {"strategic_levers" : ["low"], "operational_efficiency" : ["rough"], "stocking" : ["short", "abundant"], 
                   "product_popularity" : ["declining"], "competition" : ["high"], "economy" : ["bad"]}

    intermediary_nodes = {"external_factors" : "unfavourable", "costs" : "high", "profits" : "low", "sales" : "low"
                          , "pricing" : "high"}

    # root causes and intermediary nodes
    # root causes simple probability post evidence
    # intermediary nodes 
    # the impact on each node => P(node | evidence) - P(node)
    # the impact of it's descendants on it => P(node | evidence ^ descendant) - P(node)
    # return {root_causes : [(cause, negative_states, probability), ...], impact : [(node, impact)], ..., edges :
    # [(node, (child, impact), ... ), ...]}

    # root cause analysis
    for cause in root_causes.keys():
        prob = get_probability(cause, root_causes[cause], evidence)
        state["root_causes"][cause] = (root_causes[cause], prob)


    # impact analysis
    for node in intermediary_nodes.keys():
        impact = get_impact(node, intermediary_nodes[node], evidence)
        descendent_contr = get_parent_impact(node, evidence)
        state["impact"][node] = impact
        state["edges"][node] = descendent_contr

    return state

# test code

initialize_engine()

evidence = {"season" : "festive", "pricing" : "low", "sales" : "stable"}
print(causal_diagnosis(evidence))
