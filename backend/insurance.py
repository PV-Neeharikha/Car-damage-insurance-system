from constants import *;
#Used for policy covers
def get_policy_json(policy_type):

    policies = {
        "third_party": THIRD_PARTY,
        "policy_a": POLICY_A,
        "policy_b": POLICY_B,
        "policy_c": POLICY_C
    }

    return policies.get(policy_type, THIRD_PARTY)



#Used for calculating damage cost
def calculate_damage_cost(damage_name,severity,policy_type):

    key = f"{damage_name}_{severity.lower()}"

    raw_cost = RAW_COSTS.get(key, 0)

    policy_json = get_policy_json(policy_type)

    covered_amount = policy_json.get(key, 0)

    customer_payable = max(0,raw_cost - covered_amount)

    return (raw_cost,covered_amount,customer_payable)
