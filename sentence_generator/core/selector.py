# Logic for selecting subjects/descriptions
from ..data.loader import GlobalState
from ..data.filters import subject_filter_by_tag, filter_categories_for_tag, subject_filter_by_subcategory_tag
from .logic import enforce_constraints
from collections import defaultdict
import random

# Generate quantities for each subject, respecting any min/max requirements.
# Need to update if quantity requirements change
def decide_subject_quantities(grammar_plan):
    for subj_key, id in grammar_plan["chosen_subject_ids"].items():
        # Sets minimum quantity to requirement or 1 if there isn't one
        # Need to update if x_min/max or y_max is introduced
        min_quantity = next(
            (grammar_plan[desc_key].get("y_min_quantity")
             for desc_key, desc_data in grammar_plan.items()
             if "subjects" in desc_data
             and len(desc_data["subjects"]) > 1
             and desc_data["subjects"][1] == subj_key),
             1
        )

        if "subj_quantities" not in grammar_plan:
            grammar_plan["subj_quantities"] = {}

        subj_quantity = random.randint(min_quantity,5)
        grammar_plan["subj_quantities"][subj_key] = subj_quantity


def choose_subject_ids(desc_plan, grammar_plan):
    # Choose subject IDs for each subject
    for desc_key, desc_data in grammar_plan.items():
        if not desc_key.startswith("desc_"):
            continue

        if desc_data["type"] == "x":
            required_tags = desc_plan[desc_key]["required_tags"]
            disallowed_tags = desc_plan[desc_key]["disallowed_tags"]
            subject_key = desc_data["subjects"][0]

            filtered_categories = filter_categories_for_tag(required_tags, disallowed_tags)
            category_choice = random.choice(list(filtered_categories.keys()))
            subcategory_choice = random.choice(list(filtered_categories[category_choice]))
            
            options = subject_filter_by_subcategory_tag(subcategory_choice, required_tags, disallowed_tags)
            chosen_id = random.choice(options)
            grammar_plan["chosen_subject_ids"][subject_key] = chosen_id

        if desc_data["type"] == "xy":
            # Get requirements
            #required_tags_x = desc_plan[desc_key]["required_tags_x"]
            required_tags_y = desc_plan[desc_key]["required_tags_y"]
            #disallowed_tags_y = desc_plan[desc_key]["disallowed_tags_y"]
            
            # Id for 1st subject (x)
            subject_key = desc_data["subjects"][0]
            filtered_categories = filter_categories_for_tag(required_tags, disallowed_tags) # TODO: fix
            category_choice = random.choice(list(filtered_categories.keys()))
            subcategory_choice = random.choice(list(filtered_categories[category_choice]))
            
            options = subject_filter_by_subcategory_tag(subcategory_choice, required_tags, disallowed_tags)
            chosen_id = random.choice(options)
            grammar_plan["chosen_subject_ids"][subject_key] = chosen_id

            # Id for 2nd subject (y)
            subject_key = desc_data["subjects"][1]
            filtered_categories = filter_categories_for_tag(required_tags_y)
            category_choice = random.choice(list(filtered_categories.keys()))
            subcategory_choice = random.choice(list(filtered_categories[category_choice]))
            
            options = subject_filter_by_subcategory_tag(subcategory_choice, required_tags, disallowed_tags)
            chosen_id = random.choice(options)
            grammar_plan["chosen_subject_ids"][subject_key] = chosen_id


# TODO: only need to do candidate subjects if not desc_plan.
# if desc_plan empty (or not fully populated ie. 1 sub and 0 desc), manually set up s1.
# First, creates grammar_plan dict that contains all data needed for sentence construction
# Then, matches subjects to description
# Then, chooses the exact subjects from the subject index to use in the final sentence
def select_subjects_for_descriptions(desc_plan, constraints, subject_count):
    # This will be passed to grammar.py for final sentence construction
    grammar_plan = defaultdict(dict)
    
    for key, desc_data in desc_plan.items():
        # Start populating grammar_plan with available data from desc_plan
        grammar_plan[key] = {
            "type": desc_data["type"],
            "desc_id": desc_data["desc_id"]
        }

        # Need to update if quantity requirements change
        # Adds quantity requirements to grammar_plan from desc_plan since choose_subject_ids() uses only grammar_plan
        if "y_min_quantity" in desc_data.keys():
            grammar_plan[key]["y_min_quantity"] = desc_data["y_min_quantity"]

    # List of subjects ["s1", "s2", ...]
    # Will be passed to enforce constraints to match subjects to descriptions
    candidate_subjects = []
    for i in range(subject_count):
        subj_key = f"s{i+1}"
        candidate_subjects.append(subj_key)
        # Add spot for chosen subj IDs. default 0 as they haven't been chosen yet
        grammar_plan["chosen_subj_ids"][subj_key] = 0

    enforce_constraints(desc_plan, grammar_plan, constraints, candidate_subjects)
    
    choose_subject_ids(desc_plan, grammar_plan)

    return grammar_plan

    """
    get filtered list of subjects that match description tags and are not already used (if needed) from filters.py
    constraints applied in logic.py
    plan[f"desc_{desc_count}"] = {"type": "x", "desc_id": desc["id"]}
    """
    
# TODO: make desc plan work with 1 sub and 0 desc
# Chooses specific descriptions to use for each description in desc_mix
# Also creates a plan to pass to select_subjects_for_descriptions that facilitates 
# the enforcement of restrictions/constraints.
def select_descriptions(desc_mix):
    # This will be passed to select_subjects_for_description
    desc_plan = defaultdict(dict)
    
    if not desc_mix:
        return desc_plan

    used_desc_ids = []
    desc_counter = 1

    # Iterate through the mix of descriptions and choose a description for it
    for description in desc_mix:
        if description == "x":
            # Loop to choose a description that hasn't already been used
            while True:
                desc_entry = random.choice(list(GlobalState.index["x_descriptions"].values()))
                if desc_entry["desc_id"] not in used_desc_ids:
                    break
            
            used_desc_ids.append(desc_entry["desc_id"])

            required_tags = desc_entry.get("required_tags", [])
            disallowed_tags = desc_entry.get("disallowed_tags", [])
            
            desc_plan[f"desc_{desc_counter}"] = {
                "type": "x", 
                "desc_id": desc_entry["desc_id"], 
                "required_tags": required_tags, 
                "disallowed_tags": disallowed_tags
            }
        
        elif description == "xy":
            while True:
                desc_entry = random.choice(list(GlobalState.index["xy_descriptions"].values()))
                if desc_entry["desc_id"] not in used_desc_ids:
                    break
                    
            used_desc_ids.append(desc_entry["desc_id"])

            # Needs to be expanded if xy_desc constaints are changed
            required_tags_x = desc_entry.get("required_tags_x", [])
            required_tags_y = desc_entry.get("required_tags_y", [])
            disallowed_tags_y = desc_entry.get("disallowed_tags_y", [])
            y_min_quantity = desc_entry.get("y_min_quantity", 0)

            desc_plan[f"desc_{desc_counter}"] = {
                "type": "xy", 
                "desc_id": desc_entry["desc_id"], 
                "required_tags_x": required_tags_x, 
                "required_tags_y": required_tags_y,
                "disallowed_tags_y": disallowed_tags_y,
                "y_min_quantity": y_min_quantity
            }
        
        desc_counter += 1

    return desc_plan


# Pass this to grammar for sentence construction
'''
grammar_plan_eg = {
    "desc_1": {"type": "xy", "desc_id": 7, "subjects": ["s1", "s3"], "y_min_quantity": 2},
    "desc_2": {"type": "x", "desc_id": 8, "subjects": ["s2"]},
    "chosen_subj_ids": {"s1": 3, "s2": 4, "s3": 5}
}

desc_plan_eg = {
    "desc_1": {"type": "x", "desc_id": 7, "required_tags": ["creature"], "disallowed_tags": ["pointy"]},
    "desc_2": {"type": "x", "desc_id": 6, "required_tags": ["organic"], "disallowed_tags": ["pointy"]},
    "desc_3": {
        "type": "xy",
        "desc_id": 20,
        "required_tags_x": ["creature"],
        "required_tags_y": ["creature"],
        "disallowed_tags_x": ["pointy"],
        "disallowed_tags_y": ["pointy"]
    }
}'''