import Backend from "./backend.js";

import dummyNode from "../resources/dummy_node.js";

class Controller {
    constructor() {
        this.backend = new Backend("ws://localhost:7654");
    }

    createDummyNode() {
        this.backend.sendData({
            messageType: "CREATE_NODE",
            message: {
                node: dummyNode
            }
        });
    }

    resetNetwork() {
        this.backend.sendData({
            messageType: "RESET",
            message: {}
        });
    }

    sendNif(nodeId) {
        this.backend.sendData({
            messageType: "SEND_NIF",
            message: {
                id: nodeId
            }
        });
    }

    onNodeUpdated(callback) {
        this.backend.subscribe("NODE_UPDATED", (message) => {
            callback(message.node);
        });
    }

    onNodesList(callback) {
        this.backend.subscribe("NODES_LIST", (message) => {
            callback(message.nodes);
        });
    }
};

export default new Controller();
