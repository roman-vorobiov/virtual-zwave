import Channel from "./channel.js";

import controller from "../services/controller.js";
import { updateObject } from "../services/utils.js";

export default {
    template: `
        <div class="card">
            <div class="card-header">
                <div class="d-flex justify-content-between">
                    <div>Home ID: {{node.homeId}}, Node ID: {{node.nodeId}}</div>
                    <div>
                        <button type="button" class="btn-util btn-play shadow-none" @click="sendNif()"></button>
                        <button type="button" class="btn-util btn-reset shadow-none" @click="reset()"></button>
                        <button type="button" class="btn-util btn-close shadow-none" @click="remove()"></button>
                    </div>
                </div>
            </div>
            <ul class="list-group list-group-flush">
                <li class="list-group-item" v-for="channel in node.channels">
                    <channel :channel="channel"></channel>
                </li>
            </ul>
        </div>
    `,

    components: {
        'channel': Channel
    },

    props: {
        'node': Object
    },

    mounted() {
        controller.onNodeReset(this.onNodeReset, this.node.id);
        controller.onNodeUpdated(this.onNodeUpdated, this.node.id);
    },

    methods: {
        onNodeReset(node) {
            this.node = node;
        },
        onNodeUpdated(node) {
            updateObject(this.node, node);
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
