from flask import Flask, render_template, url_for, request, redirect
from Query import llNetxQuery, DictChecker, BidirectionalSingleQuery, NetxSingleQuery, singleSearcher, multiSearcher, convertSearch
from Visualization import to_json, to_json_netx
import pandas as pd
import colorama as clr
import networkx as nx
import time

app = Flask(__name__)

start = time.time()

print("Reading edges...", end="\x1b[1K\r")
edges_df=pd.read_pickle("./pickles/edges_table.pkl")
print("Loaded edges.")

print("Reading nodes...", end="\x1b[1K\r")
nodes_df=pd.read_pickle("./pickles/nodes_table_all_labelled.pkl")
print("Loaded nodes.")

print("Reading evidence...", end="\x1b[1K\r")
ev_df=pd.read_pickle("./pickles/evidence.pkl")
print("Loaded evidence.")

print("Reading databases...", end="\x1b[1K\r")
full_df=pd.read_pickle("./pickles/combinedDBs.pkl")
print("Loaded databases.")

print(f"{clr.Fore.GREEN}Loaded pickles in {round(time.time() - start, 3)}s.{clr.Style.RESET_ALL}")

G = nx.from_pandas_edgelist(edges_df, edge_attr=True, source="source_id", target="target_id", create_using=nx.DiGraph())


@app.route('/')
def home():
    return render_template("home.html")

@app.route("/selectQuery", methods=["POST","GET"])
def select_query():
    if request.method=="POST":
        query_type=request.form["query_type"]
        if query_type=="Make a Multi Query":
            query_type="dijkstra"
            return redirect(url_for("validate", query_type=query_type))
        else:
            query_type="single"
            return redirect(url_for("validate", query_type=query_type))
    else:
        return render_template("select_query.html")
    
@app.route('/validate/<query_type>', methods=["POST","GET"])
def validate(query_type):
    global edges_df
    if request.method=="POST":
        if request.form["queryType"]=="id":
            query=request.form["query"].split(",")
            not_in=DictChecker.check(edges_df, query)
            if len(not_in)==0:
                not_in="NONE"
            else:
                not_in="SEPARATOR".join(not_in)
            query=request.form["query"]
            return redirect(url_for("display_options", not_in=not_in, query_type=query_type, query=query))
        else:
            query=request.form["query"]
            #Remove spaces from query entries
            query=query.replace(" ","SPACE")
            string_type=request.form["queryType"]
            return redirect(url_for("pick_query", query_type=query_type, query=query, string_type=string_type))

    else:
        if query_type=="single":
            return render_template("validate_single.html")
        else:
            return render_template("validate_bfs.html")

@app.route('/pick_query/<query_type>/<query>/<string_type>', methods=["POST","GET"])
def pick_query(query_type, query, string_type):
    global nodes_df
    global full_df
    
    query_with_sep=query.split(",")
    query=query.replace("SPACE"," ")
    if query_type=="single":
        singleSearcher.query(query, nodes_df, full_df, string_type)
        result_dict=convertSearch.single_convert()
    else:
        name_query=query
        query=query.split(",")
        multiSearcher.query(query, nodes_df, full_df, string_type)
        result_dict=convertSearch.multi_convert()
        
    none_found=False
    if not result_dict:
        none_found=True

    if request.method=="POST":
        if query_type=="single": 
            selected=request.form["selected"]
            if request.form["selected"]=="Try another query":
                return redirect(url_for("select_query"))
            return redirect(url_for("make_single_query", query=selected))
        else:
            if request.form["submit"]=="Try another query":
                return redirect(url_for("select_query"))
            print(result_dict)
            query_list=[]
            for query in result_dict:
                query_list.append(request.form[query])
            query_list=",".join(query_list)
            return redirect(url_for("make_bfs_query", query=query_list,))
          
    else:
        if query_type=="single":
            return render_template("pick_results_single.html", result_dict=result_dict, none_found=none_found)
        else:
            not_in=list(set([q.lower() for q in query_with_sep])-set([k.lower() for k in result_dict.keys()]))
            return render_template("pick_results_multi.html", query=query, result_dict=result_dict, not_in=not_in, none_found=none_found)
        
    
@app.route('/options/<query_type>/<not_in>/<query>', methods=["POST","GET"])
def display_options(not_in, query_type, query):
    not_in=not_in.split("SEPARATOR")
    query_parts=query.split(",")
    present=list(set(query_parts)-set(not_in))
    if request.method=="POST":
        choice=request.form["choice"]
        if choice=="Try another query":
            return redirect(url_for("select_query"))
        else:
            if query_type=="dijkstra":
                return redirect(url_for("make_bfs_query", query=query))
            elif query_type=="single":
                return redirect(url_for("make_single_query", query=query))
    else:
        return render_template("validate_result.html", not_in=not_in, query_type=query_type, present=present, query=query)

@app.route('/bfs/<query>', methods=["POST","GET"])
def make_bfs_query(query):
    if request.method=="POST":
        query_string=query
        max_linkers=int(request.form["max_linkers"])
        return redirect(url_for("bfs_query_result",query_string=query_string, max_linkers=max_linkers))
    else:
        return render_template("bfs_search.html", query=query)

@app.route('/single_query', methods=["POST","GET"])
@app.route('/single_query/<query>', methods=["POST","GET"])
def make_single_query(query=None):
    if request.method=="POST":
        depth=request.form["depth"]
        thickness_bound1=request.form["thickness_bound1"]
        thickness_bound2=request.form["thickness_bound2"]
        return redirect(url_for("single_query_result",query=query, depth=depth, thickness_bound1=thickness_bound1, thickness_bound2=thickness_bound2))
    else:
        return render_template("single_search.html")


@app.route('/bfsresult/<query_string>/<max_linkers>')
def bfs_query_result(query_string, max_linkers):
    global edges_df
    global nodes_df
    global ev_df
    global G

    queries_id=query_string.split(",")

    max_linkers=int(max_linkers)

    llNetxQuery.query(G, edges_df, nodes_df, ev_df, queries_id, max_linkers)
    no_path_file=open("no_path.txt","r")
    no_path=[line.rstrip("\n") for line in no_path_file]

    elements=to_json_netx.clean()
    return render_template("bfs_result.html", elements=elements, no_path=no_path)



@app.route('/singleresult/<query>/<depth>/<thickness_bound1>/<thickness_bound2>')
def single_query_result(query, depth, thickness_bound1, thickness_bound2, methods=["GET"]):
    global edges_df
    global nodes_df
    global ev_df
    global G

    depth=int(depth)
    thickness_bound1=int(thickness_bound1)
    thickness_bound2=int(thickness_bound2)

    NetxSingleQuery.query(G, edges_df, nodes_df, ev_df, query, depth, thickness_bound1, thickness_bound2)
    elements=to_json.clean()
    return render_template("single_query_result.html", elements=elements)

@app.route("/process", methods=["POST"])
def process_data():
    query=request.form["next_query"]
    return redirect(url_for("make_single_query", query=query))

@app.route("/go_home", methods=["POST"])
def go_home():
    return redirect(url_for("home"))

if __name__=="__main__":
    print(f'\n{clr.Fore.BLUE}*****  IGNORE ADDRESS GIVEN BELOW. RUN USING localhost:5001  *****\n')
    app.run(host='0.0.0.0', port=5001, debug=True)