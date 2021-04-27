# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.schema import Attachment


class UserProfile:
    """
      This is our application state. Just a regular serializable Python class.
    """

    def __init__(self, name: str = "John", phone: str = "7259560352", password: str = "abc123"):
        self.name = name
        self.phone = phone
        self.password = password
