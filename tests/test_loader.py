from sentence_generator.data.loader import (
    reset_runtime_state,
    load_subjects,
    load_descriptions,
    load_weights,
    GlobalState
)

def test_loader_loads_runtime_data():
    reset_runtime_state()
    load_subjects()
    load_descriptions()
    load_weights()

    assert len(GlobalState.all_subjects) > 0
    assert len(GlobalState.index["categories"]) > 0
    assert len(GlobalState.index["subcategories"]) > 0
    assert len(GlobalState.index["tags"]) > 0
    assert len(GlobalState.index["x_descriptions"]) > 0
    assert len(GlobalState.index["xy_descriptions"]) > 0
    assert len(GlobalState.weights_data) > 0

def test_reset_runtime_state_clears_loaded_data():
    load_subjects()
    load_descriptions()
    load_weights()
    reset_runtime_state()

    assert len(GlobalState.all_subjects) == 0
    assert len(GlobalState.index["categories"]) == 0
    assert len(GlobalState.index["subcategories"]) == 0
    assert len(GlobalState.index["tags"]) == 0
    assert len(GlobalState.index["x_descriptions"]) == 0
    assert len(GlobalState.index["xy_descriptions"]) == 0
    assert len(GlobalState.weights_data) == 0