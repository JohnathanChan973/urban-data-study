import json
from util.util import setup_dir

def write_domain_ids(domain, ids):
    path = setup_dir(domain)
    full_path = path / f"{domain}_ids.txt"
    with full_path.open("w", encoding="utf-8") as f:
        for dataset_id in ids:
            f.write(dataset_id + "\n")
    return full_path

def write_data(domain, id, type_of, data):
    """
    Function to write data to a file

    domain: The domain, ie data.city.gov
    id: The id of the dataset being used
    data: The data being written
    type_of: The type of data, such as the metadata or actual data
    """
    if not data:
        return None
    outfile = f"{id}_{type_of}.json"
    output_dir = setup_dir(domain, f"{type_of}s")
    outpath = output_dir / outfile
    if isinstance(data, list):
        outpath.write_bytes(data)
    elif isinstance(data, dict):
        with outpath.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    else:
        return None
    return outpath

def read_domain_ids(domain):
    """
    Generator for ids of a domain that has been saved previously
    """
    path = setup_dir(domain)
    full_path = path / f"{domain}_ids.txt"
    with full_path.open("r", encoding="utf-8") as f:
        for line in f:
            yield line.strip()

def read_data(domain, id, type_of):
    infile = f"{id}_{type_of}.json"
    input_dir = setup_dir(domain, f"{type_of}s")
    inpath = input_dir / infile
    if inpath.exists():
        with inpath.open() as f:
            return(json.load(f))
    return None
            
    