export default {
    channels: [
        {
            generic: 0x10,
            specific: 0x01,
            associationGroups: [
                {
                    name: "Lifeline",
                    profile: [0x00, 0x01],
                    commands: [
                        [0x25, 0x03] // SWITCH_BINARY_REPORT
                    ]
                }
            ],
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
                    state: {
                        mapping: {
                            BASIC_GET: [0x25, 'SWITCH_BINARY_GET', {}],
                            BASIC_SET: [0x25, 'SWITCH_BINARY_SET', { value: '$value' }],
                            BASIC_REPORT: [0x25, 'SWITCH_BINARY_REPORT', { value: '$value' }],
                        }
                    }
                },
                {
                    class_id: 0x25, // COMMAND_CLASS_SWITCH_BINARY
                    version: 1,
                    required_security: 'HIGHEST_GRANTED'
                },
                // Note: Uncomment to make this node secure
                // {
                //     class_id: 0x98, // COMMAND_CLASS_SECURITY
                //     version: 1
                // },
                {
                    class_id: 0x85, // COMMAND_CLASS_ASSOCIATION
                    version: 2
                },
                {
                    class_id: 0x59, // COMMAND_CLASS_ASSOCIATION_GRP_INFO
                    version: 3
                }
            ]
        }
    ]
};
