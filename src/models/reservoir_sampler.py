import random
from typing import Any, List, Optional

class ReservoirSampler:
    """Maintains a uniform random sample of size k from line by line streamed data."""
    def __init__(self, k: int = 50, rng: Optional[random.Random] = None):
        if k <= 0:
            raise ValueError("Sample size k must be greater than 0.")
        self.k = k
        self.rng = rng or random.Random()
        self.sample: List[str] = []
        self._seen_count = 0

    def add(self, value: Any) -> None:
        """Processes a single stream element using Algorithm R."""
        if value is None:
            return

        val_str = str(value).strip()
        if not val_str:
            return

        self._seen_count += 1

        # Fill initial reservoir up to k elements
        if len(self.sample) < self.k:
            self.sample.append(val_str)
        else:
            # Replace elements with decreasing probability (k / _seen_count)
            r = self.rng.randint(0, self._seen_count - 1)
            if r < self.k:
                self.sample[r] = val_str