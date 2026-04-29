# Handles full sentence generation pipeline
# TODO: verify select_descriptions doesn't reuse desc_ids. same for selecting subjs
# TODO: fix filters.filter_categories_for_tag()
# TODO: fix selector.choose_subject_ids()
from ..data.loader import (
    reset_runtime_state,
    load_subjects,
    load_descriptions,
    load_weights
)
from .logic import (
    choose_subject_count,
    choose_description_count,
    decide_description_mix,
    get_constraints
)
from .selector import (
    select_descriptions,
    select_subjects_for_descriptions,
    choose_subject_ids,
    decide_subject_quantities
)
from .grammar import (
    populate_sentence_data,
    format_sentence
)


def load_data():
    reset_runtime_state()
    load_subjects()
    load_descriptions()
    load_weights()

def generate_sentence():
    subject_count = choose_subject_count()
    description_count = choose_description_count(subject_count)
    desc_mix = decide_description_mix(subject_count, description_count)
    constraints = get_constraints(subject_count, desc_mix)

    print("GEN-Subject count:", subject_count)
    print("GEN-Description count", description_count)
    print("GEN-Description mix:", desc_mix)
    print("GEN-Constraints:", constraints)

    desc_plan = select_descriptions(desc_mix)
    grammar_plan = select_subjects_for_descriptions(desc_plan, constraints, subject_count)
    choose_subject_ids(desc_plan, grammar_plan)
    decide_subject_quantities(grammar_plan)

    print("GEN-desc_plan: \n",desc_plan)
    print("GEN-grammar_plan: \n",grammar_plan)

    sentence_data = populate_sentence_data(grammar_plan)
    sentence = format_sentence(grammar_plan, sentence_data)

    return sentence

if __name__ == "__main__":
    load_data()
    print(generate_sentence())