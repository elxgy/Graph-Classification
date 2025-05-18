from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import tempfile
import sys
import time
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
    file = request.files.get("file")
    start_node = int(request.form.get("start", 0))
    time_limit = float(request.form.get("time_limit", 10)) 
    max_paths = int(request.form.get("max_paths", 10000))

    if not file:
        return jsonify({"error": "no file uploaded"})
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
            file.save(tmp.name)
            adj = read_adj_matrix(tmp.name)
        graph = Graph(adj)  # já é direcionado

        num_vertices = len(adj)
        num_arestas = sum(sum(1 for v in row if v != 0) for row in adj)

        # Eureliano
        euler = eulerian_pathfind(graph)
        has_eulerian_cycle = False
        has_eulerian_path = False
        if euler is not None and euler != []:
            if euler[0] == euler[-1]:
                has_eulerian_cycle = True
            else:
                has_eulerian_path = True

        # Hamiltoniano exato (com limite de tempo e de caminhos)
        start_time = time.time()
        all_paths = []
        for path in hamiltonian_exact_pathfind(graph):
            all_paths.append(path)
            if len(all_paths) >= max_paths or (time.time() - start_time) > time_limit:
                break
        exato_time = time.time() - start_time
        h_cycles = [path for path in all_paths if path and path[0] == path[-1]]
        h_paths = [path for path in all_paths if path and path[0] != path[-1]]
        has_hamiltonian_cycle = len(h_cycles) > 0
        has_hamiltonian_path = len(h_paths) > 0

        # Hamiltoniano heurístico
        heur_start = time.time()
        h_heur = hamiltonian_heuristic_pathfind(graph, start=start_node)
        heur_time = time.time() - heur_start
        has_hamiltonian_heur = h_heur is not None and h_heur != []

        output = {
            "graph_type": "Direcionado",
            "num_vertices": num_vertices,
            "num_arestas": num_arestas,
            "time_limit": time_limit,
            "max_paths": max_paths,
            "exato_time": exato_time,
            "heur_time": heur_time,
            "num_hamiltonian_cycles": len(h_cycles),
            "num_hamiltonian_paths": len(h_paths),
            "has_eulerian_cycle": has_eulerian_cycle,
            "has_eulerian_path": has_eulerian_path,
            "has_hamiltonian_cycle": has_hamiltonian_cycle,
            "has_hamiltonian_path": has_hamiltonian_path,
            "Eulerian": (
                "No path exists." if euler is None else
                "Graph has no edges." if euler == [] else
                " -> ".join(map(str, euler))
            ),
            "Hamiltonian cycles": [" -> ".join(map(str, path)) for path in h_cycles] if h_cycles else "No cycle exists.",
            "Hamiltonian paths": [" -> ".join(map(str, path)) for path in h_paths] if h_paths else "No path exists.",
            f"Hamiltonian (heuristic from {start_node})": (
                "No path exists." if h_heur is None else
                "Graph has no edges." if h_heur == [] else
                " -> ".join(map(str, h_heur))
            )
        }
        return jsonify(output)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if file:
            os.unlink(tmp.name)

if __name__ == "__main__":
    app.run(debug=True)
