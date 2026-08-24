import socrata_interface.transformers as trans
import pandas as pd
from pytest import raises

DATA = {'resource': {'name': 'NOPD Use of Force Incidents',
   'id': '9mnw-mbde',
   'type': 'dataset',
   'updatedAt': '2026-03-03T08:30:18.000Z',
   'createdAt': '2016-08-03T03:07:21.000Z',
   'page_views': {'page_views_last_week': 1043,
    'page_views_last_month': 4568,
    'page_views_total': 242757,
    'page_views_last_week_log': 10.027905996569885,
    'page_views_last_month_log': 12.15766272720845,
    'page_views_total_log': 17.889159314345548},
   'columns_field_name': [
    'subject_injured'],
   'columns_datatype': [
    'Text'],
   'download_count': 7201,
   'lens_view_type': 'tabular',
   'lens_display_type': 'table',
   'publication_date': '2021-10-28T15:33:49.000Z'},
  'classification': {'categories': [],
   'tags': [],
   'domain_category': 'Public Safety and Preparedness',
   'domain_tags': ['use of force'],},}

METADATA = {
 'assetType': 'dataset',
 'category': 'Public Safety and Preparedness',
 'createdAt': 1470193641,
 'displayType': 'table',
 'downloadCount': 7201,
 'publicationDate': 1635435229,
 'rowsUpdatedAt': 1772526618,
 'viewCount': 242757,
 'viewLastModified': 1635435229,
 'viewType': 'tabular',
 'columns': [
  {'id': 550825312,
   'name': 'Subject Injured',
   'dataTypeName': 'text',
   'fieldName': 'subject_injured',
   'renderTypeName': 'text',},],
 'tags': ['use of force']}

def test_load_to_df():
    df = trans.load_to_df([{'service_request': '2021-783285',
  'geocoded_column': {'latitude': '29.992361741051177',
   'longitude': '-90.11477935333389'},
  ':@computed_region_ewbu_t8bu': '13008',
  ':@computed_region_k37d_then': '1',
  ':@computed_region_m56f_hbma': '235',
  ':@computed_region_7fw3_kdpf': '50',
  ':@computed_region_spev_d8jm': '3772',
  ':@computed_region_sikx_bdeb': '235',
  ':@computed_region_evki_aju8': '7',
  ':@computed_region_u4yh_3wk9': '13008'},
 {'service_request': '2024-1127064',
  'geocoded_column': {'latitude': '30.05605380401344',
   'longitude': '-89.95646571265702'},
  ':@computed_region_ewbu_t8bu': '4879',
  ':@computed_region_k37d_then': '5',
  ':@computed_region_m56f_hbma': '172',
  ':@computed_region_7fw3_kdpf': '20',
  ':@computed_region_spev_d8jm': '4150',
  ':@computed_region_sikx_bdeb': '172',
  ':@computed_region_evki_aju8': '1',
  ':@computed_region_u4yh_3wk9': '4879'}])
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert len(df.columns) ==  10

def test_extract_schema():
    with raises(ValueError):
        trans.extract_schema(None)
    meta_schem = trans.extract_schema(METADATA)
    assert len(meta_schem) == 2
    assert meta_schem.get("attribute") == ["subject_injured"]
    data_schem = trans.extract_schema(DATA)
    assert meta_schem == data_schem

def test_extract_joinable_columns():
    schema = {"attribute": ["name", "score", "link"], "col_type": ["text", "number", "url"]}
    cols = trans.extract_joinable_columns(schema)
    assert len(cols) == 2
    assert len(cols.get("text")) == 1
    assert len(cols.get("number")) == 1

def test_extract_relevant_metadata():
    with raises(ValueError):
        trans.extract_relevant_metadata(None)
    meta_meta = trans.extract_relevant_metadata(METADATA)
    assert len(meta_meta) == 8
    data_meta = trans.extract_relevant_metadata(DATA)
    assert meta_meta == data_meta

def test_extract_sparseness():
    sparseness = trans.extract_sparseness({"row_count": 100}, {"a": 0, "b": 50, "c": 100})
    assert sparseness["table_sparseness"] == 50
    sparseness = trans.extract_sparseness({"row_count": 0}, {"a": 0, "b": 0, "c": 0})
    assert sparseness["table_sparseness"] == 0 # Used to fail because of NaN due to divide by 0. Default to 0 since cannot be sparse without any rows