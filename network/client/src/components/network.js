import Node from "./node.js";

import controller from "../services/controller.js";

export default {
    template: `
        <div>
            <button v-on:click="generateNode()">Generate</button>
            <button v-on:click="resetNetwork()">Reset</button>
        </div>
        <node v-for="node in nodes" :node-id="node[0]"></node>
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
        controller.onNodeUpdated(this.onNodeUpdated);
        controller.onNodesList(this.onNodesList);
    },

    methods: {
        generateNode() {
            controller.createDummyNode();
        },
        resetNetwork() {
            controller.resetNetwork();
        },
        onNodeUpdated(node) {
            this.nodes.set(node.id, node);
        },
        onNodesList(nodes) {
            this.nodes.clear();

            nodes.forEach(node => {
                this.nodes.set(node.id, node);
            });
        }
    }
};
