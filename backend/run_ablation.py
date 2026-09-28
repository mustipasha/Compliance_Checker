import requests
import json
import os
import argparse
import time

def run_ablation(num_runs: int = 5, host: str = "http://localhost:8000"):
    output_dir = "ablation_runs"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"🚀 Starting {num_runs} Ablation Runs (suppress_overreach=true)")
    print(f"Target: {host}/assess")
    print("Ensure the NIST AI RMF document is already uploaded via the frontend before running this.")
    print("-" * 50)
    
    for i in range(1, num_runs + 1):
        print(f"\n▶️ Starting Run {i}/{num_runs}...")
        start_time = time.time()
        
        try:
            # Call the assess endpoint with the ablation flag set
            response = requests.post(
                f"{host}/assess",
                params={
                    "mode": "triple",
                    "suppress_overreach": "true"
                },
                timeout=1200 # 20 minutes timeout to be safe
            )
            response.raise_for_status()
            
            report = response.json()
            score = report.get("compliance_score", 0)
            
            # Save the result to a dedicated folder 
            filename = os.path.join(output_dir, f"nist_ablation_run_{i}.json")
            with open(filename, "w") as f:
                json.dump(report, f, indent=2)
                
            elapsed = time.time() - start_time
            print(f"✅ Run {i} completed in {elapsed:.1f}s. Score: {score:.1f}%")
            print(f"💾 Saved to {filename}")
            
        except requests.exceptions.Timeout:
            print(f"❌ Run {i} timed out! The backend might still be processing. Check the backend logs.")
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed for Run {i}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
                
    print("\n" + "=" * 50)
    print(f"🎉 All {num_runs} ablation runs finished. Results saved in ./{output_dir}/")
    print("To compare, you can now run:")
    print("python ../Evaluation/calculate_metrics.py --run ./ablation_runs/*.json")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run ablation study for alignment overreach.")
    parser.add_argument("--runs", type=int, default=5, help="Number of runs to execute")
    parser.add_argument("--host", type=str, default="http://localhost:8000", help="Backend API host URL")
    
    args = parser.parse_args()
    run_ablation(num_runs=args.runs, host=args.host)
