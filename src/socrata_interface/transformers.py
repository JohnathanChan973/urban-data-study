import pandas as pd
from datetime import datetime, UTC

def load_to_df(dataset):
    if not isinstance(dataset, list):
        dataset = []
    return pd.DataFrame.from_records(dataset)

def extract_columns(id, df):
    if df.empty:
        return None
    column_dict = {}
    for col in df.columns:
        series = df[col]
        column_dict[(id, col)] = series
    return column_dict

def extract_schema(metadata):
    if metadata:
        resource = metadata.get("resource", None)
        if resource:
            field_name = resource.get("columns_field_name")
            datatype = resource.get("columns_datatype")
            if field_name and datatype:
                return {"attribute": field_name, "col_type": list(map(str.lower, datatype))} 
        else:
            cols = metadata.get("columns", None)
            if cols:
                att_list = []
                col_t_list = []
                for c in cols:
                    att_list.append(c.get("fieldName", None))
                    col_t_list.append(c.get("dataTypeName", None))
                return {'attribute': att_list, 'col_type': col_t_list}
    return None

def extract_relevant_metadata(metadata):
    if metadata:
        resource = metadata.get("resource")
        if resource:
            classification = metadata.get("classification")
            return {
                "asset_type": resource.get("type"),
                "category": classification.get("domain_category"), # string
                "display": resource.get("lens_display_type"), # string
                "download_count": resource.get("download_count"), # int
                "last_update": resource.get("updatedAt").replace('.000Z', '+00:00'), # string
                "publication_date": resource.get("publication_date").replace('.000Z', '+00:00'),
                "tags": classification.get("domain_tags"), # list of strings 
                "view_count": resource.get("page_views").get("page_views_total") # int
                }
        else:
            return {
                "asset_type": metadata.get("assetType"),
                "category": metadata.get("category"),
                "display": metadata.get("displayType"),
                "download_count": metadata.get("downloadCount"),
                "last_update": datetime.fromtimestamp(metadata.get("rowsUpdatedAt"), UTC).isoformat(),
                "publication_date": datetime.fromtimestamp(metadata.get("publicationDate"), UTC).isoformat(), # str (.isoformat() makes it a string)
                "tags": metadata.get("tags"),
                "view_count": metadata.get("viewCount")
                }
    return None

def extract_sparseness(row_counts, null_counts):
    """
    :param row_counts: Expected to be the row_counts() function from domain
    :param null_counts: Expected to be the null_counts() function from domain
    """
    total_rows = int(row_counts.get("row_count"))
    if total_rows == 0:
        return {"table_sparseness": 0}
    null_series = pd.Series(null_counts).astype(int)
    null_percents = null_series / total_rows * 100
    return {"table_sparseness": null_percents.mean()}

def aggregate_tabular_metadata(schema, row_counts, sparseness):
    tabular_summary = row_counts.copy()
    tabular_summary.update(sparseness)
    tabular_summary.update(schema)
    return tabular_summary
