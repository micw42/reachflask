import pandas as pd

def single_convert():
    results=pd.read_csv("singleSearchOut.csv")
    ids=results["id"].tolist()
    names=results["name"].tolist()
    
    result_dict={}
    for i in range(len(ids)):
        if ids[i] not in result_dict:
            result_dict[ids[i]]=[]
        result_dict[ids[i]].append(names[i])
    
    return result_dict

def multi_convert():
    results=pd.read_csv("multiSearchOut.csv")
    ids=results["id"].tolist()
    names=results["name"].tolist()
    queries=results["user_query"].tolist()
    
    result_dict={}
    for i in range(len(ids)):
        if queries[i] not in result_dict:
            result_dict[queries[i]]={}
        if ids[i] not in result_dict[queries[i]]:
            result_dict[queries[i]][ids[i]]=[]
        result_dict[queries[i]][ids[i]].append(names[i])
        
    return result_dict