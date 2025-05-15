import math
from collections import deque

'''test matrixes'''
adj_matrix = [
    [0, 1, 1, 0, 0],  
    [0, 0, 1, 0, 0],  
    [1, 0, 0, 1, 0],  
    [0, 0, 0, 1, 0],   
    [0, 1, 0, 0, 0],  
]

adj2_matrix = [
    # 0  1  2  3  4
    [0, 1, 0, 0, 0],  # 0 → 1
    [0, 0, 0, 1, 0],  # 1 → 3
    [1, 0, 0, 0, 0],  # 2 → 0
    [0, 0, 0, 0, 1],  # 3 → 4
    [0, 0, 1, 0, 0],  # 4 → 2
]

adj3_matrix = [
    # 0  1  2  3  4
    [0, 1, 0, 1, 0],  # 0 → 1, 0 → 3
    [0, 0, 1, 0, 1],  # 1 → 2, 1 → 4
    [1, 0, 0, 0, 1],  # 2 → 0, 2 → 4
    [1, 0, 1, 0, 0],  # 3 → 0, 3 → 2
    [0, 1, 0, 0, 0],  # 4 → 1
]

'''actual code start'''

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
            end_nodes += 1
        elif diff != 0:
            return None
        
    if not ((start_nodes == 0 and end_nodes == 0) or 
            (start_nodes == 1 and end_nodes == 1)):
        return None
    
    non_isolated_start = next((i for i in range(graph.size) 
                               if in_deg[i] + out_deg[i] > 0), None)
    
    if non_isolated_start is None:
        return []
    
    def undirected_version(start):
        seen = {start}
        q = deque([start])
        while q:
            u = q.popleft()
            for nbr in graph.nodes[u].out_neighbors + graph.nodes[u].in_neighbors:
                if nbr.id not in seen:
                    seen.add(nbr.id) 
                    q.append(nbr.id)
        return seen
        
    reachable = undirected_version(non_isolated_start)
    for i in range(graph.size):
        if (in_deg[i] + out_deg[i] > 0) and (i not in reachable):
            return None
    
    if start_nodes == 0:
        start_id = non_isolated_start
        
    local_out = {n.id: deque(n.out_neighbors) for n in graph.nodes}
    stack = [start_id]
    circuit = []
    
    while stack:
        u = stack[-1]
        if local_out[u]:
            v = local_out[u].popleft().id 
            stack.append(v)
        else:
            circuit.append(stack.pop())
    
    return circuit[::-1]

graph = Graph(adj_matrix)
trail = eulerian_pathfind(graph)
print(trail)