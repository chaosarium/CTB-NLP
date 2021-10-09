from flask import Flask
from markupsafe import escape
from flask import render_template
from flask import request
import json
from es_helper import *
from rerank_helper import rerank
from log_file_helper import get_new_session_id, update_search_log, update_user_log

INDEX = "ctb-nlp-v1" # index to search e.g. "msmacro-full"
FIELDS = ["passage", "query", "alt_query"] # fields to search in elasticsearch retrieval e.g. ["passage", "query"]
ES_CUTOFF = 10 # number of entries retrieved by elasticsearch
PORT = 6002

app = Flask(__name__, static_url_path="")

# Return index html
@app.route("/")
def return_index():
    return render_template('index.html')

# this is the class for the thing returned to the front end
class search_results_data:
    def __init__(self, search_session_id, query_input, ranks, pids, passages, citations, scores):
        """
        these are metas of a search result:
            search_session_id - intiger, unique for each search session
            query_input - string, the query

        all of the below should be of the same length and in order, they will be stored in self.table:
            ranks - list of ranks
            pids - list of pids
            passages - list of passages
            citations - list of citations
            scores - list of scores from search matching
            citations - list of citations from search matching
        """
        assert len(ranks)==len(pids)==len(citations)==len(passages)==len(scores)
        table = []
        for i, rank in enumerate(ranks):
            table.append({
                "rank": ranks[i],
                "pid": pids[i],
                "passage": passages[i],
                "citation": citations[i],
                "score": scores[i],
            })
        self.search_session_id = search_session_id
        self.query_input = query_input
        self.table = table

# get query post printed
@app.route('/search-req', methods=['POST'])
def handel_search_req():
    query_input = request.form["queryInputBox"]
    search_session_id = get_new_session_id()

    # do some retrieval and ranking here
    dummy_result = search_results_data(
        search_session_id = search_session_id,
        query_input = query_input,
        ranks = [1,2,3], 
        pids = [15324, 124, 642], 
        passages = ["名侦探柯南 国语版-动漫动画-全集高清正版视频在线观看-爱奇艺", "名侦探柯南国语版全集(国语) 名侦探柯南国语版动漫全集 在线观看 - 哈哈动漫网", "名侦探柯南(国语)-名侦探柯南(国语)全集(1-837共1000集)-动画片 - 搜狐视频"], 
        citations = ["citation 1", "citation 2", "citation 3"], 
        scores = [0.231, 0.123, 0.095]
    )

    result_count, es_hits = es_search(query_input, cutoff = ES_CUTOFF, index=INDEX, fields = FIELDS)
    es_results = direct_es_search_result(search_session_id, query_input, es_hits)

    print('**reranking**')
    model_results = rerank(es_results)

    update_search_log(model_results)
 
    return render_template('response.html', searchResult = model_results)

# logging user activity
@app.route('/log-req', methods=['POST'])
def handel_log_req():
    sessionID = json.loads(request.data)["sessionID"]
    actionType = json.loads(request.data)["actionType"]
    pid = json.loads(request.data)["pid"]
    rank = json.loads(request.data)["rank"]
    print(f"█ Logging Action: for session: {sessionID}, do: {actionType}, to pid {pid} rank: {rank}")
    update_user_log(sessionID, actionType, pid, rank)

    return "you shouldn't see this message"
    

# run the ting
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6002)