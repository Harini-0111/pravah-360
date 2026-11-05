import json

with open("data/metadata/frontend_contract_audit_results.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for d in data:
    print(f"=== {d['name']} ({d['method']} {d['endpoint']}) ===")
    print(f"  Valid: Code={d['status_code']} | Time={d['response_time_ms']} ms | Size={d['payload_size_kb']} KB")
    print(f"  Invalid Input: Code={d.get('invalid_input_status')} | Resp={str(d.get('invalid_input_response'))[:120]}")
    print(f"  Out of Coverage: Code={d.get('out_of_coverage_status')} | Resp={str(d.get('out_of_coverage_response'))[:120]}")
    sample_str = json.dumps(d.get('sample_response'))
    print(f"  Sample: {sample_str[:140]}...")
    print()
