#include "ch32fun.h"

// UIAPduino Pro Micro CH32V003 V1.4 schematic:
// D2 / BUILTIN-LED is connected to CH32V003 PC0.
#define BUILTIN_LED_PIN PC0

int main(void)
{
    SystemInit();
    funGpioInitAll();
    funPinMode(BUILTIN_LED_PIN, GPIO_Speed_10MHz | GPIO_CNF_OUT_PP);

    while (1)
    {
        funDigitalWrite(BUILTIN_LED_PIN, FUN_HIGH);
        Delay_Ms(200);
        funDigitalWrite(BUILTIN_LED_PIN, FUN_LOW);
        Delay_Ms(800);
    }
}
