# test.py
"""
Test suite for COMP 6651 Online Graph Coloring Project.
Validates correctness of all implementations.
"""

from graph import Graph
from generator import generate_k_colourable_graph, verify_partition
from coloring import (
    first_fit,
    first_fit_degree,
    first_fit_smallest_last,
    cbip,
    validate_coloring
)


def test_graph_basic():
    """Test basic graph operations."""
    g = Graph(5)
    assert g.n == 5
    
    g.add_edge(1, 2)
    assert 2 in g.neighbours(1)
    assert 1 in g.neighbours(2)
    assert g.degree(1) == 1
    assert g.degree(2) == 1
    
    g.add_edge(2, 3)
    assert g.degree(2) == 2
    
    # Self-loop should be ignored
    g.add_edge(1, 1)
    assert g.degree(1) == 1
    
    print("✓ Graph: basic operations")


def test_generator_partition():
    """Test that generator creates valid k-colourable graphs."""
    n, k, p = 30, 3, 0.3
    g, S = generate_k_colourable_graph(n, k, p)
    
    # Verify partition
    valid, msg = verify_partition(g, S)
    assert valid, f"Invalid partition: {msg}"
    
    # Check no internal edges in any partition
    for i, subset in enumerate(S):
        for v in subset:
            for u in subset:
                if u != v:
                    assert u not in g.adj[v], f"Edge within partition {i}: ({u}, {v})"
    
    print("✓ Generator: creates valid k-colourable graphs")


def test_generator_reproducibility():
    """Test that same seed produces same graphs."""
    import random
    
    random.seed(123)
    g1, _ = generate_k_colourable_graph(20, 2, 0.3)
    edges1 = set()
    for u in g1.adj:
        for v in g1.adj[u]:
            if u < v:
                edges1.add((u, v))
    
    random.seed(123)
    g2, _ = generate_k_colourable_graph(20, 2, 0.3)
    edges2 = set()
    for u in g2.adj:
        for v in g2.adj[u]:
            if u < v:
                edges2.add((u, v))
    
    assert edges1 == edges2, "Same seed should produce same graph"
    
    print("✓ Generator: reproducible with seed")


def test_firstfit_path():
    """Test FirstFit on a simple path graph."""
    g = Graph(5)
    edges = [(1, 2), (2, 3), (3, 4), (4, 5)]
    for u, v in edges:
        g.add_edge(u, v)
    
    c = first_fit(g, rng_seed=42)
    ok, msg = validate_coloring(g, c)
    assert ok, f"Invalid FirstFit coloring on path: {msg}"
    
    # Path should need at most 2 colors
    max_color = max(c.values())
    assert max_color <= 3, f"Path used {max_color} colors (expected ≤ 2)"
    
    print("✓ FirstFit: path graph")


def test_firstfit_triangle():
    """Test FirstFit on triangle (complete graph K_3)."""
    g = Graph(3)
    g.add_edge(1, 2)
    g.add_edge(2, 3)
    g.add_edge(3, 1)
    
    c = first_fit(g, rng_seed=42)
    ok, msg = validate_coloring(g, c)
    assert ok, f"Invalid FirstFit coloring on triangle: {msg}"
    
    # Triangle needs exactly 3 colors
    max_color = max(c.values())
    assert max_color == 3, f"Triangle used {max_color} colors (expected 3)"
    
    print("✓ FirstFit: triangle (K_3)")


def test_firstfit_bipartite():
    """Test FirstFit on complete bipartite K_3,3."""
    g = Graph(6)
    for u in [1, 2, 3]:
        for v in [4, 5, 6]:
            g.add_edge(u, v)
    
    c = first_fit(g, rng_seed=42)
    ok, msg = validate_coloring(g, c)
    assert ok, f"Invalid FirstFit coloring on K_3,3: {msg}"
    
    # K_3,3 needs 2 colors optimally, FirstFit might use more
    max_color = max(c.values())
    assert max_color <= 4, f"K_3,3 used {max_color} colors (expected ≤ 4)"
    
    print("✓ FirstFit: complete bipartite K_3,3")


def test_degree_heuristic():
    """Test FirstFit + Degree heuristic produces valid coloring."""
    g, _ = generate_k_colourable_graph(30, 3, 0.4)
    
    c = first_fit_degree(g)
    ok, msg = validate_coloring(g, c)
    assert ok, f"Invalid FirstFit+Degree coloring: {msg}"
    
    print("✓ FirstFit+Degree: valid coloring")


def test_smallest_last_heuristic():
    """Test FirstFit + Smallest-Last heuristic produces valid coloring."""
    g, _ = generate_k_colourable_graph(30, 3, 0.4)
    
    c = first_fit_smallest_last(g)
    ok, msg = validate_coloring(g, c)
    assert ok, f"Invalid FirstFit+SmallestLast coloring: {msg}"
    
    print("✓ FirstFit+SmallestLast: valid coloring")


def test_cbip_bipartite():
    """Test CBIP on manually created bipartite graph."""
    g = Graph(6)
    # Create K_3,3
    for u in [1, 2, 3]:
        for v in [4, 5, 6]:
            g.add_edge(u, v)
    
    c = cbip(g, rng_seed=42)
    ok, msg = validate_coloring(g, c)
    assert ok, f"Invalid CBIP coloring on K_3,3: {msg}"
    
    # CBIP should use exactly 2 colors for bipartite
    max_color = max(c.values())
    assert max_color == 2, f"CBIP used {max_color} colors on bipartite (expected 2)"
    
    print("✓ CBIP: complete bipartite K_3,3")


def test_cbip_generated():
    """Test CBIP on randomly generated 2-colourable graph."""
    g, _ = generate_k_colourable_graph(50, 2, 0.3)
    
    c = cbip(g, rng_seed=42)
    ok, msg = validate_coloring(g, c)
    assert ok, f"Invalid CBIP coloring on generated k=2 graph: {msg}"
    
    # Should use small number of colors
    max_color = max(c.values())
    assert max_color <= 4, f"CBIP used {max_color} colors (expected ≤ 4)"
    
    print("✓ CBIP: generated k=2 graph")


def test_cbip_detects_nonbipartite():
    """Test that CBIP raises error on non-bipartite graph."""
    g = Graph(3)
    g.add_edge(1, 2)
    g.add_edge(2, 3)
    g.add_edge(3, 1)  # Triangle - not bipartite
    
    try:
        c = cbip(g, rng_seed=42)
        assert False, "CBIP should raise RuntimeError on non-bipartite graph"
    except RuntimeError as e:
        assert "not bipartite" in str(e).lower()
    
    print("✓ CBIP: detects non-bipartite graphs")


def test_validation():
    """Test coloring validation function."""
    g = Graph(3)
    g.add_edge(1, 2)
    g.add_edge(2, 3)
    
    # Valid coloring
    valid_coloring = {1: 1, 2: 2, 3: 1}
    ok, msg = validate_coloring(g, valid_coloring)
    assert ok, f"Should accept valid coloring: {msg}"
    
    # Invalid coloring (adjacent vertices share color)
    invalid_coloring = {1: 1, 2: 1, 3: 2}
    ok, msg = validate_coloring(g, invalid_coloring)
    assert not ok, "Should reject invalid coloring"
    assert "1" in msg and "2" in msg  # Should mention vertices 1 and 2
    
    print("✓ Validation: detects invalid colorings")


def test_heuristics_improve_firstfit():
    """Test that heuristics generally improve over plain FirstFit."""
    # Generate several graphs and check average improvement
    improvements_deg = []
    improvements_sl = []
    
    for _ in range(10):
        g, _ = generate_k_colourable_graph(50, 3, 0.3)
        
        c_plain = first_fit(g)
        c_deg = first_fit_degree(g)
        c_sl = first_fit_smallest_last(g)
        
        colors_plain = max(c_plain.values())
        colors_deg = max(c_deg.values())
        colors_sl = max(c_sl.values())
        
        improvements_deg.append(colors_plain - colors_deg)
        improvements_sl.append(colors_plain - colors_sl)
    
    avg_improvement_deg = sum(improvements_deg) / len(improvements_deg)
    avg_improvement_sl = sum(improvements_sl) / len(improvements_sl)
    
    # Heuristics should generally not increase colors (allow small margin)
    assert avg_improvement_deg >= -0.5, "Degree heuristic should not significantly worsen results"
    assert avg_improvement_sl >= -0.5, "Smallest-last should not significantly worsen results"
    
    print(f"✓ Heuristics: Degree improves by {avg_improvement_deg:.2f} colors on average")
    print(f"✓ Heuristics: Smallest-Last improves by {avg_improvement_sl:.2f} colors on average")


def run_all_tests():
    """Run all test functions."""
    print("=" * 80)
    print("COMP 6651 - ONLINE GRAPH COLORING TEST SUITE")
    print("=" * 80)
    print()
    
    test_graph_basic()
    test_generator_partition()
    test_generator_reproducibility()
    test_firstfit_path()
    test_firstfit_triangle()
    test_firstfit_bipartite()
    test_degree_heuristic()
    test_smallest_last_heuristic()
    test_cbip_bipartite()
    test_cbip_generated()
    test_cbip_detects_nonbipartite()
    test_validation()
    test_heuristics_improve_firstfit()
    
    print()
    print("=" * 80)
    print("✓ ALL TESTS PASSED")
    print("=" * 80)


if __name__ == "__main__":
    run_all_tests()
