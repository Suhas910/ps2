import pandas as pd
import numpy as np

class GraphEngine:
    def __init__(self, edges_csv):
        self.dist_matrix = {}
        self.load_graph(edges_csv)

    def load_graph(self, csv_path):
        df = pd.read_csv(csv_path)
        # Identify all unique locations
        nodes = set()
        for _, row in df.iterrows():
            nodes.add((int(row['from_x']), int(row['from_y'])))
            nodes.add((int(row['to_x']), int(row['to_y'])))
        
        nodes = list(nodes)
        node_to_idx = {node: i for i, node in enumerate(nodes)}
        n = len(nodes)
        
        # Initialize matrix with infinity
        adj = np.full((n, n), np.inf)
        np.fill_diagonal(adj, 0)

        for _, row in df.iterrows():
            u = node_to_idx[(int(row['from_x']), int(row['from_y']))]
            v = node_to_idx[(int(row['to_x']), int(row['to_y']))]
            # Distance = minutes * multiplier (for traffic/delay)
            weight = row['distance_minutes'] * row['delay_multiplier']
            adj[u][v] = weight
            adj[v][u] = weight # Assuming bidirectional

        # Floyd-Warshall Algorithm
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    if adj[i][j] > adj[i][k] + adj[k][j]:
                        adj[i][j] = adj[i][k] + adj[k][j]
        
        # Convert back to a coordinate-based dictionary for O(1) lookups
        self.dist_map = {}
        for i, node_i in enumerate(nodes):
            for j, node_j in enumerate(nodes):
                self.dist_map[(node_i, node_j)] = adj[i][j]

    def get_dist(self, start_pos, end_pos):
        dist = self.dist_map.get((start_pos, end_pos), None)
        if dist is None or dist == np.inf:
            # Fallback: Manhattan distance with 5 minutes per unit
            dx = abs(start_pos[0] - end_pos[0])
            dy = abs(start_pos[1] - end_pos[1])
            return (dx + dy) * 5.0
        return dist