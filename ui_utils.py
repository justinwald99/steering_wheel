"""Module for the graphical elements of the ui."""
import logging
import sqlite3
import time

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

# Create a performance logger.
perf_monitor = logging.getLogger("ui_perf")


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
            "gear_display": gear_display,
            "voltage_box": voltage_box,
            "rpm_display": rpm_display,
            "driver_warning": driver_warning
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
        pre_update_mark = time.perf_counter()

        for element in self.elements:
            element.update()

        perf_monitor.debug(f"element update time: {round((time.perf_counter() - pre_update_mark) * 1000)} ms")

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


class element():
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
        """Create a new instance of element."""
        self.factory = factory
        self.parameters = parameters

    def update():
        """Update the gauge with new info from the DB and redraw on screen.

        This should be implemented by each gauge as it will be unique to each element.
        """
        print("Method not implemented.")
        exit(1)


# Vertical bar gauge.
class bar_gauge(element):
    """Bar style gauge for displaying critical information.

    Parameters
    ----------
    factory : element_factory
        Instance of the parent element factory. This is needed so this gauge can access
        the factory's surface, config, and theme.

    parameters : dict
        Dictionary containing relevant parameters read in from the config file. The following
        options are configurable:

            channel_name : string
                Name used to lookup the correct can channel in the values DB.

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

    """

    def __init__(self, factory, parameters):
        """Create a new bar_gauge."""
        super().__init__(factory, parameters)
        self.value = parameters["min_val"]

    def update(self):
        """Draw the graphical elements of the bar_gauge."""
        # Shorten vars
        p = self.parameters
        c = self.factory.config["element_config"]["bar_gauge"]
        s = self.factory.get_surface()
        t = self.factory.get_theme()

        # Retrieve updated value from db.
        conn = sqlite3.connect('messages.db')
        cursor = conn.cursor()
        # Try to fetch an updated value.
        cursor.execute(f'SELECT value FROM channel_values WHERE channel_name IS "{p["channel_name"]}"')
        result = cursor.fetchone()
        if result:
            self.value, = result
        cursor.close()

        # Label
        labelFont = pygame.font.Font('freesansbold.ttf', c["text_size"])
        labelText = labelFont.render(p["label"], False, t['PRIMARY_COLOR'])
        s.blit(
            labelText,
            (p["x_coord"] + c["bar_width"] / 2 - labelText.get_width() / 2, p["y_coord"] + c["bar_height"])
        )

        # element fill
        valueRange = p["max_val"] - p["min_val"]
        gaugePercentage = self.value / valueRange
        fillHeight = min(c["bar_height"], round(gaugePercentage * c["bar_height"]))
        fillCoords = (p["x_coord"], p["y_coord"] + c["bar_height"] - fillHeight)
        fillRect = pygame.Rect(fillCoords, (c["bar_width"], fillHeight))
        pygame.draw.rect(s, t['BAR_GAUGE_FILL'], fillRect)

        # Outline
        outlineRect = pygame.Rect((p["x_coord"], p["y_coord"]), (c["bar_width"], c["bar_height"]))
        pygame.draw.rect(s, t['PRIMARY_COLOR'],
                         outlineRect, c["outline_width"])

        # Exact readout
        readoutFont = pygame.font.Font('freesansbold.ttf', c["text_size"])
        readoutText = readoutFont.render(f'{int(self.value)} {p["unit"]}', False,
                                         t['PRIMARY_COLOR'])
        s.blit(
            readoutText,
            (p["x_coord"] + c["bar_width"] / 2 - readoutText.get_width() / 2, p["y_coord"] - readoutText.get_height())
        )


class gear_display(element):
    """Large gear display in the center of the screen.

    Parameters
    ----------
    factory : element_factory
        Instance of the parent element factory. This is needed so this gauge can access
        the factory's surface, config, and theme.

    parameters : dict
        Dictionary containing relevant parameters read in from the config file. The following
        options are configurable:

            channel_name : string
                Name used to lookup the correct can channel in the values DB.

            min_val : int
                Minimum value of this gauge.

    """

    def __init__(self, factory, parameters):
        """Create a new gear_display."""
        super().__init__(factory, parameters)
        self.value = parameters["min_val"]

    def update(self):
        """Draw the graphical elements of the gear_display."""
        # Shorten vars
        p = self.parameters
        c = self.factory.config["element_config"]["gear_display"]
        s = self.factory.get_surface()
        t = self.factory.get_theme()

        # Retrieve updated value from db.
        conn = sqlite3.connect('messages.db')
        cursor = conn.cursor()
        # Try to fetch an updated value.
        cursor.execute(f'SELECT value FROM channel_values WHERE channel_name IS "{p["channel_name"]}"')
        result = cursor.fetchone()
        if result:
            self.value, = result
        cursor.close()

        gearFont = pygame.font.Font('freesansbold.ttf', c["gear_size"])
        gearText = gearFont.render(str(int(self.value)), False, t['PRIMARY_COLOR'])
        s.blit(gearText, (s.get_width() / 2 - gearText.get_width() / 2,
                          s.get_height() / 2 - gearText.get_height() / 2))


class voltage_box(element):
    """Voltage box in the upper left corner of the display.

    Parameters
    ----------
    factory : element_factory
        Instance of the parent element factory. This is needed so this gauge can access
        the factory's surface, config, and theme.

    parameters : dict
        Dictionary containing relevant parameters read in from the config file. The following
        options are configurable:

            channel_name : string
                Name used to lookup the correct can channel in the values DB.

            min_val : int
                Minimum value of this gauge.

    """

    def __init__(self, factory, parameters):
        """Create a new gear_display."""
        super().__init__(factory, parameters)
        self.value = parameters["min_val"]

    def update(self):
        """Draw the graphical elements of the voltage_box."""
        # Shorten vars
        p = self.parameters
        c = self.factory.config["element_config"]["voltage_box"]
        s = self.factory.get_surface()
        t = self.factory.get_theme()

        # Retrieve updated value from db.
        conn = sqlite3.connect('messages.db')
        cursor = conn.cursor()
        # Try to fetch an updated value.
        cursor.execute(f'SELECT value FROM channel_values WHERE channel_name IS "{p["channel_name"]}"')
        result = cursor.fetchone()
        if result:
            self.value, = result
        cursor.close()

        """Draw the graphical elements onto the screen."""
        backgroundRect = pygame.Rect((0, 0), (150, 80))
        pygame.draw.rect(s, t['VOLTAGE_BOX_BACKGROUND'], backgroundRect)
        backgroundOutline = pygame.Rect((0, 0), (150, 80))
        pygame.draw.rect(s, t['PRIMARY_COLOR'], backgroundOutline, c["border_thickness"])
        voltageFont = pygame.font.Font('freesansbold.ttf', c["text_size"])
        voltageText = voltageFont.render(str(self.value), False, t['PRIMARY_COLOR'])
        s.blit(voltageText, (10, 5))


class rpm_display(element):
    """RPM readout at the top center of the screen.

    Parameters
    ----------
    factory : element_factory
        Instance of the parent element factory. This is needed so this gauge can access
        the factory's surface, config, and theme.

    parameters : dict
        Dictionary containing relevant parameters read in from the config file. The following
        options are configurable:

            channel_name : string
                Name used to lookup the correct can channel in the values DB.

            min_val : int
                Minimum value of this gauge.

    """

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

    def __init__(self, factory, parameters):
        """Create a new rpm_readout."""
        super().__init__(factory, parameters)
        self.value = parameters["min_val"]

    def update(self):
        """Draw the graphical elements onto the screen."""
        # Shorten vars
        p = self.parameters
        c = self.factory.config["element_config"]["rpm_display"]
        s = self.factory.get_surface()
        t = self.factory.get_theme()

        # Retrieve updated value from db.
        conn = sqlite3.connect('messages.db')
        cursor = conn.cursor()
        # Try to fetch an updated value.
        cursor.execute(f'SELECT value FROM channel_values WHERE channel_name IS "{p["channel_name"]}"')
        result = cursor.fetchone()
        if result:
            self.value, = result
        cursor.close()

        self.updateNeoPixels()
        rpmFont = pygame.font.Font('freesansbold.ttf', c["text_size"])
        rpmText = rpmFont.render(f'{int(self.value)} RPM', False, t['PRIMARY_COLOR'])
        s.blit(rpmText, (s.get_width() / 2 - rpmText.get_width() / 2, c["vertical_pos"]))

    def updateNeoPixels(self):
        """Update the neopixel sticks with the RPM."""
        # ======================================================
        # TODO: Add neopix support

        # pct = (self.value - self.threshold) / (self.max - self.threshold)
        # pct = max(pct, 0)
        # pct = min(pct, 1)
        # numLeds = round(pct * self.TOTAL_NEOPIX_LEDS / 2)
        # for i in range(0, numLeds):
        #     pixels[i] = self.NEOPIX_COLOR_ARRAY[i]
        # for i in range (self.TOTAL_NEOPIX_LEDS - 1, self.TOTAL_NEOPIX_LEDS - 1 - numLeds, -1):
        #     colorIndex = self.TOTAL_NEOPIX_LEDS - i - 1
        #     pixels[i] = self.NEOPIX_COLOR_ARRAY[colorIndex]


class driver_warning(element):
    """A warning icon that will apprear if a given conditional is encountered.

    Parameters
    ----------
    factory : element_factory
        Instance of the parent element factory. This is needed so this gauge can access
        the factory's surface, config, and theme.

    parameters : dict
        Dictionary containing relevant parameters read in from the config file. The following
        options are configurable:

            channel_list: list
                List of channel names needed to check conditions.

            x_coord : int
                The x coord of the top left of the ui_element as referenced from the top left of the screen.

            y_coord : int
                The y coord of the top left of the ui_element as referenced from the top left of the screen.

            conditionals: list
                List of strings that describe conditions by which this warning should activate. General format
                is [channel_name] [operator] [value] [is_critical].
                    - channel_name is the name of the channel this rule applies to.
                    - operator is one of ["<", ">", "<=", ">="]
                    - value should be a float
                    - critical will be blank or the text "critical". This indicates that extra warning should be
                        given to the driver.
                An example string of rules would be: ["oil_pressure > 200", "engine_rpm > 11000 critical"]. This
                would give a warning for oil_pressure values above 200 and would give a critical warning if engine_rpm
                exceeded 11,000.

            image_path: string
                Path to the image file to display if a warning is activated.

    """

    # List of valid conditional operators.
    OPERATORS = ["<", ">", "<=", ">="]

    # Create warning logger.
    warning_logger = logging.getLogger('warnings')

    def __init__(self, factory, parameters):
        """Create a new driver_warning."""
        super().__init__(factory, parameters)
        self.image = pygame.image.load(self.parameters["image_path"])
        self.rules = []
        self.add_rules(self.parameters["conditionals"])

    def update(self):
        """Check the list of conditionals and draw the icon if needed."""
        status = self.check_rules()
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
        # Shorten vars
        p = self.parameters
        self.factory.get_surface().blit(self.image, (p["x_coord"], p["y_coord"]))

    def add_rules(self, conditionals):
        """Parse the list of conditionals passed, adding them to an internal list of rules.

        Parameters
        ----------
        conditionals : list
            List of conditonals as strings that will get parsed. These conditionals
            will be in the form [channel_name] [operator] [value] [is_critical]. They will be
            space delimited for easy parsing.

        """
        # Shorten vars
        p = self.parameters

        for condition in conditionals:
            parsedValues = condition.split()
            channel = parsedValues[0]
            operator = parsedValues[1]
            value = parsedValues[2]
            isCritical = (len(parsedValues) == 4 and parsedValues[3] == "critical")
            if channel not in p["channel_list"] or operator not in self.OPERATORS:
                print(f"Invalid contional: {condition}")
                exit(1)
            self.rules.append([channel, operator, value, isCritical])

    def check_rules(self):
        """Check the rules of this warning against updated values of the can channels.

        Returns
        -------
        int
            0 if no rules are met, 1 if a warning is met, and 2 if a critical rule is met.

        """
        # Shorten vars
        p = self.parameters
        c = self.factory.config["element_config"]["driver_warning"]
        s = self.factory.get_surface()
        t = self.factory.get_theme()

        # Retrieve updated value from db.
        conn = sqlite3.connect('messages.db')
        cursor = conn.cursor()
        # Try to fetch an updated value.
        channels = ", ".join([f'"{x}"' for x in p["channel_list"]])
        cursor.execute(f'SELECT value FROM channel_values WHERE channel_name IN ({channels}) ORDER BY channel_name ASC')
        results = cursor.fetchall()
        values = {}
        for channel, value in zip(sorted(p["channel_list"]), results):
            values.update({channel: value[0]})

        cursor.close()

        rtn = 0
        rpmFont = pygame.font.Font('freesansbold.ttf', c["text_size"])
        for rule in self.rules:
            if rule[0] not in values or eval(f"{values[rule[0]]} {rule[1]} {rule[2]}") and rule[3]:
                self.warning_logger.critical(f"{rule[0]} {rule[1]} {rule[2]}")
                # Put the rule's can channel below the warning.
                rpmText = rpmFont.render(f"{rule[0][:c['text_truncate_length']]}", False,
                                         t['PRIMARY_COLOR'])
                s.blit(rpmText, (p["x_coord"], p["y_coord"] + self.image.get_height()))
                rtn = 2
            elif rule[0] not in values or eval(f"{values[rule[0]]} {rule[1]} {rule[2]}"):
                self.warning_logger.warning(f"{rule[0]} {rule[1]} {rule[2]}")
                # Put the rule's can channel below the warning.
                rpmText = rpmFont.render(f"{rule[0][:c['text_truncate_length']]}", False,
                                         t['PRIMARY_COLOR'])
                s.blit(rpmText, (p["x_coord"], p["y_coord"] + self.image.get_height()))
                rtn = 1
        return rtn
