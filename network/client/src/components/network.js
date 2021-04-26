import Node from "./node.js";

import controller from "../services/controller.js";

export default {
    template: `
        <div>
            <button v-on:click="generateNode()">Generate</button>
            <button v-on:click="resetNetwork()">Reset</button>
        </div>
        <node v-for="[nodeId, node] in nodes" :node="node"></node>
    `,

    components: {
        'node': Node
    },

    data() {
        return {
            nodes: new Map()
        };
    },

    mounted() {
        controller.onNodesList(this.onNodesList);
        controller.onNodeAdded(this.onNodeAdded);
        controller.onNodeRemoved(this.onNodeRemoved);
    },

    methods: {
        generateNode() {
            controller.createDummyNode();
        },
        resetNetwork() {
            controller.resetNetwork();
        },
        onNodesList(nodes) {
            this.nodes.clear();
            nodes.forEach(this.onNodeAdded);
        },
        onNodeAdded(node) {
            this.nodes.set(node.id, node);
        },
        onNodeRemoved(nodeId) {
            this.nodes.delete(nodeId);
        }
    }
};
