import numpy as np
import pytest
from unittest.mock import MagicMock, patch

from deepjoin.deepjoin_service import DeepJoinService
from models.join_candidate import JoinCandidate

# ------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------
@pytest.fixture
def mock_sentence_transformer():
    """Mocks SentenceTransformer to avoid loading ML models during unit tests."""
    with patch("deepjoin.deepjoin_service.SentenceTransformer") as mock_cls:
        mock_model = MagicMock()
        mock_model.get_embedding_dimension.return_value = 4

        # Return dummy normalized float32 vectors (2D numpy array)
        def mock_encode(sentences, **kwargs):
            num_sentences = len(sentences) if isinstance(sentences, list) else 1
            # Deterministic synthetic vectors of dimension 4
            vecs = np.ones((num_sentences, 4), dtype=np.float32)
            # Normalize to unit length
            return vecs / np.linalg.norm(vecs, axis=1, keepdims=True)

        mock_model.encode.side_effect = mock_encode
        mock_cls.return_value = mock_model
        yield mock_model

@pytest.fixture
def service(mock_sentence_transformer):
    """Provides an initialized FAISSJoinService instance with a mocked model."""
    return DeepJoinService(sample_size=5, similarity_threshold=0.5)

# ------------------------------------------------------------------
# Tests for _prepare_column_text
# ------------------------------------------------------------------
def test_prepare_column_text_normal_values(service):
    values = ["  apple ", "banana ", "apple", "cherry", None, ""]
    prepared = service._prepare_column_text(values)
    
    # Should deduplicate, strip whitespace, remove empty/none
    tokens = set(prepared.split())
    assert tokens == {"apple", "banana", "cherry"}

def test_prepare_column_text_empty_and_null(service):
    assert service._prepare_column_text([]) == ""
    assert service._prepare_column_text([None, "", "   "]) == ""

def test_prepare_column_text_sampling_limit(service):
    # sample_size is set to 5 in fixture
    values = [f"val_{i}" for i in range(20)]
    prepared = service._prepare_column_text(values)
    
    tokens = prepared.split()
    assert len(tokens) == 5
    assert len(set(tokens)) == 5  # Must remain unique

# ------------------------------------------------------------------
# Tests for build_index
# ------------------------------------------------------------------
def test_build_index_populates_faiss_and_mappings(service):
    service.stage_column("ds1", "col_a", ["10", "20", "30"])
    service.stage_column("ds1", "col_b", ["foo", "bar"])

    assert len(service._staged_records) == 2
    assert service.index.ntotal == 0

    service.build_index()

    # Verify staging buffer is flushed and FAISS index is populated
    assert len(service._staged_records) == 0
    assert service.index.ntotal == 2
    assert service.id_to_key[0] == ("ds1", "col_a")
    assert service.id_to_key[1] == ("ds1", "col_b")

def test_build_index_empty_staging(service):
    service.build_index()
    assert service.index.ntotal == 0

# ------------------------------------------------------------------
# Tests for find_joinable_columns
# ------------------------------------------------------------------
def test_find_joinable_columns_returns_candidates(service):
    service.stage_column("ds1", "id_col", ["07001", "07002", "07003"])
    service.stage_column("ds2", "zip_code", ["07001", "07002", "07004"])
    service.build_index()

    candidates = service.find_joinable_columns(
        query_values=["07001", "07002"],
        top_k=5,
        query_dataset_id="ds_query"
    )

    assert len(candidates) > 0
    assert isinstance(candidates[0], JoinCandidate)
    assert candidates[0].target_dataset_id in ["ds1", "ds2"]
    assert candidates[0].similarity_score is not None
    assert candidates[0].similarity_score >= 0.5

def test_find_joinable_columns_filters_self_joins(service):
    service.stage_column("ds1", "col_a", ["a", "b", "c"])
    service.stage_column("ds2", "col_b", ["a", "b", "c"])
    service.build_index()

    # Filter out candidates from query_dataset_id "ds1"
    candidates = service.find_joinable_columns(
        query_values=["a", "b"],
        top_k=5,
        query_dataset_id="ds1"
    )

    dataset_ids = [c.target_dataset_id for c in candidates]
    assert "ds1" not in dataset_ids
    assert "ds2" in dataset_ids

def test_find_joinable_columns_empty_query_or_index(service):
    # Querying empty index
    assert service.find_joinable_columns(["val1", "val2"]) == []

    # Querying with empty/invalid values on populated index
    service.stage_column("ds1", "col_a", ["x", "y"])
    service.build_index()
    
    assert service.find_joinable_columns([]) == []
    assert service.find_joinable_columns([None, ""]) == []