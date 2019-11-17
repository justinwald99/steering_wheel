from can_read import canResourceChannel, CanResource
from can import Message

channels = list()
channels.append(canResourceChannel('RPM', 1))
channels.append(canResourceChannel('Engine Temp', 100))
channels.append(canResourceChannel('Oil Pressure', 1))
channels.append(canResourceChannel('Fuel Pressure', 10))
channels.append(canResourceChannel('Throttle Position', 1))
channels.append(canResourceChannel('Oil Temp', 1))
channels.append(canResourceChannel('Battery Voltage', 1))

testResource = CanResource('Custom Data Set', channels)
msg = Message()
msg2 = Message()
msg.data = bytearray(b'\x00\x00\x00\x01\x00\x02\x00\x03')
msg2.data = bytearray(b'\x01\x00\x00\x04\x00\x05\x00\x06')

testResource.on_message_received(msg)
testResource.on_message_received(msg2)