from models.dataset_sketch import DatasetSketch
from models.column_sketch import ColumnSketch

def _is_continuous_float(val: str | int | float) -> bool:
    """Returns True if val is a continuous decimal float (e.g., '12.34', 12.34)."""
    try:
        num = float(val)
        # num.is_integer() returns True for 100.0 or 100, False for 12.34
        return not num.is_integer()
    except (ValueError, TypeError):
        # Not a parseable number (e.g., standard text string)
        return False

class DatasetSketchProcessor:
    @staticmethod
    def process_generator(
        dataset_id: str,
        candidate_cols: dict,
        socrata_generator,
        min_threshold=50
    ) -> DatasetSketch:

        text = candidate_cols.get("text", set())
        number = candidate_cols.get("number", set())

        active_sketches = {
            col: ColumnSketch(column_name=col) for col in text | number
        }

        for row in socrata_generator:
            for col in list(active_sketches.keys()):
                val = row.get(col)
                if val is None:
                    continue

                if col in number and _is_continuous_float(val):
                    del active_sketches[col]
                    continue

                active_sketches[col].update(val)

        final_sketches = {
            col: sketch
            for col, sketch in active_sketches.items()
            if sketch.rows_processed >= min_threshold
        }

        return DatasetSketch(
            dataset_id=dataset_id, column_sketches=final_sketches
        )
