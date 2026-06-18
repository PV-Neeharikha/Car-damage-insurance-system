import json
#Opening json Files
with open("class_names.json","r") as f:
    class_names = json.load(f)

with open("insurance_costs/Raw_cost.json","r") as f:
    RAW_COSTS = json.load(f)

with open("insurance_costs/Third_party_policy.json","r") as f:
    THIRD_PARTY = json.load(f)

with open("insurance_costs/Policy A.json","r") as f:
    POLICY_A = json.load(f)

with open("insurance_costs/Policy B.json","r") as f:
    POLICY_B = json.load(f)

with open("insurance_costs/Policy C.json","r") as f:
    POLICY_C = json.load(f)
