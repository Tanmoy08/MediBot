from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
)

from botbuilder.dialogs.prompts import (
    ConfirmPrompt,
    PromptOptions,
    AttachmentPrompt,
    PromptOptions,
    PromptValidatorContext,
    ChoicePrompt)

import urllib.request
import json
from botbuilder.dialogs.choices import Choice
from data_models import UserProfile
from botbuilder.core import UserState, MessageFactory, ConversationState
from helpers import CrmApiHelper, RecognizeCustomForms

class Prescription(ComponentDialog):
    def __init__(self, user_data: UserState, dialog_id: str=None):
        super(Prescription, self).__init__(dialog_id or Prescription.__name__)

        self.crm_api_helper = CrmApiHelper()
        self.recognise_custom_forms = RecognizeCustomForms() 
        self.user_data_accessor = user_data.create_property("UserProfile")
        self.add_dialog(WaterfallDialog(WaterfallDialog.__name__,
                [self.get_prescription_image,
                 self.extract_information_from_prescription,
                 #self.confirm_details,
                 self.final_step]))

        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
        self.add_dialog(AttachmentPrompt(AttachmentPrompt.__name__, Prescription.picture_prompt_validator))
        self.initial_dialog_id = WaterfallDialog.__name__
    
        
    async def get_prescription_image(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        return await step_context.prompt(AttachmentPrompt.__name__, 
            PromptOptions(prompt=MessageFactory.text("Please attach prescription image(jpeg/png)"),
            retry_prompt=MessageFactory.text("Please re-attach prescription, prescription must either be in jpeg or png format."),
            number_of_attempts=3),)

    #async def convert_image_into_bytes(self, step_context: WaterfallStepContext) -> DialogTurnResult:
    #    #step_context.values["Prescription_picture"] = (None if not
    #    #step_context.result else step_context.result[0])
    #    #if(step_context.values["Prescription_picture"] != None):
    #    #    await
    #    #    step_context.context.send_activity(MessageFactory.attachment(step_context.values["Prescription_picture"],
    #    #    "This is your prescription picture."))
    #    return await step_context.next(None)

    async def extract_information_from_prescription(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        
        
        step_context.values["Prescription_picture"] = (None if not step_context.result else step_context.result[0])
        image_url_response = urllib.request.urlopen(step_context.values["Prescription_picture"].content_url)
        image_data = image_url_response.read()
        dict_response = self.recognise_custom_forms.recognize_custom_forms(image_data)
        step_context.values["Medicine_Name"] = dict_response['json']['analyzeResult']['documentResults'][0]['fields']['Medicine details']['valueArray'][0]['valueObject']['Medicine Name']['text']
        step_context.values["Medicine_Quantity"] = dict_response['json']['analyzeResult']['documentResults'][0]['fields']['Medicine details']['valueArray'][0]['valueObject']['Quantity']['text']
        
        Confirm_text = "Please confirm your order : Medicine name - " + step_context.values["Medicine_Name"] + " and quantity - " + step_context.values["Medicine_Quantity"]
        reprompt_text = "I didn't get that, you can use the buttons below as well to respond"
        
        return await step_context.prompt(
            ConfirmPrompt.__name__,
            PromptOptions(prompt=MessageFactory.text(Confirm_text),retry_prompt=MessageFactory.text(reprompt_text)))

    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        user_data = await self.user_data_accessor.get(step_context.context, UserProfile)
        if step_context.result and step_context.result != None:
            await step_context.context.send_activity("Please wait while i am placing your order")
            api = "https://orgde91d4a0.api.crm.dynamics.com/api/data/v9.2/mom_orders"
            data = {"mom_name":user_data.name,"mom_phonenumber":user_data.phone,"mom_medicine":step_context.values["Medicine_Name"],"mom_dose":step_context.values["Medicine_Quantity"]}
            response = await self.crm_api_helper.Create_Record(api, data)
            if response.raise_for_status() == None:
                await step_context.context.send_activity("Order successfully placed for medicine name - " + step_context.values["Medicine_Name"] + " , quantity - " + step_context.values["Medicine_Quantity"])
            else:
                await step_context.context.send_activity("Unable to place the order, please try again later")
        else:
            await step_context.context.send_activity("Sure, you can try again once sure.")
        return await step_context.end_dialog()

    @staticmethod
    async def picture_prompt_validator(prompt_context: PromptValidatorContext) -> bool:
        if not prompt_context.recognized.succeeded:
            await prompt_context.context.send_activity("No attachment received kindly, re-attach prescription. prescription must either be in jpeg or png format.")
            return False
        attachments = prompt_context.recognized.value
        valid_images = [
            attachment
            for attachment in attachments
            if attachment.content_type in ["image/jpeg", "image/png"]
        ]
        prompt_context.recognized.value = valid_images
        return len(valid_images) > 0