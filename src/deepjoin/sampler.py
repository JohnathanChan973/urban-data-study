# sampler.py

import requests

# def sample_from_api(dataset_id, column, n=20): Takes the first 20 rows of the dataset
#     """
#     SAMPLE COLUMN VALUES FROM NYC OPEN DATA API.
#     Disabled until dataset is available.
#     """
#     url = f"https://data.cityofnewyork.us/resource/{dataset_id}.json?$select={column}&$limit={n}"
#     try:
#         r = requests.get(url)
#         if r.status_code != 200:
#             return []
#         data = r.json()
#         return [row.get(column, "") for row in data]
#     except:
#         return []


# def sample_from_fake(fake_data, column, n=20): Why would a dedicated sample fake be needed?
#     """
#     SAMPLE VALUES FROM A FAKE DATASET FOR TESTING PURPOSES.
#     This is what DeepJoin will use until real samples arrive.
#     """
#     return fake_data.get(column, [])[:n]
