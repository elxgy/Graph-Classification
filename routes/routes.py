from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import tempfile
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from graph_utils import (
    Graph,
    eulerian_pathfind,
    hamiltonian_exact_pathfind,
    hamiltonian_heuristic_pathfind,
)

app = Flask(__name__)
CORS(app)

def read_adj_matrix(file_path):
    matrix = []
    with open(file_path, 'r') as f:
        for line in f:
            line = line.split('#', 1)[0].strip()
            if not line:
                continue
            
            for ch in '[]()':
                line = line.replace(ch, ' ')
                
            parts = [p for p in line.replace(',', ' ').split() if p]
            try:
                row = [int(x) for x in parts]
            except ValueError as e:
                print(f"Error parsing line '{line}': {e}", file=sys.stderr)
                sys.exit(1)
            matrix.append(row)
            
    n = len(matrix)
    if any(len(row) != n for row in matrix):
        print(f"Error: adjacency matrix must be square (found {n} rows, but row lengths vary).", file=sys.stderr)
        sys.exit(1)
    return matrix

@app.route("/analyze", methods=["POST"])
def analyze_graph():
    file.request.files.get("file")
    start_node = int(request.form.get("start", 0))

    if not file:
        return jsonify({"error": "no file uploaded"})
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
            file.save(tmp.name)
            adj = read_adj_matrix(tmp.name)
            
        graph = Graph(adj)

        results = []
        euler = eulerian_pathfind(graph)
        results.append(("Eulerian", euler))

        h_exact = hamiltonian_exact_pathfind(graph)
        results.append(("Hamiltonian (exact)", h_exact))

        h_heur = hamiltonian_heuristic_pathfind(graph, start=start_node)
        results.append((f"Hamiltonian (heuristic from {start_node})", h_heur))

        output = {}
        for name, result in results:
            if result is None:
                output[name] = "No path exists."
            elif result == []:
                output[name] = "Graph has no edges."
            else:
                if isinstance(result, list) and result and isinstance(result[0], list):
                    output[name] = [" -> ".join(map(str, path)) for path in result]
                else:
                    output[name] = " -> ".join(map(str, result))

        return jsonify(output)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if file:
            os.unlink(tmp.name)

if __name__ == "__main__":
    app.run(debug=True)
