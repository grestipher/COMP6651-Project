# generator.py
"""
Random k-colourable graph generator for COMP 6651 Project.
Generates graphs by partitioning vertices into k independent sets.
"""

import random
from graph import Graph, save_to_edges_file


def generate_k_colourable_graph(n, k, p):
    """
    Generate random k-colourable undirected graph.
    
    Algorithm (from project spec):
        1. Partition vertices into k non-empty independent sets S[0..k-1]
        2. Add at least one edge from each vertex to each other partition
        3. Add additional edges between partitions with probability p
    
    Args:
        n: Number of vertices (must be >= k)
        k: Number of independent sets (target chromatic number)
        p: Edge probability for additional edges [0.0, 1.0]
        
    Returns:
        (Graph, list[set]): Graph object and partition S
        
    Raises:
        ValueError: If parameters are invalid
    """
    if k > n:
        raise ValueError(f"k ({k}) cannot be greater than n ({n})")
    if k < 1:
        raise ValueError("k must be at least 1")
    if not (0.0 <= p <= 1.0):
        raise ValueError(f"p must be in [0.0, 1.0], got {p}")
    
    g = Graph(n)
    S = [set() for _ in range(k)]
    
    # Step 1: Partition vertices ensuring no empty sets
    counter = 0
    for v in range(1, n + 1):
        if counter < k:
            # First k vertices each get their own partition
            S[counter].add(v)
            counter += 1
        else:
            # Remaining vertices distributed randomly
            idx = random.randint(0, k - 1)
            S[idx].add(v)
    
    # Step 2: Mandatory edges - each vertex connects to each other partition
    for i in range(k):
        for v in S[i]:
            for j in range(k):
                if i == j or len(S[j]) == 0:
                    continue
                # Pick random vertex from partition j
                u = random.choice(list(S[j]))
                if u not in g.adj[v]:
                    g.add_edge(u, v)
    
    # Step 3: Additional edges with probability p
    for i in range(k):
        for j in range(k):
            if i == j:
                continue
            for v in S[i]:
                for u in S[j]:
                    if u in g.adj[v]:
                        continue
                    if random.random() < p:
                        g.add_edge(u, v)
    
    return g, S


def verify_partition(graph, partition):
    """
    Verify that partition forms valid k-colourable graph.
    
    Args:
        graph: Graph object
        partition: List of vertex sets
        
    Returns:
        (bool, str): (is_valid, error_message)
    """
    k = len(partition)
    
    # Check all vertices are covered exactly once
    all_vertices = set()
    for s in partition:
        all_vertices.update(s)
    
    if all_vertices != set(graph.vertices()):
        return False, "Partition doesn't cover all vertices exactly"
    
    # Check for overlaps
    for i in range(k):
        for j in range(i + 1, k):
            overlap = partition[i] & partition[j]
            if overlap:
                return False, f"Partitions {i} and {j} overlap: {overlap}"
    
    # Check independence (no internal edges within any partition)
    for i, s in enumerate(partition):
        for u in s:
            for v in s:
                if u != v and v in graph.neighbours(u):
                    return False, f"Edge within partition {i}: ({u}, {v})"
    
    return True, "Valid k-colourable partition"


def generate_and_save_many(n_values, k_values, p, N_per_setting, folder, rng_seed=None):
    """
    Generate and save multiple graphs for experiments.
    
    Args:
        n_values: List of vertex counts
        k_values: List of chromatic numbers
        p: Edge probability
        N_per_setting: Number of graphs per (k, n) combination
        folder: Output directory
        rng_seed: Optional base random seed
    """
    import os
    
    if rng_seed is not None:
        random.seed(rng_seed)
    
    os.makedirs(folder, exist_ok=True)
    
    total = len(k_values) * len(n_values) * N_per_setting
    count = 0
    
    for k in k_values:
        for n in n_values:
            for idx in range(N_per_setting):
                g, S = generate_k_colourable_graph(n, k, p)
                
                # Verify partition (sanity check)
                valid, msg = verify_partition(g, S)
                if not valid:
                    raise RuntimeError(f"Generated invalid graph: {msg}")
                
                filename = f"graph_k{k}_n{n}_idx{idx}.edges"
                filepath = os.path.join(folder, filename)
                save_to_edges_file(g, filepath)
                
                count += 1
                if count % 100 == 0:
                    print(f"  Generated {count}/{total} graphs")
    
    print(f"Successfully generated {total} graphs in '{folder}/'")
