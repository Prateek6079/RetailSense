from flask import Flask, render_template_string, request
from pyvis.network import Network
import os
import sys

# Ensure the Engine module can be imported
# This assumes engine.py is in the same directory or on the Python path
try:
    from Engine import initialize_engine, causal_diagnosis, model, infer, compute_new_cpt, save_model
except ImportError:
    # Fallback for environments where direct import might fail,
    # assuming engine.py is in the current working directory.
    # This is a common pattern in some deployment setups.
    import importlib.util
    spec = importlib.util.spec_from_file_location("Engine", "engine.py")
    Engine = importlib.util.module_from_spec(spec)
    sys.modules["Engine"] = Engine
    spec.loader.exec_module(Engine)
    from Engine import initialize_engine, causal_diagnosis, model, infer, compute_new_cpt, save_model


# Initialize the engine and compute/save the model once on startup
initialize_engine()
# Recompute CPTs with the latest data and save the model
# This ensures the model is up-to-date when the app starts
model = compute_new_cpt()
save_model(model)

app = Flask(__name__)

def red_shade(prob):
    """
    Discrete red shades based on probability ranges for clear visual distinction.
    """
    prob = max(min(prob, 1.0), 0.0)

    if prob < 0.1:
        return "rgb(255, 180, 170)"      # light red
    elif prob < 0.3:
        return "rgb(255, 135, 135)"      # moderate red
    elif prob < 0.5:
        return "rgb(255, 102, 102)"      # red
    elif prob < 0.7:
        return "rgb(255, 51, 51)"        # strong red
    else:
        return "rgb(255, 0, 0)"          # pure red


def green_shade():
    return "#00cc66"

def edge_color(value):
    """
    Returns blue for positive, red for negative.
    Alpha used for visibility scaling but capped to a readable range.
    """
    # Ensure alpha is between 0.7 and 1.0 for visibility
    alpha = min(max(abs(value), 1), 1.0) 
    if value > 0:
        return f"rgba(0, 102, 255, {alpha:.2f})"  # strong blue
    else:
        return f"rgba(255, 51, 51, {alpha:.2f})"  # strong red


# ------------------- Template Base -------------------
template_base = """
<!DOCTYPE html>
<html>
<head>
    <title>Business Diagnostic Dashboard</title>
    <style>
        *{
        margin: 0;
        padding: 0;
        }
        body {
            font-family: Arial, sans-serif;
            background: #121212;
            color: #e0e0e0;
            padding: 0;
            margin: 0;
        }
        nav {
            display: flex;
            justify-content: center;
            background: #1e1e1e;
            padding: 10px;
            border-bottom: 2px solid #333;
        }
        nav a {
            padding: 12px 24px;
            margin: 0 10px;
            text-decoration: none;
            color: #90caf9;
            font-weight: bold;
            background: #2c2c2c;
            border-radius: 8px 8px 0 0;
            border: 1px solid #333;
            border-bottom: none;
            transition: background 0.3s ease;
        }
        nav a.active {
            background: #1976D2;
            color: white;
        }
        nav a:hover {
            background: #333;
        }
        .tab {
            background: #1e1e1e;
            padding: 0;
            margin: 0 ;
            max-width: 100%;
            border: 1px solid #333;
            border-top: none;
            border-radius: 0 0 8px 8px;
            overflow: hidden;
        }
        textarea, select, table, input[type="text"] {
            width: 100%;
            padding: 8px;
            margin-top: 10px;
            background: #2c2c2c;
            color: white;
            border: 1px solid #444;
            border-radius: 4px;
            box-sizing: border-box;
        }
        th, td {
            padding: 8px;
            text-align: left;
            border: 1px solid #555;
        }
        table {
            border-collapse: collapse;
            width: 100%;
        }
        iframe {
            width: 100%;
            height: calc(100vh - 180px);
            border: none;
            margin: 0;
            padding: 0;
            background-color: #121212;
            display: block;
            overflow: hidden;
        }

        button {
            margin-top: 10px;
            padding: 10px 20px;
            background-color: #1976D2;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }
        button:hover {
            background-color: #1565C0;
        }
        .form-group {
            margin-bottom: 15px;
        }
        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        hr {
            border: 0;
            height: 1px;
            background: #444;
            margin: 20px 0;
        }
        h3 {
            color: #90caf9;
            margin-bottom: 15px;
        }
        ul {
            list-style: none;
            padding: 0;
        }
        ul li {
            background: #2c2c2c;
            margin-bottom: 8px;
            padding: 10px;
            border-radius: 4px;
            border: 1px solid #444;
        }
    </style>
</head>
<body>
    <header style="background:#0c1f3c; padding: 20px; text-align: center; color: white;">
        <h1 style="margin: 0; font-size: 2em;">Business Diagnosis Dashboard</h1>
    </header>
    <nav>
        <a href="/" class="{{ 'active' if active=='realtime' else '' }}">Real-time Business State</a>
        <a href="/monthly" class="{{ 'active' if active=='monthly' else '' }}">Monthly Diagnosis</a>
        <a href="/market" class="{{ 'active' if active=='market' else '' }}">Market Insights</a>
        <a href="/training" class="{{ 'active' if active=='training' else '' }}">Training Configuration</a>
    </nav>
    <div class="tab">
        {{ content|safe }}
    </div>
</body>
</html>
"""

# ------------------- Real-time Route -------------------
@app.route("/")
def realtime():
    # Node positions for graph layout to ensure a consistent and readable layout
    # Scaled positions by 4.0 to make the graph larger and fill the space better
    scale_factor = 4.0 # Increased scale factor
    positions = {
        "season": (-600  , 10 ), 
        "economy": (-450 , 100 ), 
        "competition": (-300 , 150 ),
        "external_factors": (-300 , -100 ), 
        "product_popularity": (50 , 300 ), 
        "sales": (50 , -200 ),
        "profits": (300 , -300 ), 
        "costs": (500 , 100 ), 
        "pricing": (350 , 50 ),
        "stocking": (200 , 150 ), 
        "strategic_levers": (200 , -50 ), 
        "operational_efficiency": (550 , 200 )
    }

    # Define the current evidence for real-time diagnosis
    # Ensure states match the model's expected states (e.g., lowercase)
    evidence = {k: v.lower() for k, v in {
        "season": "off", 
        "sales": "low", 
        "pricing": "high", 
    }.items()}

    # Debugging: Print valid states for evidence variables to ensure consistency
    # for var in evidence:
    #     try:
    #         valid_states = model.get_cpds(var).state_names[var]
    #         print(f"DEBUG: {var}: evidence = {evidence[var]}, valid = {valid_states}")
    #     except Exception as e:
    #         print(f"DEBUG: Could not get states for {var}: {e}")

    # Run causal diagnosis with the provided evidence
    state = causal_diagnosis(evidence)
    if state is None:
        # If diagnosis fails (e.g., invalid evidence), display an error message
        return render_template_string(template_base, content='<p style="color:red;">❌ Invalid or unseen evidence provided. Please check the input values.</p>', active='realtime')

    # Debugging: Print the calculated edge impacts to understand why edges might be missing
    print("DEBUG: Calculated Edge Impacts:", state["edges"])

    # Create a pyvis network graph
    # Changed height to "100%" to fill the iframe vertically
    net = Network(height="549px", width="100%", directed=True, bgcolor="#2c2c2c", font_color="white")

    # Add nodes to the graph
    for node in model.nodes():
        label = node.replace("_", " ").title() # Format node names for display

        # Determine node color and title based on its role in the diagnosis
        if node in evidence:
            color = green_shade() # Green for evidence nodes
            title = f"{label}\nEvidence: {evidence[node].title()}"
        elif node in state["root_causes"]:
            # Red shades for root causes based on their probability
            prob = state["root_causes"][node][1]
            color = red_shade(prob)
            title = f"{label}\nRoot Cause Probability: {prob:.2f}"
        elif node in state["impact"]:
            # Red shades for impacted nodes based on their impact value
            impact = state["impact"][node]
            color = red_shade(impact)
            title = f"{label}\nImpact: {impact:.2f}"
        else:
            color = "#888" # Grey for other nodes
            title = label

        # Get fixed positions for nodes for consistent layout
        x, y = positions.get(node, (0, 0))
        net.add_node(node, label=label, shape="box", color=color, x=x, y=y, fixed=True, title=title, font={"color": "white"})

    # Add edges to the graph based on calculated impacts
    for target, contributors in state["edges"].items():
        for source, value in contributors.items():
            # Only add edges if both source and target nodes exist in the model
            if source in model.nodes and target in model.nodes:
                color = edge_color(value) # Determine edge color based on impact value
                # Add edge from source to target with an arrow
                net.add_edge(target, source, arrows="to", color=color, title=f"Impact: {value:.2f}", width=abs(value)*4 + 3) # Vary width by impact

    # Configure pyvis network options for better visualization
    net.set_options("""
    {
        "layout": {"randomSeed": 1, "improvedLayout": false},
        "physics": {"enabled": false},
        "nodes": {
            "font": {
                "color": "white",
                "size": 22,
                "face": "Arial",
                "strokeWidth": 3,
                "strokeColor": "rgba(0,0,0,1)"
            },
            "shape": "box",
            "scaling": {"min": 20, "max": 40},
            "borderWidthSelected": 4
        },
        "edges": {
            "arrows": {"to": {"enabled": true}},
            "smooth": false,
            "width": 2,
            "color": {
                "inherit": false
            }
        },
        "interaction": {
            "hover": true,
            "zoomView": false,
            "dragView": false
        },
        "fit": true
    }
    """)

    # Save the graph to an HTML file and render it in an iframe
    graph_file_path = "graph.html"
    net.write_html(graph_file_path)
    return render_template_string(template_base, content=f'<iframe src="/{graph_file_path}"></iframe>', active='realtime')


@app.route("/graph.html")
def serve_graph():
    # Serve the generated graph HTML file
    try:
        with open("graph.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Graph not found. Please navigate to the Real-time Business State page first to generate it."

# ------------------- Monthly Diagnosis -------------------
@app.route("/monthly", methods=["GET", "POST"])
def monthly():
    result = "<p>Suggestions will appear here...</p>"

    # Define allowed variables for monthly diagnosis input
    allowed_vars = ["season", "sales", "pricing"] # Added more variables for demonstration
    options = {}

    # Populate options for dropdowns based on model's CPDs
    for cpd in model.get_cpds():
        if cpd.variable in allowed_vars:
            options[cpd.variable] = cpd.state_names[cpd.variable]

    if request.method == "POST":
        # Collect evidence from form submission
        evidence = {k: v.lower() for k, v in request.form.items() if k in allowed_vars}
        
        # Perform causal diagnosis
        state = causal_diagnosis(evidence)
        if not state:
            result = "<p style='color:red;'>❌ Invalid or unseen input values. Please select valid options for all fields.</p>"
        else:
            # Format root causes and impacts for display
            root_html = "".join([f"<li><b>{k.replace('_', ' ').title()}</b>: {v[0]} &rarr; {v[1]:.2f}</li>" for k, v in state["root_causes"].items()])
            impact_html = "".join([f"<li><b>{k.replace('_', ' ').title()}</b> impacted with value {v:.2f}</li>" for k, v in state["impact"].items()])
            
            result = f"""
                <h3>Root Causes Identified</h3>
                <ul>{root_html}</ul>
                <h3>Key Impacts</h3>
                <ul>{impact_html}</ul>
            """

    # Generate HTML for evidence input forms (dropdowns)
    evidence_inputs = ""
    for var, vals in options.items():
        evidence_inputs += f"""
        <div class="form-group">
            <label for="{var}">{var.replace('_', ' ').title()}:</label>
            <select name='{var}' id='{var}'>
                {''.join([f"<option value='{opt}'>{opt.title()}</option>" for opt in vals])}
            </select>
        </div>
        """

    content = f"""
        <form method='POST'>
            <div style='display:grid;grid-template-columns:1fr 1fr;gap:20px;'>
                {evidence_inputs}
            </div>
            <button type='submit'>🧠 Diagnose Business State</button>
        </form>
        <hr>
        {result}
    """
    return render_template_string(template_base, content=content, active='monthly')

# ------------------- Market Insights -------------------
@app.route("/market")
def market():
    content = """
    <h3>Most Likely States for Business Variables (Based on Prior Probabilities)</h3>
    <table>
        <tr><th>Variable</th><th>Most Likely Value (Probability)</th></tr>
    """
    # Iterate through all nodes in the model to infer their most likely state
    for node in model.nodes():
        try:
            state_names = model.get_cpds(node).state_names[node]
            # Query the marginal probability distribution for each variable
            result = infer.query(variables=[node])
            # Find the state with the highest probability
            top_state = max(zip(state_names, result.values), key=lambda x: x[1])
            content += f"<tr><td>{node.replace('_', ' ').title()}</td><td>{top_state[0].title()} ({top_state[1]:.2f})</td></tr>"
        except Exception as e:
            content += f"<tr><td>{node.replace('_', ' ').title()}</td><td>Error: Could not infer state ({str(e)})</td></tr>"
    content += "</table>"
    return render_template_string(template_base, content=content, active='market')

# ------------------- Training Configuration -------------------
@app.route("/training", methods=["GET", "POST"])
def training():
    global model # Declare model as global to modify it
    message = ""
    if request.method == "POST":
        # Get selected training period (though compute_new_cpt currently doesn't use it)
        selected = request.form.get("period", "last 6 months")
        try:
            # Recompute CPTs and save the updated model
            model = compute_new_cpt()
            save_model(model)
            message = f"<p style='color:green;'>✅ Model successfully retrained using data from <b>{selected}</b>.</p>"
        except Exception as e:
            message = f"<p style='color:red;'>❌ Error retraining model: {str(e)}. Please check the database connection and data.</p>"
    
    content = f"""
    <form method='POST'>
        <h3>Select Data Range for Model Retraining</h3>
        <div class="form-group">
            <label><input type='radio' name='period' value='last 6 months' checked> Last 6 months</label><br>
            <label><input type='radio' name='period' value='last 1 year'> Last 1 year</label><br><br>
        </div>
        <button type='submit'>🔄 Retrain Model to Latest Data</button>
    </form>
    {message}
    """
    return render_template_string(template_base, content=content, active='training')

# ------------------- Run App -------------------
if __name__ == "__main__":
    # Ensure the graph.html file is cleaned up on exit if needed, though not strictly necessary for this app
    # if os.path.exists("graph.html"):
    #     os.remove("graph.html")
    app.run(debug=True, port=5000)
