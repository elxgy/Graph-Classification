import math
import networkx as nx
import matplotlib.pyplot as plt

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
