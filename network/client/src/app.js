let ws = new WebSocket("ws://localhost:7654");

let sendData = function(data) {
    console.log(data);
    ws.send(JSON.stringify(data));
}

ws.onopen = function() {
    sendData({
        messageType: "GET_NODES",
        message: {}
    });
};

let nodes = {};

let addNewButton = function(id) {
    let newDiv = document.createElement("div");
    let newButton = document.createElement("button");

    newButton.appendChild(document.createTextNode(id));

    newButton.onclick = function() {
        let homeId = nodes[id].homeId;
        let nodeId = nodes[id].nodeId;

        sendNif(id);
    };

    newDiv.appendChild(newButton);

    let nodesDiv = document.getElementById("nodes");
    nodesDiv.appendChild(newDiv);
};

let removeButtons = function() {
    let nodesDiv = document.getElementById("nodes");

    while (nodesDiv.firstChild) {
        nodesDiv.removeChild(nodesDiv.firstChild);
    }
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
        removeButtons();
        message.nodes.forEach(onNewNode);
    }
};

let sendNif = function(id) {
    sendData({
        messageType: "SEND_NIF",
        message: {
            id: id
        }
    });
};

let onResetClicked = function() {
    sendData({
        messageType: "RESET",
        message: {}
    });
};

let onGenerateClicked = function() {
    sendData({
        messageType: "CREATE_NODE",
        message: {}
    });
};
