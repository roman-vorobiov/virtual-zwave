export default {
    channels: [
        {
            generic: 0x10,
            specific: 0x01,
            commandClasses: [
                {
                    class_id: 0x72, // COMMAND_CLASS_MANUFACTURER_SPECIFIC
                    version: 1,
                    state: {
                        manufacturerId: 1,
                        productTypeId: 2,
                        productId: 3
                    }
                },
                {
                    class_id: 0x5E, // COMMAND_CLASS_ZWAVEPLUS_INFO
                    version: 2,
                    state: {
                        zwavePlusVersion: 2,
                        roleType: 0x05,
                        nodeType: 0x00,
                        installerIconType: 0x0700,
                        userIconType: 0x0701
                    }
                },
                {
                    class_id: 0x86, // COMMAND_CLASS_VERSION
                    version: 1,
                    state: {
                        protocolLibraryType: 0x06,
                        protocolVersion: [1, 0],
                        applicationVersion: [1, 0]
                    }
                },
                {
                    class_id: 0x20, // COMMAND_CLASS_BASIC
                    version: 1,
                    state: {}
                },
                {
                    class_id: 0x20, // COMMAND_CLASS_SWITCH_BINARY
                    version: 1,
                    required_security: 'HIGHEST_GRANTED',
                    state: {}
                },
                {
                    class_id: 0x98, // COMMAND_CLASS_SECURITY
                    version: 1,
                    state: {}
                }
            ]
        }
    ]
};
