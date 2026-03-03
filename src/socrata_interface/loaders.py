import json
from util.util import setup_dir

def write_domain_ids(domain, ids):
    path = setup_dir(domain)
    full_path = path / f"{domain}_ids.txt"
    with full_path.open("w", encoding="utf-8") as f:
        for dataset_id in ids:
            f.write(dataset_id + "\n")
    return full_path

def write_data(domain, id, data, type_of):
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