from can_read import CanResourceChannel, CanResource
from can import Message
from ui_utils import BarGauge, GearDisplay, VoltageBox, RPM_Display
import pygame
import sys

class TestCanResource():
    def __init__(self, name, channels):
        self.name = name
        self.channels = channels

channels = list()
channels.append(CanResourceChannel('Oil P', .1))
channels.append(CanResourceChannel('Oil T', .1))
channels.append(CanResourceChannel('Water T', .1))
channels.append(CanResourceChannel('Fuel P', .1))
channels.append(CanResourceChannel('Gear Display', 1))
channels.append(CanResourceChannel('Voltage', .01))
channels.append(CanResourceChannel('RPM', 1))

testResource = CanResource('Custom Data Set', channels)
msg = Message()
msg2 = Message()
msg3 = Message()
# key: [index] [oil p] [oil t] [water t]
# value: [0] [250] [210] [190]
# data: [0] [2500] [2100] [1900]
msg.data = bytearray(b'\x00\x00\x09\xC4\x08\x34\x07\x6C')
# key: [index] [fuel p] [gear display] [voltage]
# value: [1] [290] [3] [12.9]
# data: [1] [2900] [3] [1290]
msg2.data = bytearray(b'\x01\x00\x0B\x54\x00\x03\x05\x0A')
# key: [index] [rpm] [] []
# value: [2] [2500] [0] [0]
# data: [2] [2500] [0] [0]
msg3.data = bytearray(b'\x02\x00\x09\xC4')

testResource.on_message_received(msg)
testResource.on_message_received(msg2)
testResource.on_message_received(msg3)

pygame.init()
screen = pygame.display.set_mode([720, 480])

gauges = list()
gauges.append(BarGauge(screen, (100, 150), "Oil P", channels[0], 'PSI', 0, 300))
gauges.append(BarGauge(screen, (220, 150), "Oil T", channels[1], 'F', 0, 250))
gauges.append(BarGauge(screen, (460, 150), "Water T", channels[2], 'F', 0, 220))
gauges.append(BarGauge(screen, (580, 150), "Fuel P", channels[3], 'PSI', 0, 500))
gauges.append(GearDisplay(screen, None, "Gear", channels[4], None, 0, 6))
gauges.append(VoltageBox(screen, None, "Voltage", channels[5], 'Volts', 0, 15))
gauges.append(RPM_Display(screen, None, "RPM", channels[6], 'rpm', 0, 15000))

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
    
    # Update the gauges
    for gauge in gauges:
        gauge.updateGauge()

    # "Flip" the display (update the display with the newly created surface.
    pygame.display.flip()
