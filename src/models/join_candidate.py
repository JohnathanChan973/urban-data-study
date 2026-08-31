from dataclasses import dataclass
from typing import Optional

@dataclass
class JoinCandidate:    
    target_dataset_id: str
    target_column_name: str
    query_dataset_id: Optional[str] = None
    query_column_name: Optional[str] = None
    similarity_score: Optional[float] = None