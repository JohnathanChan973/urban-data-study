import random
from typing import List, Optional, Tuple, Generator, Any

import faiss
import numpy as np
from pandas import DataFrame
from models.reservoir_sampler import ReservoirSampler
from models.join_candidate import JoinCandidate
from sentence_transformers import SentenceTransformer

class DeepJoinService:
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2", # Not the best option as it does not attunde to actual columns, but sentences
        sample_size: int = 50,
        similarity_threshold: float = 0.7,
        device: Optional[str] = None,
    ):
        self.sample_size = sample_size
        self.similarity_threshold = similarity_threshold
        self.model = SentenceTransformer(model_name, device=device)
        self.vector_dim = self.model.get_embedding_dimension()

        # Replaces linear scan with a graph-based Approximate Nearest Neighbor index
        M = 32  # Number of graph connection links per vector node
        self.index = faiss.IndexHNSWFlat(self.vector_dim, M, faiss.METRIC_INNER_PRODUCT)

        # Staging buffer: stores (dataset_id, column_name, concatenated_text)
        self._staged_records: List[Tuple[str, str, str]] = []

        # Mapping: FAISS ID -> (dataset_id, column_name)
        self.id_to_key: dict[int, Tuple[str, str]] = {}
        self._next_id = 0

    def _prepare_column_text(self, values: List[str]) -> str:
        """Extracts unique sample values and joins them into a single string document."""
        if not values:
            return ""

        clean_values = list({str(v).strip() for v in values if v is not None})
        if not clean_values:
            return ""

        if len(clean_values) > self.sample_size:
            sampled = random.sample(clean_values, self.sample_size)
        else:
            sampled = clean_values

        return " ".join(sampled)

    def stage_column(
        self, dataset_id: str, column_name: str, values: List[str]
    ) -> None:
        col_text = self._prepare_column_text(values)
        if col_text:
            self._staged_records.append((dataset_id, column_name, col_text))

    def stage_dataset(
        self, dataset_id: str, column_dict: dict[str, List[str]]
    ) -> None:
        for col_name, values in column_dict.items():
            self.stage_column(dataset_id, col_name, values)

    def stage_dataframe(self, dataset_id: str, df: DataFrame) -> None:
        for col_name in df.columns:
            clean_series = df[col_name].dropna().astype(str).tolist()
            self.stage_column(dataset_id, str(col_name), clean_series)

    def stage_socrata_stream(
        self,
        dataset_id: str,
        row_generator: Generator[dict[str, Any], None, None],
        target_columns: Optional[List[str]] = None,
    ) -> None:
        samplers: dict[str, ReservoirSampler] = {}

        for row in row_generator:
            cols_to_process = target_columns or row.keys()
            for col_name in cols_to_process:
                if col_name in row:
                    if col_name not in samplers:
                        samplers[col_name] = ReservoirSampler(k=self.sample_size)
                    samplers[col_name].add(row[col_name])

        for col_name, sampler in samplers.items():
            if sampler.sample:
                self.stage_column(dataset_id, col_name, sampler.sample)

    def build_index(self, encode_batch_size: int = 256) -> None:
        """Encodes all staged columns in a single batch pass and populates the FAISS index."""
        if not self._staged_records:
            return

        # 1. Extract texts for batch encoding
        col_texts = [text for _, _, text in self._staged_records]

        # 2. Single batched forward pass through PyTorch
        embeddings: np.ndarray = self.model.encode(
            col_texts,
            batch_size=encode_batch_size,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True,
        ).astype(np.float32)

        # 3. Commit vector matrix into C++ FAISS memory
        self.index.add(embeddings)

        # 4. Record ID mappings and flush staging buffer
        for ds_id, col_name, _ in self._staged_records:
            self.id_to_key[self._next_id] = (ds_id, col_name)
            self._next_id += 1

        self._staged_records.clear()

    def find_joinable_columns(
        self,
        query_values: List[str],
        top_k: int = 5,
        query_dataset_id: Optional[str] = None,
    ) -> List[JoinCandidate]:
        """Query the index for top_k join candidates matching a query column."""
        if self.index.ntotal == 0:
            return []

        query_text = self._prepare_column_text(query_values)
        if not query_text:
            return []

        query_vector: np.ndarray = self.model.encode(
            [query_text],
            convert_to_numpy=True,
            normalize_embeddings=True,
        ).astype(np.float32)

        distances, indices = self.index.search(query_vector, top_k)

        candidates = []
        for score, faiss_id in zip(distances[0], indices[0]):
            if faiss_id == -1 or score < self.similarity_threshold:
                continue

            ds_id, col_name = self.id_to_key[faiss_id]

            if query_dataset_id and ds_id == query_dataset_id:
                continue

            candidates.append(
                JoinCandidate(
                    target_dataset_id=ds_id,
                    target_column_name=col_name,
                    similarity_score=float(score),
                )
            )

        return candidates