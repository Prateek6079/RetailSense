from flask import Flask, request, jsonify
from flask_cors import CORS

import Engine

app = Flask(__name__)
CORS(app)

Engine.initialize_engine()


@app.route("/api/analyze", methods=["POST"])
def analyze():
    data = request.get_json()

    day = data.get("day", 1)

    result = Engine.causal_diagnosis(day)

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, port=5000)