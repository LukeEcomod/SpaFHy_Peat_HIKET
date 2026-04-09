"""
run_model.py — SpaFHy model run
Submitted via run_regions.sh as a SLURM batch job.

Usage:
    python run_regions.py <region>
"""

import sys
import os
import traceback

from model_driver import driver

# ── Configuration ──────────────────────────────────────────────────────────────
BASE_DIR = '/scratch/project_2000908/nousu/HIKET/SpaFHyData'
PARAM_MODULE = "parameters_regions"

# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    if len(sys.argv) < 2:
        print("ERROR: please provide a region name, e.g.  python run_regions.py PPKai", file=sys.stderr)
        sys.exit(1)

    region = sys.argv[1]
    folder = os.path.join(BASE_DIR, region)

    print(f"Working directory: {os.getcwd()}")
    print(f"Region:            {region}")
    print(f"Forcing folder:    {folder}")
    print(f"Parameter module:  {PARAM_MODULE}")

    try:
        print("\n--- Running model driver ---")
        outputfile = driver(
            create_ncf=True,
            folder=folder,
            param_module=PARAM_MODULE
        )
        print(f"Model finished. Output file: {outputfile}")

    except Exception as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()