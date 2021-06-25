import pandas as pd

def check(edges_table, queries_id):
    sources = edges_table["source_id"].tolist()
    targets = edges_table["target_id"].tolist()

    all_species = list(set(sources + targets))
    not_in=[]

    for query in queries_id:
        if query not in all_species:
            not_in.append(query)
        else:
            continue

    return not_in


