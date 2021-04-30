import NODE_TYPES          from "../../../resources/node_types.js";
import ROLE_TYPES          from "../../../resources/role_types.js";
import GENERIC_ICON_TYPES  from "../../../resources/generic_icon_types.js";
import SPECIFIC_ICON_TYPES from "../../../resources/specific_icon_types.js";

export default {
    template: `
        <div class="container p-0">
            <div class="row g-2">
                <div class="col-6 form-floating">
                    <select class="form-select" v-model="installerIconType" id="installer-icon-type-input">
                        <option v-for="type in installerIconTypes" :value="type">{{type}}</option>
                    </select>
                    <label for="installer-icon-type-input">Installer Icon Type</label>
                </div>
                <div class="col-6 form-floating">
                    <select class="form-select" v-model="userIconType" id="user-icon-type-input">
                        <option v-for="type in userIconTypes" :value="type">{{type}}</option>
                    </select>
                    <label for="user-icon-type-input">User Icon Type</label>
                </div>
            </div>
        </div>
    `,

    data() {
        return {
            installerIconType: 'GENERIC_ON_OFF_POWER_SWITCH',
            userIconType: 'SPECIFIC_ON_OFF_POWER_SWITCH_PLUGIN'
        };
    },

    computed: {
        installerIconTypes() {
            return Object.keys(GENERIC_ICON_TYPES);
        },
        userIconTypes() {
            let iconTypes = [this.installerIconType];

            if (this.installerIconType in SPECIFIC_ICON_TYPES) {
                iconTypes.push(...Object.keys(SPECIFIC_ICON_TYPES[this.installerIconType]));
            }

            return iconTypes;
        }
    },

    methods: {
        buildInfo() {
            return {
                classId: 0x5E,
                version: 2,
                state: {
                    zwavePlusVersion: 2,
                    roleType: NODE_TYPES['NODE_TYPE_ZWAVEPLUS_NODE'],
                    nodeType: ROLE_TYPES['SLAVE_ALWAYS_ON'],
                    installerIconType: GENERIC_ICON_TYPES[this.installerIconType],
                    userIconType: SPECIFIC_ICON_TYPES[this.installerIconType]?.[this.userIconType] ||
                                  GENERIC_ICON_TYPES[this.userIconType]
                }
            };
        }
    }
};
