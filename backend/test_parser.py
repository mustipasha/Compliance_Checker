from criteria_parser import parse_criteria
import json

try:
    criteria = parse_criteria("criteria_new.json")
    print(f"Successfully parsed {len(criteria)} criteria.")
    if criteria:
        print("First criterion sample:")
        print(json.dumps(criteria[0], indent=2))
except Exception as e:
    print(f"Test failed: {e}")
