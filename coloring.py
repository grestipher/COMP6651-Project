# coloring.py
"""
Graph coloring algorithms for COMP 6651 Project:
- FirstFit: Standard greedy online coloring
- FirstFit + Degree Heuristic: Process high-degree vertices first
- FirstFit + Smallest-Last Heuristic: Advanced offline ordering
- CBIP: Coloring Based on Interval Partitioning (k=2 only)
"""

import random
import heapq
from collections import deque


def validate_coloring(graph, coloring):
    """
    Verify coloring is proper: no adjacent vertices share the same color.
    
    Args:
        graph: Graph object
        coloring: Dictionary mapping vertex -> color (positive integers)
        
    Returns:
        (bool, str): (is_valid, message)
    """
    for v in graph.vertices():
        for u in graph.neighbours(v):
            cv = coloring.get(v)
            cu = coloring.get(u)
            if cv is None or cu is None:
                continue
            if cv == cu:
                return False, f"Adjacent vertices {v} and {u} both have color {cv}"
    
    return True, "Valid coloring"


# ==================== FirstFit (Random Order) ====================

def first_fit(graph, rng_seed=None):
    """
    Standard FirstFit greedy online coloring algorithm.
    
    For random presentation order σ:
        Assign each vertex the smallest color not used by revealed neighbors.
    
    Args:
        graph: Graph object
        rng_seed: Optional random seed for reproducibility
        
    Returns:
        dict: vertex -> color (positive integers)
    """
    if rng_seed is not None:
        random.seed(rng_seed)
    
    vertices = graph.vertices()
    random.shuffle(vertices)  # Random online order
    
    color = {v: None for v in vertices}
    revealed = set()
    
    for v in vertices:
        neighbours_revealed = [u for u in graph.neighbours(v) if u in revealed]
        used_colors = set(color[u] for u in neighbours_revealed if color[u] is not None)
        
        # Find smallest available color
        c = 1
        while c in used_colors:
            c += 1
        
        color[v] = c
        revealed.add(v)
    
    return color


# ==================== FirstFit + Degree Heuristic ====================

def first_fit_degree(graph):
    """
    FirstFit with degree-ordering heuristic.
    Process vertices in non-increasing degree order instead of random.
    
    Rationale: High-degree vertices are more constrained, so coloring
    them first may reduce total colors needed.
    
    Args:
        graph: Graph object
        
    Returns:
        dict: vertex -> color (positive integers)
    """
    vertices = graph.vertices()
    # Sort by degree (descending)
    vertices.sort(key=lambda v: len(graph.neighbours(v)), reverse=True)
    
    color = {v: None for v in vertices}
    revealed = set()
    
    for v in vertices:
        neighbours_revealed = [u for u in graph.neighbours(v) if u in revealed]
        used_colors = set(color[u] for u in neighbours_revealed if color[u] is not None)
        
        c = 1
        while c in used_colors:
            c += 1
        
        color[v] = c
        revealed.add(v)
    
    return color


# ==================== FirstFit + Smallest-Last Heuristic ====================

def _smallest_last_ordering(graph):
    """
    Compute smallest-last vertex ordering using a min-heap.
    
    Algorithm:
        Repeatedly remove vertex of minimum degree, tracking order.
        Return vertices in reverse order of removal.
    
    Time complexity: O(V log V + E)
    
    Args:
        graph: Graph object
        
    Returns:
        list: Vertices in smallest-last order
    """
    degrees = {v: len(graph.neighbours(v)) for v in graph.vertices()}
    removed = set()
    order = []
    
    # Min-heap: (degree, vertex)
    heap = [(degrees[v], v) for v in graph.vertices()]
    heapq.heapify(heap)
    
    while heap:
        deg, v = heapq.heappop(heap)
        
        if v in removed:
            continue
        
        removed.add(v)
        order.append(v)
        
        # Update degrees of neighbors and add to heap
        for u in graph.neighbours(v):
            if u not in removed:
                degrees[u] -= 1
                heapq.heappush(heap, (degrees[u], u))
    
    # Reverse order: smallest-last becomes largest-first for coloring
    order.reverse()
    return order


def first_fit_smallest_last(graph):
    """
    FirstFit with smallest-last ordering heuristic.
    
    Classic offline heuristic: repeatedly remove minimum-degree vertex,
    then color in reverse order.
    
    Args:
        graph: Graph object
        
    Returns:
        dict: vertex -> color (positive integers)
    """
    vertices = _smallest_last_ordering(graph)
    
    color = {v: None for v in vertices}
    revealed = set()
    
    for v in vertices:
        neighbours_revealed = [u for u in graph.neighbours(v) if u in revealed]
        used_colors = set(color[u] for u in neighbours_revealed if color[u] is not None)
        
        c = 1
        while c in used_colors:
            c += 1
        
        color[v] = c
        revealed.add(v)
    
    return color


# ==================== CBIP (k=2 only) ====================

def cbip(graph, rng_seed=None):
    """
    CBIP (Coloring Based on Interval Partitioning) for bipartite graphs.
    
    For each vertex v in random online order:
        1. Consider induced graph on {v} ∪ revealed vertices
        2. Find connected component of v in this induced graph
        3. Bipartition component into (A, B) with v ∈ A
        4. Color v with smallest color NOT used in B (opposite partition)
    
    This guarantees proper coloring if the graph is bipartite.
    
    Args:
        graph: Graph object (must be bipartite/2-colourable)
        rng_seed: Optional random seed for reproducibility
        
    Returns:
        dict: vertex -> color (positive integers)
        
    Raises:
        RuntimeError: If graph is not bipartite
    """
    if rng_seed is not None:
        random.seed(rng_seed)
    
    vertices = graph.vertices()
    random.shuffle(vertices)  # Random online order
    
    color = {}
    revealed = set()
    
    for v in vertices:
        # First vertex: trivial case
        if not revealed:
            color[v] = 1
            revealed.add(v)
            continue
        
        # Allowed vertices for component: revealed vertices + v
        allowed = set(revealed)
        allowed.add(v)
        
        # Step 1: Find connected component of v in induced subgraph
        component = set([v])
        queue = deque([v])
        
        while queue:
            x = queue.popleft()
            for u in graph.neighbours(x):
                if u in allowed and u not in component:
                    component.add(u)
                    queue.append(u)
        
        # Step 2: Bipartition component with v fixed in partition A
        A = set([v])
        B = set()
        side = {v: 0}  # 0 -> A, 1 -> B
        
        queue = deque([v])
        is_bipartite = True
        
        while queue:
            x = queue.popleft()
            for u in graph.neighbours(x):
                if u not in component:
                    continue
                
                if u not in side:
                    # Assign opposite partition
                    side[u] = 1 - side[x]
                    if side[u] == 0:
                        A.add(u)
                    else:
                        B.add(u)
                    queue.append(u)
                else:
                    # Check bipartiteness constraint
                    if side[u] == side[x]:
                        is_bipartite = False
        
        if not is_bipartite:
            raise RuntimeError(
                f"Graph is not bipartite (odd cycle detected at vertex {v})"
            )
        
        # Step 3: Choose smallest color NOT used in B (opposite partition of v)
        used_colors = set()
        for u in B:
            if u in color and color[u] is not None:
                used_colors.add(color[u])
        
        c = 1
        while c in used_colors:
            c += 1
        
        color[v] = c
        revealed.add(v)
    
    return color
