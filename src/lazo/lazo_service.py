from typing import Optional, List
from datasketch import MinHashLSHEnsemble
from models.column_sketch import ColumnSketch
from models.dataset_sketch import DatasetSketch
from models.join_candidate import JoinCandidate

class LAZOService:
    def __init__(self, containment_threshold: float = 0.7, num_part: int = 32):
        self.threshold = containment_threshold
        self.num_part = num_part
        self.ensemble = MinHashLSHEnsemble(
            threshold=containment_threshold, num_part=num_part
        )
        self._staged_records = []
        self._registered_datasets = set()

    def stage_column(
        self,
        col_sketch: ColumnSketch,
        dataset_id: str = "standalone",
    ) -> None:
        """Stage a single ColumnSketch for indexing."""
        composite_key = f"{dataset_id}::{col_sketch.column_name}"
        cardinality = int(col_sketch.hll.count())
        self._staged_records.append(
            (composite_key, col_sketch.minhash, cardinality)
        )

    def stage_dataset(self, dataset_sketch: DatasetSketch) -> None:
        """Stage all columns inside a DatasetSketch."""
        if dataset_sketch.dataset_id in self._registered_datasets:
            raise ValueError("This dataset has already been registered.")
        for col_sketch in dataset_sketch.column_sketches.values():
            self.stage_column(
                col_sketch=col_sketch, dataset_id=dataset_sketch.dataset_id
            )
        self._registered_datasets.add(dataset_sketch.dataset_id)

    def build_index(self) -> None:
        """Indexes all accumulated dataset sketches."""
        if self._staged_records:
            self.ensemble.index(self._staged_records)

    def find_joinable_columns(
        self,
        query_sketch: ColumnSketch,
        query_dataset_id: Optional[str] = None,
    ) -> List[JoinCandidate]:
        """Finds joinable columns across the lake.

        Parameters:
        -----------
        query_sketch : ColumnSketch
            The sketch of the column you want to search for.
        query_dataset_id : Optional[str]
            If provided, filters out self-joins from the same dataset. Pass
            None for one-off standalone columns.
        """
        query_size = int(query_sketch.hll.count())
        if query_size == 0:
            return []

        # Query the ensemble with (MinHash, size)
        raw_matches = self.ensemble.query(
            query_sketch.minhash, query_size
        )

        candidates = []
        for key in raw_matches:
            ds_id, col_name = key.split("::", 1)

            # Skip self-joins if a dataset_id was provided
            if query_dataset_id and ds_id == query_dataset_id:
                continue

            candidates.append(
                JoinCandidate(
                    target_dataset_id=ds_id, 
                    target_column_name=col_name,
                    query_dataset_id=query_dataset_id,
                    query_column_name=query_sketch.column_name,
                )
            )

        return candidates