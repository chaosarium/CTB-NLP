from sentence_transformers import SentenceTransformer
from pprint import pprint
import torch
from sentence_transformers import util

if torch.cuda.is_available():
    DEVICE = torch.device("cuda:0")  
    print("Running on the GPU")
else:
    DEVICE = torch.device("cpu")
    print("Running on the CPU")

# sentence_transformer_model = SentenceTransformer('distiluse-base-multilingual-cased-v1', device=DEVICE)
# later use this bigger model for higher performance 'paraphrase-multilingual-mpnet-base-v2'
sentence_transformer_model_v2 = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2', device=DEVICE)

def rerank(es_results):
    '''
    gets a result table, reranks it, and returns a reranked result table
    '''
    passages = [hit['passage'] for hit in es_results.table]
    queries = [es_results.query_input]
    query_embeddings = sentence_transformer_model_v2.encode(queries, convert_to_tensor=True)
    sentence_embeddings = sentence_transformer_model_v2.encode(passages, convert_to_tensor=True)

    sentence_embeddings = sentence_embeddings.to(DEVICE)
    sentence_embeddings = util.normalize_embeddings(sentence_embeddings)

    query_embeddings = query_embeddings.to(DEVICE)
    query_embeddings = util.normalize_embeddings(query_embeddings)

    reranked_ranking = util.semantic_search(query_embeddings, sentence_embeddings, score_function=util.dot_score)

    reranked_table = []
    for index, entry_at_rank in enumerate(reranked_ranking[0]):
        corpus_id = entry_at_rank['corpus_id']
        entry = es_results.table[corpus_id]
        entry['score'] = entry_at_rank['score']
        entry['rank'] = index

        reranked_table.append(entry)
    es_results.table = reranked_table
    
    return es_results