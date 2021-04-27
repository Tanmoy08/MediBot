# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
)
from botbuilder.dialogs.prompts import (
    TextPrompt,
    NumberPrompt,
    ChoicePrompt,
    ConfirmPrompt,
    AttachmentPrompt,
    PromptOptions,
    PromptValidatorContext,
    DateTimePrompt
)
from botbuilder.dialogs.choices import Choice
from botbuilder.core import MessageFactory, UserState
from dialogs import Prescription, NonPrescription

from data_models import UserProfile


class UserProfileDialog(ComponentDialog):
    def __init__(self, user_state: UserState, prescription_dialog : Prescription, non_prescription_dialog = NonPrescription):
        super(UserProfileDialog, self).__init__(UserProfileDialog.__name__)

        self.user_profile_accessor = user_state.create_property("UserProfile")
        self.prescription_dialog_id = prescription_dialog.id
        self.non_prescription_dialog_id = non_prescription_dialog.id

        self.add_dialog(prescription_dialog)
        self.add_dialog(non_prescription_dialog)
        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    self.transport_step,
                    self.method_step,
                    self.summary_step,
                ],
            )
        )
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))

        self.initial_dialog_id = WaterfallDialog.__name__

    async def transport_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        # WaterfallStep always finishes with the end of the Waterfall or with another dialog;
        # here it is a Prompt Dialog. Running a prompt here means the next WaterfallStep will
        # be run when the users response is received.
        return await step_context.prompt(
            ChoicePrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.text("Please choose mode of order placement."),
                choices=[Choice("Prescription"), Choice("Non-Prescription")],
                number_of_attempts=3
            ),
        )

    async def method_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        if step_context.result.value == "Prescription":
            return await step_context.begin_dialog(self.prescription_dialog_id)
        elif step_context.result.value == "Non-Prescription":
            return await step_context.begin_dialog(self.non_prescription_dialog_id)
        return await step_context.next(None);

    async def summary_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        await step_context.context.send_activity("Say Hi to restart")
        return await step_context.end_dialog()
