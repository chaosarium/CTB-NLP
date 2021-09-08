console.log("main script loaded");

function logAction(sessionID, actionType, pid, rank) {
    console.assert(sessionID, actionType, pid, rank)
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/log-req");
    xhr.setRequestHeader("Accept", "application/json");
    xhr.setRequestHeader("Content-Type", "application/json");

    xhr.send(JSON.stringify({
        sessionID: sessionID, // unique identifiers for each session
        actionType: actionType, // upvote, expand, or downvote
        pid: pid, // the evaluated passage id
        rank: rank, // the target result entry
    }));
    
}