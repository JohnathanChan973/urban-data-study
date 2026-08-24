# Big Data Final Project - NYC Open Data Joinability

This repo explores the NYC Open Data (Socrata) catalog and joinability across datasets via LAZO and DeepJoin perspectives.

## Repository Layout (BEING REFACTORED)
- `models`
  - `column_sketch.py` - dataclass used for sketching columns.
  - `data_summary.py` - dataclass used for summarizing metadata of ingested datasets.
  - `dataset_sketch.py` - dataclass used for sketching columns of a dataset.
  - `join_candidate.py` - dataclass used for candidates of joinable columns.
- `socrata_interface`
  - `domain.py` - Socrata helper.
  - `io.py` - basic input output functions.
  - `transformers.py` - functions used to manipulate raw data from `domain.py` into more usable forms by models.
  - `plotter.py` - creates graphs based off of metadata gotten using `domain.py`. (WIP)
- `lazo`
  - `dataset_sketch_process.py` - process used to create dataset sketches.
  - `join_graph.py` - builds dataset-level graph (also offers pyvis HTML export if needed). (WIP)
  - `joinability_service.py` - uses datasketch library to enable quick and succinct calculations of Jaccard Similarity using MinHashing
  - `run_join_graph.py` - end-to-end: load sketches, compute joinability, export CSV + static charts. (WIP)
  - `visualize_joinability.py` - visualizes joinability based on results. (WIP)
- `deepjoin` (TO BE LABELED)
  - `config.py`
  - `deepjoin_all_api.py`
  - `deepjoin_barchart.py`
  - `deepjoin_visualize.py`
  - `encoder.py`
  - `sample_loader.py`
  - `sampler.py`
- `util`
  - `decorators.py` - decorators used for retry logic and logging.
  - `util.py` - utility functions to create directories and loggers.
- `downloader.ipnb` - notebook that is currently being used as a testing ground.
- `graphics.ipynb` - notebook that allows for simple use of `plotter.py`. (WIP)
- `city_pops.csv` - csv containing population data and city names for domains to be used by `graphics.ipynb`.
- `find_domains.ipynb` — notebook using the Socrata API for domain crawling, domain filtering.
- `socrata_domains.txt` / `socrata_domains_cities_only.txt` - discovered Socrata portals, filtered to city portals.
- Outputs (generated): `data/`, `logs/`, `reports/`.

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
Tokens (optional but recommended to avoid throttling): set `SODAPY_APPTOKEN` or per-domain creds in your shell env before running scripts.

## Workflow (BEING REFACTORED)

## LAZO Highlights
- MinHash signature (K=128) for Jaccard; HLL-style cardinality per column.

## Notes
- `find_domains.ipynb` contains the original catalog crawl and domain filtering utilities.
- Generated files are large; `.gitignore` already excludes bulk data and env artifacts.
