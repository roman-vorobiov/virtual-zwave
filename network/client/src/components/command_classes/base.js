import controller from "../../../services/controller.js";

export let Base = {
    props: {
        data: Object
    },

    computed: {
        node() {
            return this.$parent.node;
        },
        channel() {
            return this.$parent.channel;
        }
    }
};

export let createStateWatcher = (propertyName) => {
    return function (newValue, oldValue) {
        controller.updateNode(this.node.id, this.channel.endpoint, this.data.classId, {
            [propertyName]: this[propertyName]
        });
    };
};
