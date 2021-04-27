# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.core import (
    ActivityHandler,
    TurnContext,
    UserState,
    ConversationState,
    CardFactory,
    MessageFactory
)
from botbuilder.schema import (
    ChannelAccount,
    HeroCard,
    CardImage,
    CardAction,
    ActionTypes, 
    Attachment, 
    Activity, 
    ActivityTypes
)

import os
import json
from botbuilder.dialogs import Dialog
from helpers.dialog_helper import DialogHelper
from data_models import UserProfile

CARDS = ["AuthenticationAdaptiveCard.json"]

class DialogBot(ActivityHandler):
    """
    This Bot implementation can run any type of Dialog. The use of type parameterization is to allows multiple
    different bots to be run at different endpoints within the same project. This can be achieved by defining distinct
    Controller types each with dependency on distinct Bot types. The ConversationState is used by the Dialog system. The
    UserState isn't, however, it might have been used in a Dialog implementation, and the requirement is that all
    BotState objects are saved at the end of a turn.
    """

    def __init__(
        self,
        conversation_state: ConversationState,
        user_state: UserState,
        dialog: Dialog,
    ):
        if conversation_state is None:
            raise TypeError(
                "[DialogBot]: Missing parameter. conversation_state is required but None was given"
            )
        if user_state is None:
            raise TypeError(
                "[DialogBot]: Missing parameter. user_state is required but None was given"
            )
        if dialog is None:
            raise Exception("[DialogBot]: Missing parameter. dialog is required")

        self.conversation_state = conversation_state
        self.user_state = user_state
        self.dialog = dialog
        self.user_state_accessor = self.user_state.create_property("UserProfile")


    async def on_turn(self, turn_context: TurnContext):
        await super().on_turn(turn_context)

        # Save any state changes that might have ocurred during the turn.
        await self.conversation_state.save_changes(turn_context)
        await self.user_state.save_changes(turn_context)

    async def on_members_added_activity(self, members_added: [ChannelAccount], turn_context: TurnContext):
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                message = Activity(type = ActivityTypes.message, attachments=[self._create_adaptive_card_attachment()],)
                await turn_context.send_activity(message)

    async def on_message_activity(self, turn_context: TurnContext):
        user_data = await self.user_state_accessor.get(turn_context, UserProfile)

        if user_data.phone == None or user_data.password == None:
            if 'phone' in turn_context.activity.value and 'password' in turn_context.activity.value:
                user_data.phone = turn_context.activity.value['phone']
                user_data.password = turn_context.activity.value['password']
                await turn_context.send_activity("Hi "+ user_data.name)
            else:
                message = Activity(type = ActivityTypes.message, attachments=[self._create_adaptive_card_attachment()],)
                await turn_context.send_activity(message)
        if user_data.phone != None and user_data.password != None:
            await DialogHelper.run_dialog(
                    self.dialog,
                    turn_context,
                    self.conversation_state.create_property("DialogState"),
                    )

    def _create_adaptive_card_attachment(self) -> Attachment:
         card_path = os.path.join(os.getcwd(), CARDS[0])
         with open(card_path, "rb") as in_file:
             card_data = json.load(in_file)
         return CardFactory.adaptive_card(card_data)