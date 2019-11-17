import can
from can_read import canResourceChannel, CanResource


def setup():
    # Create the CAN bus. SocketCan is the kernel support for CAN,
    # can0 is the network created with SocketCan, and the bitrate
    # of the network is 1000000 bits/s.
    canBus = can.interface.Bus(bustype='socketcan', channel='can0', bitrate=1000000)

    # Add a filter to only listen on CAN ID 10, the custom data set ID from motec.
    canBus.set_filters([{"can_id": 10, "can_mask": 0xF, "extended": False}])

    # Register a list of channels, in order, that match those specifed in Motec's
    # Custom Data Set section. **Note: Order is important and should be the same
    # as in the Custom Data Set. 
    channels = list()
    channels.append(canResourceChannel('Runtime', 1))
    channels.append(canResourceChannel('RPM', 1))
    channels.append(canResourceChannel('Engine Temp', .1))
    channels.append(canResourceChannel('Oil Pressure', .1))
    channels.append(canResourceChannel('Fuel Pressure', .1))
    channels.append(canResourceChannel('Gear Display', 1))
    channels.append(canResourceChannel('Throttle Position', .1))

    # Register the Custom Data Set as a CanResource. Technically, more
    # CAN channels could be added, but the filter is only allowing some
    # CAN traffic through.
    resources = []
    resources.append(CanResource('Custom Data Set', channels))

    # Create the notifier object that will listen to the CAN bus and
    # notify any Listeners registered to it if a message is recieved.
    canNotifier = can.notifier.Notifier(canBus, resources)

    # Function that keeps the program running until input is recieved.
    input()

if __name__ == '__main__':
    setup()