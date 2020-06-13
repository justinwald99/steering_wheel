import pygame

class Gauge():
    def __init__(self, surface, canResource, x_coord=0, y_coord=0, label="no name", unit="", min_val=0, max_val=1):
        self.surface = surface
        self.x_coord = x_coord
        self.y_coord = y_coord
        self.label = label
        self.canResource = canResource
        self.unit = unit
        self.min = min_val
        self.max = max_val
        
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
    GAUGE_FILL_COLOR = (255, 0, 0)
    GAUGE_OUTLINE_COLOR = (0, 0, 0)
    GAUGE_LABEL_COLOR = (0, 0, 0)
    TEXT_SIZE = 24

    def __init__(self, surface, canResource, x_coord=0, y_coord=0, label="no name", unit="", min_val=0, max_val=1, **kwargs):
        super().__init__(surface, canResource=canResource, x_coord=x_coord, y_coord=y_coord, label=label, unit=unit, min_val=min_val, max_val=max_val)

    def draw(self):

        # Label
        labelFont = pygame.font.Font('freesansbold.ttf', self.TEXT_SIZE)
        labelText = labelFont.render(self.label, False, self.GAUGE_LABEL_COLOR)
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
        pygame.draw.rect(self.surface, self.GAUGE_FILL_COLOR, fillRect)

        # Outline
        outlineRect = pygame.Rect((self.x_coord, self.y_coord), (self.GAUGE_WIDTH, self.GAUGE_HEIGHT))
        pygame.draw.rect(self.surface, self.GAUGE_OUTLINE_COLOR, outlineRect, self.GAUGE_OUTLINE_WIDTH)

        # Exact readout
        readoutFont = pygame.font.Font('freesansbold.ttf', self.TEXT_SIZE)
        readoutText = readoutFont.render(f'{int(self.value)} {self.unit}', False, self.GAUGE_LABEL_COLOR)
        self.surface.blit(
            readoutText, 
            (self.x_coord + self.GAUGE_WIDTH / 2 - readoutText.get_width() / 2, self.y_coord - readoutText.get_height())
        )

# Numerical gauge indicating the current gear.
class GearDisplay(Gauge):

    GEAR_COLOR = (0, 0, 0)
    GEAR_SIZE = 256

    def __init__(self, surface, canResource, **kwargs):
        super().__init__(surface, canResource)

    def draw(self):
        gearFont = pygame.font.Font('freesansbold.ttf', self.GEAR_SIZE)
        gearText = gearFont.render(str(int(self.value)), False, self.GEAR_COLOR)
        self.surface.blit(gearText, (self.surface.get_width() / 2 - gearText.get_width() / 2, self.surface.get_height() / 2 - gearText.get_height() / 2))

# Voltage box in the upper left corner of the display.
class VoltageBox(Gauge):

    BACKGROUND_COLOR = (253, 255, 130)
    BORDER_COLOR = (0, 0, 0)
    BORDER_THICKNESS = 5
    TEXT_COLOR = (0, 0, 0)
    TEXT_SIZE = 64

    def __init__(self, surface, canResource, **kwargs):
        super().__init__(surface, canResource)

    def draw(self):
        backgroundRect = pygame.Rect((0,0), (150, 80))
        pygame.draw.rect(self.surface, self.BACKGROUND_COLOR, backgroundRect)
        backgroundOutline = pygame.Rect((0,0), (150, 80))
        pygame.draw.rect(self.surface, self.BORDER_COLOR, backgroundOutline, self.BORDER_THICKNESS)
        voltageFont = pygame.font.Font('freesansbold.ttf', self.TEXT_SIZE)
        voltageText = voltageFont.render(str(self.value), False, self.TEXT_COLOR)
        self.surface.blit(voltageText, (10, 5))

class RPM_Display(Gauge):

    TEXT_COLOR = (0, 0, 0)
    TEXT_SIZE = 64
    VERTICAL_POS = 10

    def __init__(self, surface, canResource, **kwargs):
        super().__init__(surface, canResource)

    def draw(self):
        rpmFont = pygame.font.Font('freesansbold.ttf', self.TEXT_SIZE)
        rpmText = rpmFont.render(f'{int(self.value)} RPM', False, self.TEXT_COLOR)
        self.surface.blit(rpmText, (self.surface.get_width() / 2 - rpmText.get_width() / 2, self.VERTICAL_POS))

class DriverWarning():

    OPERATORS = ["<", ">", "<=", ">="]

    def __init__(self, surface, canResource, x_coord=0, y_coord=0, conditional="", imagePath="", **kwargs):
        self.surface = surface
        self.canResource = canResource
        self.x_coord = x_coord
        self.y_coord = y_coord
        self.conditional = conditional
        self.imagePath = imagePath
        self.value = 0
        self.image = pygame.image.load(self.imagePath)

    def updateElement(self):
        self.value = self.canResource.getValue()
        self.draw()

    def draw(self):
        operator = self.conditional.split()[0]
        value = self.conditional.split()[1]
        
        if (operator in self.OPERATORS and value.isdecimal() and eval(f"{self.value} {operator} {value}")):
            self.surface.blit(self.image, (self.x_coord, self.y_coord))

class Background():

    THRESHOLD=11000
    MAX_VALUE=12500

    def __init__(self, surface, canResource, imagePath="", **kwargs):
        self.surface = surface
        self.canResource = canResource
        self.imagePath = imagePath
        self.value = 0
        self.image = image = pygame.image.load(self.imagePath)

    def updateElement(self):
        self.value = self.canResource.getValue()
        self.draw()

    def draw(self):
        alpha = (self.value - self.THRESHOLD)/(self.MAX_VALUE - self.THRESHOLD) * 255
        self.image.set_alpha(alpha)
        self.surface.blit(self.image, (0, 0))