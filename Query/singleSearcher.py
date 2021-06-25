import pandas as pd

def name_query(name, nodes, full_df):
    
    # Note: this searches the df for the query name anywhere
    name_query = full_df.query('name.str.contains(@name, na=False)', engine='python').reset_index(drop=True)

    # The following nodes are in the network, but REACH likely grounds to more
    in_net = pd.merge(nodes, name_query, left_on="Only_Id", right_on="id", how="inner").iloc[:, 3:5].drop_duplicates().reset_index(drop=True)

    return in_net


def query(name, nodes, full_df):
    
    name_query(name, nodes, full_df).to_csv("singleSearchOut.csv", index=False)
