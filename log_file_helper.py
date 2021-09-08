import pandas as pd

SEARCH_LOG_FILE_PATH = "logs/resultsLog.tsv"
USER_LOG_FILE_PATH = "logs/userActionLog.tsv"
SEARCH_LOG_FILE = pd.read_csv(SEARCH_LOG_FILE_PATH, sep='\t')
USER_LOG_FILE = pd.read_csv(USER_LOG_FILE_PATH, sep='\t')

def write_search_log():
    with open(SEARCH_LOG_FILE_PATH,'w') as write_tsv:
        write_tsv.write(SEARCH_LOG_FILE.to_csv(sep='\t', index=False))

def write_user_log():
    with open(USER_LOG_FILE_PATH,'w') as write_tsv:
        write_tsv.write(USER_LOG_FILE.to_csv(sep='\t', index=False))

def get_new_session_id():
    return SEARCH_LOG_FILE.iloc[-1, 0] + 1

def update_search_log(result_object):
    global SEARCH_LOG_FILE
    for item in result_object.table:
        SEARCH_LOG_FILE = SEARCH_LOG_FILE.append({"search_session_id": result_object.search_session_id, "query": result_object.query_input, "rank": item["rank"], "qid": item["pid"], "pid": item["pid"], "score": item["score"]} , ignore_index=True)
    write_search_log()

def update_user_log(sessionID, actionType, pid, rank):
    global USER_LOG_FILE
    USER_LOG_FILE = USER_LOG_FILE.append({"search_session_id": sessionID, "action_type": actionType, "pid": pid, "rank": rank} , ignore_index=True)
    write_user_log()
