from models.column_sketch import ColumnSketch

def test_update():
    sketch = ColumnSketch("asdf")
    sketch.update("asdf")
    assert sketch.rows_processed == 1

def test_minhash():
    sketch1 = ColumnSketch("asdf")
    sketch1.update("asdf")
    sketch2 = ColumnSketch("qwerty")
    sketch2.update("asdf")
    assert sketch1.jaccard_similarity(sketch2) == 1