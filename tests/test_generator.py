from sentence_generator.core import generator
from sentence_generator.data.loader import GlobalState


def test_1subject_0descriptions(monkeypatch):
    generator.load_data()

    def set_subject_count():
        return 1

    def set_description_count(subject_count):
        return 0

    captured = {}
    original_populate = generator.populate_sentence_data

    def capture_sentence_data(grammar_plan):
        captured["grammar_plan"] = grammar_plan
        return original_populate(grammar_plan)

    monkeypatch.setattr(generator, "choose_subject_count", set_subject_count)
    monkeypatch.setattr(generator, "choose_description_count", set_description_count)
    monkeypatch.setattr(generator, "populate_sentence_data", capture_sentence_data)

    sentence = generator.generate_sentence()
    grammar_plan = captured["grammar_plan"]

    assert isinstance(sentence, str)
    assert len(grammar_plan["chosen_subject_ids"]) == 1
    assert not any(key.startswith("desc_") for key in grammar_plan)

    subject_text = sentence.strip().removeprefix("The image is of ").removesuffix(".")
    quantity_text, _, subject_name = subject_text.partition(" ")

    assert quantity_text in("1", "2", "3", "4", "multiple")
    
    plurality = "singular" if quantity_text == "1" else "plural"
    assert any(
        subject[plurality] == subject_name
        for subject in GlobalState.all_subjects.values()
    )


def test_3subject_1xy_description(monkeypatch):
    generator.load_data()

    def set_subject_count():
        return 3

    def set_description_count(subject_count):
        return 1

    captured = {}
    original_populate = generator.populate_sentence_data

    def capture_sentence_data(grammar_plan):
        captured["grammar_plan"] = grammar_plan
        return original_populate(grammar_plan)

    monkeypatch.setattr(generator, "choose_subject_count", set_subject_count)
    monkeypatch.setattr(generator, "choose_description_count", set_description_count)
    monkeypatch.setattr(generator, "populate_sentence_data", capture_sentence_data)

    sentence = generator.generate_sentence()
    grammar_plan = captured["grammar_plan"]

    assert isinstance(sentence, str)

    descriptions = [
        data
        for key, data in grammar_plan.items()
        if key.startswith("desc_")
    ]
    assert len(descriptions) == 1
    assert descriptions[0]["type"] == "xy"
    assert len(descriptions[0]["subjects"]) == 2
    assert len(set(descriptions[0]["subjects"])) == 2

    assigned_subjects = set()

    for key, data in grammar_plan.items():
        if key.startswith("desc"):
            for subject in data["subjects"]:
                assigned_subjects.add(subject)

    assert len(grammar_plan["chosen_subject_ids"]) == 3
    unreferenced_subjects = (
        set(grammar_plan["chosen_subject_ids"]) - assigned_subjects
    )
    assert len(unreferenced_subjects) == 1

    for subject_key in unreferenced_subjects:
        assert grammar_plan["chosen_subject_ids"][subject_key] in GlobalState.all_subjects
        assert 1 <= grammar_plan["subj_quantities"][subject_key] <= 5

    