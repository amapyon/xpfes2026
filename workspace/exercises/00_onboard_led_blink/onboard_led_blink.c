#include "ch32fun.h"

/* UIAPduino Pro Micro CH32V003 V1.4: D2 / BUILTIN-LED is PC0, active Low. */
#define BUILTIN_LED_PIN PC0
#define BUILTIN_LED_ON FUN_LOW
#define BUILTIN_LED_OFF FUN_HIGH

int main(void)
{
    SystemInit();
    funGpioInitAll();
    funPinMode(BUILTIN_LED_PIN, GPIO_CFGLR_OUT_10Mhz_PP);

    while (1) {
        funDigitalWrite(BUILTIN_LED_PIN, BUILTIN_LED_ON);
        Delay_Ms(200);
        funDigitalWrite(BUILTIN_LED_PIN, BUILTIN_LED_OFF);
        Delay_Ms(800);
    }
}
