from decorators import setup

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
    
    def null_counts(self, id, cols):
        """
        Docstring for null_counts
        
        :param self: object
        :param id: id of the desired dataset
        :param cols: columns object from metadata of the same id
        """
        usable_cols = []
        SKIP_TYPES = {"point", "location", "polygon", "multipolygon", "line", "multiline", "multipoint"} # These types break queries (1NF violation)
        for col in cols:
            field = col.get("fieldName", "")
            dtype = col.get("dataTypeName", "")

            if dtype in SKIP_TYPES:
                self.log.debug(f"{id}: Skipping geometry column '{field}' (type: {dtype})")
                continue
            else:
                usable_cols.append(self._build_chunk_select_clause(field, dtype))
        
        if not usable_cols:
            self.log.warning(f"{id}: No queryable columns found")
            return []
        
        select_clause = ', '.join(usable_cols)
        return self.select(id, select_clause)

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
    