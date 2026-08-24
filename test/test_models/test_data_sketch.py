from lazo.dataset_sketch_process import DatasetSketchProcessor
from models.dataset_sketch import DatasetSketch

def test_process_generator():
    dataset_id = "asdf"
    candidate_cols = {"text": set(["asdf"]), "number": set(["qwerty", "zxcvb"])}
    test_rows = [
        {"asdf": "asdf", "qwerty": "31", "zxcvb": "3.1"}
    ]
    gen = iter(test_rows)
    result = DatasetSketchProcessor().process_generator(dataset_id, candidate_cols, gen, min_threshold=0)
    assert isinstance(result, DatasetSketch)
    assert result.total_columns == 2

def test_compare():
    id_1 = "qwerty"
    id_2 = "asdf"
    candidate_cols = {"text": set(["asdf"]), "number": set(["qwerty", "zxcvb"])}
    test_rows = [
            {"asdf": "asdf", "qwerty": "31", "zxcvb": "3.1"}
        ]
    gen1 = iter(test_rows)
    gen2 = iter(test_rows)
    sketch_1 = DatasetSketchProcessor().process_generator(id_1, candidate_cols, gen1, min_threshold=0)
    sketch_2 = DatasetSketchProcessor().process_generator(id_2, candidate_cols, gen2, min_threshold=0)
    result = sketch_1.compare(sketch_2)
    assert len(result) == 2 # Both columns should have perfect matches with each other (trivially)
    assert result[0].get("left_dataset") == id_1
    assert result[0].get("right_dataset") == id_2
    assert result[0].get("jaccard_similarity") == 1