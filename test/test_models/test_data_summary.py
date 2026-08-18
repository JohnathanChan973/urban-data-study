from models.data_summary import DataSummary
from collections import Counter

def test_creation():
    context = DataSummary()

    assert isinstance(context.category, Counter)

def test_ingest():
    summary = DataSummary()
    summary.ingest({"tags": ["police", "council"], 
                    "download_count": 13, 
                    "category": "Public Safety and Preparedness", 
                    "publication_date": "2021-10-28T15:33:49+00:00",
                    'attribute': ['subject_injured']})
    
    assert len(summary.tags) == 2 # tests lists
    assert summary.tags["police"] == 1
    assert summary.download_count["0-100"] == 1 # tests ints
    assert summary.category["Public Safety and Preparedness"] == 1 # tests strings
    assert len(summary.publication_date) == 1 # tests dates
    assert summary.attribute["0-10"] == 1 # tests attribute which was an edge case

def test_add():
    summary1 = DataSummary()
    summary2 = DataSummary()
    summary1.ingest({"tags": ["police"]})
    summary2.ingest({"tags": ["council"]})
    assert len(summary1.tags) == 1
    summary1 += summary2
    assert len(summary1.tags) == 2