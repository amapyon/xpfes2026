#include "ch32fun.h"
#include "rv003usb.h"

#define ENCODER_S1_PIN PC7
#define ENCODER_S2_PIN PC6
#define ENCODER_DIRECTION 1
#define ENCODER_REPORT_SIZE 2u

#define HID_REQ_GET_REPORT 0x01A1u
#define HID_REQ_GET_IDLE   0x02A1u
#define HID_REQ_SET_IDLE   0x0A21u

static volatile int8_t pending_delta;
static volatile uint8_t report_sequence;
static uint8_t current_report[ENCODER_REPORT_SIZE];
static uint8_t idle_rate;

static const int8_t transition_table[16] = {
     0, -1,  1,  0,
     1,  0,  0, -1,
    -1,  0,  0,  1,
     0,  1, -1,  0
};

void usb_handle_user_in_request(struct usb_endpoint *e, uint8_t *scratchpad,
                                int endp, uint32_t sendtok,
                                struct rv003usb_internal *ist)
{
    (void)e;
    (void)scratchpad;
    (void)ist;

    if (endp == 1) {
        int8_t delta = pending_delta;
        pending_delta = 0;
        current_report[0] = (uint8_t)delta;
        current_report[1] = report_sequence++;
        usb_send_data(current_report, ENCODER_REPORT_SIZE, 0, sendtok);
    } else {
        usb_send_empty(sendtok);
    }
}

void usb_handle_other_control_message(struct usb_endpoint *e,
                                      struct usb_urb *s,
                                      struct rv003usb_internal *ist)
{
    uint16_t request = s->wRequestTypeLSBRequestMSB;
    uint16_t value = (uint16_t)(s->lValueLSBIndexMSB & 0xffffu);
    uint16_t length = s->wLength;
    (void)ist;

    switch (request) {
    case HID_REQ_GET_REPORT:
        e->opaque = current_report;
        e->max_len = (length < ENCODER_REPORT_SIZE) ? length : ENCODER_REPORT_SIZE;
        break;
    case HID_REQ_GET_IDLE:
        e->opaque = &idle_rate;
        e->max_len = (length < 1u) ? length : 1u;
        break;
    case HID_REQ_SET_IDLE:
        idle_rate = (uint8_t)(value >> 8);
        break;
    default:
        break;
    }
}

int main(void)
{
    SystemInit();
    funGpioInitAll();
    funPinMode(ENCODER_S1_PIN, GPIO_CFGLR_IN_PUPD);
    funPinMode(ENCODER_S2_PIN, GPIO_CFGLR_IN_PUPD);
    funDigitalWrite(ENCODER_S1_PIN, FUN_HIGH);
    funDigitalWrite(ENCODER_S2_PIN, FUN_HIGH);

    uint8_t previous = (uint8_t)((funDigitalRead(ENCODER_S1_PIN) << 1) |
                                 funDigitalRead(ENCODER_S2_PIN));
    int8_t quarter_steps = 0;

    Delay_Ms(1);
    usb_setup();

    for (;;) {
        uint8_t current = (uint8_t)((funDigitalRead(ENCODER_S1_PIN) << 1) |
                                    funDigitalRead(ENCODER_S2_PIN));
        if (current != previous) {
            int8_t movement = transition_table[(previous << 2) | current];
            previous = current;
            quarter_steps = (int8_t)(quarter_steps + movement);

            if (quarter_steps >= 4) {
                if (pending_delta < 120) pending_delta = (int8_t)(pending_delta + ENCODER_DIRECTION);
                quarter_steps = 0;
            } else if (quarter_steps <= -4) {
                if (pending_delta > -120) pending_delta = (int8_t)(pending_delta - ENCODER_DIRECTION);
                quarter_steps = 0;
            }
        }
        Delay_Ms(1);
    }
}
