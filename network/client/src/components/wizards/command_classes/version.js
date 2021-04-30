import LIBRARY_TYPES from "../../../resources/library_types.js";

export default {
    template: `
        <div class="container p-0">
            <div class="row g-2">
                <div class="col-6 form-floating">
                    <input type="text" class="form-control" id="protocol-version-major-input" v-model.number="protocolVersion[0]">
                    <label for="protocol-version-major-input" class="form-label">Major</label>
                </div>
                <div class="col-6 form-floating">
                    <input type="text" class="form-control" id="protocol-version-minor-input" v-model.number="protocolVersion[1]">
                    <label for="protocol-version-minor-input" class="form-label">Minor</label>
                </div>
            </div>
        </div>
    `,

    data() {
        return {
            protocolVersion: [1, 0],
            applicationVersion: [1, 0]
        };
    },

    methods: {
        buildInfo() {
            return {
                classId: 0x86,
                version: 1,
                state: {
                    protocolLibraryType: LIBRARY_TYPES['SLAVE_ROUTING'],
                    protocolVersion: [1, 0],
                    applicationVersion: [1, 0]
                }
            };
        }
    }
};
