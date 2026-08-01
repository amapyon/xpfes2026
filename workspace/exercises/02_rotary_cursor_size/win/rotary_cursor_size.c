#include "ch32fun.h"
#include "rv003usb.h"
#include <stdint.h>

#define ENCODER_A_PIN PC6
#define ENCODER_B_PIN PC7

static volatile int8_t pending_delta;

static int8_t transition_delta(uint8_t previous, uint8_t current)
{
    static const int8_t table[16] = {
         0, -1,  1,  0,
         1,  0,  0, -1,
        -1,  0,  0,  1,
         0,  1, -1,  0
    };
    return table[((previous & 3u) << 2) | (current & 3u)];
}

int main(void)
{
    SystemInit();
    funGpioInitAll();
    funPinMode(ENCODER_A_PIN, GPIO_CFGLR_IN_PUPD);
    funPinMode(ENCODER_B_PIN, GPIO_CFGLR_IN_PUPD);
    funDigitalWrite(ENCODER_A_PIN, FUN_HIGH);
    funDigitalWrite(ENCODER_B_PIN, FUN_HIGH);
    Delay_Ms(10);
    usb_setup();

    uint8_t previous = (uint8_t)((funDigitalRead(ENCODER_A_PIN) << 1) |
                                 funDigitalRead(ENCODER_B_PIN));
    int8_t accumulator = 0;

    while (1) {
        uint8_t current = (uint8_t)((funDigitalRead(ENCODER_A_PIN) << 1) |
                                    funDigitalRead(ENCODER_B_PIN));
        if (current != previous) {
            accumulator += transition_delta(previous, current);
            previous = current;
            if (accumulator >= 4) {
                if (pending_delta < 127) ++pending_delta;
                accumulator = 0;
            } else if (accumulator <= -4) {
                if (pending_delta > -127) --pending_delta;
                accumulator = 0;
            }
        }
        Delay_Ms(1);
    }
}

void usb_handle_user_in_request(struct usb_endpoint *e, uint8_t *scratchpad,
                                int endp, uint32_t sendtok,
                                struct rv003usb_internal *ist)
{
    (void)e; (void)scratchpad; (void)ist;
    if (endp == 1) {
        static int8_t report;
        report = pending_delta;
        pending_delta = 0;
        usb_send_data(&report, 1, 0, sendtok);
    } else {
        usb_send_empty(sendtok);
    }
}

void usb_handle_user_data(struct usb_endpoint *e, int current_endpoint,
                          uint8_t *data, int len,
                          struct rv003usb_internal *ist)
{
    (void)e; (void)current_endpoint; (void)data; (void)len; (void)ist;
}
