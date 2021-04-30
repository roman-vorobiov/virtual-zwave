import CommandClassWizard   from "./command_class_wizard.js";
import AssociationsWizard   from "./associations_wizard.js";
import BinarySwitch         from "./command_classes/binary_switch.js";
import Basic                from "./command_classes/basic.js";
import ZWavePlusInfo        from "./command_classes/zwaveplus_info.js";
import ManufacturerSpecific from "./command_classes/manufacturer_specific.js";
import Version              from "./command_classes/version.js";

import SUPPORTED_COMMAND_CLASSES from "../../resources/supported_command_classes.js";

import GENERIC_DEVICE_TYPES  from "../../resources/generic_device_types.js";
import SPECIFIC_DEVICE_TYPES from "../../resources/specific_device_types.js";

export default {
    template: `
        <div class="container">
            <div class="row g-2">
                <div class="col-6">
                    <select class="form-select" v-model="generic">
                        <option v-for="type in genericDeviceTypes" :value="type">{{type}}</option>
                    </select>
                </div>
                <div class="col-6">
                    <select class="col-6 form-select" v-model="specific">
                        <option v-for="type in specificDeviceTypes" :value="type">{{type}}</option>
                    </select>
                </div>
            </div>
        </div>
        <associations-wizard ref="associations"></associations-wizard>
        <hr/>
        <div class="container-fluid">
            <div class="row g-3">
                <div v-for="[cc, mandatory] in commandClasses" class="col-12">
                    <command-class-wizard :title="cc" :mandatory="mandatory">
                        <component :is="cc" :ref="makeRef"></component>
                    </command-class-wizard>
                </div>
            </div>
        </div>
        <div v-if="supportedCommandClasses.length > 0">
            <hr/>
            <div class="container-fluid">
                <div class="row g-2">
                    <div class="col">
                        <select class="form-select" v-model="newCommandClass">
                            <option v-for="cc in supportedCommandClasses" :value="cc">{{cc}}</option>
                        </select>
                    </div>
                    <div class="col-auto">
                        <button type="button" class="btn btn-primary" @click="addCommandClass">Add Command Class</button>
                    </div>
                </div>
            </div>
        </div>
    `,

    props: {
        'mandatoryCommandClasses': {
            type: Array,
            default: []
        }
    },

    components: {
        'command-class-wizard': CommandClassWizard,
        'associations-wizard': AssociationsWizard,

        'COMMAND_CLASS_SWITCH_BINARY':         BinarySwitch,
        'COMMAND_CLASS_BASIC':                 Basic,
        'COMMAND_CLASS_ZWAVEPLUS_INFO':        ZWavePlusInfo,
        'COMMAND_CLASS_MANUFACTURER_SPECIFIC': ManufacturerSpecific,
        'COMMAND_CLASS_VERSION':               Version
    },

    data() {
        return {
            generic: 'GENERIC_TYPE_SWITCH_BINARY',
            specific: 'SPECIFIC_TYPE_POWER_SWITCH_BINARY',
            newCommandClass: null,
            commandClasses: new Map(this.mandatoryCommandClasses.map(cc => [cc, true])),
            commandClassRefs: []
        };
    },

    computed: {
        genericDeviceTypes() {
            return Object.keys(GENERIC_DEVICE_TYPES);
        },
        specificDeviceTypes() {
            return Object.keys(SPECIFIC_DEVICE_TYPES[this.generic]);
        },
        supportedCommandClasses() {
            return SUPPORTED_COMMAND_CLASSES.filter(cc => !this.commandClasses.has(cc));
        }
    },

    beforeUpdate() {
        this.commandClassRefs = [];
    },

    methods: {
        makeRef(element) {
            if (element !== null) {
                this.commandClassRefs.push(element);
            }
        },
        addCommandClass() {
            if (this.newCommandClass !== null) {
                this.commandClasses.set(this.newCommandClass, false);
                this.newCommandClass = null;
            }
        },
        buildInfo() {
            const COMMAND_CLASS_ASSOCIATION          = { class_id: 0x85, version: 2 };
            const COMMAND_CLASS_ASSOCIATION_GRP_INFO = { class_id: 0x59, version: 3 };

            let channelInfo = {
                generic: GENERIC_DEVICE_TYPES[this.generic],
                specific: SPECIFIC_DEVICE_TYPES[this.generic][this.specific],
                associationGroups: this.$refs.associations.buildInfo(),
                commandClasses: this.commandClassRefs.map(cc => cc.buildInfo())
            };

            if (channelInfo.associationGroups.length > 0) {
                channelInfo.commandClasses.push(
                    COMMAND_CLASS_ASSOCIATION,
                    COMMAND_CLASS_ASSOCIATION_GRP_INFO
                );
            }

            return channelInfo;
        }
    }
};
