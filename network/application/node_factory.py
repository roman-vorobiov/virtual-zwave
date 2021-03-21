from .node import Node
from .command_classes.management.manufacturer_specific import ManufacturerSpecific
from .command_classes.management.zwaveplus_info import ZWavePlusInfo
from .command_classes.application.basic import Basic

from common import Network


def create_node(
    network: Network,
    basic: int,
    generic: int,
    specific: int,
    manufacturer_id: int,
    product_type_id: int,
    product_id: int,
    role_type: int,
    installer_icon_type: int,
    user_icon_type: int
) -> Node:
    node = Node(network, basic=basic, generic=generic, specific=specific)

    node.add_command_class(ManufacturerSpecific,
                           manufacturer_id=manufacturer_id,
                           product_type_id=product_type_id,
                           product_id=product_id)

    node.add_command_class(ZWavePlusInfo,
                           zwave_plus_version=2,
                           role_type=role_type,
                           node_type=0x00,
                           installer_icon_type=installer_icon_type,
                           user_icon_type=user_icon_type)

    node.add_command_class(Basic)

    return node
