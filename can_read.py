"""Handles the CAN-bus functionality of the steering wheel."""
import sqlite3

from can.listener import Listener


class can_channel(Listener):
    """CAN ID-level CAN object.

    can_channel is a subclass of listener that updates values of
    compound can channels that were sent via the on_message_recieved method.
    Being a subclass of listener, it should be passed to a Notifier so that can_channel
    is called when a message is recieved by the Notifier.

    Parameters
    ----------
    name : string
        Name of this CAN id.

    """

    def __init__(self, name):
        """Construct a new can_channel."""
        self.name = name
        self.sub_channels = list()
        conn = sqlite3.connect('messages.db')
        c = conn.cursor()
        c.execute("""DROP TABLE IF EXISTS channel_values""")
        c.execute('''CREATE TABLE channel_values
             (idx int PRIMARY KEY, channel_name text, value float)
        ''')
        c.close()
        conn.commit()
        super().__init__()

    def on_message_received(self, msg):
        """Respond to a new message being recieved.

            This is the method that is called by the Notifier
            when a new CAN Message is recieved.

        Parameters
        ----------
        msg : can.Message
            Raw message object recieved by the CAN bus.
            msg.data will be in the form:
                Index: [0] [1]    [2] [3]     [4] [5]     [6] [7]
                Data: [index 0] [channel 0] [channel 1] [channel 2]

        """
        # Parse index from message
        triplet_index = int.from_bytes(msg.data[0:2], byteorder='little', signed=False)

        # Get number of compound channels in message
        num_compound_channels = (msg.dlc - 2) // 2

        for channel_offset in range(0, num_compound_channels):
            # Index into can message data bytes
            data_offset = channel_offset * 2 + 2
            # Index into compound channel list
            channel_index = triplet_index * 3 + channel_offset
            # Subchannel object
            sub_channel = self.sub_channels[channel_index]

            value = int.from_bytes(msg.data[data_offset: data_offset + 2], byteorder="big") * sub_channel.scaling_factor

            conn = sqlite3.connect('messages.db')
            c = conn.cursor()
            c.execute(
                'INSERT OR REPLACE INTO channel_values (idx, channel_name, value) '
                f'VALUES ({channel_index}, "{sub_channel.name}", {value})'
            )
            conn.commit()

    def add_compound_channel(self, name, scaling_factor):
        """Associate a new compound channel to this resource.

        name : string
            Name of the compound channel.

        scaling_factor : float
            Factor by which all raw values will be multiplied on this channel.

        """
        new_channel = compound_can_channel(name, scaling_factor)
        self.sub_channels.append(new_channel)


class compound_can_channel():
    """Single channel sent via compound messaging.

    Parameters
    ----------
    index : int
        Index of this channel in the compound messaging scheme.

    name : string
        Name of the channel Ex. Oil Temperature.

    scaling_factor : float
        Scaling factor associated with the channel. Ex. .01

    """

    def __init__(self, name, scaling_factor):
        """Create a new compound_can_channel."""
        self.name = name
        self.scaling_factor = scaling_factor
