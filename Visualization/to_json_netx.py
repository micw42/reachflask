import pandas as pd
import numpy as np



def clean_nodes():

    nodes_df=pd.read_csv("query_nodes.csv",header = 0)

    return nodes_df

def clean_edges():

    edges_df=pd.read_csv("query_edges.csv",header = 0)

    #Take square root of thickness column so values aren't too big
    edges_df["thickness"]=5*np.sqrt(edges_df["thickness"])

    #Convert the color col into hex color strings
    def get_color(color_val):
        if float(color_val)<.1:
            return "#ff0000"
        elif float(color_val)<.2:
            return "#ff4545"
        elif float(color_val)<.3:
            return "#ff7a7a"
        elif float(color_val)<.4:
            return "#ffb0b0"
        elif float(color_val)<.5:
            return "#ffffff"
        elif float(color_val)<.6:
            return "#dbe8ff"
        elif float(color_val)<.7:
            return "#99beff"
        elif float(color_val)<.8:
            return "#669eff"
        elif float(color_val)<.9:
            return "#2b79ff"
        return "#005eff"

    edges_df["color_col"]=edges_df["color_col"].apply(get_color)

    return edges_df

#Convert nodes and edges tables into one json-style list
def convert(nodes_df, edges_df):

    nodes=[]
    for _, row in nodes_df.iterrows():
        parts=row.values.tolist()
        nodes.append(parts)

    elements=[]
    for node in nodes:
        node_dict={"data":{"id":node[2], "label":node[1]}}
        elements.append(node_dict)

    edges=[]
    for _, row in edges_df.iterrows():
        parts=row.values.tolist()
        edges.append(parts)

    for edge in edges:
        edge_id=edge[1]+edge[3]
        edge_dict={"data":{"id":edge_id, "source":edge[1], "target":edge[3], "weight":5*edge[5], "color":edge[4], "ev":edge[6]}}
        elements.append(edge_dict)


    return elements

def clean():
    nodes_df=clean_nodes()
    edges_df=clean_edges()
    return convert(nodes_df, edges_df)





