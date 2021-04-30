export default {
    template: `
        <div class="card">
            <div class="card-header">
                <div class="d-flex justify-content-between">
                    <div>{{title}}</div>
                    <button v-if="!mandatory" type="button" class="btn-util btn-close shadow-none" @click="onClose"></button>
                </div>
            </div>
            <div class="card-body">
                <slot></slot>
            </div>
        </div>
    `,

    props: {
        'title': String,
        'mandatory': {
            type: Boolean,
            default: false
        }
    },

    methods: {
        onClose() {
            delete this.$parent.commandClasses.delete(this.title);
        }
    }
};
