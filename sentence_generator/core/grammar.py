# Grammar and formatting utilities
from ..data.loader import GlobalState
from collections import defaultdict

def format_sentence(grammar_plan, sentence_data):
    """
    Format the final natural-language sentence based on subject descriptions and relations.

    Args:
        grammar_plan (dict): Contains raw structure info (desc_x entries, subject IDs, etc.).
        sentence_data (dict): Cleaned data from populate_sentence_data() with subject names,
            quantities, and pluralized descriptions.

    Returns:
        str: The fully formatted sentence string.
    """

    # ─────────────────────────────────────
    # Construct the initial subject line
    # ─────────────────────────────────────
    
    # Build a list like ["2 dwarves", "multiple wolves", "1 sword"]
    subject_chunks = []

    for subj_key, subject in sentence_data["subjects"].items():
        quantity = sentence_data["quantities"][subj_key]
        subject_chunks.append(f"{quantity} {subject}")
    
    # Format list with commas and "and"
    if len(subject_chunks) == 1:
        subject_line = f"The image is of {subject_chunks[0]}. "
    else:
        # Join all but last with commas, then add "and [last]"
        all_but_last = ", ".join(subject_chunks[:-1])
        subject_line = f"The image is of {all_but_last}, and {subject_chunks[-1]}. "    

    # ─────────────────────────────────────
    # Construct the description sentences
    # ─────────────────────────────────────
    description_lines = []

    for desc_key, desc_data in grammar_plan.items():
        # Skip all non-description entries
        if not desc_key.startswith("desc_"):
            continue

        description_text = sentence_data["descriptions"][desc_key]

        if desc_data["type"] == "xy":
            # Get both subject names
            subj1_key, subj2_key = desc_data["subjects"]
            subj1 = sentence_data["subjects"][subj1_key]
            subj2 = sentence_data["subjects"][subj2_key]

            # Format as: "The [subj1] [verb phrase] the [subj2]. "
            description_lines.append(f"The {subj1} {description_text} the {subj2}. ")

        elif desc_data["type"] == "x":
            # Get the single subject name
            subj_key = desc_data["subjects"][0]
            subj = sentence_data["subjects"][subj_key]

            # Format as: "The [subj] [verb phrase]. "
            description_lines.append(f"The {subj} {description_text}. ")

    # Combine all parts into one sentence
    sentence = subject_line + "".join(description_lines)
    return sentence


def populate_sentence_data(grammar_plan):
    """
    Build a simplified structure from grammar_plan to prepare for sentence formatting.

    Args:
        grammar_plan (dict): The raw planning data containing descriptions, subject IDs, and quantities.

    Returns:
        dict: Structured sentence_data with finalized description text, subject names, and readable quantities.
    """

    sentence_data = {
        "descriptions": {},
        "subjects": {},
        "quantities": {}
    }

    # ─────────────────────────────────────
    # Handle each description (desc_# keys)
    # ─────────────────────────────────────
    for grammar_key, grammar_data in grammar_plan.items():
        # Grab description text and add it to sentence_data.
        if grammar_key.startswith("desc_"):
            # First check if the grammar for the desc should be plural
            first_subj_key = grammar_data["subjects"][0]
            plurality = "plural" if grammar_plan["subj_quantities"][first_subj_key] > 1 else "singular"
            
            # Check if desc is x or xy for what index to look in
            desc_type = "x_descriptions" if grammar_data["type"] == "x" else "xy_descriptions"

            # Get the base description text from GlobalState
            desc_id = grammar_data["desc_id"]
            text = GlobalState.index[desc_type][desc_id]

            # Adjust verb for plurality ("is" → "are", etc.)
            if plurality == "plural":
                if text.startswith("is "):
                    text = text.replace("is ", "are ", 1)
                elif text.startswith("looks "):
                    text = text.replace("looks ", "look ", 1)

            # Store the final description
            sentence_data["descriptions"][grammar_key] = text

    # ─────────────────────────────────────
    # Replace subject IDs with their names
    # ─────────────────────────────────────
    for subj_key, id in grammar_plan["chosen_subject_ids"].items():
        plurality = "singular" if grammar_plan["subj_quantities"][subj_key] == 1 else "plural"
        sentence_data["subjects"][subj_key] = GlobalState.all_subjects[id][plurality]

    # ─────────────────────────────────────
    # Convert raw quantities to strings
    # ─────────────────────────────────────
    for subj_key, subj_quantity in grammar_plan["subj_quantities"].items():
        # Use "multiple" for quantities of 5
        quantity = str(subj_quantity) if subj_quantity < 5 else "multiple"
        sentence_data["quantities"][subj_key] = quantity

    return sentence_data

'''
grammar_plan = {
    "desc_1": {"type": "xy", "desc_id": 4, "subjects": ["s1", "s2"], "y_min_quantity": 3},
    "desc_2": {"type": "x", "desc_id": 2, "subjects": ["s3"]},
    "chosen_subject_ids": {"s1": 101, "s2": 102, "s3": 103},
    "subj_quantities": {"s1": 2, "s2": 4, "s3": 1}
}

sentence_data = {
    "descriptions": {"desc_1": "are fighting with"},
    "subjects": {"s1": "humans", "s2": "elves"},
    "quantities": {"s1":"2", "s2": "2"}
}'''