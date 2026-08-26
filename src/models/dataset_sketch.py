from dataclasses import dataclass, field
from typing import Dict
from models.column_sketch import ColumnSketch

@dataclass
class DatasetSketch:
    dataset_id: str
    column_sketches: Dict[str, ColumnSketch] = field(default_factory=dict)

    @property
    def total_columns(self) -> int:
        return len(self.column_sketches) 

    def compare(
        self, other: "DatasetSketch", threshold: float = 0.5
    ) -> list[dict]:
        """Compares all columns in this dataset against all columns in another dataset.

        Returns matching column pairs that meet or exceed the similarity
        threshold.
        """
        matches = []

        # Avoid self-comparison if accidentally passed the same dataset
        if self.dataset_id == other.dataset_id:
            return matches

        for col_name_a, sketch_a in self.column_sketches.items():
            for col_name_b, sketch_b in other.column_sketches.items():
                js = sketch_a.jaccard_similarity(sketch_b)

                if js >= threshold:
                    matches.append(
                        {
                            "left_dataset": self.dataset_id,
                            "left_column": col_name_a,
                            "right_dataset": other.dataset_id,
                            "right_column": col_name_b,
                            "jaccard_similarity": js,
                        }
                    )

        return matches