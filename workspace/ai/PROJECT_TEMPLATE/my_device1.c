#include "ch32fun.h"

/* UIAPduino Pro Micro CH32V003 V1.4: D2 / PC0 is active High. */
#define BUILTIN_LED_PIN PC0

int main(void)
{
    SystemInit();

    /* Safe template state: keep the on-board LED off and drive no external pin. */
    funGpioInitAll();
    funPinMode(BUILTIN_LED_PIN, GPIO_CFGLR_OUT_10Mhz_PP);
    funDigitalWrite(BUILTIN_LED_PIN, FUN_LOW);

    while (1)
    {
        Delay_Ms(1000);
    }
}
