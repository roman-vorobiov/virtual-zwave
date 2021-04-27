import Node from "./node.js";

import controller from "../services/controller.js";

export default {
    template: `
        <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
            <div class="container-fluid">
                <span class="navbar-brand">ZWave</span>
                <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbar-content">
                    <span class="navbar-toggler-icon text-white"></span>
                </button>
                <div class="collapse navbar-collapse" id="navbar-content">
                    <div class="navbar-nav">
                        <button class="btn shadow-none" type="button" @click="generateNode()">Generate</button>
                        <button class="btn shadow-none" type="button" @click="resetNetwork()">Reset</button>
                    </div>
                </div>
            </div>
        </nav>
        <div class="container-fluid p-3">
            <div class="row row-cols-auto g-3">
                <node v-for="[nodeId, node] in nodes" :node="node"></node>
            </div>
        </div>
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
