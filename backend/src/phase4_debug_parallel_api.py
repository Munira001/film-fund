"""
Debug - See REAL Parallel API data structure
"""

import json
from parallel_api import ParallelAPI


def main():
    print("\n" + "="*70)
    print("DEBUG - PARALLEL API REAL DATA STRUCTURE")
    print("="*70 + "\n")
    
    api = ParallelAPI()
    results = api.search("documentary filmmaker grants", limit=3)
    
    print(f"Found {len(results)} results\n")
    
    for i, opp in enumerate(results[:2], 1):
        print(f"Opportunity {i}:")
        print(json.dumps(opp, indent=2))
        print("\n" + "-"*70 + "\n")


if __name__ == "__main__":
    main()