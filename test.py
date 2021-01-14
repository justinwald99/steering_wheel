import sys
import time
import random

import can
import pygame

from gpiozero.pins.mock import MockFactory, MockPWMPin
from gpiozero import Device, Button, PWMLED

# Set the default pin factory to a mock factory
Device.pin_factory = MockFactory(pin_class=MockPWMPin)

from steering_wheel import SteeringWheel

# BCM pin number of the bottom right button.
BR_BUTTON_PIN = 16

# Refresh rate in Hz.
REFRESH_RATE = 30

# Path to the config file.
CONFIG_PATH = "config.yaml"

# Number of logs kept at a time.
KEPT_LOGS = 25

def setup():
    """Run on steering wheel startup.

    """

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

    # Create the right button below the screen.
    button = Button(BR_BUTTON_PIN, pull_up=False, pin_factory=MockFactory())
    button.when_held = wheel.toggle_night_mode
    button.when_activated = wheel.change_brightness

    # Get a reference to mock pin 16 (used by the button)
    btn_pin = button.pin_factory.pin(BR_BUTTON_PIN)

    testBus = can.interface.Bus(bustype="virtual", bitrate=1000000)
    testBus.send(can.Message(arbitration_id=10, data=bytearray(b'\x00\x00\x09\xC4\x08\x34\x07\x6C')))
    testBus.send(can.Message(arbitration_id=10, data=bytearray(b'\x01\x00\x0B\x54\x00\x03\x05\x0A')))
    testBus.send(can.Message(arbitration_id=10, data=bytearray(b'\x02\x00\x09\xC4')))

    # rpm = 8000
    # inc = 15
    lastUpdateTime = time.perf_counter()
    while 1:
        for event in pygame.event.get():
            # Exit button.
            if event.type == pygame.QUIT:
                sys.exit()
            # Escape to stop running.
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_b:
                btn_pin.drive_high()
            else:
                btn_pin.drive_low()

        # Update screen at given refresh rate.
        if (time.perf_counter() - lastUpdateTime > 1 / REFRESH_RATE):
            print(f"framerate: {round(1 / (time.perf_counter() - lastUpdateTime))}")
            lastUpdateTime = time.perf_counter()
            wheel.update()

        # testBus.send(can.Message(arbitration_id=10, data=bytearray(
        #     list([0, 0, 1, int(random.random()*255), 1, int(random.random()*255), 1, int(random.random()*255)])))
        # )
        # rpm = rpm + inc
        # if rpm > 12500 or rpm < 8000:
        #     inc = inc * -1
        # testBus.send(can.Message(arbitration_id=10, data=bytearray(list([2, 0, int(rpm / 256 % 256), int(rpm % 256)]))))
        # testBus.send(can.Message(arbitration_id=10, data=bytearray(list([1, 0, 0, 0, 0, int(random.choice(range(1, 7)))]))))


if __name__ == '__main__':
    setup()
