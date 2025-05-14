import math
import networkx as nx
import matplotlib.pyplot as plt
from collections import deque


ajd_matrix = [
    [0, 1, 1, 0, 0],  
    [0, 0, 1, 0, 0],  
    [1, 0, 0, 1, 0],  
    [0, 0, 0, 1, 0],   
    [0, 1, 0, 0, 0],  
]


class Node:
    def __init__(self, id):
        self.id = id
        self.out_neighbors = []
        self.in_neighbors = []

class Graph:
    def __init__(self, adjacency_matrix):
        self.size = len(adjacency_matrix)
        self.nodes = [Node(i) for i in range(self.size)]
        self.matrix = adjacency_matrix
        self._build_graph()

    def _build_graph(self):
        for i in range(self.size):
            for j in range(self.size):
                if self.matrix[i][j] > 0:
                    from_node = self.nodes[i]
                    to_node = self.nodes[j]
                    from_node.out_neighbors.append(to_node)
                    to_node.in_neighbors.append(from_node)

def eulerian_pathfind(graph):
    """
    returns: 
         - None if no path
         - []   if graph has no edges
         - [v0, v1, ..., vk] the trail or circuit
    """
    out_deg = [len(n.out_neighbors) for n in graph.nodes]
    in_deg = [len(n.in_neighbors) for n in graph.nodes]
    
    start_nodes = end_nodes = 0
    start_id = 0
    for i in range(graph.size):
        diff = out_deg[i] - in_deg[i]
        if diff == 1:
            start_nodes += 1
            start_id = i
        elif diff == -1:
            end_nodes += -1
        elif diff != 0:
            return None
        
    if not ((start_nodes == 0 and end_nodes == 0) or 
            (start_nodes == 1 and end_nodes == 1)):
        return None
    
    non_isolated_start = next((i for i in range(graph.size) 
                               if in_deg[i] + out_deg[i] > 0), None)
    
    if non_isolated_start is None:
        return []
        
    

    



'''test shit'''

##do not uncomment
# def visualize_directed_graph(graph):
#     G = nx.DiGraph()  # Directed graph

#     # Add nodes
#     for node in graph.nodes:
#         G.add_node(node.id)

#     # Add directed edges
#     for from_node in graph.nodes:
#         for to_node in from_node.out_neighbors:
#             G.add_edge(from_node.id, to_node.id)

#     # Draw
#     pos = nx.spring_layout(G)  # or try: nx.circular_layout(G)
#     nx.draw(G, pos, with_labels=True, arrows=True, node_color='lightblue', node_size=800, font_size=12, font_weight='bold')
#     nx.draw_networkx_edges(G, pos, arrows=True, arrowstyle='->', arrowsize=20)
#     plt.title("Directed Graph")
#     plt.savefig("graph_output.png", dpi=300)

# graph = Graph(ajd_matrix)
# visualize_directed_graph(graph)
