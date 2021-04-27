from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
)

from botbuilder.dialogs.prompts import ConfirmPrompt, PromptOptions
from botbuilder.core import UserState, MessageFactory, ConversationState

class NonPrescription(ComponentDialog):
    def __init__(self, user_data: UserState, dialog_id: str = None):
        super(NonPrescription, self).__init__(dialog_id or NonPrescription.__name__)

        self.user_data_accessor = user_data.create_property("UserProfile")
        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    self.final_step
                ]
            )
        )

        self.initial_dialog_id = WaterfallDialog.__name__

    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        await step_context.context.send_activity("Inside Prescription")
        return await step_context.end_dialog()