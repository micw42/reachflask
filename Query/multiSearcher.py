import pandas as pd

def name_query(name, nodes, full_df, string_type):
    if string_type == "starts_with":
        name_query = full_df.query('name.str.startswith(@name, na=False)', engine='python').reset_index(drop=True)
    
    elif string_type == "ends_with":
        name_query = full_df.query('name.str.endswith(@name, na=False)', engine='python').reset_index(drop=True)
    
    elif string_type == "contains":
        name_query = full_df.query('name.str.contains(@name, na=False)', engine='python').reset_index(drop=True)

    # The following nodes are in the network, but REACH likely grounds to more
    in_net = pd.merge(nodes, name_query, left_on="Only_Id", right_on="id", how="inner").iloc[:, 3:5].drop_duplicates().reset_index(drop=True)
    in_net["user_query"] = name
    return in_net


def multi_query(query_list, nodes, full_df):
    # initialize empty dataframe
    full_query = pd.DataFrame()

    for query in query_list:
        full_query = full_query.append(name_query(query, nodes, full_df))

    return full_query


def query(query_list, nodes, full_df):
    
    # Turns all entries into lower case
    case_proof = [x.lower() for x in query_list]

    multi_query(case_proof, nodes, full_df).to_csv("multiSearchOut.csv", index=False)
