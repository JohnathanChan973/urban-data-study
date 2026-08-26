from dataclasses import dataclass
from typing import Optional

@dataclass
class JoinCandidate:
    target_dataset_id: str
    target_column_name: str
    similarity_score: Optional[float] = None