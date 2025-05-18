import math
from collections import deque
from itertools import permutations

'''test matrixes
adj_matrix = [
    [0, 1, 1, 0, 0],  
    [0, 0, 1, 0, 0],  
    [1, 0, 0, 1, 0],  
    [0, 0, 0, 1, 0],   
    [0, 1, 0, 0, 0],  
]

adj2_matrix = [
    [0, 1, 0, 0, 0],  
    [0, 0, 0, 1, 0],  
    [1, 0, 0, 0, 0],  
    [0, 0, 0, 0, 1],  
    [0, 0, 1, 0, 0],  
]

adj3_matrix = [
    [0, 1, 0, 1, 0],  
    [0, 0, 1, 0, 1],  
    [1, 0, 0, 0, 1],  
    [1, 0, 1, 0, 0],  
    [0, 1, 0, 0, 0],  
]
'''

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
#first version o hamiltonian pathfind that will be split in heuristic and exact version
'''
def hamiltonian_pathfind(graph):
    def backtrack(path, visited):
        if len(path) == graph.size:
            last = graph.nodes[path[-1]]
            
            if graph.nodes[path[0]] in last.out_neighbors:
                return path + [path[0]]
            
            else:
                return path


        last_node = path[-1]
        for neighbor in graph.nodes[last_node].out_neighbors:
            if neighbor.id not in visited:
                visited.add(neighbor.id)
                path.append(neighbor.id)
                
                result = backtrack(path, visited)
                
                if result:
                    return result
                
                path.pop()
                visited.remove(neighbor.id)
                
        return None

    for start_node in range(graph.size):
        visited = set([start_node])
        path = [start_node]
        result = backtrack(path, visited)
        
        if result:
            return result
    
    return None

h_trail = hamiltonian_pathfind(graph1)
print(h_trail)
'''
def hamiltonian_exact_pathfind(graph):
    """
        returns:
            - if paths are possible -> all paths: [[], [], ... []]
            - if no paths exist -> None
    """
    paths = []
    for perm in permutations(range(graph.size)):
        valid = True
        
        for u, v in zip(perm, perm[1:]):
            if graph.nodes[v] not in graph.nodes[u].out_neighbors:
                valid = False
                break
            
        if not valid:
            continue

        if graph.nodes[perm[0]] in graph.nodes[perm[-1]].out_neighbors:
            paths.append(list(perm) + [perm[0]])
            
        else:
            paths.append(list(perm))

    return paths


def hamiltonian_heuristic_pathfind(graph, start=0):
    """
        returns:
            - if any path is possible -> first path found [v1, v2, ... vk]
            - if gets stuck due to next_node rules -> None
            - if no paths exist -> None
    """
    visited = set()
    path = [start]
    visited.add(start)
    
    current = start
    while len(path) < graph.size:
        
        next_node = None
        min_options = float('inf')
        
        for neighbor in graph.nodes[current].out_neighbors:
            if neighbor.id not in visited:
                
                options = sum(1 for nbr in neighbor.out_neighbors if nbr.id not in visited)
                if options < min_options:
                    min_options = options
                    next_node = neighbor.id
                    
        if next_node is None:
            return None
        
        path.append(next_node)
        visited.add(next_node)
        current = next_node
        
    if any(nbr.id == start for nbr in graph.nodes[current].out_neighbors):
        path.append(start)
        
    return path
