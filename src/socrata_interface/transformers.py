def extract_schema(metadata):
    """
    Docstring for extract_columns_from_dataset
    
    :param dataset: Tuple containing the dataset's id and their columns
    """
    if df.empty:
        return None
    str_cols = df.select_dtypes(include=["object", "string"]).columns.tolist()
    num_cols = df.select_dtypes(include=["number", "float", "int"]).columns.tolist()
    cols = list(dict.fromkeys(str_cols + num_cols))  # preserve order, avoid duplicates
    column_dict = {}
    for col in cols:
        series = df[col]
        column_dict[(dataset_id, col)] = series
    return column_dict

# def get_relevant_metadata(self, dataset_id, outfile=None, retry_timeout=None):
#         self._ensure_logger()
#         if outfile is None:
#             outfile = f"metadata_{dataset_id}.txt"
        
#         # Use custom timeout if provided, otherwise use instance timeout
#         timeout_to_use = retry_timeout if retry_timeout is not None else self.timeout
        
#         try:
#             self._setup_client()
#             # Temporarily set timeout for this request
#             original_timeout = self.client.timeout
#             self.client.timeout = timeout_to_use
            
#             metadata = self.client.get_metadata(dataset_id)
            
#             # Reset timeout
#             self.client.timeout = original_timeout
            
#             # Build relevant metadata structure
#             relevant_metadata = {
#                 "category": metadata.get("category"),
#                 "format": metadata.get("viewType"),
#                 "tags": metadata.get("tags"),
#                 "downloadCount": metadata.get("downloadCount"),
#                 "viewCount": metadata.get("viewCount"),
#                 "createdAt": metadata.get("createdAt"),
#                 "publicationDate": metadata.get("publicationDate"),
#                 "updatedAt": metadata.get("viewLastModified")
#             }
            
#             # Only process columns for tabular datasets that are queryable
#             if relevant_metadata.get("format") == "tabular":
#                 # Check if this is a queryable dataset
#                 asset_type = metadata.get("assetType", "")
                
#                 # Skip column stats for non-queryable asset types
#                 if asset_type in ['filter', 'href', 'external', 'link', 'file', 'chart', 'map', 'story']:
#                     self.log.info(f"{dataset_id}: Non-queryable asset type '{asset_type}', skipping column stats")
                    
#                     # Still include basic schema info if available
#                     cols = metadata.get("columns") or []
#                     if cols:
#                         relevant_columns = [
#                             {
#                                 "name": c.get("fieldName"), 
#                                 "type": c.get("dataTypeName"),
#                             }
#                             for c in cols if c.get("fieldName")
#                         ]
#                         relevant_metadata["columns"] = relevant_columns
                        
#                         # Use metadata's rowCount if available
#                         if "rowCount" in metadata:
#                             relevant_metadata["rowCount"] = int(metadata["rowCount"])
                    
#                     return relevant_metadata
                
#                 # For queryable datasets (assetType == 'dataset'), proceed normally
#                 cols = metadata.get("columns") or []
#                 relevant_columns = [
#                     {
#                         "name": c.get("fieldName"), 
#                         "type": c.get("dataTypeName"),
#                     }
#                     for c in cols if c.get("fieldName")
#                 ]
                
#                 if relevant_columns:
#                     try:
#                         counts = self.fetch_all_column_stats(dataset_id, cols)
                        
#                         if counts and "total_rows" in counts:
#                             relevant_metadata["rowCount"] = int(counts["total_rows"])
                            
#                             for col in relevant_columns:
#                                 name = col["name"]
#                                 col["nulls"] = int(counts.get(f"{name}_nulls", 0))
#                                 col["semantic_nulls"] = int(counts.get(f"{name}_semantic_nulls", 0))
                            
#                             relevant_metadata["columns"] = relevant_columns
#                         else:
#                             self.log.warning(f"{dataset_id}: column stats incomplete, skipping column info")
                            
#                     except Exception as e:
#                         self.log.warning(f"{dataset_id}: failed to fetch column stats — {e}")
#                 else:
#                     self.log.warning(f"{dataset_id}: schema empty — skipping")
            
#             return relevant_metadata
            
#         except Exception as e:
#             error_str = str(e).lower()
#             is_timeout = 'timeout' in error_str or 'timed out' in error_str
#             is_connection = 'connection' in error_str or 'remote' in error_str
            
#             if is_timeout:
#                 self.log.error(f"{dataset_id}: timeout after {timeout_to_use}s — {e}")
#             elif is_connection:
#                 self.log.error(f"{dataset_id}: connection error — {e}")
#             else:
#                 self.log.error(f"{dataset_id}: failed to fetch metadata — {e}")
            
#             return None

#     def summarize_metadata(self): # relevant metadata must be downloaded first
#         outpath = self.metadatadir / "summary"
#         outpath.mkdir(exist_ok=True)
        
#         # Check if there are any JSON files in metadatadir
#         json_files = list(self.metadatadir.glob("*.json"))
        
#         if not json_files:
#             print(f"No metadata files found in {self.metadatadir}. Please run download_all_relevant_metadata() first.")
#             return
        
#         print(f"Found {len(json_files)} metadata files to analyze...")
        
#         # Load all JSON files into a list
#         metadata_list = []
#         invalid_count = 0
        
#         for file in json_files:
#             try:
#                 with open(file, 'r') as f:
#                     data = json.load(f)
                    
#                     # Validate the data
#                     if data is None:
#                         invalid_count += 1
#                         continue
                    
#                     if not isinstance(data, dict):
#                         invalid_count += 1
#                         continue
                    
#                     if not data:  # Empty dict
#                         invalid_count += 1
#                         continue
                    
#                     # Optionally check for required fields
#                     # if 'category' not in data and 'format' not in data:
#                     #     invalid_count += 1
#                     #     continue
                    
#                     metadata_list.append(data)
                    
#             except json.JSONDecodeError:
#                 invalid_count += 1
#                 continue
#             except Exception as e:
#                 print(f"Warning: Could not process {file}: {e}")
#                 invalid_count += 1
#                 continue
        
#         if not metadata_list:
#             print(f"No valid metadata found in {self.metadatadir}.")
#             return
        
#         if invalid_count > 0:
#             print(f"Warning: Skipped {invalid_count} invalid/empty metadata files")
        
#         print(f"Processing {len(metadata_list)} valid metadata files...")
        
#         df = pd.DataFrame(metadata_list)
        
#         # Tag Analysis
#         tags = df['tags'].explode()
#         tag_counts = tags.value_counts().reset_index()
#         tag_counts.columns = ['tag', 'count']
#         # tag_counts.to_json(outpath / "tag_counts.json", orient='records', indent=2)
#         tag_dct = dict(zip(tag_counts["tag"], tag_counts["count"]))
#         with open(outpath / "tag_counts.json", "w") as f:
#             json.dump(tag_dct, f, indent=2)
        
#         # Row Count Buckets
#         df['row_bucket'] = pd.cut(
#             df['rowCount'],
#             bins=[0, 1000, 10000, 100000, 1000000, 10000000, float('inf')],
#             labels=['0-1K', '1K-10K', '10K-100K', '100K-1M', '1M-10M', '10M+'],
#             right=False
#         )
#         bucket_counts = df['row_bucket'].value_counts().reset_index()
#         bucket_counts.columns = ['bucket', 'count']
#         bucket_counts = bucket_counts.sort_values('bucket')
#         # bucket_counts.to_json(outpath / "row_buckets.json", orient='records', indent=2)
#         row_dct = dict(zip(bucket_counts["bucket"], bucket_counts["count"]))
#         with open(outpath / "row_buckets.json", "w") as f:
#             json.dump(row_dct, f, indent=2)
        
#         # View Count Buckets
#         df['view_bucket'] = pd.cut(
#             df['viewCount'],
#             bins=[0, 100, 1000, 10000, float('inf')],
#             labels=['0-100', '100-1K', '1K-10K', '10K+'],
#             right=False
#         )
#         view_bucket_counts = df['view_bucket'].value_counts().reset_index()
#         view_bucket_counts.columns = ['bucket', 'count']
#         view_bucket_counts = view_bucket_counts.sort_values('bucket')
#         # view_bucket_counts.to_json(outpath / "view_buckets.json", orient='records', indent=2)
#         view_dct = dict(zip(view_bucket_counts["bucket"], view_bucket_counts["count"]))
#         with open(outpath / "view_buckets.json", "w") as f:
#             json.dump(view_dct, f, indent=2)

#         # Download Count Buckets
#         df['download_bucket'] = pd.cut(
#             df['downloadCount'],
#             bins=[0, 100, 1000, 10000, float('inf')],
#             labels=['0-100', '100-1K', '1K-10K', '10K+'],
#             right=False
#         )
#         download_bucket_counts = df['download_bucket'].value_counts().reset_index()
#         download_bucket_counts.columns = ['bucket', 'count']
#         download_bucket_counts = download_bucket_counts.sort_values('bucket')
#         # download_bucket_counts.to_json(outpath / "download_buckets.json", orient='records', indent=2)
#         download_dct = dict(zip(download_bucket_counts["bucket"], download_bucket_counts["count"]))
#         with open(outpath / "download_buckets.json", "w") as f:
#             json.dump(download_dct, f, indent=2)
        
#         # Category distribution
#         category_counts = df['category'].value_counts().reset_index()
#         category_counts.columns = ['category', 'count']
#         # category_counts.to_json(outpath / "categories.json", orient='records', indent=2)
#         category_dct = dict(zip(category_counts["category"], category_counts["count"]))
#         with open(outpath / "categories.json", "w") as f:
#             json.dump(category_dct, f, indent=2)
        
#         # Format distribution
#         format_counts = df['format'].value_counts().reset_index()
#         format_counts.columns = ['format', 'count']
#         # format_counts.to_json(outpath / "formats.json", orient='records', indent=2)
#         format_dct = dict(zip(format_counts["format"], format_counts["count"]))
#         with open(outpath / "formats.json", "w") as f:
#             json.dump(format_dct, f, indent=2)
        
#         # Age of publication in months
#         current_time = datetime.now().timestamp()

#         # Handle missing publicationDate values
#         df['age_months'] = ((current_time - df['publicationDate']) / (30.44 * 24 * 3600))
#         df['age_months'] = df['age_months'].fillna(-1).astype(int)

#         # Create counts
#         age_counts = df[df['age_months'] >= 0]['age_months'].value_counts()

#         # Fill in missing months with 0
#         if len(age_counts) > 0:
#             max_age = age_counts.index.max()
#             min_age = age_counts.index.min()
            
#             # Create complete range
#             full_range = pd.Series(0, index=range(min_age, max_age + 1))
            
#             # Update with actual counts
#             full_range.update(age_counts)
            
#             # Convert to dict
#             age_dct = full_range.to_dict()
#         else:
#             age_dct = {}

#         with open(outpath / "publication_age.json", "w") as f:
#             json.dump(age_dct, f, indent=2)

#         # Months since last update
#         df['months_since_update'] = ((current_time - df['updatedAt']) / (30.44 * 24 * 3600))
#         # Fill NaN values before converting to int
#         df['months_since_update'] = df['months_since_update'].fillna(-1).astype(int)

#         # Now create the counts, optionally filtering out invalid ages
#         update_counts = df[df['months_since_update'] >= 0]['months_since_update'].value_counts()
#         # Fill in missing months with 0
#         if len(update_counts) > 0:
#             max_update = update_counts.index.max()
#             min_update = update_counts.index.min()
#             # Create complete range
#             update_range = pd.Series(0, index=range(min_update, max_update + 1))
#             # Update with actual counts
#             update_range.update(update_counts)
#             # Convert to dict
#             update_dct = update_range.to_dict()
#         else:
#             update_dct = {}

#         with open(outpath / "last_update.json", "w") as f:
#             json.dump(update_dct, f, indent=2)

#         # Number of attributes (columns) per dataset
#         # Handle missing columns (NaN values)
#         df['num_attributes'] = df['columns'].apply(lambda x: len(x) if isinstance(x, list) else 0)

#         df['attr_bucket'] = pd.cut(
#             df['num_attributes'],
#             bins=[0, 10, 20, 30, 40, 50, float('inf')],
#             labels=['0-10', '10-20', '20-30', '30-40', '40-50', '50+'],
#             right=False
#         )
#         attr_counts = df['attr_bucket'].value_counts().reset_index()
#         attr_counts.columns = ['attribute_bucket', 'count']
#         attr_counts = attr_counts.sort_values('attribute_bucket')
#         # attr_counts.to_json(outpath / "attribute_counts.json", orient='records', indent=2)
#         attr_dct = dict(zip(attr_counts["attribute_bucket"], attr_counts["count"]))
#         with open(outpath / "attribute_counts.json", "w") as f:
#             json.dump(attr_dct, f, indent=2)
        
#         # Types of attributes (distribution of column types)
#         all_column_types = []
#         for columns_list in df['columns']:
#             # Skip if columns is NaN (float)
#             if isinstance(columns_list, list):
#                 for col in columns_list:
#                     all_column_types.append(col['type'])

#         type_counts = pd.Series(all_column_types).value_counts().reset_index()
#         type_counts.columns = ['type', 'count']
#         # type_counts.to_json(outpath / "column_types.json", orient='records', indent=2)
#         type_dct = dict(zip(type_counts["type"], type_counts["count"]))
#         with open(outpath / "column_types.json", "w") as f:
#             json.dump(type_dct, f, indent=2)
        
#         # Table sparseness (percentage of semantic_nulls across all columns)
#         sparseness_data = []
#         for idx, row in df.iterrows():
#             row_count = row['rowCount']
#             columns_list = row['columns']
            
#             # Skip if columns is NaN or rowCount is invalid
#             if isinstance(columns_list, list) and row_count > 0:
#                 null_percentages = []
#                 for col in columns_list:
#                     null_pct = (col['semantic_nulls'] / row_count * 100)
#                     null_percentages.append(null_pct)
                
#                 if null_percentages:
#                     avg_sparseness = sum(null_percentages) / len(null_percentages)
#                     sparseness_data.append(avg_sparseness)

#         if sparseness_data:  # Only create analysis if we have data
#             sparseness_df = pd.DataFrame({'avg_sparseness': sparseness_data})
#             sparseness_df['sparseness_bucket'] = pd.cut(
#                 sparseness_df['avg_sparseness'],
#                 bins=[0, 1, 5, 10, 25, 50, 100],
#                 labels=['< 1% sparse', '1-5% sparse', '5-10% sparse', '10-25% sparse', '25-50% sparse', '50%+ sparse'],
#                 right=False
#             )
            
#             sparseness_counts = sparseness_df['sparseness_bucket'].value_counts().reset_index()
#             sparseness_counts.columns = ['sparseness_bucket', 'count']
#             sparseness_counts = sparseness_counts.sort_values('sparseness_bucket')
#             # sparseness_counts.to_json(outpath / "table_sparseness.json", orient='records', indent=2)
#             sparseness_dct = dict(zip(sparseness_counts["sparseness_bucket"], sparseness_counts["count"]))
#             with open(outpath / "table_sparseness.json", "w") as f:
#                 json.dump(sparseness_dct, f, indent=2)
#         else:
#             print("No sparseness data available")
        
#         print(f"Analysis complete! Results saved to {outpath}")