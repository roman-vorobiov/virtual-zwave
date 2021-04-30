export default {
    template: `<div></div>`,

    methods: {
        buildInfo() {
            return {
                classId: 0x25,
                version: 1,
                requiredSecurity: 'HIGHEST_GRANTED'
            };
        }
    }
};
