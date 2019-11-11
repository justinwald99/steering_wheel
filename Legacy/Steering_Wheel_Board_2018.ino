
#define CAN_RATE_1000  18
#include <Serial_CAN_Module.h>
#include <SoftwareSerial.h>

Serial_CAN can;

#define can_tx  3           // tx of serial can module connect to D3
#define can_rx  2           // rx of serial can module connect to D2

void setup()
{    Serial.begin(9600);
 CANSET:
    can.begin(can_tx, can_rx, 9600);      // tx, rx

    if(can.canRate(CAN_RATE_1000))
    {
        Serial.println("set can rate ok");
    }
    else
    {
        Serial.println("set can rate fail");
        goto CANSET;
    }
}


unsigned long id = 10;
unsigned char dta[8];

void loop()
{
    if(can.recv(&id, dta))
    {
        Serial.print("GET DATA FROM ID: ");
        Serial.println(id);
        for(int i=0; i<8; i++)
        {
            Serial.print("0x");
            Serial.print(dta[i], HEX);
            Serial.print('\t');
        }
        Serial.println();
    }
}


// END FILE
