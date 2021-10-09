# we will use elasticsearch-dsl this time; a higher level python es client
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from elasticsearch_dsl import Q
es_client = Elasticsearch()
from pprint import pprint

# this is the search result object
from app import search_results_data

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
    ranks, pids, passages, citations, scores = [], [], [], [], []

    for index, hit in enumerate(hits):
        ranks.append(index)
        pids.append(hit['_source']['pid'])
        passages.append(hit['_source']['passage'])
        citations.append(hit['_source']['citation'])
        scores.append(hit['_score'])
    
    result = search_results_data(
        search_session_id = search_session_id,
        query_input = query_input,
        ranks = ranks, 
        pids = pids, 
        passages = passages, 
        citations = citations, 
        scores = scores
    )

    return result
