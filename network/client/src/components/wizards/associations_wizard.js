export default {
    template: `<div></div>`,

    methods: {
        buildInfo() {
            // Todo
            return [
                {
                    name: "Lifeline",
                    profile: [0x00, 0x01],
                    commands: [
                        [0x25, 0x03] // SWITCH_BINARY_REPORT
                    ]
                }
            ];
        }
    }
};
