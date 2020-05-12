import sys, pygame
import random
from ui_utils import Gauge, GearDisplay, VoltageBox, RPM_Display

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
print(f'{screen.get_width()} x {screen.get_height()}')

oilPressure = Gauge(screen, (100, 150), "Oil P", 'PSI', 0, 200)
oilTemperature = Gauge(screen, (220, 150), "Oil T", 'F', 0, 250)
waterTemperature = Gauge(screen, (460, 150), "Water T", 'F', 0, 220)
fuelPressure = Gauge(screen, (580, 150), "Fuel P", 'PSI', 0, 500)
gearPosition = GearDisplay(screen)
voltageBox = VoltageBox(screen)
rpmDisplay = RPM_Display(screen)

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                sys.exit()

    screen.fill((255, 255, 255))

    oilPressure.updateGauge(140)
    oilTemperature.updateGauge(210)
    waterTemperature.updateGauge(180)
    fuelPressure.updateGauge(round(random.random() * 300))
    gearPosition.updateGear(3)
    voltageBox.updateVoltage(12.7)
    rpmDisplay.updateRPM(round(random.random() * 10000))

    pygame.display.flip()
