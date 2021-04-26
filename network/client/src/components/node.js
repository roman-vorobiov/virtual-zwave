import Channel from "./channel.js";

import controller from "../services/controller.js";
import { updateObject } from "../services/utils.js";

export default {
    template: `
        <div>
            <span>Home ID: {{node.homeId}}, Node ID: {{node.nodeId}}</span><br>
            <button v-on:click="remove()">Remove</button>
            <button v-on:click="sendNif()">Send NIF</button>
            <button v-on:click="reset()">Reset</button>
            <channel v-for="channel in node.channels" :channel="channel"></channel>
        </div>
    `,

    components: {
        'channel': Channel
    },

    props: {
        node: Object
    },

    mounted() {
        controller.onNodeReset(this.onNodeReset, this.node.id);
        controller.onNodeUpdated(this.onNodeUpdated, this.node.id);
    },

    methods: {
        onNodeReset(node) {
            updateObject(this.node, node);
        },
        onNodeUpdated(node) {
            this.node = node;
        },
        sendNif() {
            controller.sendNif(this.node.id);
        },
        reset() {
            controller.resetNode(this.node.id);
        },
        remove() {
            controller.removeNode(this.node.id);
        }
    }
};
