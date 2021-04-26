from ..command_class import CommandClass, command_class
from ..security_level import SecurityLevel
from ...channel import Channel
from ...request_context import Context
from ...utils import InternalNonce, ExternalNonce

from network.protocol import Command
from network.resources import CONSTANTS

from tools import Object, make_object, visit, log_warning

import random
import asyncio
import itertools
from enum import IntFlag
from collections import defaultdict
from typing import List, Dict, Tuple, Optional


MAX_FRAME_LENGTH = 46
SECURITY_ENCAP_OVERHEAD = 20
MAX_SECURITY_FRAME_LENGTH = MAX_FRAME_LENGTH - SECURITY_ENCAP_OVERHEAD


class SecuritySchemes(IntFlag):
    SECURITY_0 = 0


def require_secure(fn):
    def wrapper(self, command: Command, context: Context):
        if context.secure:
            fn(self, command, context)
        else:
            log_warning("Incorrect security level")

    return wrapper


@command_class('COMMAND_CLASS_SECURITY', version=1)
class Security1(CommandClass):
    def __init__(self, channel: Channel, required_security: SecurityLevel):
        super().__init__(channel, SecurityLevel.NONE)

        self.internal_nonce_table = defaultdict(InternalNonce)
        self.external_nonce_table = defaultdict(ExternalNonce)
        self.sequence_table: Dict[Tuple[int, int], List[int]] = {}
        self.sequence_counter = itertools.cycle(range(0x10))

    def __getstate_impl__(self):
        return {}

    def reset_state(self):
        self.internal_nonce_table.clear()
        self.external_nonce_table.clear()
        self.sequence_table.clear()
        self.sequence_counter = itertools.cycle(range(0x10))

    @visit('SECURITY_SCHEME_GET')
    def handle_scheme_get(self, command: Command, context: Context):
        self.send_scheme_report(context)

    @visit('NETWORK_KEY_SET')
    @require_secure
    def handle_network_key_set(self, command: Command, context: Context):
        self.node.secure = True
        self.node.security_utils.set_network_key(command.network_key)
        self.send_network_key_verify(context)

        self.node.on_state_change()

    @visit('SECURITY_NONCE_GET')
    def handle_nonce_get(self, command: Command, context: Context):
        self.send_nonce_report(context)

    @visit('SECURITY_NONCE_REPORT')
    def handle_nonce_report(self, command: Command, context: Context):
        self.external_nonce_table[context.node_id].set(command.nonce)

    @visit('SECURITY_MESSAGE_ENCAPSULATION')
    def handle_message_encapsulation(self, command: Command, context: Context):
        self.handle_encapsulated_command(command, context, header=0x81)

    @visit('SECURITY_MESSAGE_ENCAPSULATION_NONCE_GET')
    def handle_message_encapsulation_nonce_get(self, command: Command, context: Context):
        self.handle_encapsulated_command(command, context, header=0xC1)
        self.send_nonce_report(context)

    @visit('SECURITY_COMMANDS_SUPPORTED_GET')
    @require_secure
    def handle_commands_supported_get(self, command: Command, context: Context):
        self.send_commands_supported_report(context)

    def send_scheme_report(self, context: Context):
        self.send_command(context, 'SECURITY_SCHEME_REPORT',
                          supported_security_schemes=SecuritySchemes.SECURITY_0)

    def send_network_key_verify(self, context: Context):
        self.send_command(context, 'NETWORK_KEY_VERIFY')

    def send_nonce_get(self, context: Context):
        self.send_command(context.copy(secure=False), 'SECURITY_NONCE_GET')

    def send_nonce_report(self, context: Context):
        nonce = self.generate_nonce()
        self.internal_nonce_table[context.node_id].set(nonce)

        self.send_command(context.copy(secure=False), 'SECURITY_NONCE_REPORT', nonce=nonce)

    def send_commands_supported_report(self, context: Context):
        command_class_ids = [cc.class_id for cc in self.channel.command_classes.values()
                             if cc.advertise_in_nif and not cc.supported_non_securely]

        # Note: if for some reason a node has over 48 secure command classes the list won't fit in 2 encapsulated frames
        # Todo: split the list using the 'reports_to_follow' field
        assert len(command_class_ids) + 3 * 2 <= MAX_SECURITY_FRAME_LENGTH * 2

        self.send_command(context, 'SECURITY_COMMANDS_SUPPORTED_REPORT',
                          reports_to_follow=0,
                          command_class_ids=command_class_ids)

    def send_encapsulated_command(self, context: Context, command: List[int]):
        if len(command) <= MAX_SECURITY_FRAME_LENGTH:
            payload = make_object(sequenced=False, second=False, sequence_counter=0, command=command)

            async def flow():
                try:
                    self.send_nonce_get(context)
                    nonce = await self.external_nonce_table[context.node_id].get()

                    await self.encrypt_and_send(context, payload, nonce)
                except asyncio.TimeoutError:
                    pass

            asyncio.create_task(flow())
        else:
            assert len(command) <= MAX_SECURITY_FRAME_LENGTH * 2

            sequence = next(self.sequence_counter)
            first_command = command[:MAX_SECURITY_FRAME_LENGTH]
            first_payload = make_object(sequenced=True, second=False, sequence_counter=sequence, command=first_command)
            second_command = command[MAX_SECURITY_FRAME_LENGTH:]
            second_payload = make_object(sequenced=True, second=True, sequence_counter=sequence, command=second_command)

            async def flow():
                try:
                    self.send_nonce_get(context)
                    nonce = await self.external_nonce_table[context.node_id].get()

                    await self.encrypt_and_send(context, first_payload, nonce)
                    nonce = await self.external_nonce_table[context.node_id].get()

                    await self.encrypt_and_send(context, second_payload, nonce)
                except asyncio.TimeoutError:
                    pass

            asyncio.create_task(flow())

    async def encrypt_and_send(self, context: Context, payload: Object, nonce: List[int]):
        if payload.sequenced and not payload.second:
            command_name = 'SECURITY_MESSAGE_ENCAPSULATION_NONCE_GET'
        else:
            command_name = 'SECURITY_MESSAGE_ENCAPSULATION'

        initialization_vector = self.generate_nonce()

        encrypted, tag = self.node.security_utils.encrypt_and_sign(
            payload=self.node.serializer.from_object('EncryptedPayload', payload),
            sender_nonce=initialization_vector,
            receiver_nonce=nonce,
            header=CONSTANTS['CommandId']['COMMAND_CLASS_SECURITY'][command_name],
            sender=self.node.node_id,
            receiver=context.node_id
        )

        self.send_command(context.copy(secure=False), command_name,
                          initialization_vector=initialization_vector,
                          encrypted_payload=encrypted,
                          receiver_nonce_id=nonce[0],
                          message_authentication_code=tag)

    def handle_encapsulated_command(self, command: Command, context: Context, header: int):
        nonce = self.internal_nonce_table[context.node_id].get()
        if nonce is None or nonce[0] != command.receiver_nonce_id:
            log_warning("Failed to decrypt the message: nonce expired")
            return

        decrypted = self.node.security_utils.decrypt_and_verify(
            payload=command.encrypted_payload,
            sender_nonce=command.initialization_vector,
            receiver_nonce=nonce,
            header=header,
            sender=context.node_id,
            receiver=self.node.node_id,
            mac=command.message_authentication_code
        )

        if decrypted is not None:
            payload = self.node.serializer.to_object('EncryptedPayload', decrypted)
            if (command := self.get_command(context, payload)) is not None:
                self.channel.handle_command(command, context.copy(secure=True))
        else:
            log_warning("Failed to decrypt the message: unable to verify")

    def get_command(self, context: Context, payload: Object) -> Optional[List[int]]:
        if not payload.sequenced:
            return payload.command
        elif not payload.second:
            self.sequence_table[(context.node_id, payload.sequence_counter)] = payload.command
        else:
            first = self.sequence_table.pop((context.node_id, payload.sequence_counter))
            return first + payload.command

    @classmethod
    def generate_nonce(cls) -> List[int]:
        return list(random.randbytes(8))
