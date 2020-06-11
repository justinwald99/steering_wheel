import csv
import sys
import time

import can
import pygame

from can_read import CanResource, CanResourceChannel
from ui_utils import BarGauge, GearDisplay, RPM_Display, VoltageBox, Warning

# Refresh rate in Hz.
REFRESH_RATE = 20

# Path to the config file.
CONFIG_PATH = "config.csv"

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
        self.gauges = list()

        # Initialize the Notifier componoent.
        super().__init__(bus, list((CanResource("Custom Data Set", list()),)))

        # Read the config.
        self.readConfig()

    def readConfig(self):
        # Open the config file.
        with open(CONFIG_PATH, newline='') as configFile:
            # Read the config as a csv.
            configReader = csv.reader(configFile)
            # Skip the header row.
            next(configReader)
            for row in configReader:
                # GAUGE_TYPE,LABEL,SCALING_FACTOR,X_COORD,Y_COORD,UNIT,MIN_VALUE,MAX_VALUE
                if row[0] == "BarGauge":
                    newChannel = CanResourceChannel(row[1], float(row[2]))
                    self.listeners[0].channels.append(newChannel)
                    self.gauges.append(BarGauge(self.surface, (int(row[3]), int(row[4])), row[1], newChannel, row[5], float(row[6]), float(row[7])))
                elif row[0] == "GearDisplay":
                    newChannel = CanResourceChannel(row[1], float(row[2]))
                    self.listeners[0].channels.append(newChannel)
                    self.gauges.append(GearDisplay(self.surface, (0, 0), row[1], newChannel, row[5], float(row[6]), float(row[7])))
                elif row[0] == "VoltageBox":
                    newChannel = CanResourceChannel(row[1], float(row[2]))
                    self.listeners[0].channels.append(newChannel)
                    self.gauges.append(VoltageBox(self.surface, (0, 0), row[1], newChannel, row[5], float(row[6]), float(row[7])))
                elif row[0] == "RPM_Display":
                    newChannel = CanResourceChannel(row[1], float(row[2]))
                    self.listeners[0].channels.append(newChannel)
                    self.gauges.append(RPM_Display(self.surface, (0, 0), row[1], newChannel, row[5], float(row[6]), float(row[7])))
                elif row[0] == "Warning":
                    self.listeners[0].channels.append(newChannel)
                    self.gauges.append(RPM_Display(self.surface, (0, 0), row[1], newChannel, lambda x: x > ))
                else:
                    print(f"Invalid gauge type: {row[0]}")
            print (self.gauges)

    def update(self):
        '''Redraw the gauges with updated values and blit the screen.

        '''

        # Write black to the screen before every blit.
        self.surface.fill((255, 255, 255))

        for gauge in self.gauges:
            gauge.draw()

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

    testBus = can.interface.Bus(bustype="virtual", bitrate=100000)
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
        if (time.time() - lastUpdateTime < 1 / REFRESH_RATE):
            wheel.update()
        

if __name__ == '__main__':
    setup()
