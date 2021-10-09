# we will use elasticsearch-dsl this time; a higher level python es client
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from elasticsearch_dsl import Q
es_client = Elasticsearch()
from pprint import pprint

# this is the class for the thing returned to the front end
class search_results_data:
    def __init__(self, search_session_id, query_input, ranks, qids, q_labels, alt_qids, alt_q_labels, pids, passages, citations, scores):
        """
        these are metas of a search result:
            search_session_id - intiger, unique for each search session
            query_input - string, the query

        all of the below should be of the same length and in order, they will be stored in self.table:
            ranks - list of ranks
            qids - list of ranks
            q_labels - list of ranks
            alt_qids - list of ranks
            alt_q_labels - list of ranks
            pids - list of pids
            passages - list of passages
            citations - list of citations
            scores - list of scores from search matching
            citations - list of citations from search matching
        """
        assert len(ranks)==len(qids)==len(q_labels)==len(alt_qids)==len(alt_q_labels)==len(pids)==len(citations)==len(passages)==len(scores)
        table = []
        for i, rank in enumerate(ranks):
            table.append({
                "rank": ranks[i],
                "qid": qids[i],
                "q_label": q_labels[i],
                "alt_qid": alt_qids[i],
                "alt_q_label": alt_q_labels[i],
                "pid": pids[i],
                "passage": passages[i],
                "citation": citations[i],
                "score": scores[i],
            })
        self.search_session_id = search_session_id
        self.query_input = query_input
        self.table = table

def es_search(query, cutoff = 1000, index="ctb-nlp-v1", fields = ["passage", "query"]):
    q = Q({"multi_match": {"query": query, "fields": fields}})

    s = Search(using=es_client, index=index).query(q)

    s.update_from_dict({"size": cutoff})

    response = s.execute()
    response_dict = response.to_dict()
    hits = response_dict['hits']['hits']
    result_count = len(hits)
    return result_count, hits

def direct_es_search_result(search_session_id, query_input, hits):
    '''
    this parses the search result and returns the search results object
    '''
    ranks, qids, q_labels, alt_qids, alt_q_labels, pids, passages, citations, scores = [], [], [], [], [], [], [], [], []

    for index, hit in enumerate(hits):
        ranks.append(index)
        qids.append(hit['_source']['qid'])
        q_labels.append(hit['_source']['query'])
        alt_qids.append(hit['_source']['alt_qid'])
        alt_q_labels.append(hit['_source']['alt_query'])
        pids.append(hit['_source']['pid'])
        passages.append(hit['_source']['passage'])
        citations.append(hit['_source']['citation'])
        scores.append(hit['_score'])
    
    result = search_results_data(
        search_session_id = search_session_id,
        query_input = query_input,
        ranks = ranks, 
        pids = pids, 
        qids = qids, 
        q_labels = q_labels, 
        alt_qids = alt_qids, 
        alt_q_labels = alt_q_labels, 
        passages = passages, 
        citations = citations, 
        scores = scores
    )

    return result
