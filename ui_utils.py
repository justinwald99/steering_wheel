"""Module for the graphical elements of the ui."""
import logging

# import board
# import neopixel
import pygame
from gpiozero import LED

# BCM pin number of the left LED.
L_LED_PIN = 5

# BCM pin number of the right LED.
R_LED_PIN = 6

leftLED = LED(L_LED_PIN)
rightLED = LED(R_LED_PIN)

# pixels = neopixel.NeoPixel(board.D18, 16)


class element_factory():
    """Factory to produce and track ui elements on the steering wheel."""

    def __init__(self, surface, theme, config):
        """Create the element factory.

        Parameters
        ----------
        surface : pygame.surface
            The surface that all elements will be written to.

        theme : dict
            Theme used to color elements. Should be a dict with
            key-value pairs of labels and colors.

        """
        self.surface = surface
        self.theme = theme
        self.config = config
        self.elements = list()

        # Create the list of element constructors.
        self.constructors = {
            "bar_gauge": bar_gauge,
            "GearDisplay": GearDisplay,
            "VoltageBox": VoltageBox,
            "RPM_Display": RPM_Display,
            "DriverWarning": DriverWarning,
            "Background": Background
        }

    def add_element(self, parameters):
        """Add an element to the list of elements on the screen.

        Parameters
        ----------
        parameters : dict
            Dict of key-value pairs that specify the parameters for the gauge. The can channel(s)
            should be specified in a list.
            Ex: type: Background
                channel_name: [engine_rpm]
                imagePath: assets/wmf_wolf.png
                min_val: 11000
                max_val: 12500

        Returns
        -------
        Integer ID for the new element created.

        """
        new_id = len(self.elements)
        new_element = self.constructors[parameters["type"]](self, parameters)
        self.elements.append(new_element)

        return new_id

    def delete_element(self, id):
        """Delete an element by its ID.

        Parameters
        ----------
        id : int
            ID of the element to delete from the list of elements.

        """
        self.elements.pop(id)

    def update_element(self, id):
        """Update a single element, by id, with new info from the DB.

        Parameters
        ----------
        id : int
            Int id of the element to update.

        """
        self.elements[id].update()

    def update_all(self):
        """Update all of the elements from the list with info from the DB."""
        for element in self.elements:
            element.update()

    def set_theme(self, theme):
        """Set the theme that all of the elements will use on next redraw.

        Parameters
        ----------
        theme : dict
            Theme used to color elements. Should be a dict with
            key-value pairs of labels and colors.

        """
        self.theme = theme

    def get_theme(self):
        """Return the current theme dict.

        This will be used by elements to get any applicable colors.

        """
        return self.theme

    def get_surface(self):
        """Return the surface for the factory."""
        return self.surface


class Gauge():
    """Class that holds common functionality for everything that can be described as a gauge.

    Parameters
    ----------
    factory : element_factory
        Parent factory this element will be a part of that will provide surface and theme.

    parameters : dict
        Dict of parameters used to construct the gauge. Must contain at least the following:
            channel_name : String
                A single "channel" within a compound can message that data is pulled from.

    """

    def __init__(self, factory, parameters):
        """Create a new instance of Gauge."""
        self.factory = factory
        self.parameters = parameters

    def update():
        """Update the gauge with new info from the DB and redraw on screen.

        This should be implemented by each gauge as it will be unique to each element.
        """
        print("Method not implemented.")
        exit(1)


# Vertical bar gauge.
class bar_gauge(Gauge):
    """Bar style gauge for displaying critical information.

    Parameters
    ----------
    surface : pygame.surface
        The screen surface that will ultimately be written to.

    canResource : can_read.CanResource
        A single "channel" within a compound can message that data is pulled from.

    theme : dict
        Dictionary with the key-values describing colors to use in the ui.

    x_coord : int
        The x coord of the top left of the ui_element as referenced from the top left of the screen.

    y_coord : int
        The y coord of the top left of the ui_element as referenced from the top left of the screen.

    label : string
        The label for a gauge if applicable.

    unit : string
        Unit of the gauge if applicable.

    min_value : int
        The minimum value a gauge can take on.

    max_value : int
        The maximum value a gauge can take on.

    kwargs : dict
        A dictionary of any parameters not explicitly used by the bar_gauge.

    """

    def __init__(self, factory, parameters):
        """Create a new bar_gauge."""
        super().__init__(factory, parameters)
        self.value = parameters["min_val"]

    def update(self):
        # **************
        # TODO
        # Convert can_read to write to a db and update gauge by that.

        """Draw the graphical elements of the bar_gauge."""
        # Shorten vars
        p = self.parameters
        c = self.factory.config["element_config"]["bar_gauge"]

        # Label
        labelFont = pygame.font.Font('freesansbold.ttf', c["text_size"])
        labelText = labelFont.render(p["label"], False, self.factory.get_theme()['PRIMARY_COLOR'])
        self.factory.get_surface().blit(
            labelText,
            (p["x_coord"] + c["bar_width"] / 2 - labelText.get_width() / 2, p["y_coord"] + c["bar_height"])
        )

        # Gauge fill
        valueRange = p["max_val"] - p["min_val"]
        gaugePercentage = self.value / valueRange
        fillHeight = min(c["bar_height"], round(gaugePercentage * c["bar_height"]))
        fillCoords = (p["x_coord"], p["y_coord"] + c["bar_height"] - fillHeight)
        fillRect = pygame.Rect(fillCoords, (c["bar_width"], fillHeight))
        pygame.draw.rect(self.factory.get_surface(), self.factory.get_theme()['BAR_GAUGE_FILL'], fillRect)

        # Outline
        outlineRect = pygame.Rect((p["x_coord"], p["y_coord"]), (c["bar_width"], c["bar_height"]))
        pygame.draw.rect(self.factory.get_surface(), self.factory.get_theme()['PRIMARY_COLOR'],
                         outlineRect, c["outline_width"])

        # Exact readout
        readoutFont = pygame.font.Font('freesansbold.ttf', c["text_size"])
        readoutText = readoutFont.render(f'{int(self.value)} {p["unit"]}', False,
                                         self.factory.get_theme()['PRIMARY_COLOR'])
        self.factory.get_surface().blit(
            readoutText,
            (p["x_coord"] + c["bar_width"] / 2 - readoutText.get_width() / 2, p["y_coord"] - readoutText.get_height())
        )


class GearDisplay(Gauge):
    """Large gear display in the center of the screen.

    Parameters
    ----------
    surface : pygame.surface
        The screen surface that will ultimately be written to.

    canResource : can_read.CanResource
        A single "channel" within a compound can message that data is pulled from.

    theme : dict
        Dictionary with the key-values describing colors to use in the ui.

    kwargs : dict
        Key words arguments that are optionally passed. None are used for gear display.

    """

    # Text size of the gear readout.
    GEAR_SIZE = 256

    def __init__(self, surface, canResource, theme, **kwargs):
        """Create a new GearDisplay instance."""
        super().__init__(surface, canResource, theme)

    def draw(self):
        """Draw the graphical elements of the GearDisplay."""
        gearFont = pygame.font.Font('freesansbold.ttf', self.GEAR_SIZE)
        gearText = gearFont.render(str(int(self.value)), False, self.theme['PRIMARY_COLOR'])
        self.surface.blit(gearText, (self.surface.get_width() / 2 - gearText.get_width() / 2,
                          self.surface.get_height() / 2 - gearText.get_height() / 2))


class VoltageBox(Gauge):
    """Voltage box in the upper left corner of the display.

    Parameters
    ----------
    surface : pygame.surface
        The screen surface that will ultimately be written to.

    canResource : can_read.CanResource
        A single "channel" within a compound can message that data is pulled from.

    theme : dict
        Dictionary with the key-values describing colors to use in the ui.

    kwargs : dict
        A dictionary of any parameters not explicitly used by the VoltageBox.

    """

    # Number of pixels in the border.
    BORDER_THICKNESS = 5

    # Size of the text.
    TEXT_SIZE = 64

    def __init__(self, surface, canResource, theme, **kwargs):
        """Create a new voltage box instance."""
        super().__init__(surface, canResource, theme)

    def draw(self):
        """Draw the graphical elements onto the screen."""
        backgroundRect = pygame.Rect((0, 0), (150, 80))
        pygame.draw.rect(self.surface, self.theme['VOLTAGE_BOX_BACKGROUND'], backgroundRect)
        backgroundOutline = pygame.Rect((0, 0), (150, 80))
        pygame.draw.rect(self.surface, self.theme['PRIMARY_COLOR'], backgroundOutline, self.BORDER_THICKNESS)
        voltageFont = pygame.font.Font('freesansbold.ttf', self.TEXT_SIZE)
        voltageText = voltageFont.render(str(self.value), False, self.theme['PRIMARY_COLOR'])
        self.surface.blit(voltageText, (10, 5))


class RPM_Display(Gauge):
    """RPM readout at the top center of the screen.

    Parameters
    ----------
    surface : pygame.surface
        The screen surface that will ultimately be written to.

    canResource : can_read.CanResource
        A single "channel" within a compound can message that data is pulled from.

    theme : dict
        Dictionary with the key-values describing colors to use in the ui.

    kwargs : dict
        A dictionary of any parameters not explicitly used by the RPM_Display.
    """

    # Size of the text.
    TEXT_SIZE = 64

    # Vertical distance, in pixels, from the top of the screen.
    VERTICAL_POS = 10

    # Number of Neopix LEDS.
    TOTAL_NEOPIX_LEDS = 16

    # Array for the color of the shift lights at different levels.
    GREEN = (50, 168, 82)
    YELLOW = (247, 255, 5)
    RED = (255, 5, 5)
    BLUE = (5, 59, 255)
    NEOPIX_COLOR_ARRAY = [
        GREEN, GREEN, YELLOW,
        YELLOW, RED, RED,
        BLUE, BLUE
    ]

    def __init__(self, surface, canResource, theme, threshold_val=10000, max_val=13000, **kwargs):
        """Create a new RPM_Display."""
        self.threshold = threshold_val
        super().__init__(surface, canResource, theme, max_val=max_val)

    def draw(self):
        """Draw the graphical elements onto the screen."""
        self.updateNeoPixels()
        rpmFont = pygame.font.Font('freesansbold.ttf', self.TEXT_SIZE)
        rpmText = rpmFont.render(f'{int(self.value)} RPM', False, self.theme['PRIMARY_COLOR'])
        self.surface.blit(rpmText, (self.surface.get_width() / 2 - rpmText.get_width() / 2, self.VERTICAL_POS))

    def updateNeoPixels(self):
        """Update the neopixel sticks with the RPM."""
        pct = (self.value - self.threshold) / (self.max - self.threshold)
        # pct = max(pct, 0)
        # pct = min(pct, 1)
        # numLeds = round(pct * self.TOTAL_NEOPIX_LEDS / 2)
        # for i in range(0, numLeds):
        #     pixels[i] = self.NEOPIX_COLOR_ARRAY[i]
        # for i in range (self.TOTAL_NEOPIX_LEDS - 1, self.TOTAL_NEOPIX_LEDS - 1 - numLeds, -1):
        #     colorIndex = self.TOTAL_NEOPIX_LEDS - i - 1
        #     pixels[i] = self.NEOPIX_COLOR_ARRAY[colorIndex]


class DriverWarning():
    """A warning icon that will apprear if a given conditional is encountered.

    Parameters
    ----------
    surface : pygame.surface
        The screen surface that will ultimately be written to.

    channels : dict
        A dictionary of canResources with items in the following format:
        {channel_name: canResource}

    theme : dict
        Dictionary with the key-values describing colors to use in the ui.

    x_coord : int
        x_coord of the warning. Default = 0

    y_coord : int
        y_coord of the warning. Default = 0

    conditionals : list
        A list of conditionals in the form [can_channel] [operator] [value]. These
        values are space delimited.

    imagePath : string
        That path used by the warning to load the image for the warning.

    kwargs : dict
        Extra key word arguments.

    """

    # List of valid conditional operators.
    OPERATORS = ["<", ">", "<=", ">="]

    # Create steering_wheel logger.
    wheelLogger = logging.getLogger('wheelLogger')

    # Text size under warning.
    TEXT_SIZE = 14

    # Max length of warning text before truncating.
    TEXT_TRUNCATE_LENGTH = 9

    def __init__(self, surface, channels, theme, x_coord=0, y_coord=0, conditionals=[], imagePath="", **kwargs):
        """Create a new driver warning."""
        super().__init__(theme)
        self.surface = surface
        self.channels = channels
        self.x_coord = x_coord
        self.y_coord = y_coord
        self.imagePath = imagePath
        self.image = pygame.image.load(self.imagePath)
        self.rules = []
        self.addConditions(conditionals)

    def updateElement(self):
        """Check the list of conditionals and draw the icon if needed."""
        status = self.checkRules()
        if status == 1:
            leftLED.on()
            self.draw()
        elif status == 2:
            leftLED.on()
            rightLED.on()
            self.draw()
        else:
            leftLED.off()
            rightLED.off()

    def draw(self):
        """Draw the graphical elements to the surface for this icon."""
        self.surface.blit(self.image, (self.x_coord, self.y_coord))

    def addConditions(self, conditionals):
        """Parse the list of conditionals passed, adding them to an internal list of rules.

        Parameters
        ----------
        conditionals : list
            List of conditonals as strings that will get parsed. These conditionals
            will be in the form {can_channel} {operator} {value}. They will be
            space delimited for easy parsing.

        """
        for condition in conditionals:
            parsedValues = condition.split()
            channel = parsedValues[0]
            operator = parsedValues[1]
            value = parsedValues[2]
            isCritical = len(parsedValues) == 4 and parsedValues[3] == "critical"
            if channel not in self.channels.keys() or operator not in self.OPERATORS:
                print(f"Invalid contional: {condition}")
                exit(1)
            self.rules.append([self.channels[channel], operator, value, isCritical])

    def checkRules(self):
        """Check the rules of this warning against updated values of the can channels.

        Returns
        -------
        int
            0 if no rules are met, 1 if a warning is met, and 2 if a critical rule is met.

        """
        rtn = 0
        for rule in self.rules:
            if eval(f"{rule[0].getValue()} {rule[1]} {rule[2]}") and rule[3]:
                self.wheelLogger.warning(f"{rule[0].name} {rule[1]} {rule[2]}")
                # Put the rule's can channel below the warning.
                rpmFont = pygame.font.Font('freesansbold.ttf', self.TEXT_SIZE)
                rpmText = rpmFont.render(f"{rule[0].name[:self.TEXT_TRUNCATE_LENGTH]}", False,
                                         self.theme['PRIMARY_COLOR'])
                self.surface.blit(rpmText, (self.x_coord, self.y_coord + self.image.get_height()))
                rtn = 2
            elif eval(f"{rule[0].getValue()} {rule[1]} {rule[2]}"):
                self.wheelLogger.warning(f"{rule[0].name} {rule[1]} {rule[2]}")
                # Put the rule's can channel below the warning.
                rpmFont = pygame.font.Font('freesansbold.ttf', self.TEXT_SIZE)
                rpmText = rpmFont.render(f"{rule[0].name[:self.TEXT_TRUNCATE_LENGTH]}", False,
                                         self.theme['PRIMARY_COLOR'])
                self.surface.blit(rpmText, (self.x_coord, self.y_coord + self.image.get_height()))
                rtn = 1
        return rtn


class Background():
    """Viper-inspired background animation that activates between a given RPM threshold.

    Parameters
    ----------
    surface : pygame.surface
        The screen surface that will ultimately be written to.

    canResource : can_read.CanResource
        A single "channel" within a compound can message that data is pulled from.

    theme : dict
        Dictionary with the key-values describing colors to use in the ui.

    imagePath : string
        Path to the file to use as the background image.

    min_val : int
        Minimum value that the effect begins.

    max_val : int
        Maximum value of the effect.

    kwargs : dict
        Extra key word arguments.

    """

    def __init__(self, surface, canResource, theme, imagePath="", min_val=0, max_val=1, **kwargs):
        """Create a new Background object."""
        super().__init__(theme)
        self.surface = surface
        self.canResource = canResource
        self.imagePath = imagePath
        self.min_val = min_val
        self.max_val = max_val
        self.value = 0
        self.image = pygame.image.load(self.imagePath)

    def updateElement(self):
        """Check to see if the background is white, if so draw the background animation."""
        if self.theme['BACKGROUND_COLOR'] == pygame.Color("white"):
            self.value = self.canResource.getValue()
            self.draw()

    def draw(self):
        """Calculate the proper alpha (transparency) and draw the background."""
        alpha = (self.value - self.min_val)/(self.max_val - self.min_val) * 255
        alpha = max(alpha, 0)
        alpha = min(alpha, 255)
        self.image.set_alpha(alpha)
        self.surface.blit(self.image, (0, 0))
