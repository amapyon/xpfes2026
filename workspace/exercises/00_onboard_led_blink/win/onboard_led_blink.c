#include "ch32fun.h"

int main(void)
{
    SystemInit();
    funGpioInitAll();

    funPinMode(PC0, GPIO_CFGLR_OUT_10Mhz_PP);

    while (1) {
        funDigitalWrite(PC0, FUN_LOW);
        Delay_Ms(200);
        funDigitalWrite(PC0, FUN_HIGH);
        Delay_Ms(800);
    }
}
