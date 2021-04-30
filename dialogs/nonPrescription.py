from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
)

from data_models import UserProfile
from helpers import CrmApiHelper
from botbuilder.dialogs.choices import Choice
from botbuilder.dialogs.prompts import ConfirmPrompt, PromptOptions ,TextPrompt, NumberPrompt, ChoicePrompt
from botbuilder.core import UserState, MessageFactory, ConversationState


class NonPrescription(ComponentDialog):
    def __init__(self, user_data: UserState, dialog_id: str=None):
        super(NonPrescription, self).__init__(dialog_id or NonPrescription.__name__)

        self.crm_api_helper = CrmApiHelper()
        self.user_data_accessor = user_data.create_property("UserProfile")
        self.add_dialog(WaterfallDialog(WaterfallDialog.__name__,
                [self.get_medicine_name,
                    self.get_dose,
                    self.confirm_dose,
                    self.final_step]))
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(NumberPrompt(NumberPrompt.__name__))
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))
        self.initial_dialog_id = WaterfallDialog.__name__

    async def get_medicine_name(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        return await step_context.prompt(TextPrompt.__name__,
            PromptOptions(prompt=MessageFactory.text("Please enter medicine name.")),)

    async def get_dose(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        step_context.values["medicine_name"] = step_context.result
        return await step_context.prompt(NumberPrompt.__name__,
            PromptOptions(prompt=MessageFactory.text("Please enter medicine quantity")),)

    async def confirm_dose(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        step_context.values["medicine_dose"] = step_context.result
        Confirm_text = "Please confirm your order : Medicine name - " + step_context.values["medicine_name"] + " and quantity - " + str(step_context.values["medicine_dose"])
        reprompt_text = "I didn't get that, you can use the buttons below as well to respond"
        return await step_context.prompt(
                        ConfirmPrompt.__name__,
                        PromptOptions(prompt=MessageFactory.text(Confirm_text),retry_prompt=MessageFactory.text(reprompt_text)))

    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        user_data = await self.user_data_accessor.get(step_context.context, UserProfile)
        if step_context.result and step_context.result != None:
            await step_context.context.send_activity("Please wait while i am placing your order")
            api ="https://orgde91d4a0.api.crm.dynamics.com/api/data/v9.2/mom_orders"
            data = {"mom_name":user_data.name,"mom_phonenumber":user_data.phone,"mom_medicine":step_context.values["medicine_name"],"mom_dose":str(step_context.values["medicine_dose"])}
            response = await self.crm_api_helper.Create_Record(api, data)
            if response.raise_for_status() == None:
                await step_context.context.send_activity("Order successfully placed for medicine name - "+ step_context.values["medicine_name"] +" , quantity - " + str(step_context.values["medicine_dose"]))
            else:
                await step_context.context.send_activity("Unable to place the order, please try again later")
        else:
            await step_context.context.send_activity("Sure, you can try again once sure.")
        return await step_context.end_dialog()