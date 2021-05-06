from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
)
import json
from data_models import UserProfile
from helpers import CrmApiHelper
from resources.crm_api import CrmApi, Orders, MedicineInventory, MedicineLineItems 
from botbuilder.dialogs.choices import Choice
from botbuilder.dialogs.prompts import ConfirmPrompt, PromptOptions ,TextPrompt, NumberPrompt, ChoicePrompt
from botbuilder.core import UserState, MessageFactory, ConversationState


class NonPrescription(ComponentDialog):
    def __init__(self, user_data: UserState,dialog_id: str=None):
        super(NonPrescription, self).__init__(dialog_id or NonPrescription.__name__)

        self.crm_api_helper = CrmApiHelper()
        self.user_data_accessor = user_data.create_property("UserProfile")
        self.add_dialog(WaterfallDialog(WaterfallDialog.__name__,
            [self.get_medicine_name,
                self.confirm_medicine,
                self.get_quantity,
                self.confirm_quantity,
                self.add_new_medicine,
                self.confirm_add_new_medicine,
                self.final_step]))
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(NumberPrompt(NumberPrompt.__name__))
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))
        self.initial_dialog_id = WaterfallDialog.__name__

    async def get_medicine_name(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        return await step_context.prompt(TextPrompt.__name__,
            PromptOptions(prompt=MessageFactory.text("Please enter medicine name.")),)

    async def confirm_medicine(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        user_data = await self.user_data_accessor.get(step_context.context, UserProfile)
        step_context.values["medicine_name"] = step_context.result
        api = CrmApi.root_url.value + MedicineInventory.name.value + MedicineInventory.get_medicine.value + "'" + step_context.values["medicine_name"] + "'"
        response = await self.crm_api_helper.check_medicine(api)
        if response.raise_for_status() == None:
            deserialised_response = json.loads(response.text)
            if(deserialised_response['value'] != [] and deserialised_response['value'][0] != None):
                user_data.medicine_inventory = deserialised_response['value']
                medicine_dose = []
                for medicine in user_data.medicine_inventory:
                    medicine_dose.append(Choice(medicine[MedicineInventory.dose.value]))
                return await step_context.prompt(ChoicePrompt.__name__,PromptOptions(prompt=MessageFactory.text("Please choose a dose"),choices=medicine_dose,),)                    
            else:
                await step_context.context.send_activity("medicine unavailable in the inventory")
                return await step_context.replace_dialog(NonPrescription.__name__)
                

    async def get_quantity(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        step_context.values["selected_dose"] = step_context.result.value
        return await step_context.prompt(NumberPrompt.__name__,
            PromptOptions(prompt=MessageFactory.text("Please enter medicine quantity")),)

    async def confirm_quantity(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        step_context.values["medicine_quantity"] = step_context.result
        user_data = await self.user_data_accessor.get(step_context.context, UserProfile)

        inventory_medicine_quantity = 0
        for medicine in user_data.medicine_inventory:
            if(medicine[MedicineInventory.dose.value] == step_context.values["selected_dose"]):
                inventory_medicine_quantity = medicine[MedicineInventory.inventory_stock.value]
                step_context.values["medicine_id"] = medicine["mom_medicineinventoryid"]
                break

        if(inventory_medicine_quantity == 0):
            await step_context.context.send_activity("Medicine is out of stock")
            return await step_context.next(None)

        if(step_context.values["medicine_quantity"] <= inventory_medicine_quantity):
            Confirm_text = "do you want add this to cart? : Medicine name - " + step_context.values["medicine_name"] + " " + step_context.values["selected_dose"] + " " + " and quantity - " + str(step_context.values["medicine_quantity"])
            reprompt_text = "I didn't get that, you can use the buttons below as well to respond"
            return await step_context.prompt(ConfirmPrompt.__name__,
                            PromptOptions(prompt=MessageFactory.text(Confirm_text),retry_prompt=MessageFactory.text(reprompt_text)))

        elif(step_context.values["medicine_quantity"] > inventory_medicine_quantity):
            step_context.values["medicine_quantity"] = inventory_medicine_quantity
            await step_context.context.send_activity("Only " + str(step_context.values["medicine_quantity"]) + "quantity of medicine is available in stock")
            Confirm_text = "do you want add this to cart? : Medicine name - " + step_context.values["medicine_name"] + " " + step_context.values["selected_dose"] + " " + " and quantity - " + str(step_context.values["medicine_quantity"])
            reprompt_text = "I didn't get that, you can use the buttons below as well to respond"
            return await step_context.prompt(ConfirmPrompt.__name__,
                            PromptOptions(prompt=MessageFactory.text(Confirm_text),retry_prompt=MessageFactory.text(reprompt_text)))

    
    async def add_new_medicine(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        user_data = await self.user_data_accessor.get(step_context.context, UserProfile)
     
        if step_context.result and step_context.result != None:
            
            user_data.medicine_data.append({"medicine_name":step_context.values["medicine_name"],"selected_dose":step_context.values["selected_dose"],"medicine_quantity":step_context.values["medicine_quantity"],"medicine_id":step_context.values["medicine_id"]})
        
        Confirm_text = "Do you want to add more medicines?"
        reprompt_text = "I didn't get that, you can use the buttons below as well to respond"

        return await step_context.prompt(ConfirmPrompt.__name__,
                                         PromptOptions(prompt=MessageFactory.text(Confirm_text),retry_prompt=MessageFactory.text(reprompt_text)))

    async def confirm_add_new_medicine(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        user_data = await self.user_data_accessor.get(step_context.context, UserProfile)
        if step_context.result and step_context.result != None:
            return await step_context.replace_dialog(NonPrescription.__name__)
        else:
            confirm_text = "Please confirm your order for above medicines in cart:"
            reprompt_text = "I didn't get that, you can use the buttons below as well to respond"
            for each_medicine in user_data.medicine_data:
                await step_context.context.send_activity("Medicine name - " + each_medicine["medicine_name"] + " " + each_medicine["selected_dose"] + " " + " and quantity - " + str(each_medicine["medicine_quantity"]))
            return await step_context.prompt(ConfirmPrompt.__name__,
                                         PromptOptions(prompt=MessageFactory.text(confirm_text),retry_prompt=MessageFactory.text(reprompt_text)))
           
    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        user_data = await self.user_data_accessor.get(step_context.context, UserProfile)
        if True:#step_context.result and step_context.result != None:
            #order creation
            api = CrmApi.root_url.value + Orders.name.value + "?$select=mom_name,mom_orderid"
            data = {Orders.customer_name.value:user_data.name,Orders.phone_number.value:user_data.phone}
            response = await self.crm_api_helper.Create_Record(api, data)
            
            if response.raise_for_status() == None:
                order_id = json.loads(response.text)["mom_orderid"]
            
            #medicine line item creation            
            api = CrmApi.root_url.value + MedicineLineItems.name.value
            for each_medicine in user_data.medicine_data:
                data = {MedicineLineItems.order_name.value:"/mom_orders(" + order_id + ")",MedicineLineItems.quantity.value:121,MedicineLineItems.medicine.value:"/mom_medicineinventories("+each_medicine["medicine_id"]+")"}
                response = await self.crm_api_helper.Create_Record(api, data)
                #Medicine Inventory Quantity Deduction.

        else:
            await step_context.context.send_activity("Sure, you can try again once sure.")
        return await step_context.end_dialog()