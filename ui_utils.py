import pygame
import random

class Gauge():
    def __init__(self, surface, coordinates, label, canResource, unit, valueMin, valueMax):
        self.surface = surface
        self.coordinates = coordinates
        self.label = label
        self.canResource = canResource
        self.unit = unit
        self.min = valueMin
        self.max = valueMax
        
        self.value = valueMin

    def updateGauge(self):
        self.value = self.canResource.getValue
        self.draw()

    def draw(self):
        pass


# Vertical bar gauge.
class BarGauge(Gauge):

    GAUGE_WIDTH = 40
    GAUGE_HEIGHT = 200
    GAUGE_OUTLINE_WIDTH = 5
    GAUGE_FILL_COLOR = (255, 0, 0)
    GAUGE_OUTLINE_COLOR = (0, 0, 0)
    GAUGE_LABEL_COLOR = (0, 0, 0)
    TEXT_SIZE = 24

    def __init__(self, surface, coordinates, label, canResource, unit, valueMin, valueMax):
        super(surface, coordinates, label, unit, valueMin, valueMax)

    def draw(self):
        # Label
        labelFont = pygame.font.Font('freesansbold.ttf', self.TEXT_SIZE)
        labelText = labelFont.render(self.label, False, self.GAUGE_LABEL_COLOR)
        self.surface.blit(
            labelText, 
            (self.coordinates[0] + self.GAUGE_WIDTH / 2 - labelText.get_width() / 2, self.coordinates[1] + self.GAUGE_HEIGHT)
        )

        # Gauge fill
        valueRange = self.max - self.min
        gaugePercentage = self.value / valueRange
        fillHeight = min(self.GAUGE_HEIGHT, round(gaugePercentage * self.GAUGE_HEIGHT))
        fillCoords = (self.coordinates[0], self.coordinates[1] + self.GAUGE_HEIGHT - fillHeight) 
        fillRect = pygame.Rect(fillCoords, (self.GAUGE_WIDTH, fillHeight))
        pygame.draw.rect(self.surface, self.GAUGE_FILL_COLOR, fillRect)

        # Outline
        outlineRect = pygame.Rect(self.coordinates, (self.GAUGE_WIDTH, self.GAUGE_HEIGHT))
        pygame.draw.rect(self.surface, self.GAUGE_OUTLINE_COLOR, outlineRect, self.GAUGE_OUTLINE_WIDTH)

        # Exact readout
        readoutFont = pygame.font.Font('freesansbold.ttf', self.TEXT_SIZE)
        readoutText = readoutFont.render(f'{self.value} {self.unit}', False, self.GAUGE_LABEL_COLOR)
        self.surface.blit(
            readoutText, 
            (self.coordinates[0] + self.GAUGE_WIDTH / 2 - readoutText.get_width() / 2, self.coordinates[1] - readoutText.get_height())
        )

# Numerical gauge indicating the current gear.
class GearDisplay(Gauge):

    GEAR_COLOR = (0, 0, 0)
    GEAR_SIZE = 256

    def __init__(self, surface):
        super(surface, coordinates, label, unit, valueMin, valueMax)
        self.gear = 'N'

    def draw(self):
        gearFont = pygame.font.Font('freesansbold.ttf', self.GEAR_SIZE)
        gearText = gearFont.render(str(self.gear), False, self.GEAR_COLOR)
        self.surface.blit(gearText, (self.surface.get_width() / 2 - gearText.get_width() / 2, self.surface.get_height() / 2 - gearText.get_height() / 2))

# Voltage box in the upper left corner of the display.
class VoltageBox(Gauge):

    BACKGROUND_COLOR = (253, 255, 130)
    BORDER_COLOR = (0, 0, 0)
    BORDER_THICKNESS = 5
    TEXT_COLOR = (0, 0, 0)
    TEXT_SIZE = 64

    def __init__(self, surface):
        self.voltage = 0
        self.surface = surface

    def draw(self):
        backgroundRect = pygame.Rect((0,0), (150, 80))
        pygame.draw.rect(self.surface, self.BACKGROUND_COLOR, backgroundRect)
        backgroundOutline = pygame.Rect((0,0), (150, 80))
        pygame.draw.rect(self.surface, self.BORDER_COLOR, backgroundOutline, self.BORDER_THICKNESS)
        voltageFont = pygame.font.Font('freesansbold.ttf', self.TEXT_SIZE)
        voltageText = voltageFont.render(str(self.voltage), False, self.TEXT_COLOR)
        self.surface.blit(voltageText, (10, 5))

