import ChannelWizard from "./channel_wizard.js";

import controller from "../../services/controller.js";

export default {
    template: `
        <div class="modal fade" id="node-wizard" tabindex="-1" ref="modal">
            <div class="modal-dialog modal-xl modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Generate node</h5>
                    </div>
                    <div class="modal-body">
                        <channel-wizard ref="rootChannel" :mandatoryCommandClasses="mandatoryCommandClasses"></channel-wizard>
                        <hr/>
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" id="secure-input" v-model="secure">
                            <label class="form-check-label" for="secure-input">Secure</label>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" @click="onSubmit()">Generate</button>
                    </div>
                </div>
            </div>
        </div>
    `,

    components: {
        'channel-wizard': ChannelWizard
    },

    data() {
        return {
            secure: false,

            mandatoryCommandClasses: [
                'COMMAND_CLASS_ZWAVEPLUS_INFO',
                'COMMAND_CLASS_MANUFACTURER_SPECIFIC',
                'COMMAND_CLASS_VERSION'
            ]
        };
    },

    methods: {
        onSubmit() {
            try {
                let nodeInfo = this.buildInfo();
                controller.createNode(nodeInfo);

                bootstrap.Modal.getInstance(this.$refs.modal).hide();
            }
            catch(e) {
                console.error(e);
            }
        },
        buildInfo() {
            const COMMAND_CLASS_MULTI_CHANNEL = { class_id: 0x60, version: 3 };
            const COMMAND_CLASS_SECURITY      = { class_id: 0x98, version: 1 };

            let nodeInfo = {
                channels: [
                    // Todo: multi channel
                    this.$refs.rootChannel.buildInfo()
                ]
            };

            if (nodeInfo.channels.length > 1) {
                nodeInfo.channels[0].commandClasses.push(COMMAND_CLASS_MULTI_CHANNEL);
            }

            for (let channel of nodeInfo.channels) {
                if (this.secure) {
                    channel.commandClasses.push(COMMAND_CLASS_SECURITY);
                }
            }

            return nodeInfo;
        }
    }
};
