import can
from can_read import CanResourceChannel, CanResource
from ui_utils import BarGauge, GearDisplay, VoltageBox, RPM_Display
import pygame

class SteeringWheel(can.notifier.Notifier):

    def __init__(self, bus):
        # Initialize the display.
        pygame.init()
        self.surface = pygame.display.set_mode([720, 480])
        self.gauges = list()
        super().__init__(bus, CanResource("Custom Data Set", list()))
        self.constructors = {
            "BarGauge": BarGauge,
            "GearDisplay": GearDisplay,
            "VoltageBox": VoltageBox,
            "RPM_Display": RPM_Display
        }

    def addGauge(self, channel_name, scaling_factor, gaugeType, label, unit, min_value, max_value, coords = (0,0)):
        if gaugeType in self.constructors:
            newChannel = CanResourceChannel(channel_name, scaling_factor)
            super().listeners = list(super().listeners[0].channels.append(newChannel))
            self.gauges.append(self.constructors[gaugeType](self.surface, coords, label, newChannel, unit, min_value, max_value))
        else:
            print(f"Invalid gauge type: {gaugeType}")

def setup():
    # Create the CAN bus. SocketCan is the kernel support for CAN,
    # can0 is the network created with SocketCan, and the bitrate
    # of the network is 1000000 bits/s.
    canBus = can.interface.Bus(bustype='socketcan', channel='can0', bitrate=1000000)

    # Add a filter to only listen on CAN ID 10, the custom data set ID from motec.
    canBus.set_filters([{"can_id": 10, "can_mask": 0xF, "extended": False}])

    
    # Create the notifier object that will listen to the CAN bus and
    # notify any Listeners registered to it if a message is recieved.
    canNotifier = can.notifier.Notifier(canBus, resources)

def readConfig():
    config = list()
    with open("config.txt") as configFile:
        for line in configFile.read():
            config.append()
    return config

    

if __name__ == '__main__':
    setup()