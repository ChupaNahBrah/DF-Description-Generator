# Logic related decisions
import random
import os
import json
from ..data.loader import GlobalState

# Loads data from weights.json and chooses an option from one of the dicts inside it with weighted randomness
# weights.json contains both dicts and lists of dicts so both must be handled slightly differently
def weighted_choice(weights_data, key):
    if key not in weights_data:
        raise Exception(f"LOGIC-weighted_choice: key '{key}' not found in weights_data") # Replace with log

    if isinstance(weights_data[key], dict):
        options = list(map(int, weights_data[key].keys()))
        weight_values = list(weights_data[key].values())

    elif isinstance(weights_data[key], list):
        options = [entry["mix"] for entry in weights_data[key]]
        weight_values = [entry["weight"] for entry in weights_data[key]]

    # Replace with a log
    if not options or len(options) != len(weight_values):
        raise Exception(
            f"LOGIC-weighted_choice: error condition met\n"
            f"Key: {key}\n"
            f"List lengths: options({len(options)}) weights({len(weight_values)})"
        )

    return random.choices(options, weights=weight_values, k=1)[0]


def choose_subject_count():
    return weighted_choice(GlobalState.weights_data, "subject_count")


def choose_description_count(subject_count):
    subject_count = int(subject_count)
    key = f"{subject_count}subj_desc_count"
    return weighted_choice(GlobalState.weights_data, key)


# Returns a mix of 2 descriptions for 2 subjects based on weights.json rule
def decide_2_2_mix():
    desc_mix = weighted_choice(GlobalState.weights_data, "2subj_2desc_mix")
    return ["xy"] * desc_mix[0] + ["x"] * desc_mix[1]


# Returns a mix of 3 descriptions for 3 subjects 
def decide_3_3_mix():
    desc_mix = weighted_choice(GlobalState.weights_data, "3subj_3desc_mix")
    return ["xy"] * desc_mix[0] + ["x"] * desc_mix[1]


# Returns a mix of 4 descriptions for 3 subjects 
def decide_3_4_mix():
    desc_mix = weighted_choice(GlobalState.weights_data, "3subj_4desc_mix")
    return ["xy"] * desc_mix[0] + ["x"] * desc_mix[1]


# Returns a list of the number and types of descriptions to use
# If there are multiple options, calls a function to determine the mix
def decide_description_mix(subject_count, desc_count):
    # (subj_count, desc_count): list of descriptions to use
    desc_mix_map = {
        (1,0): [],
        (1,1): ["x"],
        (2,1): ["xy"],
        (2,2): decide_2_2_mix,
        (2,3): ["xy","x","x"],
        (3,1): ["xy"],
        (3,2): ["xy","x"],
        (3,3): decide_3_3_mix,
        (3,4): decide_3_4_mix
    }

    mix = desc_mix_map.get((subject_count, desc_count))
    return mix() if callable(mix) else mix


# Creates constraints for subject selection base on the description mix
def get_constraints(subject_count, desc_mix):
    constraints = []

    if desc_mix.count("xy") >= 2:
        constraints.append("xy_unique")
    
    if desc_mix.count("x") > 1 and subject_count > 1:
        constraints.append("x_balance")
    
    #print(f"LOGIC-get_constraints: constraints: {constraints}\n")
    return constraints

# DEPRICATED - look into 3,2 and maybe add to get_constraints
# (subj_count, desc_count): list of constraints
'''
rule_constraints = {
    (2,2): ["x_balance"],
    (2,3): ["x_balance"],
    (3,2): [] # Refer to design doc. Is this necessary? would it be funny to have a useless subject?
}'''

# Ensures constraints like xy_unique are upheld when assigning subjects.
# Chooses subjects (s1) from candidate_subjects to be used for each description
# Need to re-evaluate later. can still choose a candidate for an x desc that was used as x in xy desc
def enforce_constraints(desc_plan, grammar_plan, constraints, candidate_subjects):
    # Tracks candidate chosen as x in xy descriptions to enforce xy_unique constraint
    xy_unique_list = []

    # Same for x description and x_balance constraint
    x_balance_list = []

    for desc_key, desc_data in desc_plan.items():
        # Temp list to remove entries from candidate_subjects so the same subj isn't chosen
        # for x and y for an xy desc
        temp_candidates_xy = candidate_subjects.copy()
        
        if desc_data["type"] == "xy":
            # choose 1st subject for the xy desc
            # If xy_unique constaint is active, only accept choices that haven't already been chosen
            while True:
                rand_selection = random.randint(0,len(temp_candidates_xy)-1)
                x_choice = temp_candidates_xy[rand_selection]
                if x_choice not in xy_unique_list:
                    # Remove x_choice so the same exact subj isn't chosen for y_choice
                    temp_candidates_xy.pop(rand_selection)
                    break

            if "xy_unique" in constraints:
                xy_unique_list.append(x_choice)
            
            # Choose 2nd subject
            rand_selection = random.randint(0,len(temp_candidates_xy)-1)
            y_choice = temp_candidates_xy[rand_selection]

            # Add choices to grammar_plan
            grammar_plan[desc_key]["subjects"] = [x_choice, y_choice]
        

        if desc_data["type"] == "x":
            # Choose the subject
            while True:
                x_choice = random.choice(candidate_subjects)
                if x_choice not in x_balance_list:
                    break
            
            # Add choice to x_balance list so future loops won't choose it if x_balance constraint is active
            if "x_balance" in constraints:
                x_balance_list.append(x_choice)

            # Add choice to grammar_plan
            grammar_plan[desc_key]["subjects"] = [x_choice]