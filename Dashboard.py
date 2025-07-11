# Dashboard that provides that provides the information to the user
from flask import Flask, render_template_string, request
from pyvis.network import Network
import os
from Engine import initialize_engine, causal_diagnosis, model, infer

initialize_engine()
from Engine import compute_new_cpt, save_model

model = compute_new_cpt()
save_model(model)

app = Flask(__name__)

def red_shade(prob):
    """
    Discrete red shades based on probability ranges for clear visual distinction.
    """
    prob = max(min(prob, 1.0), 0.0)

    if prob < 0.1:
        return "rgb(255, 180, 170)"    # light red
    elif prob < 0.3:
        return "rgb(255, 135, 135)"    # moderate red
    elif prob < 0.5:
        return "rgb(255, 102, 102)"    # red
    elif prob < 0.7:
        return "rgb(255, 51, 51)"      # strong red
    else:
        return "rgb(255, 0, 0)"        # pure red



def green_shade():
    return "#00cc66"

def edge_color(value):
    """
    Returns blue for positive, red for negative.
    Alpha used for visibility scaling but capped to a readable range.
    """
    alpha = min(max(abs(value), 0.7), 1.0)  # avoid <0.3 transparency
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
            font-family: Arial;
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
            padding: 20px;
            margin: 0 auto;
            max-width: 100%;
            border: 1px solid #333;
            border-top: none;
            border-radius: 0 0 8px 8px;
            overflow: hidden;
        }
        textarea, select, table, input {
            width: 100%;
            margin-top: 10px;
            background: #2c2c2c;
            color: white;
            border: 1px solid #444;
        }
        th, td {
            padding: 8px;
            text-align: left;
            border: 1px solid #555;
        }
        table {
            border-collapse: collapse;
        }
        iframe {
        width: 100%;
        height: calc(100vh - 180px);  /* adjust height based on header/nav */
        border: none;
        margin: 0;
        padding: 0;
        background-color: #121212;
        display: block;
        overflow: hidden;
        }

        button {
            margin-top: 10px;
            padding: 8px 16px;
            background-color: #1976D2;
            color: white;
            border: none;
            border-radius: 4px;
        }
        button:hover {
            background-color: #1565C0;
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
    from Engine import model, causal_diagnosis  # in case not at top

    # Node positions for graph layout
    positions = {
        "season": (-600, 10), "economy": (-450, 100), "competition": (-300, 150),
        "external_factors": (-300, -100), "product_popularity": (50, 300), "sales": (50, -200),
        "profits": (300, -300), "costs": (500, 100), "pricing": (350, 50),
        "stocking": (200, 150), "strategic_levers": (200, -50), "operational_efficiency": (550, 200)
    }

    # ✅ Normalize case to match model
    evidence = {k: v.lower() for k, v in {
        "season": "off", "sales": "low", "pricing": "high", 
    }.items()}

    # Debug: Print valid states
    for var in evidence:
        valid_states = model.get_cpds(var).state_names[var]
        print(f"{var}: evidence = {evidence[var]}, valid = {valid_states}")

    # ✅ Run diagnosis
    state = causal_diagnosis(evidence)
    if state is None:
        return render_template_string(template_base, content='<p style="color:red;">❌ Invalid or unseen evidence.</p>', active='realtime')

    # In dashboard.py, inside realtime() function, after state = causal_diagnosis(evidence)
    print("Calculated Edge Impacts:", state["edges"])

    # ✅ Create graph
    net = Network(height="600px", width="100%", directed=True, bgcolor="#2c2c2c")

    for node in model.nodes():
        label = node.replace("_", " ").title()

        if node in evidence:
            color = green_shade()
            title = f"{label}\nEvidence"
        elif node in state["root_causes"]:
            prob = state["root_causes"][node][1]
            color = red_shade(prob)
            title = f"{label}\nRoot Cause Probability: {prob:.2f}"
        elif node in state["impact"]:
            impact = state["impact"][node]
            color = red_shade(impact)
            title = f"{label}\nImpact: {impact:.2f}"
        else:
            color = "#888"
            title = label

        x, y = positions.get(node, (0, 0))
        net.add_node(node, label=label, shape="box", color=color, x=x, y=y, fixed=True, title=title, font={"color": "white"})

    for target, contributors in state["edges"].items():
        for source, value in contributors.items():
            if source in model.nodes and target in model.nodes:
                color = edge_color(value)
                net.add_edge(target, source, arrows="to", color=color, title=f"Impact: {value:.2f}")

    net.set_options("""
    {
        "layout": {"randomSeed": 1, "improvedLayout": false},
        "physics": {"enabled": false},
        "nodes": {
            "font": {"size": 18},
            "shape": "box",
            "scaling": {"min": 20, "max": 40},
            "borderWidthSelected": 4
        },
        "edges": {
            "arrows": {"to": {"enabled": true}},
            "smooth": false
        },
        "interaction": {
            "hover": true,
            "zoomView": true,
            "dragView": true
        }
    }
    """)

    net.write_html("graph.html")
    return render_template_string(template_base, content='<iframe src="/graph.html"></iframe>', active='realtime')


@app.route("/graph.html")
def serve_graph():
    with open("graph.html", "r", encoding="utf-8") as f:
        return f.read()

# ------------------- Monthly Diagnosis -------------------
@app.route("/monthly", methods=["GET", "POST"])
def monthly():
    result = "<p>Suggestions will appear here...</p>"

    allowed_vars = ["season", "sales", "pricing"]
    options = {}

    for cpd in model.get_cpds():
        if cpd.variable in allowed_vars:
            options[cpd.variable] = cpd.state_names[cpd.variable]

    if request.method == "POST":
        evidence = {k: v for k, v in request.form.items() if k in allowed_vars}
        state = causal_diagnosis(evidence)
        if not state:
            result = "<p style='color:red;'>❌ Invalid or unseen input values.</p>"
        else:
            root_html = "".join([f"<li><b>{k}</b>: {v[0]} → {v[1]:.2f}</li>" for k, v in state["root_causes"].items()])
            impact_html = "".join([f"<li><b>{k}</b> impacted by <i>{v}</i></li>" for k, v in state["impact"].items()])
            result = f"""
                <h3>Root Causes</h3><ul>{root_html}</ul>
                <h3>Impact</h3><ul>{impact_html}</ul>
            """

    evidence_inputs = "".join([
        f"<label>{var.title()}: <select name='{var}'>" +
        "".join([f"<option value='{opt}'>{opt}</option>" for opt in vals]) +
        "</select></label><br>" for var, vals in options.items()
    ])

    content = f"""
        <form method='POST'>
            <div style='display:grid;grid-template-columns:1fr 1fr;gap:20px;'>
                {evidence_inputs}
            </div>
            <button type='submit'>🧠 Diagnose</button>
        </form>
        <hr>
        {result}
    """
    return render_template_string(template_base, content=content, active='monthly')

# ------------------- Market Insights -------------------
@app.route("/market")
def market():
    content = """
    <h3>Top Variables by Probability</h3>
    <table>
        <tr><th>Variable</th><th>Most Likely Value</th></tr>
    """
    for node in model.nodes():
        try:
            state_names = model.get_cpds(node).state_names[node]
            result = infer.query(variables=[node])
            top_state = max(zip(state_names, result.values), key=lambda x: x[1])
            content += f"<tr><td>{node}</td><td>{top_state[0]} ({top_state[1]:.2f})</td></tr>"
        except Exception as e:
            content += f"<tr><td>{node}</td><td>Error: {str(e)}</td></tr>"
    content += "</table>"
    return render_template_string(template_base, content=content, active='market')

# ------------------- Training Configuration -------------------
@app.route("/training", methods=["GET", "POST"])
def training():
    from Engine import compute_new_cpt, save_model
    global model
    message = ""
    if request.method == "POST":
        selected = request.form.get("period", "last 6 months")
        try:
            model = compute_new_cpt()
            save_model(model)
            message = f"✅ Model retrained using data from <b>{selected}</b>."
        except Exception as e:
            message = f"<p style='color:red;'>❌ Error retraining model: {str(e)}</p>"
    content = f"""
    <form method='POST'>
        <h3>Time Range for Training</h3>
        <label><input type='radio' name='period' value='last 6 months' checked> Last 6 months</label><br>
        <label><input type='radio' name='period' value='last 1 year'> Last 1 year</label><br><br>
        <button type='submit'>🔄 Retrain to Latest Data</button>
    </form>
    {message}
    """
    return render_template_string(template_base, content=content, active='training')

# ------------------- Run App -------------------
if __name__ == "__main__":
    app.run(debug=True, port=5000)
