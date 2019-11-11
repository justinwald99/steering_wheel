# Steering-Wheel

## Setup

The CAN board used by the steering wheel needs to be setup before it can be used in the Python code for the wheel.

**Step 1:** &nbsp;Add the CAN device to the /boot/config.txt folder on the Pi. To do this, run vim (not installed by default) on the config.txt file with sudo by running the following command:  

    sudo vim /boot/config.txt
and add the following lines:  

    dtoverlay=spi1-3cs
    dtoverlay=mcp2515-can1-1,oscillator=16000000,interrupt=12
The line `dtoverlay=spi1-3cs` tells the raspberry Pi to enable the second spi bus, which is spi1.0, spi1.1, and spi1.2 (the .0, .1, and .2 indicate which chip select a device is using and is allowed reffered to as CS or CE). We need to use the second spi bus because the first one (spi0.0 and spi0.1) is being used by the screen.  
The next line, `dtoverlay=mcp2515-can1-1,oscillator=16000000,interrupt=12` is where we register our CAN chip. This is done by loading the `mcp2515-can1-1` overlay and passing it parameters for the oscillator and interrupt. This overlay will have to be downloaded from this repo (in the Pi `Overlays/Compiled` folder) because the default linux overlays for the MCP2515 only work for spi 0.0 and 0.1. Typically, the 1-1 version should be used, which is written for spi1.1 (CS on BCM pin 17), but I've also created and compiled overlays for 1.0 and 1.2 in case those pins are more convenient. The parameters should be pretty simple, the oscillator is the frequency of the crystal oscillator hooked to the mcp2515 and the interrupt is the pin wired to the interrupt of the MCP2515.  
If done correctly, an entry named **can0** should appear when running the `ifconfig -a` command.

**Step 2:**&nbsp; Automatically start the can network on system start. You can manually start the can0 network with the `sudo ip link set can0 up type can bitrate 1000000` command. Ideally, however, we want this network to be created on startup. This is achieved by adding the following code to the `/etc/network/interfaces` file:

    auto can0
    iface can0 inet manual
        pre-up ip link set $IFACE type can bitrate 1000000 listen-only off restart-ms 1
        up /sbin/ifconfig $IFACE up
        down /sbin/ifconfig $IFACE down
If successful, the command `candump can0` shouldn't produce an error and should provide a stream of can messages being received by the board.  
**Step 3:**&nbsp; Setup the screen. To do this, paste the following commands into the Pi's terminal:

    cd ~
    wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/adafruit-pitft.sh
    chmod +x adafruit-pitft.sh
    sudo ./adafruit-pitft.sh
This will run Adafruit's automated setup procedure. Fill out the options for the 3.5in resistive screen and rotate it 90 degrees. Then answer "no" to the question `Would you like the console to appear on the PiTFT display` and yes to the question `Would you like the HDMI display to mirror to the PiTFT display?`. For more information about this process follow the guide at  https://learn.adafruit.com/adafruit-pitft-3-dot-5-touch-screen-for-raspberry-pi/easy-install-2.
