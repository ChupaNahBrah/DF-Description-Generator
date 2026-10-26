# Logic for selecting subjects/descriptions
from ..data.loader import GlobalState
from ..data.filters import subject_filter_by_tag, filter_categories_for_tag, subject_filter_by_subcategory_tag
from .logic import assign_subjects_to_descriptions
from collections import defaultdict
import random
import logging
logger = logging.getLogger(__name__)

# Generate quantities for each subject, respecting any min/max requirements.
# Need to update if quantity requirements change
def decide_subject_quantities(grammar_plan):
    logger.info("generating subject quantities")
    
    for subj_key, id in grammar_plan["chosen_subject_ids"].items():
        # Sets minimum quantity to requirement or 1 if there isn't one
        # Need to update if x_min/max or y_max is introduced
        for desc_data in grammar_plan.values():
            if (
                "subjects" in desc_data
                and len(desc_data["subjects"]) > 1
                and desc_data["subjects"][1] == subj_key
            ):
                min_quantity = desc_data.get("y_min_quantity")
                break
            else:
                min_quantity = 1

        if "subj_quantities" not in grammar_plan:
            grammar_plan["subj_quantities"] = {}

        subj_quantity = random.randint(min_quantity,5)
        logger.debug(
            "generated quantity for subject %r: quantity=%s min_quantity=%s max=%s",
            subj_key, subj_quantity, min_quantity, 5
        )
        grammar_plan["subj_quantities"][subj_key] = subj_quantity
    logger.info("generated subject quantities: %r", grammar_plan["subj_quantities"])


def choose_subject_ids(desc_plan, grammar_plan):
    logger.info("choosing IDs for subjects in grammar_plan")
    logger.debug("number of subjects=%s", len(grammar_plan["chosen_subject_ids"]))
    
    # Choose subject IDs for each subject
    for desc_key, desc_data in grammar_plan.items():
        if not desc_key.startswith("desc_"):
            continue

        if desc_data["type"] == "x":
            required_tags = desc_plan[desc_key]["required_tags"]
            disallowed_tags = desc_plan[desc_key]["disallowed_tags"]
            subject_key = desc_data["subjects"][0]
            logger.debug("choosing ID for %s", subject_key)

            filtered_categories = filter_categories_for_tag(required_tags, disallowed_tags)
            category_choice = random.choice(list(filtered_categories.keys()))
            subcategory_choice = random.choice(list(filtered_categories[category_choice]))
            
            options = subject_filter_by_subcategory_tag(subcategory_choice, required_tags, disallowed_tags)
            chosen_id = random.choice(options)
            logger.debug(
                "selected id for %r: id=%s, category=%r, subcategory=%r, filtered options=%r",
                subject_key, chosen_id, category_choice, subcategory_choice, len(options)
            )
            grammar_plan["chosen_subject_ids"][subject_key] = chosen_id

        if desc_data["type"] == "xy":            
            # Id for 1st subject (x)
            required_tags_x = desc_plan[desc_key]["required_tags_x"]
            subject_key = desc_data["subjects"][0]
            logger.debug("choosing ID for %s", subject_key)
            
            filtered_categories = filter_categories_for_tag(required_tags_x)
            category_choice = random.choice(list(filtered_categories.keys()))
            subcategory_choice = random.choice(list(filtered_categories[category_choice]))
            
            options = subject_filter_by_subcategory_tag(subcategory_choice, required_tags_x)
            chosen_id = random.choice(options)
            logger.debug(
                "selected id for %r: id=%s, category=%r, subcategory=%r, filtered options=%r",
                subject_key, chosen_id, category_choice, subcategory_choice, len(options)
            )
            grammar_plan["chosen_subject_ids"][subject_key] = chosen_id

            # Id for 2nd subject (y)
            required_tags_y = desc_plan[desc_key]["required_tags_y"]
            disallowed_tags_y = desc_plan[desc_key]["disallowed_tags_y"]
            subject_key = desc_data["subjects"][1]
            logger.debug("choosing ID for %r", subject_key)
            
            filtered_categories = filter_categories_for_tag(required_tags_y, disallowed_tags_y)
            category_choice = random.choice(list(filtered_categories.keys()))
            subcategory_choice = random.choice(list(filtered_categories[category_choice]))
            
            options = subject_filter_by_subcategory_tag(subcategory_choice, required_tags_y, disallowed_tags_y)
            chosen_id = random.choice(options)
            logger.debug(
                "selected id for %r: id=%s, category=%r, subcategory=%r, filtered options=%r",
                subject_key, chosen_id, category_choice, subcategory_choice, len(options)
            )
            grammar_plan["chosen_subject_ids"][subject_key] = chosen_id

    # Populate any subject IDs that have yet to be selected (or for when there are 0 descriptions)
    for subject_key, subject_id in grammar_plan["chosen_subject_ids"].items():
        if subject_id == 0:
            logger.debug("choosing ID for %s", subject_key)
            
            filtered_categories = filter_categories_for_tag()
            category_choice = random.choice(list(filtered_categories.keys()))
            subcategory_choice = random.choice(list(filtered_categories[category_choice]))
            
            options = subject_filter_by_subcategory_tag(subcategory_choice)
            chosen_id = random.choice(options)
            logger.debug(
                "selected id for %r: id=%s, category=%r, subcategory=%r, filtered options=%r",
                subject_key, chosen_id, category_choice, subcategory_choice, len(options)
            )
            grammar_plan["chosen_subject_ids"][subject_key] = chosen_id
    logger.info("selected subject IDs: %r", grammar_plan["chosen_subject_ids"])


# Creates grammar_plan which is passed to grammar.py for final sentence construction
# if desc_plan empty (or not fully populated ie. 1 sub and 0 desc), manually set up s1.
# First, creates grammar_plan dict that contains all data needed for sentence construction
# Then, matches subjects to description
def build_grammar_plan(desc_plan, constraints, subject_count):
    logger.info("building grammar_plan and pairing subject placeholders with descriptions")
    logger.debug("subj count=%s, description count=%s, constraints=%s", subject_count, len(desc_plan), constraints)
    grammar_plan = defaultdict(dict)
    
    for key, desc_data in desc_plan.items():
        # Start populating grammar_plan with available data from desc_plan
        grammar_plan[key] = {
            "type": desc_data["type"],
            "desc_id": desc_data["desc_id"]
        }
        logger.debug("added %s to grammar_plan; type=%s, desc_id=%s", key, desc_data["type"], desc_data["desc_id"])

        # Need to update if quantity requirements change
        # Copies quantity requirements from desc_plan to grammar_plan since choose_subject_ids() uses only grammar_plan
        if "y_min_quantity" in desc_data.keys():
            grammar_plan[key]["y_min_quantity"] = desc_data["y_min_quantity"]
            logger.debug("  y_min_quantity=%s", desc_data["y_min_quantity"])

    # List of subjects ["s1", "s2", ...] - Will be used to pair subjects with descriptions
    candidate_subjects = []
    for i in range(subject_count):
        subj_key = f"s{i+1}"
        candidate_subjects.append(subj_key)
        # Add spot for chosen subj IDs. default 0 as they haven't been chosen yet
        grammar_plan["chosen_subject_ids"][subj_key] = 0
    logger.debug("candidate subjects created: %s", candidate_subjects)
    logger.debug("initialized chosen subject placeholders: %s", grammar_plan["chosen_subject_ids"])

    assign_subjects_to_descriptions(desc_plan, grammar_plan, constraints, candidate_subjects)
    
    logger.info("created grammar_plan with %s descriptions and %s subjects", sum(1 for k in grammar_plan if k.startswith("desc_")), len(grammar_plan["chosen_subject_ids"]))
    logger.debug("grammar_plan: %s", grammar_plan)
    return grammar_plan


# Chooses specific descriptions to use for each description in desc_mix
# Also creates desc_plan to pass to select_subjects_for_descriptions()
def build_description_plan(desc_mix):
    logger.info("selecting descriptions")
    desc_plan = defaultdict(dict)
    
    if not desc_mix:
        logger.info("no descriptions to select. desc_plan is empty")
        return desc_plan

    used_desc_ids = []
    desc_counter = 1

    # Iterate through the mix of descriptions and choose a description for it
    for description in desc_mix:
        if description == "x":
            # Randomly select an x description that hasn't already been used
            while True:
                desc_entry = random.choice(list(GlobalState.index["x_descriptions"].values()))
                if desc_entry["desc_id"] not in used_desc_ids:
                    break
            
            used_desc_ids.append(desc_entry["desc_id"])

            required_tags = desc_entry.get("required_tags", [])
            disallowed_tags = desc_entry.get("disallowed_tags", [])
            
            logger.debug(
                "selected desc %s/%s: type=x id=%s required_tags=%s disallowed_tags=%s", 
                desc_counter, len(desc_mix), desc_entry["desc_id"], required_tags, disallowed_tags
            )

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

            logger.debug(
                "selected desc %s/%s: type=xy id=%s required_tags_x=%s required_tags_y=%s disallowed_tags_y=%s y_min_quantity=%s", 
                desc_counter, len(desc_mix), desc_entry["desc_id"], required_tags_x, required_tags_y, disallowed_tags_y, y_min_quantity
            )
            
            desc_plan[f"desc_{desc_counter}"] = {
                "type": "xy", 
                "desc_id": desc_entry["desc_id"], 
                "required_tags_x": required_tags_x, 
                "required_tags_y": required_tags_y,
                "disallowed_tags_y": disallowed_tags_y,
                "y_min_quantity": y_min_quantity
            }

        desc_counter += 1
    logger.info("created desc_plan with %s descriptions", len(desc_plan))
    return desc_plan