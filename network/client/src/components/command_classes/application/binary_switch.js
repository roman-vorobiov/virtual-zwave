import { Base, createStateWatcher } from "../base.js";

export default {
    mixins: [Base],

    template: `
        <div>
            <span>{{commandClass.className}}: </span>
            <input type="checkbox" v-model="commandClass.state.value">
        </div>
    `,

    computed: {
        value() {
            return this.commandClass.state.value;
        }
    },

    watch: {
        value: createStateWatcher("value")
    }
};
