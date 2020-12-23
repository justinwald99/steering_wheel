"""Main module of the steering wheel that facilitates display."""
import datetime
import logging
import os
import sys
import time

import can
import pygame
import yaml
from gpiozero import PWMLED, Button

from can_read import CanResource, CanResourceChannel
from ui_utils import element_factory

# Path to the config file.
CONFIG_PATH = "config.yaml"

# Path to the config for aspects of the ui and can functionality.
WHEEL_CONFIG_PATH = "wheel_config.yaml"

# Number of log files with debug info kept at a time.
KEPT_LOGS = 25

# Check if there are more than KEPT_LOGS number of log files, delete oldest if neccesary.
while (len(os.listdir("logs")) > KEPT_LOGS - 1):
    fileList = dict()
    for logFile in os.listdir("logs"):
        fileList.update({os.path.getctime(f"logs/{logFile}"): logFile})
    sortedFiles = list(fileList.keys())
    os.remove(f"logs/{fileList[sortedFiles[0]]}")
# Create a new logfile with timestamp.
logging.basicConfig(
    filename=f"logs/steering_wheel_log_{datetime.datetime.now().strftime('%I.%M.%S%p_%a-%b-%d-%Y')}.txt", level="DEBUG")
wheelLogger = logging.getLogger('wheelLogger')

wheelLogger.debug("Starting log...")

# Open the config file.
with open(CONFIG_PATH, 'r') as configFile:
    try:
        config = yaml.safe_load(configFile)
    except yaml.YAMLError as exc:
        wheelLogger.critical(f"Could not open config file: {exc}")
        exit(0)


class SteeringWheel(can.notifier.Notifier):
    """An instance of the steering wheel display.

    Parameters
    ----------
    bus : can.Bus
        Instance of the CAN bus used to recieve messages.

    """

    # Default background color
    BACKGROUND_COLOR = pygame.Color("white")

    def __init__(self, bus):
        """Create a new instance of the steering wheel."""
        # Initialize the display.
        pygame.init()
        self.surface = pygame.display.set_mode([config["options"]["h_res"], config["options"]["v_res"]])
        wheelLogger.debug("Display initialized.")
        self.isNightMode = False
        self.brightnessControl = PWMLED(config["pi_pins"]["brightness_pin"], frequency=1000)
        self.change_brightness()

        # Initialize the Notifier componoent.
        super().__init__(bus, list((CanResource("Custom Data Set", list()),)))

        # Read the config.
        self.read_config()

    def read_config(self):
        """Read the config and create elements."""
        # Open the wheel config file.
        with open(WHEEL_CONFIG_PATH, 'r') as configFile:
            try:
                wheel_config = yaml.safe_load(configFile)
            except yaml.YAMLError as exc:
                wheelLogger.critical(f"Could not open config file: {exc}")
                exit(0)

        # Initialize the ui element factory.
        self.factory = element_factory(self.surface, self.read_theme(config["paths"]["default_theme_path"]),
                                       wheel_config)

        # Add CAN channels to the notifier.
        for channel in wheel_config["can_channels"]:
            self.listeners[0].channels.append(CanResourceChannel(
                channel['name'], channel['scaling_factor']))
            wheelLogger.debug(f"Channel loaded: {channel['name']}.")

        # Add each element in wheel_config.
        for element in wheel_config['ui_elements']:
            self.factory.add_element(element)

    def update(self):
        """Redraw the elements with updated values and blit the screen."""
        # Write black to the screen before every blit.
        self.surface.fill(self.factory.get_theme()['BACKGROUND_COLOR'])

        self.factory.update_all()

        # "Flip" the display (update the display with the newly created surface.
        pygame.display.flip()

    def read_theme(self, fileName):
        """Load in a new theme from a fileName and updates the reference used by all ui_elements.

        Parameters
        ----------
        fileName : string
            Path to the file that contains the theme information to use.

        """
        with open(fileName, "r") as theme:
            loaded_theme = yaml.safe_load(theme)
        # Convert the hex colors in pygame.Color objects.
        for name, color in loaded_theme.items():
            loaded_theme.update({name: pygame.Color(color)})
        return loaded_theme

    def toggle_night_mode(self):
        """Toggle nightmode on the screen."""
        if self.isNightMode:
            self.isNightMode = False
            self.factory.set_theme(config["paths"]["default_theme_path"])
        else:
            self.isNightMode = True
            self.factory.set_theme(config["paths"]["night_theme_path"])

    def change_brightness(self):
        """Change the brightness of the screen in 25% incremenets."""
        self.brightnessControl.value = (
            self.brightnessControl.value - .25) % 1.25


def setup():
    """Run on steering wheel startup."""

    # Create the CAN bus. SocketCan is the kernel support for CAN,
    # can0 is the network created with SocketCan, and the bitrate
    # of the network is 1000000 bits/s.
    canBus = can.interface.Bus(bustype='socketcan', channel='can0', bitrate=1000000)

    # Add a filter to only listen on CAN ID 10, the custom data set ID from motec.
    canBus.set_filters([{"can_id": config["can_info"]["can_channel_id"], "can_mask": 0xF, "extended": False}])

    # Create an instance of the steering wheel listener.
    global wheel
    wheel = SteeringWheel(canBus)

    # Create the right button below the screen.
    global button
    button = Button(config["pi_pins"]["br_button_pin"], pull_up=False)
    button.when_held = wheel.toggle_night_mode
    button.when_activated = wheel.change_brightness

    # Start the loop.
    screen_loop()


def screen_loop():
    lastUpdateTime = time.time()
    while True:
        for event in pygame.event.get():
            # Exit button.
            if event.type == pygame.QUIT:
                sys.exit()
            # Escape to stop running.
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                sys.exit()

        # Update screen at given refresh rate.
        if (time.time() - lastUpdateTime > 1 / config["options"]["refresh_rate"]):
            wheel.update()
            lastUpdateTime = time.time()


if __name__ == '__main__':
    setup()
