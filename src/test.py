from domain import Domain
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from all_domain import All_Domain
from plotter import All_Domain_Plotter
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
    # nola = Domain("data.nola.gov")
    # reading = Domain("data.readingpa.gov")
    # honolulu = Domain("data.honolulu.gov")
    # nola.download_all_raw_dataset()
    # print(nola.fetch_schema("x5fx-4tmu"))
    # print(nola.fetch_schema("devm-es8b"))
    # print(nola.fetch_schema("em4n-zidu"))
    # fail = nola.load_dataset_to_df("mwpi-m8zd")
    # nola.get_relevant_metadata("wy29-i338")
    # print(nola.summarize_metadata())
    # print(reading.download_all_relevant_metadata())
    # print(reading.summarize_metadata())
    # honolulu.download_all_relevant_metadata()
    # honolulu.summarize_metadata()
    # current_time = datetime.now().timestamp()
    # Handle missing publicationDate values
    # print((current_time - 1740785216) / (30.44 * 24 * 3600))
    # All_Domain().aggregate_summaries()
    # nyc = Domain("data.cityofnewyork.gov")
    # nyc.get_relevant_metadata("nc67-uf89")
    # nyc_domain = "data.cityofnewyork.us"

    # domain = Domain(nyc_domain)

    # print(domain.city_datasets_count()) # currently 2994 returned from getting the count for data.cityofnewyork.us
    # oakland = Domain("data.oaklandca.gov")
    # print(oakland.get_relevant_metadata("a2eb-iq6b"))
    # from sodapy import Socrata

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