import BinarySwitch from "./command_classes/application/binary_switch.js";

export default {
    template: `
        <div>
            <component v-for="cc in channel.commandClasses" :is="cc.className" :data="cc"></component>
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
    }
};
