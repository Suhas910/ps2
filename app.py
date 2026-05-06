from flask import Flask, render_template, jsonify
from simulation import run_simulation

app = Flask(__name__, static_folder='static', template_folder='templates')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/simulate', methods=['POST'])
def simulate():
    results = run_simulation(export_metrics=False, verbose=False)
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
