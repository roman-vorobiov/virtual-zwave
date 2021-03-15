from .node import Node
from .command_classes.management.manufacturer_specific import ManufacturerSpecific
from .command_classes.management.zwaveplus_info import ZWavePlusInfo
from .command_classes.application.basic import Basic

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zwave.core import Network


def create_node(
    network: 'Network',
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
    node = Node(
        network,
        basic=basic,
        generic=generic,
        specific=specific
    )

    manufacturer_specific = ManufacturerSpecific(
        node,
        manufacturer_id=manufacturer_id,
        product_type_id=product_type_id,
        product_id=product_id
    )

    zwaveplus_info = ZWavePlusInfo(
        node,
        zwave_plus_version=2,
        role_type=role_type,
        node_type=0x00,
        installer_icon_type=installer_icon_type,
        user_icon_type=user_icon_type
    )

    basic = Basic(node)

    for cc in [manufacturer_specific, zwaveplus_info, basic]:
        node.command_classes[cc.class_id] = cc

    return node
