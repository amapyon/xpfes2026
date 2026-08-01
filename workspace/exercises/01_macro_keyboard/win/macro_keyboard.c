#include "ch32fun.h"
#include "rv003usb.h"
#include <stdint.h>

#define ENCODER_KEY_PIN PC3
#define DEBOUNCE_MS 20

static volatile uint8_t macro_step;
static uint8_t hid_idle_rate;
static uint8_t hid_protocol = 1;

static void fill_report(uint8_t report[8], uint8_t step)
{
    for (int i = 0; i < 8; ++i) report[i] = 0;
    switch (step) {
        case 1: report[0] = 0x02; report[2] = 0x04; break; /* A */
        case 3: report[2] = 0x05; break;                  /* b */
        case 5: report[0] = 0x02; report[2] = 0x06; break; /* C */
        case 7: report[2] = 0x07; break;                  /* d */
        case 9: report[0] = 0x02; report[2] = 0x08; break; /* E */
        default: break;                                   /* release */
    }
}

int main(void)
{
    SystemInit();
    funGpioInitAll();
    funPinMode(ENCODER_KEY_PIN, GPIO_CFGLR_IN_PUPD);
    funDigitalWrite(ENCODER_KEY_PIN, FUN_HIGH);
    Delay_Ms(10);
    usb_setup();

    uint8_t stable = (uint8_t)funDigitalRead(ENCODER_KEY_PIN);
    uint8_t sample = stable;
    uint8_t count = 0;

    while (1) {
        uint8_t now = (uint8_t)funDigitalRead(ENCODER_KEY_PIN);
        if (now == sample) {
            if (count < DEBOUNCE_MS) ++count;
        } else {
            sample = now;
            count = 0;
        }
        if (count == DEBOUNCE_MS && stable != sample) {
            stable = sample;
            if (stable == FUN_LOW && macro_step == 0) macro_step = 1;
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
        static uint8_t report[8];
        uint8_t step = macro_step;
        fill_report(report, step);
        usb_send_data(report, sizeof(report), 0, sendtok);
        if (step != 0) {
            ++step;
            macro_step = (step > 10) ? 0 : step;
        }
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

void usb_handle_other_control_message(struct usb_endpoint *e,
                                      struct usb_urb *s,
                                      struct rv003usb_internal *ist)
{
    (void)ist;
    static uint8_t report[8];
    const uint16_t request = s->wRequestTypeLSBRequestMSB;
    const uint16_t value = (uint16_t)(s->lValueLSBIndexMSB & 0xffffu);
    switch (request) {
        case 0x01A1: /* GET_REPORT */
            fill_report(report, macro_step);
            e->opaque = report;
            e->max_len = (s->wLength < sizeof(report)) ? s->wLength : sizeof(report);
            break;
        case 0x02A1: /* GET_IDLE */
            e->opaque = &hid_idle_rate;
            e->max_len = 1;
            break;
        case 0x0A21: /* SET_IDLE */
            hid_idle_rate = (uint8_t)(value >> 8);
            e->opaque = 0;
            e->max_len = 0;
            break;
        case 0x03A1: /* GET_PROTOCOL */
            e->opaque = &hid_protocol;
            e->max_len = 1;
            break;
        case 0x0B21: /* SET_PROTOCOL */
            hid_protocol = (uint8_t)(value & 1u);
            e->opaque = 0;
            e->max_len = 0;
            break;
        default:
            e->opaque = 0;
            e->max_len = 0;
            break;
    }
}
