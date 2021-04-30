import SUPPORTED_COMMAND_CLASSES from "../../../resources/supported_command_classes.js";

export default {
    template: `
        <div class="container p-0">
            <div class="row g-2">
                <div class="col-12 form-floating">
                    <select class="form-select" v-model="commandClass" id="command-class-input">
                        <option v-for="cc in commandClasses" :value="cc">{{cc}}</option>
                    </select>
                    <label for="command-class-input">Mapped Command Class</label>
                </div>
            </div>
        </div>
    `,

    data() {
        return {
            commandClass: null
        };
    },

    computed: {
        commandClasses() {
            return SUPPORTED_COMMAND_CLASSES.filter(cc => cc !== 'COMMAND_CLASS_BASIC' &&
                                                          this.$parent.$parent.commandClasses.has(cc));
        }
    },

    methods: {
        buildInfo() {
            if (this.commandClass === null) {
                throw "'Mapped Command Class' field is required";
            }

            return {
                classId: 0x20,
                version: 1,
                state: {
                    mappedCommandClass: this.commandClass
                }
            };
        }
    }
};
