let ws = new WebSocket("ws://localhost:7654");

ws.onopen = function() {
    ws.send("list");
};

let nodes = {};

let addNewButton = function(id) {
    let newDiv = document.createElement("div");
    let newButton = document.createElement("button");

    newButton.appendChild(document.createTextNode(id));

    newButton.onclick = function() {
        let homeId = nodes[id].homeId;
        let nodeId = nodes[id].nodeId;

        sendNif(homeId, nodeId);
    };

    newDiv.appendChild(newButton);

    document.body.appendChild(newDiv);
};

let onNodeUpdated = function(node) {
    nodes[node.id] = {
        homeId: node.homeId,
        nodeId: node.nodeId
    };
};

let onNewNode = function(node) {
    onNodeUpdated(node);
    addNewButton(node.id);
};

ws.onmessage = function(event) {
    let data = JSON.parse(event.data);

    let messageType = data.messageType;
    let message = data.message;

    if (messageType === "NODE_UPDATED") {
        if (nodes.hasOwnProperty(message.id)) {
            onNodeUpdated(message);
        } else {
            onNewNode(message);
        }
    } else if (messageType === "NODES_LIST") {
        message.nodes.forEach(onNewNode);
    }
};

let sendNif = function(homeId, nodeId) {
    ws.send(`nif ${homeId} ${nodeId}`);
};

let onGenerateClicked = function() {
    ws.send("generate");
};
