from socrata_interface.domain import Domain
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from socrata_interface.all_domain import All_Domain
from visualizers.plotter import All_Domain_Plotter
import pandas as pd

# with ThreadPoolExecutor(max_workers=10) as ex:
#     future_map = {
#         ex.submit(count_nulls, domain, dataset_id, col): col
#         for col in column_names
#     }

# results = {
#     future_map[f]: f.result()
#     for f in future_map
# }

def main():
    all_domain = All_Domain()
    # all_domain.tagcloud("data.honolulu.gov")
    plotter = All_Domain_Plotter(all_domain)
    # plotter.tagcloud("data.honolulu.gov")
    plotter.line_graph("update", domain="data.honolulu.gov")

    # pops = "city_pops.csv"
    # pops_df = pd.read_csv(pops)
    # print(pops_df)
    # print(tabulate(pops_df, headers = 'keys', tablefmt="fancy_grid", showindex=False))

    # client = Socrata("data.buffalony.gov", None, timeout=0.001)  # Very short timeout

    # try:
    #     client.get("dataset_id", limit=1)
    # except Exception as e:
    #     print(f"Exception type: {type(e)}")
    #     print(f"Exception message: {e}")
    #     print(f"Is timeout in message: {'timeout' in str(e).lower()}")

    # plotter.row_count()
    # print(plotter.data_count_cat())

if '__main__':
    main()