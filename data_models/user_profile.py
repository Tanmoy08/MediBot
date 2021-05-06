# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.schema import Attachment


class UserProfile:
    """
      This is our application state. Just a regular serializable Python class.
    """

    def __init__(self, name: str = "John", phone: str = None, password: str = None, medicine_data:list = [], medicine_inventory:dict = None):
        self.name = name
        self.phone = phone
        self.password = password
        self.medicine_data = medicine_data
        self.medicine_inventory = medicine_inventory