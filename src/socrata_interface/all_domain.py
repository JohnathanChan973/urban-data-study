import time
import json
from pathlib import Path
from .domain import Domain
from tqdm.auto import tqdm  # auto detects notebook vs terminal
from requests.exceptions import Timeout as RequestsTimeout

# class All_Domain:
#     def __init__(self, parent_dir="all_city_data"):
#         self.parent_dir = Path(parent_dir)
#         self.parent_dir.mkdir(exist_ok=True)
#         self.all_domain = []
#         with open("socrata_domains_cities_only.txt") as f:
#             for line in f:
#                 self.all_domain.append(Domain(line.strip()))
#         self.base = self.parent_dir / "all_cities"
#         self.base.mkdir(exist_ok=True)