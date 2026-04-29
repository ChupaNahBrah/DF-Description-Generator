# Loads JSON files with subjects and descriptions

from pathlib import Path
import json
from collections import defaultdict

# Path to resource folder
RESOURCE_DIR = Path(__file__).resolve().parent.parent / "resources"

# Data structures for the loaded data to be stroed in memory
class GlobalState:
    # Master subject dictionary: ID → subject data
    all_subjects = None

    # categories is a dict containing set/lists of all subcategories contained in each category found in the JSON files
    # subcat and tags are dicts mapping filters to lists of IDs 
    # e.g. subcategories["plants_trees"] -> list of all tree IDs
    # tags also stores subcategory and tags meta data for the subjects to use in filtering
    # e.g. tags["creatures"] -> list of dicts containing IDs, tags, and subcategories for each subject that has the creatures tag
    index = None

    # Weight map dict
    weights_data = None


# Initializes or resets all runtime data containers.
def reset_runtime_state():
    GlobalState.all_subjects = {}
    GlobalState.weights_data = {}

    GlobalState.index = {
        "categories": defaultdict(set), 
        "subcategories": defaultdict(list),
        "tags": defaultdict(dict),
        "x_descriptions": defaultdict(list),
        "xy_descriptions": defaultdict(list)
    }


# Loads all subjects from JSON files in the 'resources' folder.
# Builds the flat subject list and indexes bycategory, subcategory, and tags.
def load_subjects():
    _valid_prefixes = ("creatures", "objects", "plants", "shapes")
 
    for filepath in RESOURCE_DIR.iterdir(): 
        # Skip all non-subject files
        if filepath.suffix != ".json" or not filepath.name.startswith(_valid_prefixes):
            continue
        
        with filepath.open("r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error reading {filepath.name}: {e}")
                continue
            
            # Iterate through each entry in the current subject file
            for current_subj in data:
                current_subj_id = current_subj["id"]

                # Add current subject to all_subjects (subject_id → full subject data)
                GlobalState.all_subjects[current_subj_id] = current_subj
                
                # Map category → set(subcategories)
                current_subj_cat = current_subj["category"]
                current_subj_subcat = current_subj["subcategory"]
                GlobalState.index["categories"][current_subj_cat].add(current_subj_subcat)
                
                # Map subcategory → list(subject IDs in subcat)
                GlobalState.index["subcategories"][current_subj_subcat].append(current_subj_id)

                # Multi-level dict tag_name: [{id: id#, tags: [tags], subcategory: subcat_name}, {...}]
                current_subj_tags = current_subj['tags']
                for tag in current_subj["tags"]:
                    GlobalState.index["tags"][tag][current_subj_id] = {
                        "id": current_subj_id,
                        "tags": current_subj_tags,
                        "subcategory": current_subj_subcat}


def load_descriptions():
    _valid_prefixes = ("x_descriptions", "xy_descriptions")

    for filepath in RESOURCE_DIR.iterdir():
        if filepath.suffix != ".json" or not filepath.name.startswith(_valid_prefixes):
            continue

        with filepath.open("r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error reading {filepath.name}: {e}")
                continue

            if filepath.name.startswith("x_descriptions"):
                
                for current_desc in data:
                    current_desc_id = current_desc["desc_id"]

                    GlobalState.index["x_descriptions"][current_desc_id] = current_desc
            
            if filepath.name.startswith("xy_descriptions"):
                
                for current_desc in data:
                    current_desc_id = current_desc["desc_id"]

                    GlobalState.index["xy_descriptions"][current_desc_id] = current_desc


def load_weights():
    filename = "weights.json"
    filepath = RESOURCE_DIR / filename

    #print(f"LOADER-weights: Attempting to load weights from {filepath}\n")

    with filepath.open("r", encoding="utf-8") as f:
        try:
            GlobalState.weights_data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error reading {filename}: {e}")
    #print(f"LOADER-weights: Loaded data keys: {list(GlobalState.weights_data.keys())}\n")



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
