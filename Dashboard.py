from flask import Flask, render_template_string, request, redirect, url_for

from pyvis.network import Network
import os
import sys

# Ensure the Engine module can be imported
# This assumes engine.py is in the same directory or on the Python path
try:
    from Engine import initialize_engine, causal_diagnosis, model, infer
except ImportError:
    # Fallback for environments where direct import might fail,

    import importlib.util
    spec = importlib.util.spec_from_file_location("Engine", "Engine.py")
    Engine = importlib.util.module_from_spec(spec)
    sys.modules["Engine"] = Engine
    spec.loader.exec_module(Engine)
    from Engine import initialize_engine, causal_diagnosis, model, infer

initialize_engine()
# Initialize the engine and compute/save the model once on startup


app = Flask(__name__)

# global day variable
current_day = 1

def red_shade(prob):
    """
    Discrete red shades based on probability ranges for clear visual distinction.
    """
    prob = max(min(prob, 1.0), 0.0)

    if prob < 0.1:
        return "rgb(255, 180, 170)"       # light red
    elif prob < 0.3:
        return "rgb(255, 135, 135)"       # moderate red
    elif prob < 0.5:
        return "rgb(255, 102, 102)"       # red
    elif prob < 0.7:
        return "rgb(255, 51, 51)"         # strong red
    else:
        return "rgb(255, 0, 0)"           # pure red


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
            width: 100%; /* Keep 100% for smaller screens */
            max-width: 98%; /* Set a maximum width for the table */
            margin: 20px auto; /* Center the table horizontally and add some vertical margin */
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); /* Add a subtle shadow for depth */
            border-radius: 8px; /* Slightly rounded corners for the table */
            overflow: hidden; /* Ensures border-radius applies to inner elements */
        }
        
        /* ADDED/MODIFIED CSS FOR TABLE HEADERS AND DATA CELLS */
        th {
            background-color: #2a3d54; /* Darker blue shade for headers */
            color: #e0e0e0; /* Lighter text for contrast */
            font-weight: bold;
            text-transform: uppercase; /* Makes headers stand out */
            letter-spacing: 0.5px;
        }
        td {
            background-color: #2c2c2c; /* Ensure table data cells have a distinct background */
            color: #e0e0e0;
        }
        /* END ADDED/MODIFIED CSS */

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
            margin-left: 10px;
        }
        hr {
            border: 0;
            height: 1px;
            background: #444;
            margin: 20px 0;
        }
        h3 {
            margin-top: 5px;
            color: #90caf9;
            margin-bottom: 15px;
            text-align: center;
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


        /* Styles for the new daily context feature */
        .daily-context-container {
            padding: 20px;
            background: #1e1e1e;
            border-radius: 8px;
            margin-bottom: 20px;
            border: 1px solid #333;
        }
        .day-selector-group {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 20px;
            flex-wrap: wrap; /* Allow wrapping on small screens */
        }
        .day-selector-group label {
            font-size: 1.1em;
            white-space: nowrap;
        }
        .day-selector-group input[type="range"] {
            flex-grow: 1;
            -webkit-appearance: none;
            width: 100%;
            height: 8px;
            background: #444;
            border-radius: 5px;
            outline: none;
            opacity: 0.7;
            transition: opacity .2s;
        }
        .day-selector-group input[type="range"]::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: #1976D2;
            cursor: pointer;
            border: 2px solid #fff;
        }
        .day-selector-group input[type="range"]::-moz-range-thumb {
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: #1976D2;
            cursor: pointer;
            border: 2px solid #fff;
        }
        .day-number-line {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 10px;
            padding: 0 5px;
            position: relative;
            height: 30px;
        }
        .day-number-line::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 0;
            right: 0;
            height: 2px;
            background: #555;
            transform: translateY(-50%);
            z-index: 0;
        }
        .day-number {
            width: 25px; /* Fixed width for each day circle */
            height: 25px; /* Fixed height for each day circle */
            background: #444;
            border-radius: 50%;
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 0.8em;
            font-weight: bold;
            color: #bbb;
            position: relative;
            z-index: 1;
            transition: background 0.3s ease, color 0.3s ease, border 0.3s ease, box-shadow 0.3s ease; /* Added border and box-shadow to transition */
            cursor: pointer;
            flex-shrink: 0; /* Prevent shrinking */
        }
        .day-number.highlighted {
            background: #1976D2;
            color: white;
            box-shadow: 0 0 8px rgba(25, 118, 210, 0.8);
            border: 2px solid #66bb6a;
        }
        .day-number.past-day {
            background: #3a3a3a; /* Slightly different shade for past days */
        }
        .day-number:hover {
            transform: scale(1.1);
        }
        .evidence-list, .predictions-list {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        .evidence-item, .prediction-item {
            background: #2c2c2c;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #444;
        }
        .evidence-item p, .prediction-item p {
            margin: 5px 0;
            font-size: 0.95em;
        }
        .evidence-item strong, .prediction-item strong {
            color: #90caf9;
        }
        /* Styling for the nested probability list */
        .probability-list {
            list-style: none; /* Remove bullet points */
            padding-left: 0;
            margin-top: 5px;
        }
        .probability-list li {
            background-color: #383838; /* Slightly darker background for inner list items */
            padding: 5px 10px;
            margin-bottom: 3px;
            border-radius: 3px;
            font-size: 0.9em;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .probability-bar {
            height: 10px;
            background-color: #66bb6a; /* Green for probability bar */
            border-radius: 2px;
            margin-left: 10px;
        }

        /* Styles for custom radio buttons */
        .form-group label input[type="radio"] {
            /* Hide the default radio button */
            -webkit-appearance: none;
            -moz-appearance: none;
            appearance: none;
            border: none; /* Remove default border */
            outline: none; /* Remove outline on focus */
            margin-right: 8px; /* Space between custom box and label text */
            position: relative; /* For positioning the custom box */
            top: 2px; /* Adjust vertical alignment if needed */
            vertical-align: middle; /* Align with text */
            cursor: pointer;
        }

        .form-group label input[type="radio"]::before {
            content: '';
            display: inline-block;
            width: 18px; /* Size of the custom box */
            height: 18px; /* Size of the custom box */
            border: 2px solid #90caf9; /* Border color for the unchecked box */
            border-radius: 4px; /* Slightly rounded corners for a modern look */
            background-color: #2c2c2c; /* Background of the unchecked box */
            transition: all 0.2s ease; /* Smooth transition for changes */
            vertical-align: middle;
        }

        .form-group label input[type="radio"]:checked::before {
            background-color: #1976D2; /* Background of the checked box */
            border-color: #1976D2; /* Border color of the checked box */
        }

        .form-group label input[type="radio"]:checked::after {
            content: '✔'; /* Unicode checkmark character */
            font-size: 14px; /* Size of the tick */
            color: white; /* Color of the tick */
            position: absolute;
            left: 2px; /* Adjust tick position within the box */
            top: 0px; /* Adjust tick position within the box */
            line-height: 18px; /* Vertically center the tick */
            text-align: center;
            width: 18px;
            height: 18px;
        }

        /* Optional: improve focus styling for accessibility */
        .form-group label input[type="radio"]:focus::before {
            box-shadow: 0 0 0 3px rgba(25, 118, 210, 0.5); /* Blue glow on focus */
        }

        /* To ensure labels are block elements for better alignment and clickable area */
        .form-group label {
            display: flex; /* Use flexbox to align input and text */
            align-items: center; /* Vertically center items */
            margin-bottom: 10px; /* Space between radio options */
            cursor: pointer;
            font-size: 1.1em; /* Make text a bit larger */
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
        {% if active == 'realtime' %} {# <--- CONDITIONALLY RENDER THIS BLOCK #}
        <div class="daily-context-container">
            <h3>Daily Business Context Simulation</h3>
            <div style="font-size: 1.2em; font-weight: bold; color: #90caf9; text-align: center; margin-bottom: 15px;">
                Current Day: <span id="currentDayDisplay">Day {{ current_day }}</span>
            </div>
            <div class="day-number-line">
                {% for i in range(1, 32) %}
                    <span class="day-number {% if i <= current_day %}past-day{% endif %} {% if i == current_day %}highlighted{% endif %}" onclick="setDay({{ i }})">{{ i }}</span>
                {% endfor %}
            </div>

            <h3 style="margin-top: 25px;">Current Active Evidence</h3>
            <div class="evidence-list">
                {% if active_evidence %}
                    {% for var, val in active_evidence.items() %}
                        <div class="evidence-item">
                            <p><strong>{{ var.replace('_', ' ').title() }}:</strong> {{ val.title() }}</p>
                            <p><strong>Confidence:</strong> {{ active_evidence_confidence[var] * 100 | int }}%</p>
                        </div>
                    {% endfor %}
                {% else %}
                    <p>No active evidence for this day yet.</p>
                {% endif %}
            </div>

            <h3 style="margin-top: 25px;">Future Predictions</h3>
            <div class="predictions-list">
                <div class="prediction-item">
                    <p><strong>Predicted Profits:</strong>
                        {{ future_predictions['predicted_profits'][0].title() }}
                        ({{ (future_predictions['predicted_profits'][1] * 100) | round(2) }}%)
                    </p>
                </div>
            </div>
        </div>
        <hr>
        <iframe src="/graph.html?day={{ current_day }}"></iframe>
        {% endif %} {# <--- END OF CONDITIONAL BLOCK #}

        {{ content | safe }} {# <--- THIS IS WHERE THE SPECIFIC PAGE CONTENT GOES #}
    </div>

    {% if active == 'realtime' %} {# <--- CONDITIONALLY INCLUDE SCRIPT #}
    <script>
        function updateDay(day) {
            document.getElementById('currentDayDisplay').innerText = 'Day ' + day;
            // Update the URL to trigger Flask route reload with new day
            window.location.href = '/?day=' + day;
        }

        function setDay(day) {
            updateDay(day);
        }
    </script>
    {% endif %}
</body>
</html>
"""

# ------------------- Real-time Route -------------------
@app.route("/")
def realtime():
    global current_day
    current_day = int(request.args.get("day", current_day))

    full_state = causal_diagnosis(current_day)
    print("📦 Full State from causal_diagnosis():", full_state) # Keep this for debugging
    evidence = full_state.get("evidence", {})
    print("🔍 Evidence dictionary:", evidence) # Keep this for debugging

    # This seems correct as it extracts the state name (first element of the tuple)
    active_evidence = {k: v[0] for k, v in evidence.items()}  # state name
    active_evidence_confidence = {k: v[1] for k, v in evidence.items()}  # confidence score

    diagnosis = causal_diagnosis(current_day) # Re-call diagnosis after evidence is processed to get latest state

    net = Network(height="549px", width="100%", directed=True, bgcolor="#2c2c2c", font_color="white")

    for node in model.nodes():
        label = node.replace("_", " ").title()
        title = label # Default title

        try:
            state_names = model.get_cpds(node).state_names[node]
            result = infer.query(variables=[node], evidence=evidence)
            top_state = max(zip(state_names, result.values), key=lambda x: x[1])
            # top_state[0] is the state name (string), so .title() is fine here
            title = f"{label}\nState: {top_state[0].title()}\nConfidence: {top_state[1]*100:.2f}%"
        except Exception as e: # Catch specific exceptions or log them instead of bare except
            print(f"Error inferring state for node {node}: {e}")
            title = label # Fallback to just label if inference fails

        # Evidence node tag - FIX IS HERE
        if node in evidence:
            evid_val_tuple = evidence[node] # This is a tuple, e.g., ('high', 0.9)
            evid_state_name = evid_val_tuple[0] # Extract the state name string
            conf_val = active_evidence_confidence.get(node, 1.0)
            title += f"\nType: Evidence\nEvidence Value: {evid_state_name.title()}\nEvidence Confidence: {conf_val*100:.2f}%"

        # Root cause tag
        if node in diagnosis["root_causes"]:
            cause_vals, prob = diagnosis["root_causes"][node]
            # cause_vals can be a list of strings, so ', '.join(cause_vals) is correct
            title += f"\nType: Root Cause\nTarget State(s): {', '.join(cause_vals).title()}\nRoot Cause Probability: {prob*100:.2f}%"


        # Impact info
        if node in diagnosis["impact"]:
            title += f"\nImpact Value: {diagnosis['impact'][node]:.2f}"

        # Node color
        if node in diagnosis["root_causes"]:
            color = red_shade(diagnosis["root_causes"][node][1])
        elif node in evidence:
            color = green_shade()
        else:
            color = "#888"

        x, y = positions.get(node, (0, 0))
        net.add_node(
            node,
            label=label,
            shape="box",
            color=color,
            x=x,
            y=y,
            fixed=True,
            title=title, # This is the corrected title string
            font={"color": "white"}
        )

    # ... (rest of your realtime function)
    # The second net.add_node call for the same node is redundant and can be removed:
    # net.add_node(node, label=label, shape="box", color=color, x=x, y=y, fixed=True, title=title, font={"color": "white"})

    for target, contributors in diagnosis["edges"].items():
        for source, value in contributors.items():
            if source in model.nodes and target in model.nodes:
                color = edge_color(value)
                net.add_edge(target, source, arrows="to", color=color, title=f"Impact: {value:.2f}", width=abs(value)*4 + 3)

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

    net.write_html("graph.html")

    return render_template_string(template_base,
                                  active="realtime",
                                  current_day=current_day,
                                  active_evidence=active_evidence,
                                  active_evidence_confidence=active_evidence_confidence,
                                  future_predictions={"predicted_profits": ("unknown", 0.0)})



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
    <h3>Prior Probability Distribution for Business Variables</h3>
    <table>
        <tr><th>Variable</th><th>Probability Distribution</th></tr>
    """
    # Iterate through all nodes in the model to infer their most likely state
    for node in model.nodes():
        try:
            state_names = model.get_cpds(node).state_names[node]
            # Query the marginal probability distribution for each variable
            result = infer.query(variables=[node])
            
            # Start a nested unordered list for the probabilities
            prob_list_html = "<ul class='probability-list'>"
            
            # Sort states by probability (descending) to show highest first
            sorted_probabilities = sorted(zip(state_names, result.values), key=lambda x: x[1], reverse=True)

            for state_name, probability in sorted_probabilities:
                # Add a list item for each state and its probability
                # Include a simple visual bar for probability
                prob_list_html += f"""
                <li>
                    <span>{state_name.title()}</span>
                    <span style="font-weight: bold;">{probability:.2f}</span>
                    <div class="probability-bar" style="width: {(probability * 100):.0f}%;"></div>
                </li>
                """
            prob_list_html += "</ul>"

            content += f"<tr><td>{node.replace('_', ' ').title()}</td><td>{prob_list_html}</td></tr>"
        except Exception as e:
            content += f"<tr><td>{node.replace('_', ' ').title()}</td><td>Error: Could not infer states ({str(e)})</td></tr>"
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
            # Assuming compute_new_cpt and save_model are defined in Engine.py
            from Engine import compute_new_cpt, save_model
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
