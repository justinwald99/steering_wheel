// WM Racing steering wheel arduino board 2018
// use Seeed Studio CAN Bus Shield and Library

//Libraries:
#include <Adafruit_NeoPixel.h>
#include <SPI.h>
#include "mcp_can.h"

//NeoPixel Strip Pin
#define PIN 6

// CAN Address of the recieveing device:
#define CAN_ID 10

// CAN sensor channels, in the order they appear in the custom data set 2
// in MoTeC. Each channel has 2 bytes of data for compound messaging
// Message format: 0:index 1:0 2:a 3:b 4:c 5:d 6:e 7:f
//                 1:index 1:0 2:g 3:h 4:i 5:j 6:k 7:l
// Where the number is the byte number and the letter is the specific index

#define number_channels 5 //number of CAN channels being sent

// Channel set 1 
#define run_time [2 3] // channel 1 [a, b]
//#define rpm [4, 5]  // channel 2 [c, d]
#define engine_temp [6, 7]  // channel 3 [e, f]

// Channel set 2
#define oil_pressure [2, 3]  // channel 4 [g, h]
#define throttle_position [4, 5]  // channel 5 [i, j]

#define channel_layout [0, 1, 2, 3, 4, 5, 6, 7]

// To convert CAN message from HEX to measured value:
// Channel data = (256*a + b)x
// where a = first byte, b = second byte, x = scaling factor
// Scaling factor comes from MoTeC document PSAU0015
double scaling[] = {1, 1, .1, .1, .1}; // in order of the channels


//Constants:
// the cs pin of the version after v1.1 is default to D9
// v0.9b and v1.0 is default D10
const int SPI_CS_PIN = 9;

unsigned char len = 0;
unsigned char buf[8];


// Initiate NeoPixel strip
Adafruit_NeoPixel strip = Adafruit_NeoPixel(16, PIN, NEO_GRB + NEO_KHZ800);

uint32_t 
  green = strip.Color(0, 255, 0),
  yellow = strip.Color(255, 255, 0),
  red = strip.Color(255, 0, 0),
  flash1 = strip.Color(255, 255, 255),
  flash2 = strip.Color(0, 0, 255),
  color[3] = {green, yellow, red};

long prevBlinkTime = 0;

int 
  prev_range = 10,
  shiftPT[2] = {1500, 3000},  // point 0 = the activation point 1 = warning point
  ledStages[4] = {0,3,5,7},   // this is where each stage of the led strip is set. i.e. from ledStages[0] and ledStages[1] is stage one and so on
  warningState = 0,
  blinkInterval = 150,
  security_led_opt = 0,       // 0 = off, 1 = blink , 2 = knight rider
  stripBrightness = 255,      // 0 = off, 255 = fullbright
  ledFlip[] = {15, 14, 13, 12, 11, 10, 9, 8},
  chan1,
  chan2,
  chan3,
  chan4,
  chan5,
  chan6;

MCP_CAN CAN(SPI_CS_PIN);    // Set CS (chip select) pin

//Debugging
#define Serial_start 1


void setup()
{
    if(Serial_start == 1)
    {
        Serial.begin(19200);
    }
    
    while (CAN_OK != CAN.begin(CAN_1000KBPS))   // init can bus : baudrate = 1000k
    {
        Serial.println("CAN BUS Shield init fail");
        Serial.println(" Init CAN BUS Shield again");
        delay(100);
    }
    Serial.println("CAN BUS Shield init ok!");

      strip.begin();
  strip.setBrightness(stripBrightness);
  strip.show(); // Initialize all pixels to 'off'
}


void loop()
{
    unsigned char len = 0;
    unsigned char buf[8];

    if(CAN_MSGAVAIL == CAN.checkReceive())            // check if data coming
    {
        CAN.readMsgBuf(&len, buf);    // read data,  len: data length, buf: data buf

        unsigned long canId = CAN.getCanId();    // gets CAN address
        if (canId == CAN_ID) 
        {        
        //    Serial.println("-----------------------------");
         //   Serial.print("Get data from ID: 0x");
          //  Serial.println(canId, HEX);
            
            for(int i = 0; i<len; i++)    // print the data
            {
              //  Serial.print(buf[i], HEX);
              //  Serial.print("\t");
            }
            
            messageConversion(buf);
            
         //   Serial.print("\t");
         //   Serial.print(len, HEX);
         //  Serial.println();
        } 
    
     }
    
}

void messageConversion(unsigned char buf[])
{    
    if(buf[0] == 0)  // Channel set 1
    {
      int chan1 = ((buf[2])* 256 + (buf[3]))*scaling[0];
      int chan2 = ((buf[4])* 256 + (buf[5]))*scaling[1];
      int chan3 = ((buf[6])* 256 + (buf[7]))*scaling[2];
      Serial.println(chan2);
      shift_lights(chan2); 
    }
    else if(buf[0] == 1)
    {
      int chan4 = ((buf[2])* 256 + (buf[3]))*scaling[3];
      int chan5 = ((buf[4])* 256 + (buf[5]))*scaling[4];
 //     int chan6 = ((buf[6])* 256 + (buf[7]))*scaling[5];

    }   

}

void shift_lights(int rpm)
{
unsigned long currentMillis = millis();
  Serial.println(rpm);
  if (rpm >= shiftPT[0] && rpm < shiftPT[1]) { //if the RPM is between the activation pt and the shift pt
    //map the RPM values to 9(really 8 since the shift point and beyond is handled below)and constrain the range
    int rpmMapped = map(rpm, shiftPT[0], shiftPT[1], 0, 8);
    int rpmConstrained = constrain(rpmMapped, 0, 8);
    
   
    if (prev_range != rpmConstrained) { //This makes it so we only update the LED when the range changes so we don't readdress the strip every reading
      prev_range = rpmConstrained;
#ifdef USE_SERIAL      
      Serial.print("RPM LED Range: ");
      Serial.println(rpmConstrained);
      Serial.print("RPM: ");
      Serial.println(rpm);
#endif     
      clearStrip();
      for (int ledNum = 0; ledNum <= rpmConstrained; ledNum++) {
        if (ledNum <= ledStages[1]) 
        { 
          strip.setPixelColor(ledNum, color[0]);
          strip.setPixelColor(ledFlip[ledNum], color[0]); 
        }
        else if (ledNum > ledStages[1] && ledNum <= ledStages[2])
        { 
          strip.setPixelColor(ledNum, color[1]);
          strip.setPixelColor(ledFlip[ledNum], color[1]);  
        }
        else if (ledNum > ledStages[2] && ledNum < strip.numPixels()) 
        { 
          strip.setPixelColor(ledNum, color[2]);
          strip.setPixelColor(ledFlip[ledNum], color[2]);  
        }
      }
      strip.show();
    }
  }
  else if (rpm >= shiftPT[1]) { //SHIFT DAMNIT!! This blinks the LEDS back and forth with no delay to block button presses
    prev_range = 8;
    if (currentMillis - prevBlinkTime > blinkInterval){
      prevBlinkTime = currentMillis;
      
      if (warningState == 0){
        warningState = 1;
        for(int i = 0; i < strip.numPixels(); i=i+2){
          strip.setPixelColor(i, flash1);
        }
        for(int i = 1; i < strip.numPixels(); i=i+2){
          strip.setPixelColor(i, 0);
        }
      }
      else {
        warningState = 0;
        for(int i = 1; i < strip.numPixels(); i=i+2){
          strip.setPixelColor(i, flash2);
        }
        for(int i = 0; i < strip.numPixels(); i=i+2){
          strip.setPixelColor(i, 0);
        }
      }
      strip.show();
    }
  }
  else {
    if (prev_range != 10) {
      prev_range = 10;
      clearStrip();
#ifdef USE_SERIAL      
      Serial.println("Exiting strip range");
#endif      
    }
  }
}

//====================
// Clears the led strip
//====================
void clearStrip() {
  for (int ledNum = ledStages[0]; ledNum <= strip.numPixels(); ledNum++) {
    strip.setPixelColor(ledNum, 0);
  }
  strip.show(); 
}

//====================
// Blink the first led 
//====================
void blink_led(int count, int ms_delay, int colorInt) {
  clearStrip();
  strip.setBrightness(stripBrightness/4);
  for (int i = 0; i < count; i++) {
    strip.setPixelColor(0, colorInt);
    strip.show(); 
    delay(ms_delay);
    clearStrip();
    delay(ms_delay/2);
  }
  strip.setBrightness(stripBrightness);
  clearStrip();
}


/*********************************************************************************************************
  END FILE
*********************************************************************************************************/
