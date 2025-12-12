# analyze.py
"""
Analysis and visualization for COMP 6651 Project results.
Generates plots comparing algorithm performance.
"""

import os
import csv


def load_results_csv(filepath):
    """Load results from CSV file."""
    results = []
    with open(filepath, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["k"] = int(row["k"])
            row["n"] = int(row["n"])
            row["N"] = int(row["N"])
            row["avg_ratio"] = float(row["avg_ratio"])
            row["sd_ratio"] = float(row["sd_ratio"])
            row["min_ratio"] = float(row["min_ratio"])
            row["max_ratio"] = float(row["max_ratio"])
            results.append(row)
    return results


def generate_plots(ff_results, cbip_results, output_dir="plots"):
    """
    Generate comparison plots.
    
    Requires matplotlib: pip install matplotlib
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed. Install with: pip install matplotlib")
        print("Skipping plot generation.")
        return
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Plot 1: All algorithms for k=2
    ff_k2 = [r for r in ff_results if r["k"] == 2 and r["Algorithm"] == "FirstFit"]
    ff_deg_k2 = [r for r in ff_results if r["k"] == 2 and r["Algorithm"] == "FirstFit+Degree"]
    ff_sl_k2 = [r for r in ff_results if r["k"] == 2 and r["Algorithm"] == "FirstFit+SmallestLast"]
    cbip_k2 = [r for r in cbip_results if r["k"] == 2]
    
    if ff_k2 and cbip_k2:
        # Sort by n
        ff_k2.sort(key=lambda r: r["n"])
        ff_deg_k2.sort(key=lambda r: r["n"])
        ff_sl_k2.sort(key=lambda r: r["n"])
        cbip_k2.sort(key=lambda r: r["n"])
        
        plt.figure(figsize=(10, 6))
        
        ns = [r["n"] for r in ff_k2]
        plt.plot(ns, [r["avg_ratio"] for r in ff_k2], 
                marker="o", label="FirstFit", linewidth=2, markersize=8)
        plt.plot(ns, [r["avg_ratio"] for r in ff_deg_k2], 
                marker="s", label="FirstFit+Degree", linewidth=2, markersize=8)
        plt.plot(ns, [r["avg_ratio"] for r in ff_sl_k2], 
                marker="^", label="FirstFit+SmallestLast", linewidth=2, markersize=8)
        plt.plot(ns, [r["avg_ratio"] for r in cbip_k2], 
                marker="D", label="CBIP", linewidth=2, markersize=8)
        
        plt.xlabel("Number of Vertices (n)", fontsize=13, fontweight="bold")
        plt.ylabel("Competitive Ratio ρ(Alg)", fontsize=13, fontweight="bold")
        plt.title("Algorithm Comparison on 2-Colourable Graphs", fontsize=14, fontweight="bold")
        plt.legend(fontsize=11, loc="best")
        plt.grid(True, alpha=0.3, linestyle="--")
        plt.tight_layout()
        
        filepath = os.path.join(output_dir, "comparison_k2_all_algorithms.png")
        plt.savefig(filepath, dpi=300, bbox_inches="tight")
        print(f"✓ Generated: {filepath}")
        plt.close()
    
    # Plot 2: FirstFit for different k values
    for algo_name in ["FirstFit", "FirstFit+Degree", "FirstFit+SmallestLast"]:
        plt.figure(figsize=(10, 6))
        
        for k in [2, 3, 4]:
            data_k = [r for r in ff_results if r["Algorithm"] == algo_name and r["k"] == k]
            if data_k:
                data_k.sort(key=lambda r: r["n"])
                ns = [r["n"] for r in data_k]
                ratios = [r["avg_ratio"] for r in data_k]
                plt.plot(ns, ratios, marker="o", label=f"k={k}", linewidth=2, markersize=8)
        
        plt.xlabel("Number of Vertices (n)", fontsize=13, fontweight="bold")
        plt.ylabel("Competitive Ratio ρ(Alg)", fontsize=13, fontweight="bold")
        plt.title(f"{algo_name}: Performance vs Graph Size", fontsize=14, fontweight="bold")
        plt.legend(fontsize=11, loc="best")
        plt.grid(True, alpha=0.3, linestyle="--")
        plt.tight_layout()
        
        filename = f"{algo_name.replace('+', '_')}_by_k.png"
        filepath = os.path.join(output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches="tight")
        print(f"✓ Generated: {filepath}")
        plt.close()
    
    # Plot 3: Direct comparison - FirstFit vs CBIP for k=2
    if ff_k2 and cbip_k2:
        plt.figure(figsize=(10, 6))
        
        ns = [r["n"] for r in ff_k2]
        ff_ratios = [r["avg_ratio"] for r in ff_k2]
        cbip_ratios = [r["avg_ratio"] for r in cbip_k2]
        
        plt.plot(ns, ff_ratios, marker="o", label="FirstFit", 
                linewidth=2.5, markersize=10, color="#e74c3c")
        plt.plot(ns, cbip_ratios, marker="s", label="CBIP", 
                linewidth=2.5, markersize=10, color="#27ae60")
        
        # Fill between to show improvement
        plt.fill_between(ns, ff_ratios, cbip_ratios, alpha=0.2, color="#3498db")
        
        plt.xlabel("Number of Vertices (n)", fontsize=13, fontweight="bold")
        plt.ylabel("Competitive Ratio ρ(Alg)", fontsize=13, fontweight="bold")
        plt.title("CBIP vs FirstFit on Bipartite Graphs (k=2)", fontsize=14, fontweight="bold")
        plt.legend(fontsize=12, loc="best")
        plt.grid(True, alpha=0.3, linestyle="--")
        plt.tight_layout()
        
        filepath = os.path.join(output_dir, "firstfit_vs_cbip_k2.png")
        plt.savefig(filepath, dpi=300, bbox_inches="tight")
        print(f"✓ Generated: {filepath}")
        plt.close()


def print_analysis(ff_results, cbip_results):
    """Print textual analysis of results."""
    print("\n" + "=" * 80)
    print("ANALYSIS SUMMARY")
    print("=" * 80)
    print()
    
    # Analyze growth trends
    for algo_name in ["FirstFit", "FirstFit+Degree", "FirstFit+SmallestLast"]:
        for k in [2, 3, 4]:
            data = [r for r in ff_results if r["Algorithm"] == algo_name and r["k"] == k]
            if len(data) >= 2:
                data.sort(key=lambda r: r["n"])
                first_ratio = data[0]["avg_ratio"]
                last_ratio = data[-1]["avg_ratio"]
                growth = (last_ratio - first_ratio) / first_ratio * 100
                
                print(f"{algo_name} (k={k}):")
                print(f"  n={data[0]['n']}: ρ={first_ratio:.4f}")
                print(f"  n={data[-1]['n']}: ρ={last_ratio:.4f}")
                print(f"  Growth: {growth:.2f}%")
                print()
    
    # Compare algorithms for k=2
    ff_k2 = [r for r in ff_results if r["Algorithm"] == "FirstFit" and r["k"] == 2]
    ff_deg_k2 = [r for r in ff_results if r["Algorithm"] == "FirstFit+Degree" and r["k"] == 2]
    ff_sl_k2 = [r for r in ff_results if r["Algorithm"] == "FirstFit+SmallestLast" and r["k"] == 2]
    cbip_k2 = [r for r in cbip_results if r["k"] == 2]
    
    if ff_k2 and ff_deg_k2:
        improvements = []
        for r_ff, r_deg in zip(ff_k2, ff_deg_k2):
            imp = (r_ff["avg_ratio"] - r_deg["avg_ratio"]) / r_ff["avg_ratio"] * 100
            improvements.append(imp)
        avg_imp = sum(improvements) / len(improvements)
        print(f"Degree Heuristic Improvement over FirstFit (k=2): {avg_imp:.2f}%")
    
    if ff_k2 and ff_sl_k2:
        improvements = []
        for r_ff, r_sl in zip(ff_k2, ff_sl_k2):
            imp = (r_ff["avg_ratio"] - r_sl["avg_ratio"]) / r_ff["avg_ratio"] * 100
            improvements.append(imp)
        avg_imp = sum(improvements) / len(improvements)
        print(f"Smallest-Last Improvement over FirstFit (k=2): {avg_imp:.2f}%")
    
    if ff_k2 and cbip_k2:
        improvements = []
        for r_ff, r_cbip in zip(ff_k2, cbip_k2):
            imp = (r_ff["avg_ratio"] - r_cbip["avg_ratio"]) / r_ff["avg_ratio"] * 100
            improvements.append(imp)
        avg_imp = sum(improvements) / len(improvements)
        print(f"CBIP Improvement over FirstFit (k=2): {avg_imp:.2f}%")
        print(f"  → CBIP significantly outperforms FirstFit on bipartite graphs!")


def main():
    """Main analysis function."""
    results_dir = "results"
    ff_file = os.path.join(results_dir, "results_firstfit_family.csv")
    cbip_file = os.path.join(results_dir, "results_cbip.csv")
    
    if not os.path.exists(ff_file) or not os.path.exists(cbip_file):
        print("ERROR: Results files not found.")
        print("Please run 'python main.py' first to generate results.")
        return 1
    
    print("=" * 80)
    print("ANALYZING EXPERIMENT RESULTS")
    print("=" * 80)
    print()
    
    # Load results
    ff_results = load_results_csv(ff_file)
    cbip_results = load_results_csv(cbip_file)
    
    print(f"Loaded {len(ff_results)} FirstFit family results")
    print(f"Loaded {len(cbip_results)} CBIP results")
    
    # Generate plots
    print()
    print("Generating plots...")
    generate_plots(ff_results, cbip_results)
    
    # Print analysis
    print_analysis(ff_results, cbip_results)
    
    print()
    print("=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print()
    print("Check the 'plots/' directory for visualization files.")
    print()
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
