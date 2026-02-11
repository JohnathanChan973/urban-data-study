import time
from sodapy import Socrata
from functools import wraps

MAX_TIMEOUT = 60

def setup(times=3, delay=2):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if not self.log:
                self.log = self.setup_logger(self.domain)

            self.log.info(f"Task Started for {self.domain}: {func.__name__}")

            for i in range(times):
                try:
                    if not self.client:
                        print(f"Initializing client for {self.domain}...")
                        self.client = Socrata(self.domain, self.token, timeout=self.timeout)
                    elif self.timeout > self.client.timeout:
                        self.client.timeout = self.timeout
                    self.timeout = min(self.timeout*2, MAX_TIMEOUT)

                    result = func(self, *args, **kwargs)
                    
                    self.log.info(f"Task Successful for {self.domain}: {func.__name__}")
                    return result
                
                except Exception as e:
                    if i == times - 1:
                        self.log.error(f"Final failure in for {self.domain}'s {func.__name__}: {str(e)}")
                        raise e
                    self.log.warning(f"Attempt {i+1}/{times} failed for {self.domain}'s {func.__name__}: {str(e)}")
                    time.sleep(delay)
        return wrapper
    return decorator

class Domain:    
    def __init__(self, domain, token=None, timeout=15):
        __slots__ = ("domain", "token", "timeout", "client", "log")

        self.domain = domain
        self.token = token
        self.timeout = timeout
        self.client = None
        self.log = None

    @setup()
    def datasets_generator(self, **kwargs):
        """
        Calls the library, yields items one by one, 
        then ensures the big list is cleared.
        """
        data = self.client.datasets(**kwargs)
        
        # Yield each item individually
        for item in data:
            yield item
            
        # Manual cleanup after the loop finishes
        del data 

    def city_datasets_count(self):
        # Counts using the generator
        return sum(1 for _ in self.datasets_generator())
        
    def city_datasets_ids(self):
        return map(lambda x: x.get("resource", {}).get("id"), self.datasets_generator())

    @setup()
    def dataset(self, id, all_data=False):
        return self.client.get_all(id) if all_data else self.client.get(id)
    
    @setup()
    def metadata(self, id):
        return self.client.get_metadata(id)
    
    @setup()
    def select(self, id, query):
        return self.client.get(id, select=query)

    def row_counts(self, id):
        return self.select(id, "count(*)")
    
    def null_counts(self, dataset_id, cols):
        """
        Docstring for null_counts
        
        :param self: object
        :param dataset_id: id of the desired dataset
        :param cols: columns object from metadata of the same id
        """
        usable_cols = []
        SKIP_TYPES = {"point", "location", "polygon", "multipolygon", "line", "multiline", "multipoint"} # These types break queries (1NF violation)
        for col in cols:
            field = col.get("fieldName", "")
            dtype = col.get("dataTypeName", "")

            if dtype in SKIP_TYPES:
                self.log.debug(f"{dataset_id}: Skipping geometry column '{field}' (type: {dtype})")
                continue
            else:
                usable_cols.append(self._build_chunk_select_clause(field, dtype))
        
        if not usable_cols:
            self.log.warning(f"{dataset_id}: No queryable columns found")
            return []
        
        select_clause = ', '.join(usable_cols)
        return self.select(dataset_id, select_clause)

    def _build_chunk_select_clause(self, field, dtype):
        """
        Builds a SELECT clause with simplified semantic null checks.
        """
        select_parts = []

        quoted_field = self._quote_field_name(field)
        safe_alias = field.replace(":", "_").replace("@", "_").replace("-", "_")
        
        # null count
        select_parts.append(
            f"(count(*) - count({quoted_field})) AS {safe_alias}_nulls"
        )
        
        # Simplified semantic nulls for text fields only
        TEXT_LIKE_TYPES = {"text", "url", "email", "phone", "html"}
        if dtype in TEXT_LIKE_TYPES:
            # Simpler check - just trim and empty string
            semantic = (
                f"sum(CASE WHEN "
                f"{quoted_field} IS NULL OR "
                f"trim({quoted_field}) = '' "
                f"THEN 1 ELSE 0 END) AS {safe_alias}_semantic_nulls"
            )
            select_parts.append(semantic)
        
        return ", ".join(select_parts)

    def _quote_field_name(self, field):
        """
        Quote field names that need it (contain special characters).
        """
        special_chars = {':', '@', '-', ' ', '.', '/', '\\', '(', ')'}
        if any(c in field for c in special_chars):
            escaped = field.replace('`', '``')
            return f"`{escaped}`"
        return field
    