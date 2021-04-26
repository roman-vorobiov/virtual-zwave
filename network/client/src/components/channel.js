import BinarySwitch from "./command_classes/application/binary_switch.js";

import controller from "../services/controller.js";
import { updateObject } from "../services/utils.js";

export default {
    template: `
        <div>
            <span>Channel {{channel.endpoint}}: </span>
            <component v-for="cc in channel.commandClasses" :is="cc.className" :commandClass="cc"></component>
        </div>
    `,

    components: {
        'COMMAND_CLASS_SWITCH_BINARY': BinarySwitch
    },

    props: {
        channel: Object
    },

    computed: {
        node() {
            return this.$parent.node;
        }
    },

    mounted() {
        controller.onChannelUpdated(this.onChannelUpdated, this.node.id, this.channel.endpoint);
    },

    methods: {
        onChannelUpdated(channel) {
            updateObject(this.channel, channel);
        }
    }
};
