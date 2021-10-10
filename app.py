from flask import Flask
from markupsafe import escape
from flask import render_template
from flask import request, jsonify
import numpy
import json
import time
from es_helper import *
from rerank_helper import rerank
from log_file_helper import get_new_session_id, update_search_log, update_user_log

INDEX = "ctb-nlp-v1" # index to search e.g. "msmacro-full"
FIELDS = ["passage", "query", "alt_query"] # fields to search in elasticsearch retrieval e.g. ["passage", "query"]
ES_CUTOFF = 2 # number of entries retrieved by elasticsearch for reranking
PORT = 6002

app = Flask(__name__, static_url_path="")

def handel_search(query):
    search_session_id = get_new_session_id()
    
    print(f'> > > es searching for ... {query}')
    result_count, es_hits = es_search(query, cutoff = ES_CUTOFF, index=INDEX, fields = FIELDS)
    es_results = direct_es_search_result(search_session_id, query, es_hits)

    print('> > > reranking...')
    tic = time.time()
    model_results = rerank(es_results)
    toc = time.time()
    print(f'> > > that took {toc - tic} seconds')

    update_search_log(model_results)

    return model_results

# Return index html
@app.route("/")
def return_index():
    return render_template('index.html')

# get query post printed
@app.route('/search-req', methods=['POST', 'GET'])
def handel_search_req():
    query_input = request.form["queryInputBox"]
    request_type = request.form["reqType"]

    model_results = handel_search(query_input)
 
    return render_template('response.html', searchResult = model_results)

@app.route('/search-api', methods=['GET'])
def api_handelling():
    # check if things exist
    print('api req received')
    
    try:
        query_input = request.args['queryInputBox']
        request_type = request.args['reqType']
    except:
        return "Error: request incomplete. plz include 'queryInputBox' and 'reqType' in req artument."

    model_results = handel_search(query_input)

    if request_type == "json":
        result_dic = {
                'search_session_id': model_results.search_session_id,
                'query_input': model_results.query_input, 
                'table': model_results.table
            }
        
        # the numpy.int64 data type doesn't work with json so we need to fix this by copying code from somewhere
        def convert(o):
            if isinstance(o, numpy.int64): return int(o)  
            raise TypeError
        json_response = json.dumps(result_dic, default=convert)

        return json_response
    else:
        return "err something is wrong. are you requesting for a json?"


# logging user activity
@app.route('/log-req', methods=['POST'])
def handel_log_req():
    sessionID = json.loads(request.data)["sessionID"]
    actionType = json.loads(request.data)["actionType"]
    pid = json.loads(request.data)["pid"]
    rank = json.loads(request.data)["rank"]
    print(f"> > > Logging Action: for session: {sessionID}, do: {actionType}, to pid {pid} rank: {rank}")
    update_user_log(sessionID, actionType, pid, rank)

    return "you shouldn't see this message"
    

# run the thing
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)