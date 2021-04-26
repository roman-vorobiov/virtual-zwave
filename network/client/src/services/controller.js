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

    removeNode(nodeId) {
        this.backend.sendData({
            messageType: "REMOVE_NODE",
            message: {
                nodeId: nodeId
            }
        });
    }

    resetNetwork() {
        this.backend.sendData({
            messageType: "RESET_NETWORK",
            message: {}
        });
    }

    sendNif(nodeId) {
        this.backend.sendData({
            messageType: "SEND_NIF",
            message: {
                nodeId: nodeId
            }
        });
    }

    updateCommandClass(nodeId, channelId, classId, state) {
        this.backend.sendData({
            messageType: "UPDATE_COMMAND_CLASS",
            message: {
                nodeId: nodeId,
                channelId: channelId,
                classId: classId,
                state: state
            }
        });
    }

    resetNode(nodeId) {
        this.backend.sendData({
            messageType: "RESET_NODE",
            message: {
                nodeId: nodeId
            }
        });
    }

    onNodeAdded(callback) {
        this.backend.subscribe("NODE_ADDED", (message) => {
            callback(message.node);
        });
    }

    onNodeRemoved(callback) {
        this.backend.subscribe("NODE_REMOVED", (message) => {
            callback(message.nodeId);
        });
    }

    onNodesList(callback) {
        this.backend.subscribe("NODES_LIST", (message) => {
            callback(message.nodes);
        });
    }

    onNodeReset(callback, nodeIdFilter) {
        this.backend.subscribe("NODE_RESET", (message) => {
            let node = message.node;

            if (node.id === nodeIdFilter) {
                callback(node);
            }
        });
    }

    onNodeUpdated(callback, nodeIdFilter) {
        this.backend.subscribe("NODE_UPDATED", (message) => {
            let node = message.node;

            if (node.id === nodeIdFilter) {
                callback(node);
            }
        });
    }

    onChannelUpdated(callback, nodeIdFilter, channelIdFilter) {
        this.backend.subscribe("CHANNEL_UPDATED", (message) => {
            let nodeId = message.nodeId;
            let channel = message.channel;

            if (nodeId === nodeIdFilter && channel.endpoint === channelIdFilter) {
                callback(channel);
            }
        });
    }

    onCommandClassUpdated(callback, nodeIdFilter, channelIdFilter, classIdFilter) {
        this.backend.subscribe("COMMAND_CLASS_UPDATED", (message) => {
            let nodeId = message.nodeId;
            let channelId = message.channelId;
            let commandClass = message.commandClass;

            if (nodeId === nodeIdFilter && channelId === channelIdFilter && commandClass.classId === classIdFilter) {
                callback(commandClass);
            }
        });
    }
};

export default new Controller();
