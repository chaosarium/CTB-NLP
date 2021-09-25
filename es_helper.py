# we will use elasticsearch-dsl this time; a higher level python es client
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from elasticsearch_dsl import Q
es_client = Elasticsearch()
from pprint import pprint

# this is the search result object
from app import search_results_data

def es_search(query, cutoff = 1000, index="msmacro-full", fields = ["passage", "query"]):
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
    ranks, qids, pids, query_labels, passages, scores = [], [], [], [], [], []

    for index, hit in enumerate(hits):
        ranks.append(index)
        qids.append(hit['_source']['qid'])
        pids.append(hit['_source']['pid'])
        query_labels.append(hit['_source']['query'])
        passages.append(hit['_source']['passage'])
        scores.append(hit['_score'])
    
    result = search_results_data(
        search_session_id = search_session_id,
        query_input = query_input,
        ranks = ranks, 
        qids = qids, 
        pids = pids, 
        query_labels = query_labels, 
        passages = passages, 
        scores = scores
    )

    return result
