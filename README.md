# Big Data Final Project - NYC Open Data Joinability

This repo explores the NYC Open Data (Socrata) catalog and joinability across datasets via LAZO and DeepJoin perspectives.

## Repository Layout (BEING REFACTORED)
- `models`
  - `column_sketch.py` - dataclass used for sketching columns.
  - `data_summary.py` - dataclass used for summarizing metadata of ingested datasets.
  - `dataset_sketch.py` - dataclass used for sketching columns of a dataset.
  - `join_candidate.py` - dataclass used for candidates of joinable columns.
  - `reservoir_sampler.py` - model used to properly sample data from a stream.
- `socrata_interface`
  - `domain.py` - Socrata wrapper.
  - `io.py` - basic input output functions.
  - `transformers.py` - functions used to manipulate raw data from `domain.py` into more usable forms by models.
- `lazo`
  - `dataset_sketch_process.py` - process used to create dataset sketches.
  - `joinability_service.py` - uses datasketch library to enable quick and succinct calculations of Jaccard Similarity using MinHashing
- `deepjoin`
  - `deepjoin_service.py` - mimics the deepjoin strategy for discovering joinability by embedding columns and finding near by columns spatially.
- `util`
  - `decorators.py` - decorators used for retry logic and logging.
  - `util.py` - utility functions to create directories and loggers.
- `visualize` (WIP)
  - `deepjoin_barchart.py`
  - `deepjoin_visualize.py`
  - `join_graph.py` - builds dataset-level graph (also offers pyvis HTML export if needed).
  - `plotter.py` - creates graphs based off of metadata gotten using `domain.py`. 
  - `run_join_graph.py` - end-to-end: load sketches, compute joinability, export CSV + static charts. (WIP)
  - `visualize_joinability.py` - visualizes joinability based on results. (WIP)
- `examples`
  - `deepjoin.ipynb` - example behavior of using deepjoin for joinability.
  - `lazo.ipynb` - example behavior of using LAZO for joinability.
  - `summary.ipynb` - example behavior of summarizing datasets.
- `downloader.ipnb` - notebook that is currently being used as a testing ground.
- `graphics.ipynb` - notebook that allows for simple use of `plotter.py`. (WIP)
- `city_pops.csv` - csv containing population data and city names for domains to be used by `graphics.ipynb`.
- `find_domains.ipynb` — notebook using the Socrata API for domain crawling, domain filtering.
- `socrata_domains.txt` / `socrata_domains_cities_only.txt` - discovered Socrata portals, filtered to city portals.
- Outputs (generated): `data/`, `logs/`, `reports/`.

## Setup
pip:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install . # `pip install -e .[dev]` for pytest
```
uv:
```bash
uv sync # `uv sync --no-dev` if is pytest not wanted
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```
Tokens (optional but recommended to avoid throttling): set `SODAPY_APPTOKEN` or per-domain creds in your shell env before running scripts.

## Workflow
1. Use the domain object to connect to a city's socrata service.
2. Acquire the desired data using domain methods and alter them as desired using functions in transformers.
3. Input the transformed data into the provided models.

## LAZO Highlights
- MinHash signature (K=128) for Jaccard; HLL-style cardinality per column.

## Notes
- `find_domains.ipynb` contains the original catalog crawl and domain filtering utilities.
- Generated files are large; `.gitignore` already excludes bulk data and env artifacts.
