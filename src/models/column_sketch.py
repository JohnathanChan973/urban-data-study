from dataclasses import dataclass, field
from datasketch import HyperLogLog, MinHash

@dataclass
class ColumnSketch:
    column_name: str
    num_perm: int = 128
    hll_precision: int = 10

    # Initialize sketches automatically upon creation
    minhash: MinHash = field(init=False)
    hll: HyperLogLog = field(init=False)
    rows_processed: int = 0

    def __post_init__(self):
        self.minhash = MinHash(num_perm=self.num_perm)
        self.hll = HyperLogLog(p=self.hll_precision)

    def update(self, val: str) -> None:
        """Cleans, encodes, and feeds a single value into both sketches."""
        clean_val = str(val).strip().lower().encode("utf-8")
        if clean_val:
            self.minhash.update(clean_val)
            self.hll.update(clean_val)
            self.rows_processed += 1

    def jaccard_similarity(self, other: "ColumnSketch") -> float:
        """Computes Jaccard Similarity between this column and another ColumnSketch."""
        return self.minhash.jaccard(other.minhash)