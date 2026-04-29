# Applies tag-based filtering

# list_of_available_subcats = set(entry["subcategory"] for entry in _index["tags"][tag to lookup])

from ..data.loader import GlobalState
from collections import defaultdict

# Filters and adds subjects to a list that have the specified tag, excluding any disallowed tags
def subject_filter_by_tag(tag_filter, excluded_tags):
    filtered_list = []

    for subject in GlobalState.index["tags"][tag_filter].values():
        # Exclude from the filter any subject that has any tags that are prohibited
        if not any(tag in subject["tags"] for tag in excluded_tags):
            filtered_list.append(subject)
    
    return filtered_list


def filter_categories_for_tag(tag_filter=None, excluded_tags=None):
    '''
    Build a filtered category → subcategory mapping, based on included and excluded tags.
    Subcategories will be all subcategories seen in the list of subjects filtered by tags.

    Args:
        tag_filter (str or list[str]): Tag or list of tags that subjects must have
        excluded_tags (list[str]): Tags that disqualify a subject

    Returns:
        filtered_category_dict[category, set[subcategories]]: Filtered mapping of categories to subcategories
    '''
    # Ensure tag_filter is a list for unified processing
    if isinstance(tag_filter, str):
        tag_filter = [tag_filter]

    filtered_subcategory_list = set()
    filtered_category_dict = defaultdict(set)

    # ─────────────────────────────────────
    # Collect all subject IDs matching any required tag
    # ─────────────────────────────────────
    tag_filter = tag_filter or [] # No required tags if falsy
    excluded_tags = excluded_tags or [] # Consider all tags if falsy
    
    # Early exit if there are no requirements for the filter -> use the default category map
    if not tag_filter and not excluded_tags:
        return GlobalState.index["categories"]

    if tag_filter:
        subject_ids = set()
        for tag in tag_filter:
            subject_ids.update(GlobalState.index["tags"].get(tag, {}).keys())
    else:
        # No tag filter -> start with all tags
        subject_ids = set(GlobalState.all_subjects.keys())

    # ─────────────────────────────────────
    # Filter out subjects with excluded tags, collect valid subcategories
    # ─────────────────────────────────────
    for subject_id in subject_ids:
        subject = GlobalState.all_subjects[subject_id]

        # Exclude from the filter any subject that has any tags that are prohibited
        # "If none of the tags in excluded_tags are present in this subject's tag list"
        if not any(tag in subject["tags"] for tag in excluded_tags):
            filtered_subcategory_list.add(subject["subcategory"])
        
    # ─────────────────────────────────────
    # Rebuild filtered category → subcategory mapping
    # ─────────────────────────────────────
    for category, subcategories in GlobalState.index["categories"].items():
        for sub in subcategories:
            if sub in filtered_subcategory_list:
                filtered_category_dict[category].add(sub)

    return filtered_category_dict


# Filters and adds subjects to a list that have the specified tag, in the specified subcategory, 
# excluding any disallowed tags
def subject_filter_by_subcategory_tag(subcategory, tag_filter, excluded_tags):
    # Normalize args so the function can safely accept None, a single string, or a list.
    if tag_filter is None:
        tag_filter = []
    if isinstance(tag_filter, str):
        tag_filter = [tag_filter]
    if excluded_tags is None:
        excluded_tags = []
    if isinstance(excluded_tags, str):
        excluded_tags = [excluded_tags]
    
    
    filtered_list = []

    for candidate_id in GlobalState.index["subcategories"][subcategory]:
        candidate_dict = GlobalState.all_subjects[candidate_id]
        candidate_tags = candidate_dict["tags"]
        # If the possible candidate subject has all the required tags and none of the excluded ones
        if all(tag in candidate_tags for tag in tag_filter) and not any(tag in candidate_tags for tag in excluded_tags):
            filtered_list.append(candidate_id)

    return filtered_list