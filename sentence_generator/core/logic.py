# Logic related decisions
import random
from ..data.loader import GlobalState
import logging
logger = logging.getLogger(__name__)

# Looks in weights_data and chooses an option from one of the dicts inside it with weighted randomness
# weights_data contains both dicts and lists of dicts so both must be handled slightly differently
def weighted_choice(weights_data, key, variable=None, caller=None):
    if key not in weights_data:
        if variable is not None and caller is not None:
            logger.debug("weighted_choice failed for %s assignment in %s", variable, caller)
        logger.error("key, '%s' not found. weights_data: %s", key, weights_data)
        raise Exception(f"ERROR- logic.py: weighted_choice(): no weights found for {key}")

    if isinstance(weights_data[key], dict):
        options = list(map(int, weights_data[key].keys()))
        weight_values = list(weights_data[key].values())

    elif isinstance(weights_data[key], list):
        options = [entry["mix"] for entry in weights_data[key]]
        weight_values = [entry["weight"] for entry in weights_data[key]]

    else: # weights_data is an unsupported type
        logger.error("weights_data[%s] is type: %s. must be a dict or list", key, type(weights_data[key]).__name__)
        raise Exception(f"ERROR- logic.py: weighted_choice: weights_data[{key}] is an unsupported type")

    if not options or len(options) != len(weight_values):
        if variable is not None and caller is not None:
            logger.debug("weighted_choice failed for %s assignment in %s", variable, caller)
        logger.error("options empty or options/weight_value mismatch \noptions: %s \nweight_values: %s", options, weight_values)
        raise Exception("ERROR- logic.py: weighted_choice: options empty or options/weight_values mismatch")

    choice = random.choices(options, weights=weight_values, k=1)[0]

    logger.debug(
        "weighted choice for %s assignment in %s \nkey=&s \nweights=&s \nchoice=%s",
        variable, caller, key, options, weight_values, choice
    )
    return choice


def choose_subject_count():
    return weighted_choice(GlobalState.weights_data, "subject_count", variable="subject_count", caller="choose_subject_count")


def choose_description_count(subject_count):
    subject_count = int(subject_count)
    key = f"{subject_count}subj_desc_count"
    return weighted_choice(GlobalState.weights_data, key, variable="desc_count", caller="choose_description_count")


# Returns a mix of 2 descriptions for 2 subjects based on weights.json rule
def decide_2_2_mix():
    desc_mix = weighted_choice(GlobalState.weights_data, "2subj_2desc_mix", variable="desc_mix", caller="decide_2_2_mix")
    return ["xy"] * desc_mix[0] + ["x"] * desc_mix[1]


# Returns a mix of 3 descriptions for 3 subjects 
def decide_3_3_mix():
    desc_mix = weighted_choice(GlobalState.weights_data, "3subj_3desc_mix", variable="desc_mix", caller="decide_3_3_mix")
    return ["xy"] * desc_mix[0] + ["x"] * desc_mix[1]


# Returns a mix of 4 descriptions for 3 subjects 
def decide_3_4_mix():
    desc_mix = weighted_choice(GlobalState.weights_data, "3subj_4desc_mix", variable="desc_mix", caller="decide_3_4_mix")
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
    logger.debug(
        "description type(s) mix: %s xy, %s x",
        mix.count("xy"),
        mix.count("x")
    )

    return mix() if callable(mix) else mix


# Creates constraints for subject selection based on the description mix
def get_constraints(subject_count, desc_mix):
    constraints = []

    if desc_mix.count("xy") >= 2:
        constraints.append("xy_unique")
    
    if desc_mix.count("x") > 1 and subject_count > 1:
        constraints.append("x_balance")
    
    logger.debug(
        "subject selection constraints=%s", 
        "none" if constraints == [] else constraints
    )

    return constraints


# Assigns subjects (e.g. s1) from candidate_subjects to each description in desc_plan
# adds list of chosen subjects to the description's entry in grammar_plan
# Need to re-evaluate later. can still choose a candidate for an x desc that was used as x in xy desc
def enforce_constraints(desc_plan, grammar_plan, constraints, candidate_subjects):
    # Tracks candidate chosen as x in xy descriptions to enforce xy_unique constraint
    xy_unique_list = []

    # Same for x description and x_balance constraint
    x_balance_list = []

    logger.info("pairing subjects with descriptions: constraints=%s", constraints)
    for desc_key, desc_data in desc_plan.items():
        # Temp list to remove entries from candidate_subjects so the same subj isn't chosen
        # for x and y for an xy desc
        temp_candidates_xy = candidate_subjects.copy()
        
        logger.debug("%s: type=%s", desc_key, desc_data["type"])
        
        if desc_data["type"] == "xy":
            # choose 1st subject for the xy desc
            # If xy_unique constaint ids active, only accept choices that haven't already been chosen
            while True:
                rand_selection = random.randrange(len(temp_candidates_xy))
                x_choice = temp_candidates_xy[rand_selection]
                if x_choice not in xy_unique_list:
                    # Remove x_choice so the same exact subj isn't chosen for y_choice
                    temp_candidates_xy.pop(rand_selection)
                    break

            if "xy_unique" in constraints:
                xy_unique_list.append(x_choice)
            
            # Choose 2nd subject
            rand_selection = random.randrange(len(temp_candidates_xy))
            y_choice = temp_candidates_xy[rand_selection]

            logger.debug("  subjects chosen: %s, %s", x_choice, y_choice)

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


            logger.debug("  subject chosen: %s", x_choice)

            # Add choice to grammar_plan
            grammar_plan[desc_key]["subjects"] = [x_choice]
    logger.info("subject pairing complete")
    logger.debug("  grammar_plan after pairing: %s", grammar_plan)