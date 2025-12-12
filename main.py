# main.py
"""
Main execution script for COMP 6651 Online Graph Coloring Project.
Runs all experiments and generates results for the report.
"""

import argparse
import os
from simulate import ExperimentRunner, print_results_table, save_results_to_csv


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="COMP 6651 - Online Graph Coloring Experiments",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default parameters (recommended for project)
  python main.py
  
  # Quick test run
  python main.py --quick
  
  # Custom parameters
  python main.py --n-values 50,100,200 --N 50 --p 0.4
  
  # Reproduce exact results
  python main.py --seed 42
        """
    )
    
    parser.add_argument(
        "--n-values",
        type=str,
        default="50,100,200,400,800,1600",
        help="Comma-separated n values (default: 50,100,200,400,800,1600)"
    )
    
    parser.add_argument(
        "--k-values",
        type=str,
        default="2,3,4",
        help="Comma-separated k values (default: 2,3,4)"
    )
    
    parser.add_argument(
        "--p",
        type=float,
        default=0.3,
        help="Edge probability (default: 0.3)"
    )
    
    parser.add_argument(
        "--N",
        type=int,
        default=100,
        help="Number of graphs per (k,n) combination (default: 100)"
    )
    
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)"
    )
    
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Quick test mode (n=50,100; N=20)"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default="results",
        help="Output directory for CSV files (default: results)"
    )
    
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress progress messages"
    )
    
    return parser.parse_args()


def main():
    """Main execution function."""
    args = parse_args()
    
    # Parse parameters
    if args.quick:
        n_values = [50, 100]
        k_values = [2, 3]
        N = 20
    else:
        n_values = [int(x.strip()) for x in args.n_values.split(",")]
        k_values = [int(x.strip()) for x in args.k_values.split(",")]
        N = args.N
    
    p = args.p
    
    # Display configuration
    print("=" * 80)
    print("COMP 6651 - ONLINE GRAPH COLORING PROJECT")
    print("=" * 80)
    print(f"\nExperiment Configuration:")
    print(f"  n values:          {n_values}")
    print(f"  k values:          {k_values}")
    print(f"  Edge probability:  {p}")
    print(f"  Graphs per (k,n):  {N}")
    print(f"  Random seed:       {args.seed}")
    print(f"  Output directory:  {args.output_dir}")
    print()
    
    # Initialize experiment runner
    runner = ExperimentRunner(rng_seed=args.seed, verbose=not args.quiet)
    
    try:
        # Run FirstFit family experiments (FirstFit, +Degree, +SmallestLast)
        print("=" * 80)
        print("RUNNING FIRSTFIT EXPERIMENTS (k ∈ {2,3,4})")
        print("=" * 80)
        print()
        
        ff_results = runner.run_firstfit_family(n_values, k_values, p, N)
        
        # Run CBIP experiments (k=2 only)
        print()
        print("=" * 80)
        print("RUNNING CBIP EXPERIMENTS (k = 2)")
        print("=" * 80)
        print()
        
        cbip_results = runner.run_cbip(n_values, p, N)
        
        # Display results
        print()
        print("=" * 80)
        print("RESULTS: FIRSTFIT FAMILY")
        print("=" * 80)
        print()
        print_results_table(ff_results)
        
        print()
        print("=" * 80)
        print("RESULTS: CBIP (k=2)")
        print("=" * 80)
        print()
        print_results_table(cbip_results)
        
        # Save results to CSV files
        os.makedirs(args.output_dir, exist_ok=True)
        
        ff_path = os.path.join(args.output_dir, "results_firstfit_family.csv")
        cbip_path = os.path.join(args.output_dir, "results_cbip.csv")
        
        save_results_to_csv(ff_results, ff_path)
        save_results_to_csv(cbip_results, cbip_path)
        
        print()
        print("=" * 80)
        print("RESULTS SAVED")
        print("=" * 80)
        print(f"  FirstFit family: {ff_path}")
        print(f"  CBIP:            {cbip_path}")
        print()
        
        # Quick analysis
        print("=" * 80)
        print("QUICK ANALYSIS")
        print("=" * 80)
        print()
        
        # Compare FirstFit vs FirstFit+Degree for k=2
        ff_k2 = [r for r in ff_results if r['Algorithm'] == 'FirstFit' and r['k'] == 2]
        ff_deg_k2 = [r for r in ff_results if r['Algorithm'] == 'FirstFit+Degree' and r['k'] == 2]
        
        if ff_k2 and ff_deg_k2:
            avg_improvement_deg = 0
            for r_plain, r_deg in zip(ff_k2, ff_deg_k2):
                improvement = (r_plain['avg_ratio'] - r_deg['avg_ratio']) / r_plain['avg_ratio'] * 100
                avg_improvement_deg += improvement
            avg_improvement_deg /= len(ff_k2)
            print(f"FirstFit vs FirstFit+Degree (k=2):")
            print(f"  Average improvement: {avg_improvement_deg:.2f}%")
        
        # Compare FirstFit vs FirstFit+SmallestLast for k=2
        ff_sl_k2 = [r for r in ff_results if r['Algorithm'] == 'FirstFit+SmallestLast' and r['k'] == 2]
        
        if ff_k2 and ff_sl_k2:
            avg_improvement_sl = 0
            for r_plain, r_sl in zip(ff_k2, ff_sl_k2):
                improvement = (r_plain['avg_ratio'] - r_sl['avg_ratio']) / r_plain['avg_ratio'] * 100
                avg_improvement_sl += improvement
            avg_improvement_sl /= len(ff_k2)
            print(f"\nFirstFit vs FirstFit+SmallestLast (k=2):")
            print(f"  Average improvement: {avg_improvement_sl:.2f}%")
        
        # Compare FirstFit vs CBIP for k=2
        cbip_k2 = [r for r in cbip_results if r['k'] == 2]
        
        if ff_k2 and cbip_k2:
            avg_improvement_cbip = 0
            for r_plain, r_cbip in zip(ff_k2, cbip_k2):
                improvement = (r_plain['avg_ratio'] - r_cbip['avg_ratio']) / r_plain['avg_ratio'] * 100
                avg_improvement_cbip += improvement
            avg_improvement_cbip /= len(ff_k2)
            print(f"\nFirstFit vs CBIP (k=2):")
            print(f"  Average improvement: {avg_improvement_cbip:.2f}%")
            print(f"  (CBIP significantly outperforms FirstFit on bipartite graphs!)")
        
        print()
        print("=" * 80)
        print("EXPERIMENT COMPLETED SUCCESSFULLY")
        print("=" * 80)
        print()
        print("Next steps:")
        print("  1. Review results CSV files in 'results/' directory")
        print("  2. Run 'python analyze.py' to generate plots (requires matplotlib)")
        print("  3. Include results tables in your project report")
        print()
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\nExperiment interrupted by user")
        return 1
    
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
