import pytest
from datasketch import HyperLogLog, MinHash
from lazo.lazo_service import JoinabilityService
from models.column_sketch import ColumnSketch
from models.dataset_sketch import DatasetSketch
from models.join_candidate import JoinCandidate

# Helper fixture to generate populated ColumnSketch objects easily
def create_column_sketch(
    name: str, values: list[str], num_perm: int = 128
) -> ColumnSketch:
    sketch = ColumnSketch(column_name=name, num_perm=num_perm)

    # Initialize raw datasketch primitives
    mh = MinHash(num_perm=num_perm)
    hll = HyperLogLog(p=10)

    for val in values:
        val_bytes = val.encode("utf-8")
        mh.update(val_bytes)
        hll.update(val_bytes)

    sketch.minhash = mh
    sketch.hll = hll
    sketch.rows_processed = len(values)
    return sketch

@pytest.fixture
def sample_data():
    """Generates mock datasets with known overlapping columns."""
    # Shared domain values
    user_ids_small = [f"usr_{i}" for i in range(100)]
    user_ids_large = [f"usr_{i}" for i in range(1000)]
    zip_codes = [f"070{i:02d}" for i in range(50)]
    random_strings = [f"rand_{i}" for i in range(200)]

    # Dataset 1: Users table (Small set of IDs)
    ds1 = DatasetSketch(dataset_id="ds_users")
    ds1.column_sketches["user_id"] = create_column_sketch(
        "user_id", user_ids_small
    )
    ds1.column_sketches["zip"] = create_column_sketch("zip", zip_codes)

    # Dataset 2: Orders table (Large set of IDs containing the small set)
    ds2 = DatasetSketch(dataset_id="ds_orders")
    ds2.column_sketches["customer_id"] = create_column_sketch(
        "customer_id", user_ids_large
    )
    ds2.column_sketches["notes"] = create_column_sketch(
        "notes", random_strings
    )

    return {"ds1": ds1, "ds2": ds2, "user_ids_small": user_ids_small}

def test_stage_and_index_datasets(sample_data):
    """Verifies that datasets can be staged and indexed without error."""
    service = JoinabilityService()

    service.stage_dataset(sample_data["ds1"])
    service.stage_dataset(sample_data["ds2"])

    assert len(service._staged_records) == 4
    assert len(service._registered_datasets) == 2

    with pytest.raises(Exception) as excinfo:
        service.stage_dataset(sample_data["ds2"])
    assert "This dataset has already been registered." in str(excinfo.value)

    # Build index should consume staged records
    service.build_index()

def test_dataset_containment_query_finds_matches(sample_data):
    """Verifies that searching with a dataset column finds joinable columns across datasets."""
    service = JoinabilityService()
    service.stage_dataset(sample_data["ds1"])
    service.stage_dataset(sample_data["ds2"])
    service.build_index()

    # Query using user_id from ds2 (100 IDs from ds1 are contained within ds2's 1000 IDs)
    query_col = sample_data["ds2"].column_sketches["customer_id"]
    matches = service.find_joinable_columns(
        query_sketch=query_col, query_dataset_id="ds_users"
    )

    assert len(matches) == 1
    assert matches[0] == JoinCandidate(
        target_dataset_id="ds_orders", target_column_name="customer_id"
    )

def test_filters_out_self_joins(sample_data):
    """Verifies that passing query_dataset_id excludes columns from the same dataset."""
    service = JoinabilityService()
    service.stage_dataset(sample_data["ds1"])
    service.build_index()

    query_col = sample_data["ds1"].column_sketches["user_id"]

    # When query_dataset_id is provided, matching against itself should be filtered out
    matches = service.find_joinable_columns(
        query_sketch=query_col, query_dataset_id="ds_users"
    )
    assert len(matches) == 0

def test_single_column_staging_and_one_off_query(sample_data):
    """Tests staging standalone single columns and running one-off queries (query_dataset_id=None)."""
    service = JoinabilityService()

    # Stage a single column independently
    standalone_col = create_column_sketch(
        "master_zip_list", [f"070{i:02d}" for i in range(50)]
    )
    service.stage_column(standalone_col, dataset_id="ref_geo_data")

    # Also stage ds1
    service.stage_dataset(sample_data["ds1"])
    service.build_index()

    # Create a one-off query sketch (not part of any registered dataset)
    one_off_query = create_column_sketch(
        "input_zips", [f"070{i:02d}" for i in range(50)]
    )

    # Query with query_dataset_id=None to accept matches from any dataset/column
    matches = service.find_joinable_columns(
        query_sketch=one_off_query, query_dataset_id=None
    )

    matched_keys = {
        (m.target_dataset_id, m.target_column_name) for m in matches
    }
    assert ("ds_users", "zip") in matched_keys
    assert ("ref_geo_data", "master_zip_list") in matched_keys

def test_empty_query_sketch_returns_no_matches():
    """Verifies that an unpopulated/empty column sketch returns an empty result list safely."""
    service = JoinabilityService()

    empty_col = ColumnSketch(column_name="empty")
    empty_col.minhash = MinHash(num_perm=128)
    empty_col.hll = HyperLogLog(p=10)

    matches = service.find_joinable_columns(query_sketch=empty_col)
    assert matches == []