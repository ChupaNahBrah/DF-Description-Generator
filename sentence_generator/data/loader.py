# Loads JSON files with subjects and descriptions

import os
import json
from collections import defaultdict

# Path to resource folder
RESOURCE_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'resources')

class GlobalState:
    # Data structures for the loaded data to be stroed in memory
    # Master subject dictionary: ID → subject data
    all_subjects = {}

    # categories is a dict containing sets of all subcategories contained in each category found in the JSON files
    # subcat and tags are dicts mapping filters to lists of IDs 
    # e.g. subcategories["plants_trees"] -> list of all tree IDs
    # tags also stores subcategory and tags meta data for the subjects to use in filtering
    # e.g. tags["creatures"] -> list of dicts containing IDs, tags, and subcat for each subject that has the creatures tag
    index = {
        "categories": defaultdict(set), 
        "subcategories": defaultdict(list),
        "tags": defaultdict(list),
        "x_descriptions": defaultdict(list),
        "xy_descriptions": defaultdict(list)
    }

    # Weight map dict
    weights_data = {}


# Repeatable function to clear existing data if needed
def clear_indexes():
    GlobalState.all_subjects.clear()

    for key in GlobalState.index:
        if isinstance(GlobalState.index[key], (dict, defaultdict)):
            GlobalState.index[key].clear()


# Loads all subjects from JSON files in the 'resources' folder.
# Builds the flat subject list and indexes bycategory, subcategory, and tags.
def load_subjects():
    _valid_prefixes = ("creatures", "objects", "plants", "shapes")

    # Iterate through all files in the resources folder    
    for filename in os.listdir(RESOURCE_FOLDER):
        # Skip all non-subject files
        if not filename.endswith('.json') or not filename.startswith(_valid_prefixes):
            continue
        
        filepath = os.path.join(RESOURCE_FOLDER, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error reading {filename}: {e}")
                continue
            
            # Iterate through each entry in the current subject file
            for current_subj in data:
                current_subj_id = current_subj["id"]

                # Add current subject to master subjects list
                GlobalState.all_subjects[current_subj_id] = current_subj
                
                # Populate category -> subcat map based on JSON file
                current_subj_cat = current_subj["category"]
                current_subj_subcat = current_subj["subcategory"]
                GlobalState.index["categories"][current_subj_cat].add(current_subj_subcat)
                
                # Map subcat -> list of IDs
                GlobalState.index["subcategories"][current_subj_subcat].append(current_subj_id)

                # Multi-level dict tag_name: [{id: id#, tags: [tags], subcategory: subcat_name}, {...}]
                current_subj_tags = current_subj['tags']
                for tag in current_subj["tags"]:
                    GlobalState.index["tags"][tag].append({"id": current_subj_id, "tags": current_subj_tags, "subcategory": current_subj_subcat})


def load_descriptions():
    _valid_prefixes = ("x_descriptions", "xy_descriptions")

    for filename in os.listdir(RESOURCE_FOLDER):
        if not filename.endswith('.json') or not filename.startswith(_valid_prefixes):
            continue

        filepath = os.path.join(RESOURCE_FOLDER, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error reading {filename}: {e}")
                continue

            if filename.startswith("x_descriptions"):
                
                for current_desc in data:
                    current_desc_id = current_desc["desc_id"]

                    GlobalState.index["x_descriptions"][current_desc_id] = current_desc
            
            if filename.startswith("xy_descriptions"):
                
                for current_desc in data:
                    current_desc_id = current_desc["desc_id"]

                    GlobalState.index["xy_descriptions"][current_desc_id] = current_desc


def load_weights():
    RESOURCE_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources')
    filename = "weights.json"
    filepath = os.path.join(RESOURCE_FOLDER, filename)
    #print(f"LOADER-weights: Attempting to load weights from {filepath}\n")

    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            GlobalState.weights_data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error reading {filename}: {e}")
    #print(f"LOADER-weights: Loaded data keys: {list(GlobalState.weights_data.keys())}\n")


# Return the subject dict for a given ID. Unless it's not found which gives an error
def get_subject_by_id(subj_id):
    if subj_id not in GlobalState.all_subjects:
        raise KeyError(f"LOADER-get_subjects_by_id: Subject ID '{subj_id}' not found.") # Change later to a log and pass empty list
    return GlobalState.all_subjects.get(subj_id) 


# Returns list of suitable subj IDs of a specified tag, or raises an error
def filter_subjects_by_tag(tag):
    if tag not in GlobalState.index["tags"]:
        raise KeyError(f"LOADER-filter_subjects_by_tag: Tag '{tag}' not found.") # Change later to a log and pass empty list
    return GlobalState.index["tags"].get(tag)

'''
clear_indexes()
load_subjects()
load_descriptions()
print("📁 Categories (with their subcategories):")
for cat, subcats in index["categories"].items():
    print(f"  {cat}: {list(subcats)}")

print("\n📁 Subcategories (with subject IDs):")
for subcat, ids in index["subcategories"].items():
    print(f"  {subcat}: {ids[:3]}{'...' if len(ids) > 3 else ''}")  # show up to 3 IDs

print("\n🏷️ Tags (with subject metadata):")
for tag, entries in index["tags"].items():
    example = entries[0] if entries else None
    print(f"  {tag}: {example}")

print("\n📝 X Descriptions:")
for desc_id, desc in list(index["x_descriptions"].items())[:3]:
    print(f"  ID {desc_id}: {desc['text']}")

print("\n🔁 XY Descriptions:")
for desc_id, desc in list(index["xy_descriptions"].items())[:3]:
    print(f"  ID {desc_id}: {desc['text']}")
'''