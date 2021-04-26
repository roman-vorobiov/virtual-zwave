import controller from "../../../services/controller.js";
import { updateObject } from "../../../services/utils.js";

export let Base = {
    props: {
        commandClass: Object
    },

    computed: {
        node() {
            return this.$parent.node;
        },
        channel() {
            return this.$parent.channel;
        }
    },

    mounted() {
        controller.onCommandClassUpdated(
            this.onCommandClassUpdated,
            this.node.id,
            this.channel.endpoint,
            this.commandClass.classId
        );
    },

    methods: {
        onCommandClassUpdated(commandClass) {
            updateObject(this.commandClass, commandClass);
        }
    }
};

export let createStateWatcher = (propertyName) => {
    return function (newValue, oldValue) {
        controller.updateCommandClass(this.node.id, this.channel.endpoint, this.commandClass.classId, {
            [propertyName]: this[propertyName]
        });
    };
};
