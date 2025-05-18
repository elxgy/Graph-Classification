import argparse
import os
import sys
from graph_utils import(
    Graph,
    eulerian_pathfind,
    hamiltonian_exact_pathfind,
    hamiltonian_heuristic_pathfind
    )


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

def main():
    parser = argparse.ArgumentParser(
        description="load and ajd matrix and run pathfinders"
    )
    parser.add_argument(
        "matrix_file",\
        help="path to .txt file containing adj matrix"
    )
    parser.add_argument(
        "--start",
        type=int,
        default=0,
        help="Start node for Hamiltonian heuristic (default: 0)."
    )
    args = parser.parse_args()
    
    adj = read_adj_matrix(args.matrix_file)
    graph = Graph(adj)
    
    results=[]
    euler = eulerian_pathfind(graph)
    results.append(("Eulerian", euler))
    
    h_exact = hamiltonian_exact_pathfind(graph)
    results.append(("Hamiltonian (exact)", h_exact))

    h_heur = hamiltonian_heuristic_pathfind(graph, start=args.start)
    results.append((f"Hamiltonian (heuristic from {args.start})", h_heur))
    
    for name, result in results:
        print(f"{name} result:")
        if result is None:
            print("  No path exists.")
        elif result == []:
            print("  Graph has no edges.")
        else:
            if isinstance(result, list) and result and isinstance(result[0], list):
                for idx, path in enumerate(result, 1):
                    print(f"  [{idx}]: {' -> '.join(map(str, path))}")
            else:
                print("  ", " -> ".join(map(str, result)))
        print()

if __name__ == "__main__":
    main()