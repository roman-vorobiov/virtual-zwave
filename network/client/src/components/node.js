import Channel from "./channel.js";

import controller from "../services/controller.js";

export default {
    template: `
        <div>
            <span>Home ID: {{node.homeId}}, Node ID: {{node.nodeId}}</span><br>
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

    methods: {
        sendNif() {
            controller.sendNif(this.node.id);
        },
        reset() {
            controller.resetNode(this.node.id);
        }
    }
};
