# simulate.py
"""
Simulation framework for COMP 6651 Online Graph Coloring Project.
Runs experiments and computes competitive ratio statistics.
"""

import math
import random
from generator import generate_k_colourable_graph
from coloring import (
    first_fit,
    first_fit_degree,
    first_fit_smallest_last,
    cbip,
    validate_coloring
)


def stddev(data, mean):
    """
    Compute sample standard deviation.
    
    Args:
        data: List of numeric values
        mean: Mean of the data
        
    Returns:
        float: Sample standard deviation (N-1 denominator)
    """
    if len(data) <= 1:
        return 0.0
    variance = sum((x - mean) ** 2 for x in data) / (len(data) - 1)
    return math.sqrt(variance)


def competitive_stats(ratios):
    """
    Compute statistics for competitive ratios.
    
    Args:
        ratios: List of competitive ratio values
        
    Returns:
        tuple: (avg, sd, min, max)
    """
    avg = sum(ratios) / len(ratios)
    sd = stddev(ratios, avg)
    return avg, sd, min(ratios), max(ratios)


class ExperimentRunner:
    """
    Manages and runs coloring algorithm experiments.
    """
    
    def __init__(self, rng_seed=None, verbose=True):
        """
        Initialize experiment runner.
        
        Args:
            rng_seed: Base random seed for reproducibility
            verbose: Print progress messages
        """
        self.verbose = verbose
        if rng_seed is not None:
            random.seed(rng_seed)
    
    def _log(self, message):
        """Print message if verbose mode enabled."""
        if self.verbose:
            print(message)
    
    def run_firstfit_family(self, n_values, k_values, p, N):
        """
        Run experiments for FirstFit and its heuristic variants.
        
        Tests all three variants on the SAME graphs for fair comparison:
            - FirstFit (random order)
            - FirstFit + Degree heuristic
            - FirstFit + Smallest-Last heuristic
        
        Args:
            n_values: List of vertex counts
            k_values: List of chromatic numbers
            p: Edge probability
            N: Number of graphs per (k, n) combination
            
        Returns:
            list: Results dictionaries for all algorithms
        """
        results = []
        total_experiments = len(k_values) * len(n_values)
        count = 0
        
        for k in k_values:
            for n in n_values:
                count += 1
                self._log(f"[{count}/{total_experiments}] FirstFit family: k={k}, n={n}")
                
                ratios_plain = []
                ratios_deg = []
                ratios_sl = []
                
                for _ in range(N):
                    # Generate one graph
                    g, _ = generate_k_colourable_graph(n, k, p)
                    
                    # Test all three algorithms on the SAME graph
                    
                    # 1. FirstFit (random order)
                    c_plain = first_fit(g)
                    ok, msg = validate_coloring(g, c_plain)
                    if not ok:
                        raise RuntimeError(f"Invalid FirstFit coloring: {msg}")
                    max_plain = max(c_plain.values())
                    
                    # 2. FirstFit + Degree heuristic
                    c_deg = first_fit_degree(g)
                    ok, msg = validate_coloring(g, c_deg)
                    if not ok:
                        raise RuntimeError(f"Invalid FirstFit+Degree coloring: {msg}")
                    max_deg = max(c_deg.values())
                    
                    # 3. FirstFit + Smallest-Last heuristic
                    c_sl = first_fit_smallest_last(g)
                    ok, msg = validate_coloring(g, c_sl)
                    if not ok:
                        raise RuntimeError(f"Invalid FirstFit+SmallestLast coloring: {msg}")
                    max_sl = max(c_sl.values())
                    
                    # Assumption: χ(G) ≈ k for generated k-colourable graphs
                    chi_est = k
                    ratios_plain.append(max_plain / float(chi_est))
                    ratios_deg.append(max_deg / float(chi_est))
                    ratios_sl.append(max_sl / float(chi_est))
                
                # Compute statistics for each algorithm
                for name, ratios in [
                    ("FirstFit", ratios_plain),
                    ("FirstFit+Degree", ratios_deg),
                    ("FirstFit+SmallestLast", ratios_sl)
                ]:
                    avg, sd, mn, mx = competitive_stats(ratios)
                    results.append({
                        "Algorithm": name,
                        "k": k,
                        "n": n,
                        "N": N,
                        "avg_ratio": avg,
                        "sd_ratio": sd,
                        "min_ratio": mn,
                        "max_ratio": mx
                    })
        
        return results
    
    def run_cbip(self, n_values, p, N):
        """
        Run CBIP experiments for k=2 (bipartite graphs only).
        
        Args:
            n_values: List of vertex counts
            p: Edge probability
            N: Number of graphs per n
            
        Returns:
            list: Results dictionaries for CBIP
        """
        results = []
        k = 2  # CBIP only works for bipartite graphs
        
        for idx, n in enumerate(n_values):
            self._log(f"[{idx+1}/{len(n_values)}] CBIP: k=2, n={n}")
            
            ratios = []
            
            for _ in range(N):
                g, _ = generate_k_colourable_graph(n, k, p)
                
                c_cbip = cbip(g)
                ok, msg = validate_coloring(g, c_cbip)
                if not ok:
                    raise RuntimeError(f"Invalid CBIP coloring: {msg}")
                
                max_c = max(c_cbip.values())
                # For bipartite graphs, χ(G) = 2 exactly
                chi_exact = 2
                ratios.append(max_c / float(chi_exact))
            
            avg, sd, mn, mx = competitive_stats(ratios)
            results.append({
                "Algorithm": "CBIP",
                "k": k,
                "n": n,
                "N": N,
                "avg_ratio": avg,
                "sd_ratio": sd,
                "min_ratio": mn,
                "max_ratio": mx
            })
        
        return results


def print_results_table(results):
    """
    Print results in CSV-like table format.
    
    Args:
        results: List of result dictionaries
    """
    print("Algorithm,k,n,N,avg_ratio,sd_ratio,min_ratio,max_ratio")
    for r in results:
        print(
            f"{r['Algorithm']},{r['k']},{r['n']},{r['N']},"
            f"{r['avg_ratio']:.4f},{r['sd_ratio']:.4f},"
            f"{r['min_ratio']:.4f},{r['max_ratio']:.4f}"
        )


def save_results_to_csv(results, filepath):
    """
    Save results to CSV file.
    
    Args:
        results: List of result dictionaries
        filepath: Output CSV file path
    """
    import csv
    
    if not results:
        return
    
    fieldnames = ["Algorithm", "k", "n", "N", "avg_ratio", "sd_ratio", 
                  "min_ratio", "max_ratio"]
    
    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow(r)
