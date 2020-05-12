import sys, pygame
import random
from ui_utils import BarGauge, GearDisplay, VoltageBox
import time

# Initialize the display.
pygame.init()
screen = pygame.display.set_mode([720, 480])

# Add gauges to the screen.
oilPressure = BarGauge(screen, (100, 150), "Oil P", 'PSI', 0, 200)
oilTemperature = BarGauge(screen, (220, 150), "Oil T", 'F', 0, 250)
waterTemperature = BarGauge(screen, (460, 150), "Water T", 'F', 0, 220)
fuelPressure = BarGauge(screen, (580, 150), "Fuel P", 'PSI', 0, 500)
gearPosition = GearDisplay(screen)
voltageBox = VoltageBox(screen)

# Watch for escape key.
while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                sys.exit()

    # Write black to the screen before every blit.
    screen.fill((255, 255, 255))
    
    # Update the gauges, passing their new values.
    oilPressure.updateGauge(140)
    oilTemperature.updateGauge(210)
    waterTemperature.updateGauge(180)
    fuelPressure.updateGauge(300)
    gearPosition.updateGear(3)

    voltageBox.updateVoltage(12.7)

    # "Flip" the display (update the display with the newly created surface.
    pygame.display.flip()
