import logging
import sys
import time
import random

import can
import pygame
import yaml

from can_read import CanResource, CanResourceChannel
from ui_utils import BarGauge, GearDisplay, RPM_Display, VoltageBox, Warning

# Refresh rate in Hz.
REFRESH_RATE = 25

# Path to the config file.
CONFIG_PATH = "config.yaml"

# Create steering_wheel logger.
wheelLogger = logging.getLogger('wheelLogger')

if (len(sys.argv) > 1):
    if (sys.argv[1][0:4] == "log="):
        logging.basicConfig(level=sys.argv[1][4:])
    else:
        print(
            "\nusage: python steering_wheel log=[DEBUG_LEVEL]\n"
            "    ex: python steering_wheel log=DEBUG\n"
            "    LOGGING_LEVELS:\n"
            "        DEBUG, INFO, WARNING, ERROR, CRITICAL"
        )
        exit(1)
    

wheelLogger.debug("Starting log...")

class SteeringWheel(can.notifier.Notifier):
    """ An instance of the steering wheel display.

    Parameters
    ----------
    bus : can.Bus
        Instance of the CAN bus used to recieve messages.

    """
    def __init__(self, bus):
        # Initialize the display.
        pygame.init()
        self.surface = pygame.display.set_mode([720, 480])
        self.elements = list()
        wheelLogger.debug("Display initialized.")

        # Initialize the Notifier componoent.
        super().__init__(bus, list((CanResource("Custom Data Set", list()),)))

        # Create the list of ui_util constructors.
        self.constructors = {
            "BarGauge": BarGauge,
            "GearDisplay": GearDisplay,
            "VoltageBox": VoltageBox,
            "RPM_Display": RPM_Display
        }

        # Read the config.
        self.readConfig()

    def readConfig(self):
        # Open the config file.
        with open(CONFIG_PATH, 'r') as configFile:
            try:
                config = yaml.safe_load(configFile)
            except yaml.YAMLError as exc:
                print(exc)
        
        # Add CAN channels to the notifier.
        for channel in config["can_channels"]:
            self.listeners[0].channels.append(CanResourceChannel(channel['name'], channel['scaling_factor']))
            wheelLogger.debug(f"Channel loaded: {channel['name']}.")

        for element in config['ui_elements']:
            if element['type'] in self.constructors:
                # Retrieve the correct can channel for the element.
                canChannel = None
                for channel in self.listeners[0].channels:
                    if channel.name == element['channel_name']:
                        canChannel = channel
                        break
                # Ensure a channel was found.
                if not canChannel:
                    wheelLogger.warning(f"Invalid can channel: {element['channel_name']}")
                else:
                    # Call the correct constructor.
                    self.elements.append(self.constructors[element['type']](self.surface, canChannel, **element))
                    wheelLogger.debug(f"UI element loaded: {element['type']}.")
            else:
                wheelLogger.warning(f"Invalid gauge type: {element['type']}")

    def update(self):
        '''Redraw the elements with updated values and blit the screen.

        '''

        # Write black to the screen before every blit.
        self.surface.fill((255, 255, 255))

        for element in self.elements:
            element.updateElement()

        # "Flip" the display (update the display with the newly created surface.
        pygame.display.flip()

def setup():
    # Create the CAN bus. SocketCan is the kernel support for CAN,
    # can0 is the network created with SocketCan, and the bitrate
    # of the network is 1000000 bits/s.

    # ########## REAL CAN BUS ######### #
    # canBus = can.interface.Bus(bustype='socketcan', channel='can0', bitrate=1000000)
    # ########## TEST CAN BUS ######### #
    canBus = can.interface.Bus(bustype='virtual', bitrate=1000000)

    # Add a filter to only listen on CAN ID 10, the custom data set ID from motec.
    # canBus.set_filters([{"can_id": 10, "can_mask": 0xF, "extended": False}])

    
    # # Create the notifier object that will listen to the CAN bus and
    # # notify any Listeners registered to it if a message is recieved.
    # canNotifier = can.notifier.Notifier(canBus, resources)

    wheel = SteeringWheel(canBus)

    testBus = can.interface.Bus(bustype="virtual", bitrate=1000000)
    testBus.send(can.Message(arbitration_id=10, data=bytearray(b'\x00\x00\x09\xC4\x08\x34\x07\x6C')))
    testBus.send(can.Message(arbitration_id=10, data=bytearray(b'\x01\x00\x0B\x54\x00\x03\x05\x0A')))
    testBus.send(can.Message(arbitration_id=10, data=bytearray(b'\x02\x00\x09\xC4')))

    lastUpdateTime = time.time()
    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    sys.exit()
        # Update screen at given refresh rate.
        if (time.time() - lastUpdateTime > 1 / REFRESH_RATE):
            preUpdate = time.time()
            wheel.update()
            wheelLogger.info(f"cpu_fps: {int(1 / (time.time() - preUpdate))}")
            wheelLogger.info(f"real_fps: {int(1 / (time.time() - lastUpdateTime))}")
            lastUpdateTime = time.time()
        testBus.send(can.Message(arbitration_id=10, data=bytearray(list([0,0,1,int(random.random()*255),1,int(random.random()*255),1,int(random.random()*255)]))))

if __name__ == '__main__':
    setup()
