import logging

import pygame
import yaml

class Themeable():
    def __init__(self, theme):
        self.theme = theme

class Gauge(Themeable):
    def __init__(self, surface, canResource, theme, x_coord=0, y_coord=0, label="no name", unit="", min_val=0, max_val=1):
        super().__init__(theme)
        self.surface = surface
        self.x_coord = x_coord
        self.y_coord = y_coord
        self.label = label
        self.canResource = canResource
        self.unit = unit
        self.min = min_val
        self.max = max_val
        self.theme = theme
        
        self.value = min_val

    def updateElement(self):
        self.value = self.canResource.getValue()
        self.draw()

    def draw(self):
        pass

# Vertical bar gauge.
class BarGauge(Gauge):

    GAUGE_WIDTH = 40
    GAUGE_HEIGHT = 200
    GAUGE_OUTLINE_WIDTH = 5
    TEXT_SIZE = 24

    def __init__(self, surface, canResource, theme, x_coord=0, y_coord=0, label="no name", unit="", min_val=0, max_val=1, **kwargs):
        super().__init__(surface, canResource, theme, x_coord=x_coord, y_coord=y_coord, label=label, unit=unit, min_val=min_val, max_val=max_val)

    def draw(self):

        # Label
        labelFont = pygame.font.Font('freesansbold.ttf', self.TEXT_SIZE)
        labelText = labelFont.render(self.label, False, self.theme['PRIMARY_COLOR'])
        self.surface.blit(
            labelText, 
            (self.x_coord + self.GAUGE_WIDTH / 2 - labelText.get_width() / 2, self.y_coord + self.GAUGE_HEIGHT)
        )

        # Gauge fill
        valueRange = self.max - self.min
        gaugePercentage = self.value / valueRange
        fillHeight = min(self.GAUGE_HEIGHT, round(gaugePercentage * self.GAUGE_HEIGHT))
        fillCoords = (self.x_coord, self.y_coord + self.GAUGE_HEIGHT - fillHeight) 
        fillRect = pygame.Rect(fillCoords, (self.GAUGE_WIDTH, fillHeight))
        pygame.draw.rect(self.surface, self.theme['BAR_GAUGE_FILL'], fillRect)

        # Outline
        outlineRect = pygame.Rect((self.x_coord, self.y_coord), (self.GAUGE_WIDTH, self.GAUGE_HEIGHT))
        pygame.draw.rect(self.surface, self.theme['PRIMARY_COLOR'], outlineRect, self.GAUGE_OUTLINE_WIDTH)

        # Exact readout
        readoutFont = pygame.font.Font('freesansbold.ttf', self.TEXT_SIZE)
        readoutText = readoutFont.render(f'{int(self.value)} {self.unit}', False, self.theme['PRIMARY_COLOR'])
        self.surface.blit(
            readoutText, 
            (self.x_coord + self.GAUGE_WIDTH / 2 - readoutText.get_width() / 2, self.y_coord - readoutText.get_height())
        )

# Numerical gauge indicating the current gear.
class GearDisplay(Gauge):
    GEAR_SIZE = 256

    def __init__(self, surface, canResource, theme, **kwargs):
        super().__init__(surface, canResource, theme)

    def draw(self):
        gearFont = pygame.font.Font('freesansbold.ttf', self.GEAR_SIZE)
        gearText = gearFont.render(str(int(self.value)), False, self.theme['PRIMARY_COLOR'])
        self.surface.blit(gearText, (self.surface.get_width() / 2 - gearText.get_width() / 2, self.surface.get_height() / 2 - gearText.get_height() / 2))

# Voltage box in the upper left corner of the display.
class VoltageBox(Gauge):
    BORDER_THICKNESS = 5
    TEXT_SIZE = 64

    def __init__(self, surface, canResource, theme, **kwargs):
        super().__init__(surface, canResource, theme)

    def draw(self):
        backgroundRect = pygame.Rect((0,0), (150, 80))
        pygame.draw.rect(self.surface, self.theme['VOLTAGE_BOX_BACKGROUND'], backgroundRect)
        backgroundOutline = pygame.Rect((0,0), (150, 80))
        pygame.draw.rect(self.surface, self.theme['PRIMARY_COLOR'], backgroundOutline, self.BORDER_THICKNESS)
        voltageFont = pygame.font.Font('freesansbold.ttf', self.TEXT_SIZE)
        voltageText = voltageFont.render(str(self.value), False, self.theme['PRIMARY_COLOR'])
        self.surface.blit(voltageText, (10, 5))

class RPM_Display(Gauge):

    TEXT_SIZE = 64
    VERTICAL_POS = 10

    def __init__(self, surface, canResource, theme, **kwargs):
        super().__init__(surface, canResource, theme)

    def draw(self):
        rpmFont = pygame.font.Font('freesansbold.ttf', self.TEXT_SIZE)
        rpmText = rpmFont.render(f'{int(self.value)} RPM', False, self.theme['PRIMARY_COLOR'])
        self.surface.blit(rpmText, (self.surface.get_width() / 2 - rpmText.get_width() / 2, self.VERTICAL_POS))

class DriverWarning(Themeable):

    # List of valid conditional operators.
    OPERATORS = ["<", ">", "<=", ">="]

    # Create steering_wheel logger.
    wheelLogger = logging.getLogger('wheelLogger')

    # Text size under warning.
    TEXT_SIZE = 14

    # Text color

    # Max length of warning text before truncating.
    TEXT_TRUNCATE_LENGTH = 9
    

    def __init__(self, surface, channels, theme, x_coord=0, y_coord=0, conditionals=[], imagePath="", **kwargs):
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
        self.draw()

    def draw(self):
        if self.checkRules():
            self.surface.blit(self.image, (self.x_coord, self.y_coord))

    def addConditions(self, conditionals):
        for condition in conditionals:
            parsedValues = condition.split()
            channel = parsedValues[0]
            operator = parsedValues[1]
            value = parsedValues[2]
            if channel not in self.channels.keys() or operator not in self.OPERATORS:
                print(f"Invalid contional: {condition}")
                exit(1)
            self.rules.append([self.channels[channel], operator, value])

    def checkRules(self):
        for rule in self.rules:
            if eval(f"{rule[0].getValue()} {rule[1]} {rule[2]}"):
                self.wheelLogger.info(f"{rule[0].name} {rule[1]} {rule[2]}")
                # Put the rule's can channel below the warning.
                rpmFont = pygame.font.Font('freesansbold.ttf', self.TEXT_SIZE)
                rpmText = rpmFont.render(f"{rule[0].name[:self.TEXT_TRUNCATE_LENGTH]}", False, self.theme['PRIMARY_COLOR'])
                self.surface.blit(rpmText, (self.x_coord, self.y_coord + self.image.get_height()))
                return True
        return False

class Background(Themeable):

    THRESHOLD=11000
    MAX_VALUE=12500

    def __init__(self, surface, canResource, theme, imagePath="", **kwargs):
        super().__init__(theme)
        self.surface = surface
        self.canResource = canResource
        self.imagePath = imagePath
        self.value = 0
        self.image = pygame.image.load(self.imagePath)

    def updateElement(self):
        if self.theme['BACKGROUND_COLOR'] == pygame.Color("white"):
            self.value = self.canResource.getValue()
            self.draw()

    def draw(self):
        alpha = (self.value - self.THRESHOLD)/(self.MAX_VALUE - self.THRESHOLD) * 255
        self.image.set_alpha(alpha)
        self.surface.blit(self.image, (0, 0))
