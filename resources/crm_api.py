from enum import Enum

class CrmApi(Enum):
    root_url = "https://orgde91d4a0.api.crm.dynamics.com/api/data/v9.2/"


class Orders(Enum):
    name = "mom_orders"
    customer_name = "mom_name"
    phone_number = "mom_phonenumber"

class MedicineInventory(Enum):
    name = "mom_medicineinventories"
    id = "mom_medicineinventoryid"
    medicine_name = "mom_name"
    dose = "mom_dose"
    inventory_stock = "mom_inventorystock"
    get_medicine = "?$select=mom_name,mom_dose,mom_inventorystock&$filter=mom_name eq "

class MedicineLineItems(Enum):
    name = "mom_medicinelineitems"
    order_name = "mom_MedicineLineItemOrderReferenceId@odata.bind"
    quantity = "mom_quantity"
    medicine = "mom_MedicineInventoryReferenceId@odata.bind"




