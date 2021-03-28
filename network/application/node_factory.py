from .node import Node
from .command_classes.command_class_factory import command_class_factory

from network.resources import CONSTANTS

from common import RemoteInterface


def get_user_icon_type(generic: str, specific: str) -> int:
    if (specific_icon_types := CONSTANTS['SpecificIconTypes'][generic]) is not None:
        return specific_icon_types[specific]
    else:
        return CONSTANTS['GenericIconTypes'][generic]


def create_node(
    controller: RemoteInterface,

    basic: str,
    generic: str,
    specific: str,

    manufacturer_id: int,
    product_type_id: int,
    product_id: int,

    zwave_plus_version: int,
    role_type: str,
    node_type: str,
    installer_icon_type: str,
    user_icon_type: str
) -> Node:
    node = Node(controller,
                basic=CONSTANTS['BasicType'][basic],
                generic=CONSTANTS['GenericDeviceType'][generic],
                specific=CONSTANTS['SpecificDeviceTypes'][generic][specific])

    command_class_factory.create_command_class('COMMAND_CLASS_MANUFACTURER_SPECIFIC',
                                               node,
                                               manufacturer_id=manufacturer_id,
                                               product_type_id=product_type_id,
                                               product_id=product_id)

    command_class_factory.create_command_class('COMMAND_CLASS_ZWAVEPLUS_INFO',
                                               node,
                                               zwave_plus_version=zwave_plus_version,
                                               role_type=CONSTANTS['RoleType'][role_type],
                                               node_type=CONSTANTS['NodeTypes'][node_type],
                                               installer_icon_type=CONSTANTS['GenericIconTypes'][installer_icon_type],
                                               user_icon_type=get_user_icon_type(installer_icon_type, user_icon_type))

    command_class_factory.create_command_class('COMMAND_CLASS_BASIC', node)

    return node
