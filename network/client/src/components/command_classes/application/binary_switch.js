import { Base, createStateWatcher } from "../base.js";

export default {
    mixins: [Base],

    template: `
        <div>
            <input type="checkbox" v-model="data.state.value">
        </div>
    `,

    props: {
        data: Object
    },

    computed: {
        value() {
            return this.data.state.value;
        }
    },

    watch: {
        value: createStateWatcher("value")
    }
};
