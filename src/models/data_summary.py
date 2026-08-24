from collections import Counter
from dataclasses import dataclass, field, fields
from datetime import datetime, UTC
from bisect import bisect_right
from typing import Dict, Any

CURRENT_TIME = datetime.now(UTC)

BUCKET_DCT = {
    "attribute": {
        "bins": [0, 10, 20, 30, 40, 50],
        "labels": ['0-10', '10-20', '20-30', '30-40', '40-50', '50+']
        },
    "download_count": {
        "bins": [0, 100, 1000, 10000],
        "labels": ['0-100', '100-1K', '1K-10K', '10K+']
    },
    "row_count": {
        "bins": [0, 1000, 10000, 100000, 1000000, 10000000],
        "labels": ['0-1K', '1K-10K', '10K-100K', '100K-1M', '1M-10M', '10M+']
    },
    "table_sparseness": {
        "bins": [0, 1, 5, 10, 25, 50, 100],
        "labels": ['< 1% sparse', '1-5% sparse', '5-10% sparse', '10-25% sparse', '25-50% sparse', '50%+ sparse']
    },
    "view_count": {
        "bins": [0, 100, 1000, 10000],
        "labels": ['0-100', '100-1K', '1K-10K', '10K+']
    }
}

@dataclass
class DataSummary:
    count: int = 0

    # use field(default_factory=Counter) because Counters are mutable objects.
    asset_type: Counter = field(default_factory=Counter)
    category: Counter = field(default_factory=Counter)
    display: Counter = field(default_factory=Counter)
    download_count: Counter = field(default_factory=Counter)
    last_update: Counter = field(default_factory=Counter)
    publication_date: Counter = field(default_factory=Counter)
    tags: Counter = field(default_factory=Counter)
    view_count: Counter = field(default_factory=Counter)
    
    attribute: Counter = field(default_factory=Counter)
    col_type: Counter = field(default_factory=Counter)
    row_count: Counter = field(default_factory=Counter)
    table_sparseness: Counter = field(default_factory=Counter)

    def ingest(self, dct):
        for f in fields(self):
            if f.name not in dct or f.name == "count":
                continue          
            incoming_value = dct[f.name]
            current_value = getattr(self, f.name)
            DataSummary._add(current_value, f.name, incoming_value)
        self.count += 1

    def _add(ctr, key, value):
        if isinstance(value, list):
            if key != "attribute":
                ctr.update(value)
            else:
                DataSummary._add(ctr, key, len(value)) # attribute count is desired, not actual column names
        elif isinstance(value, str):
            ctr[DataSummary._string(key, value)] += 1
        elif isinstance(value, int) or isinstance(value, float):
            ctr[DataSummary._bucket(key, value)] += 1
    
    def _bucket(key, value):
        bucket = BUCKET_DCT.get(key, None)
        if bucket:
            bin = bucket.get("bins")
            label = bucket.get("labels")
            index = bisect_right(bin, value) - 1
        return label[index]

    def _string(key, value):
        if key == "last_update" or key == "publication_date":
            return DataSummary._date(key, value)
        return value

    def _date(key, value, today = CURRENT_TIME):
        delta_time = today - datetime.fromisoformat(value)
        months = int(delta_time.days / 30)
        return months

    def sort_counter(self, name: str, counter: Counter) -> Counter:
        """Sorts a single counter based on its category rules."""
        if name in BUCKET_DCT:
            order = BUCKET_DCT[name]["labels"]
            return Counter({k: counter.get(k, 0) for k in order})
        
        if name in {"publication_date", "last_update"}:
            return Counter(dict(sorted(counter.items(), key=lambda x: x[0])))

        return Counter(dict(counter.most_common()))

    def sort_in_place(self):
        """Mutates all counters in self to be ordered."""
        for f in fields(self):
            val = getattr(self, f.name)
            if isinstance(val, Counter):
                setattr(self, f.name, self.sort_counter(f.name, val))

    def to_dict(self):
        """Returns a sorted dictionary export without mutating instance state."""
        out = {"count": self.count}
        for f in fields(self):
            val = getattr(self, f.name)
            if isinstance(val, Counter):
                sorted_ctr = self.sort_counter(f.name, val)
                out[f.name] = dict(sorted_ctr)
        return out

    @classmethod
    def from_dict(cls, dct: Dict[str, Any]) -> "DataSummary":
        kwargs = {}
        for f in fields(cls):
            if f.name in dct:
                val = dct[f.name]
                if f.type is Counter and isinstance(val, dict):
                    val = Counter(val)
                kwargs[f.name] = val
        return cls(**kwargs)

    def __add__(self, other: "DataSummary") -> "DataSummary":
        if not isinstance(other, DataSummary):
            return NotImplemented
        new_kwargs = {}
        for f in fields(self):
            val1 = getattr(self, f.name)
            val2 = getattr(other, f.name)
            new_kwargs[f.name] = val1 + val2
        return DataSummary(**new_kwargs)

    def __iadd__(self, other: "DataSummary") -> "DataSummary":
        if not isinstance(other, DataSummary):
            return NotImplemented
            
        for f in fields(self):
            val1 = getattr(self, f.name)
            val2 = getattr(other, f.name)
            
            if isinstance(val1, Counter):
                val1.update(val2)
            elif isinstance(val1, (int, float)):
                setattr(self, f.name, val1 + val2)

        return self

    def __radd__(self, other: "DataSummary") -> "DataSummary":
        if other == 0:
            return self
        return self.__add__(other)