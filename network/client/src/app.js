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
        message: {
            basic: 0x04,
            channels: [
                {
                    generic: 0x10,
                    specific: 0x01,
                    commandClasses: [
                        {
                            id: 0x72, // COMMAND_CLASS_MANUFACTURER_SPECIFIC
                            version: 1,
                            args: {
                                manufacturerId: 1,
                                productTypeId: 2,
                                productId: 3
                            }
                        },
                        {
                            id: 0x5E, // COMMAND_CLASS_ZWAVEPLUS_INFO
                            version: 2,
                            args: {
                                zwavePlusVersion: 2,
                                roleType: 0x05,
                                nodeType: 0x00,
                                installerIconType: 0x0700,
                                userIconType: 0x0701
                            }
                        },
                        {
                            id: 0x86, // COMMAND_CLASS_VERSION
                            version: 1,
                            args: {
                                protocolLibraryType: 0x06,
                                protocolVersion: [1, 0],
                                applicationVersion: [1, 0]
                            }
                        },
                        {
                            id: 0x20, // COMMAND_CLASS_BASIC
                            version: 1,
                            args: {}
                        }
                    ]
                }
            ]
        }
    });
};
