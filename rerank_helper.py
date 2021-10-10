from sentence_transformers import SentenceTransformer
from pprint import pprint
import torch
from sentence_transformers import util

# Define parameters for rerank algorithm
QUERY_CHUNK_SIZE = 100
CORPUS_CHUNK_SIZE = 500000
TOP_K = 10
SCORE_FUNCTION = util.dot_score # util.cos_sim or util.dot_score

if torch.cuda.is_available():
    DEVICE = torch.device("cuda:0")  
    print("Running on the GPU")
else:
    DEVICE = torch.device("cpu")
    print("Running on the CPU")

model = SentenceTransformer('models/multilingual-mpnet-ctb-finetuned', device=DEVICE)

def rerank(es_results):
    '''
    gets a result table, reranks it, and returns a reranked result table
    '''
    passages = [hit['passage'] for hit in es_results.table]
    queries = [es_results.query_input]
    query_embeddings = model.encode(queries, convert_to_tensor=True)
    sentence_embeddings = model.encode(passages, convert_to_tensor=True)

    sentence_embeddings = sentence_embeddings.to(DEVICE)
    sentence_embeddings = util.normalize_embeddings(sentence_embeddings)

    query_embeddings = query_embeddings.to(DEVICE)
    query_embeddings = util.normalize_embeddings(query_embeddings)

    reranked_ranking = util.semantic_search(query_embeddings, sentence_embeddings, query_chunk_size = QUERY_CHUNK_SIZE, corpus_chunk_size = CORPUS_CHUNK_SIZE, top_k = TOP_K, score_function = SCORE_FUNCTION)

    reranked_table = []
    for index, entry_at_rank in enumerate(reranked_ranking[0]):
        corpus_id = entry_at_rank['corpus_id']
        entry = es_results.table[corpus_id]
        entry['score'] = entry_at_rank['score']
        entry['rank'] = index

        reranked_table.append(entry)
    es_results.table = reranked_table
    
    # return the reranked results
    return es_results