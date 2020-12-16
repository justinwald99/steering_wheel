"""Handles the CAN-bus functionality of the steering wheel."""

from can.listener import Listener


class CanResource(Listener):
    """ID-level CAN object.

    CanResource is a subclass of listener that updates values of
    individual can channels that were sent via compount meesaging
    via the on_message_recieved method. Being a subclass
    of listener, it should be passed to a Notifier so that CanResource
    is called when a message is recieved by the Notifier.

    Parameters
    ----------
    name : string
        Name of the CAN resource. One name should be
        assigned per CAN ID.

    channels : list
        List of CAN channels associated with this CanResource.
        CAN Resources are compound messages that contain multiple
        can chhanels sent over a single CAN ID and indexed by the
        first two bytes of each CAN message.

    """

    def __init__(self, name, channels):
        """Construct a new CanResource."""
        self.name = name
        self.channels = channels
        super().__init__()

    def on_message_received(self, msg):
        """Respond to a new message being recieved.

            This is the method that is called by the Notifier
            when a new CAN Message is recieved.

        Parameters
        ----------
        msg : can.Message
            Raw message object recieved by the CAN bus.

        """
        tripletIndex = int.from_bytes([msg.data[0], msg.data[1]], byteorder='little', signed=False)
        self.updateValues(tripletIndex, msg.data)

    def updateValues(self, tripletIndex, msgData):
        """Update the values of CanResourceChannels.

        UpdateValues updates the corresponding channels with information
        from the message passed to it.

        Parameters
        ----------
        tripletIndex : int
            Index indicating which channel triplet the data is for.

        msgData : list
            msgData will be in the form:
                Index: [0] [1]    [2] [3]     [4] [5]     [6] [7]
                Data: [index 0] [channel 0] [channel 1] [channel 2]

        """
        # Remove index bytes
        msgData.pop(0)
        msgData.pop(0)
        channelsInMessage = len(msgData) // 2
        for index in range(0, channelsInMessage):
            channelIndex = tripletIndex * 3 + index
            channel = self.channels[channelIndex]
            dataIndex = index * 2
            dataBytes = [msgData[dataIndex], msgData[dataIndex + 1]]
            channel.updateValue(dataBytes)


class CanResourceChannel():
    """Single channel sent via compound messaging.

    Parameters
    ----------
    name : string
        Name of the channel Ex. Oil Temperature.

    scalingFactor : float
        Scaling factor associated with the channel. Ex. .01

    """

    def __init__(self, name, scalingFactor):
        """Create a new CanResourceChannel."""
        self.name = name
        self.value = 0
        self.scalingFactor = scalingFactor

    def updateValue(self, dataBytes):
        """Update the value field of the channel.

        Parameters
        ----------
        dataBytes : list
            List of two bytes that make up the data of a single channel.

        """
        rawData = int.from_bytes(dataBytes, byteorder='big', signed=False)
        self.value = rawData * self.scalingFactor

    def getValue(self):
        """Get the value of this CAN channel."""
        return self.value
