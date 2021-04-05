import controller from "../services/controller.js";

export default {
    template: `
        <div>
            <button v-on:click="sendNif()">{{nodeId}}</button>
        </div>
    `,

    props: {
        nodeId: String
    },

    methods: {
        sendNif() {
            controller.sendNif(this.nodeId);
        }
    }
};
