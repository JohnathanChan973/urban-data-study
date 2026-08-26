from models.reservoir_sampler import ReservoirSampler
import pytest
import random
from typing import Any, Dict, Generator
from collections import Counter
from scipy.stats import chisquare

@pytest.fixture
def seeded_rng() -> random.Random:
    """Provides a deterministic random number generator with a fixed seed."""
    return random.Random(42)

@pytest.fixture
def sample_socrata_stream() -> (
    Generator[Dict[str, Any], None, None]
):
    """Simulates a Socrata API row-by-row streaming generator."""

    def _generator() -> Generator[Dict[str, Any], None, None]:
        categories = ["Finance", "Health", "Education", "Public Safety"]
        statuses = ["Active", "Pending", "Closed"]

        for i in range(200):
            yield {
                "id": f"row_{i}",
                "value": f"val_{i}",
                "category": categories[i % len(categories)],
                "status": statuses[i % len(statuses)],
                "nullable_col": None if i % 5 == 0 else f"data_{i}",
            }

    return _generator()

@pytest.fixture
def infinite_stream() -> Generator[int, None, None]:
    """Provides an infinite generator to verify that the sampler works without

    evaluating length or loading full datasets into memory.
    """

    def _generator() -> Generator[int, None, None]:
        i = 0
        while True:
            yield i
            i += 1

    return _generator()

def test_socrata_stream_sampling_and_reservoir_size(
    sample_socrata_stream: Generator[Dict[str, Any], None, None],
    seeded_rng: random.Random,
) -> None:
    """Verifies sampling across a simulated streaming Socrata API generator."""
    sampler = ReservoirSampler(k=50, rng=seeded_rng)

    for row in sample_socrata_stream:
        sampler.add(row["value"])

    # Reservoir should hit exactly k items when stream length > k
    assert len(sampler.sample) == 50
    assert len(set(sampler.sample)) == 50  # All items should be distinct

def test_infinite_stream_execution(
    infinite_stream: Generator[int, None, None],
    seeded_rng: random.Random,
) -> None:
    """Verifies the sampler operates in O(1) memory on streams of unknown length."""
    sampler = ReservoirSampler(k=10, rng=seeded_rng)

    # Process 1,000 items from an infinite stream
    for item, _ in zip(infinite_stream, range(1000)):
        sampler.add(str(item))

    assert len(sampler.sample) == 10

def test_stream_smaller_than_k(seeded_rng: random.Random) -> None:
    """Verifies that when stream size N < k, all valid items are retained in order."""

    def _short_stream() -> Generator[str, None, None]:
        yield from ["A", "B", "C"]

    sampler = ReservoirSampler(k=10, rng=seeded_rng)
    for val in _short_stream():
        sampler.add(val)

    assert sampler.sample == ["A", "B", "C"]

def test_null_and_empty_value_filtering(
    sample_socrata_stream: Generator[Dict[str, Any], None, None],
    seeded_rng: random.Random,
) -> None:
    """Ensures None or empty string stream values are safely ignored."""
    sampler = ReservoirSampler(k=20, rng=seeded_rng)

    for row in sample_socrata_stream:
        sampler.add(row["nullable_col"])

    assert len(sampler.sample) == 20
    assert None not in sampler.sample
    assert "" not in sampler.sample

def test_reproducible_stream_sampling(
    sample_socrata_stream: Generator[Dict[str, Any], None, None],
) -> None:
    """Confirms that injecting identical seed state yields identical sample results."""
    sampler_a = ReservoirSampler(k=15, rng=random.Random(1337))
    sampler_b = ReservoirSampler(k=15, rng=random.Random(1337))

    # Run sampler A
    for row in sample_socrata_stream:
        sampler_a.add(row["id"])

    # Re-instantiate stream generator for sampler B
    stream_b = (
        f
        for f in [
            {"id": f"row_{i}"} for i in range(200)
        ]
    )
    for row in stream_b:
        sampler_b.add(row["id"])

    assert sampler_a.sample == sampler_b.sample

def test_uniform_distribution_chi_square():
    k = 3
    stream_size = 10
    num_trials = 10_000
    counts = Counter()

    # Run sampling across multiple trials
    for seed in range(num_trials):
        sampler = ReservoirSampler(k=k, rng=random.Random(seed))
        for item in range(stream_size):
            sampler.add(item)
        counts.update(sampler.sample)

    # Expected count for each item: (k / stream_size) * num_trials = 3,000
    expected_count = (k / stream_size) * num_trials
    observed_counts = [counts[str(i)] for i in range(stream_size)]

    assert sum(observed_counts) == int(expected_count * stream_size)

    # Chi-square goodness-of-fit test
    chi2, p_value = chisquare(f_obs=observed_counts, f_exp=expected_count)

    assert (
        p_value > 0.01
    ), f"Distribution is significantly non-uniform (p={p_value})"