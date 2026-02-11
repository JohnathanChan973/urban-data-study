    # def write_dataset_ids_to_file(self, filepath=None):
    #     self.ids = list(self.city_datasets_ids())
    #     if filepath is None:
    #         filepath = f"{self.sanitized}_ids.txt"
    #     full_path = self.base / filepath
    #     with full_path.open("w", encoding="utf-8") as f:
    #         for dataset_id in self.ids:
    #             f.write(dataset_id + "\n")
    #     return full_path

    # def download_all_raw_dataset(self):
    #     for dataset_id in self._set_up_ids():
    #         outfile = f"data_{dataset_id}.json"
    #         outpath = self.datadir / outfile
    #         if outpath.exists():
    #             continue
    #         self.download_raw_dataset(dataset_id)

# def download_raw_dataset(self, dataset_id, outfile=None):
    #     self._ensure_logger()
    #     url = f"https://{self.domain}/resource/{dataset_id}.json"
    #     try:
    #         resp = requests.get(url, timeout=self.timeout)
    #     except Exception as e:
    #         self.log.error(f"{dataset_id}: network error — {e}")
    #         return None

    #     # Try getting JSON first, even on 40x/50x errors
    #     payload = None
    #     try:
    #         payload = resp.json()
    #     except ValueError:
    #         pass   # Response body is not JSON

    #     # If Socrata returned a JSON error block:
    #     # e.g. {"error": true, "message": "...", "code": "..."}
    #     if isinstance(payload, dict) and payload.get("error"):
    #         self.log.error(f"{dataset_id}: Socrata error — {payload.get('message')}")
    #         return None

    #     # Now let HTTP errors raise only if it's NOT a Socrata dataset error
    #     try:
    #         resp.raise_for_status()
    #     except Exception as e:
    #         self.log.error(f"{dataset_id}: HTTP error — {e}")
    #         return None

    #     # Handle empty array
    #     if isinstance(payload, list) and all(not row for row in payload):
    #         self.log.warning(f"{dataset_id}: empty dataset")
    #         return None

    #     # If we get here, payload is valid — save it
    #     if outfile is None:
    #         outfile = f"data_{dataset_id}.json"
    #     self._ensure_data_dir()
    #     outpath = self.datadir / outfile
    #     outpath.write_bytes(resp.content)

    # def download_all_schema(self):
    #     for dataset_id in self._set_up_ids():
    #         outfile = f"schema_{dataset_id}.txt"
    #         outpath = self.schemadir / outfile
    #         if outpath.exists():
    #             continue
    #         self.download_schema(dataset_id)

    # def download_schema(self, dataset_id, outfile=None):
    #     self._ensure_logger()
    #     if outfile is None:
    #         outfile = f"schema_{dataset_id}.txt"
    #     data_file = self.datadir / f"{dataset_id}.json"
    #     schema = None
    #     if data_file.exists():
    #         try:
    #             with data_file.open() as f:
    #                 payload = json.load(f)
    #             if isinstance(payload, list) and payload:
    #                 # Find the first non-empty dict
    #                 record = next(
    #                     (row for row in payload if isinstance(row, dict) and row),
    #                     None
    #                 )
    #                 if record:
    #                     schema = list(record.keys())
    #                 else:
    #                     # All objects are empty
    #                     self.log.warning(
    #                         f"{dataset_id}: JSON file contains only empty objects — schema skipped"
    #                     )
    #                     return None
    #             else:
    #                 # JSON is [] or invalid structure
    #                 self.log.warning(
    #                     f"{dataset_id}: JSON file is empty or malformed — schema skipped"
    #                 )
    #                 return None
    #         except Exception as e:
    #             self.log.warning(f"{dataset_id}: failed to parse JSON — {e}")
    #             return None
    #     else:
    #         try:
    #             self._setup_client()
    #             metadata = self.client.get_metadata(dataset_id)
    #             cols = metadata.get("columns") or []
    #             schema = [c.get("fieldName") for c in cols if c.get("fieldName")]
    #         except Exception as e:
    #             self.log.error(f"{dataset_id}: failed to fetch metadata — {e}")
    #             return None
    #     if not schema:
    #         self.log.warning(f"{dataset_id}: schema empty — skipping file write")
    #         return None
    #     self._ensure_schema_dir()
    #     outpath = self.schemadir / outfile
    #     outpath.write_text("\n".join(schema), encoding="utf-8")
    #     return outpath
    
    # def load_dataset_to_df(self, dataset_id):
    #     self._ensure_logger()
    #     data_path = (self.datadir / f"{dataset_id}.json")
    #     if data_path.exists():
    #         with data_path.open("r", encoding="utf-8") as f:
    #                 data = json.load(f)
    #             # If the file is not a list of dicts, wrap to avoid crash.
    #         if not isinstance(data, list):
    #             data = []
    #         return pd.DataFrame.from_records(data)
    #     else: # If the file is not downloaded, fetch it via the api
    #         try:
    #             self._setup_client()
    #             table = self.client.get(dataset_id)
    #         except requests.exceptions.HTTPError as e:
    #             self.log.error(f"{dataset_id}: Socrata error — {e}")
    #             return pd.DataFrame([]) # return clean empty DataFrame
    #         except Exception as e:
    #             # broad fallback so unexpected errors never crash the loader
    #             self.log.error(f"{dataset_id}: Unexpected error — {e}")
    #             return pd.DataFrame([])
    #         if not isinstance(table, list):
    #             table = []
    #         return pd.DataFrame.from_records(table)

# def download_all_relevant_metadata(self, max_retries=2, progressive_timeout=True, max_timeout=60):
#         """
#         Download metadata for all datasets with optional retry and progressive timeout.
        
#         Args:
#             max_retries: Number of times to retry failed downloads
#             progressive_timeout: If True, increase timeout on retry
#             max_timeout: Maximum timeout to use
#         """
#         self._ensure_meta_dir()
        
#         failed_downloads = []
#         successful = 0
#         skipped = 0
        
#         for dataset_id in self._set_up_ids():
#             outfile = f"metadata_{dataset_id}.json"
#             outpath = self.metadatadir / outfile
            
#             # Skip if already exists and not empty
#             if outpath.exists():
#                 try:
#                     with outpath.open("r") as f:
#                         existing = json.load(f)
#                         if existing:  # Not empty
#                             skipped += 1
#                             continue
#                 except:
#                     pass  # File exists but corrupted, re-download
            
#             # Try downloading with retries
#             metadata = None
#             current_timeout = self.timeout
            
#             for attempt in range(max_retries):
#                 if progressive_timeout and attempt > 0:
#                     current_timeout = min(current_timeout * 1.5, max_timeout)
                
#                 metadata = self.get_relevant_metadata(dataset_id, retry_timeout=current_timeout)
                
#                 if metadata:
#                     successful += 1
#                     break
                
#                 # If failed and not last attempt, wait before retry
#                 if attempt < max_retries - 1:
#                     time.sleep(1)
            
#             # Save if we got metadata
#             if metadata:
#                 with outpath.open("w", encoding="utf-8") as f:
#                     json.dump(metadata, f, indent=2, ensure_ascii=False)
#             else:
#                 failed_downloads.append(dataset_id)
        
#         # Log summary
#         if hasattr(self, 'log'):
#             self.log.info(f"Download complete: {successful} successful, {skipped} skipped, {len(failed_downloads)} failed")
#             if failed_downloads:
#                 self.log.warning(f"Failed dataset IDs: {failed_downloads[:10]}{'...' if len(failed_downloads) > 10 else ''}")
        
#         return {
#             'successful': successful,
#             'skipped': skipped,
#             'failed': failed_downloads
#         }