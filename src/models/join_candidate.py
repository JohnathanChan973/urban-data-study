from dataclasses import dataclass

@dataclass
class JoinCandidate:
    target_dataset_id: str
    target_column_name: str