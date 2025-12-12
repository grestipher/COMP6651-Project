# graph.py
"""
Graph data structure and EDGES I/O for COMP 6651 Online Graph Coloring Project.
Undirected simple graphs with adjacency list representation.
"""

class Graph:
    """
    Undirected simple graph using adjacency lists.
    Vertices are labeled with integers 1..n.
    """
    
    def __init__(self, n):
        """
        Initialize graph with n vertices.
        
        Args:
            n: Number of vertices (non-negative integer)
            
        Raises:
            ValueError: If n is negative
        """
        if n < 0:
            raise ValueError(f"Number of vertices must be non-negative, got {n}")
        self.n = n
        self.adj = {i: set() for i in range(1, n + 1)}
    
    def add_edge(self, u, v):
        """
        Add undirected edge between vertices u and v.
        Self-loops are ignored. Duplicate edges handled automatically.
        
        Args:
            u, v: Vertex labels (integers in [1, n])
            
        Raises:
            ValueError: If vertices are out of range
        """
        if u == v:
            return  # Ignore self-loops
        
        if u < 1 or v < 1 or u > self.n or v > self.n:
            raise ValueError(f"Vertices out of range: ({u}, {v}) with n={self.n}")
        
        self.adj[u].add(v)
        self.adj[v].add(u)
    
    def neighbours(self, v):
        """Return set of neighbors of vertex v."""
        return self.adj[v]
    
    def vertices(self):
        """Return list of all vertices."""
        return list(self.adj.keys())
    
    def degree(self, v):
        """Return degree of vertex v."""
        return len(self.adj[v])


def save_to_edges_file(graph, filepath):
    """
    Save graph in ASCII EDGES format.
    Each undirected edge {u,v} is stored as two directed lines:
        u v
        v u
    
    Args:
        graph: Graph object to save
        filepath: Output file path
    """
    written = set()
    with open(filepath, "w") as f:
        for u in graph.adj:
            for v in graph.adj[u]:
                if (u, v) in written or (v, u) in written:
                    continue
                f.write(f"{u} {v}\n")
                f.write(f"{v} {u}\n")
                written.add((u, v))


def load_from_edges_file(filepath):
    """
    Load graph from EDGES format file.
    
    Args:
        filepath: Path to EDGES format file
        
    Returns:
        Graph object
    """
    edges = []
    max_vertex = 0
    
    with open(filepath, "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) != 2:
                continue
            u = int(parts[0])
            v = int(parts[1])
            edges.append((u, v))
            max_vertex = max(max_vertex, u, v)
    
    g = Graph(max_vertex)
    for u, v in edges:
        g.add_edge(u, v)
    
    return g
