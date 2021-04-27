import { Base, createStateWatcher } from "../base.js";

export default {
    mixins: [Base],

    template: `
        <div>
            <div class="form-check form-switch">
                <input class="form-check-input" type="checkbox" v-model="commandClass.state.value">
                <span>{{commandClass.className}}</span>
            </div>
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
