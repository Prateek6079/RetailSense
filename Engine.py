# bayesian network engine to compute all the probabilities, simulate the network, compute CPTs

from pgmpy.models import DiscreteBayesianNetwork
from pgmpy.estimators import BayesianEstimator
from pgmpy.inference import VariableElimination
import pandas as pd
import sqlite3
import pickle

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


def initialize_engine():
    """Load the engine from older model or create new model"""
    global model
    model = load_model()
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


def normalize_by_abs(values):
    total_abs = sum(abs(v) for v in values)
    return [v / total_abs for v in values] if total_abs != 0 else [0 for v in values]


def drift(node, new_evidence, old_evidence = dict()):
    """Returns how much the probability of a variable drifts when certain evidence presents itself"""
    states = model.get_cpds(node).state_names[node]
    drift_states = negative_states[node]
    drift = 0
    for state in drift_states:
        if state not in states:
            continue
        old_value = infer.query(variables=[node], evidence=old_evidence).get_value(**{node : states.index(state)})
        new_value = infer.query(variables=[node], evidence=new_evidence).get_value(**{node : states.index(state)})
        drift += old_value - new_value
    return drift


def get_parent_impact(node, evidence):
    """return the impace of each parent node on the intermediary node post the evidence
    P(node | evidence) - P(node | evidence ^ parent) likelihood weighted on all states
    P(node | evidence - parent) - P(node | evidence)"""
    edge_contribution = {}
    old_evidence = evidence.copy()
    new_evidence = evidence.copy()
    try:
        del new_evidence[node]
        del old_evidence[node]
    except KeyError:
        pass

    parents = model.get_parents(node)
    values = []
    for parent in parents:
        contr = 0
        try:
            # run for evidence
            temp_evidence = new_evidence[parent]
            del new_evidence[parent]
            contr = drift(node, old_evidence, new_evidence) # actually new_evidence and old_evidence are interchanged so don't be confused
            new_evidence[parent] = temp_evidence
        except KeyError:
            # run normally
            states = model.get_cpds(parent).state_names[parent]
            for label in states:
                new_evidence[parent] = label
                weight = infer.query(variables=[parent]).get_value(**{parent : states.index(label)})
                contr += drift(node, new_evidence, old_evidence) * weight
                del new_evidence[parent]
        values.append(contr)

    values = normalize_by_abs(values)
    for i in range(len(parents)):
        edge_contribution[parents[i]] = round(values[i], 3)

    return edge_contribution


def get_impact(node, evidence):
    """returns the drift of the node due to evidence"""
    if node in evidence.keys():
        print(f"{node} is part of the evidence")
        return 0
    return round(drift(node, evidence), 3)


def get_probability(variable, states, evidence):
    """get the probability of a random variable on all of the given states"""
    probability = 0.0
    result = infer.query(variables=[variable], evidence=evidence)
    state_names = model.get_cpds(variable).state_names[variable]
    for state in states:
        try:
            probability += result.get_value(**{variable : state_names.index(state)})
        except ValueError:
            print("exception occured in get_probability")
            probability += 0

    return round(probability, 3)


def causal_diagnosis(evidence = {"pricing" : "high", "sales" : "low", "season" : "festive"}):
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
    state = {"root_causes" : {}, "impact" : {}, "edges" : {}, "evidence" : {}}

    for evd in evidence.keys():
        state["evidence"][evd] = (evidence[evd], 1)

    root_causes = {"strategic_levers" : ["low"], "operational_efficiency" : ["rough"], "stocking" : ["short", "abundant"], 
                   "product_popularity" : ["declining"], "competition" : ["high"], "economy" : ["bad"]}

    intermediary_nodes = ["external_factors", "costs", "profits"]

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
    for node in intermediary_nodes:
        state["impact"][node] = get_impact(node, evidence)

    # edge weight analysis
    for node in model.nodes:
        state["edges"][node] = get_parent_impact(node, evidence)

    return state


initialize_engine()
