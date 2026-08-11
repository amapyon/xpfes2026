#include "ch32fun.h"

/* UIAPduino Pro Micro CH32V003 V1.4: D2 / BUILTIN-LED is PC0, active High. */
#define BUILTIN_LED_PIN PC0
#define BUILTIN_LED_ON FUN_HIGH
#define BUILTIN_LED_OFF FUN_LOW
#define BLINK_ON_MS 150u
#define BLINK_GAP_MS 150u
#define BLINK_PAUSE_MS 1500u
#define BLINK_FLASH_COUNT 3u

int main(void)
{
    SystemInit();
    funGpioInitAll();
    funPinMode(BUILTIN_LED_PIN, GPIO_CFGLR_OUT_10Mhz_PP);

    while (1) {
        uint8_t flash;

        for (flash = 0; flash < BLINK_FLASH_COUNT; flash++) {
            funDigitalWrite(BUILTIN_LED_PIN, BUILTIN_LED_ON);
            Delay_Ms(BLINK_ON_MS);
            funDigitalWrite(BUILTIN_LED_PIN, BUILTIN_LED_OFF);
            Delay_Ms((flash + 1u < BLINK_FLASH_COUNT) ?
                     BLINK_GAP_MS : BLINK_PAUSE_MS);
        }
    }
}
