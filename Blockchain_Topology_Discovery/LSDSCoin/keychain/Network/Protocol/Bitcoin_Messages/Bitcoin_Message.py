from abc import ABC, abstractmethod


class Bitcoin_Message(ABC):
    def __init__(self, command):
        self.command = command

    def getCommand(self):
        return self.command

    @abstractmethod
    def getPayload(self):
        pass

