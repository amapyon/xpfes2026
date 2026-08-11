#include "ch32fun.h"
#include "usb_config.h"
#include "rv003usb.h"

#include <string.h>

/* Keep the module leads straight: S1 -> D9/PC7, S2 -> D8/PC6. */
#define ENCODER_S1_PIN PC7
#define ENCODER_S2_PIN PC6
#define ENCODER_DIRECTION 1
#define ENCODER_REPORT_SIZE 3u

#define HAPTIC_PIN PC4
#define HAPTIC_PULSE_MS 60u
#define HAPTIC_COMMAND_PULSE 1u

#define HID_REQ_GET_IDLE 0x02A1u
#define HID_REQ_SET_IDLE 0x0A21u

static volatile int8_t pending_delta;
static volatile uint8_t report_sequence;
static uint8_t current_report[ENCODER_REPORT_SIZE] = {
    ENCODER_REPORT_ID,
    0,
    0
};
static uint8_t idle_rate;
static volatile uint8_t haptic_report_ready;
static uint8_t haptic_report[HAPTIC_REPORT_TOTAL_SIZE] = {
    HAPTIC_REPORT_ID,
    0
};

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
        current_report[0] = ENCODER_REPORT_ID;
        current_report[1] = (uint8_t)delta;
        current_report[2] = report_sequence++;
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

void usb_handle_user_data(struct usb_endpoint *e,
                          int current_endpoint,
                          uint8_t *data,
                          int len,
                          struct rv003usb_internal *ist)
{
    int offset;
    int to_copy;

    (void)current_endpoint;
    (void)ist;

    offset = e->count << 3;
    to_copy = e->max_len - offset;
    if (to_copy > len) {
        to_copy = len;
    }
    if (to_copy > 0 && offset < (int)sizeof(haptic_report)) {
        if (to_copy > (int)sizeof(haptic_report) - offset) {
            to_copy = (int)sizeof(haptic_report) - offset;
        }
        memcpy(haptic_report + offset, data, (size_t)to_copy);
    }

    e->count++;
    if ((e->count << 3) >= e->max_len &&
        e->max_len == (int)sizeof(haptic_report) &&
        haptic_report[0] == HAPTIC_REPORT_ID) {
        haptic_report_ready = 1;
    }
}

void usb_handle_hid_get_report_start(struct usb_endpoint *e,
                                     int req_len,
                                     uint32_t value_index)
{
    uint8_t report_id = (uint8_t)value_index;

    if (report_id == ENCODER_REPORT_ID) {
        e->opaque = current_report;
        e->max_len = (req_len < ENCODER_REPORT_SIZE) ?
                     req_len : ENCODER_REPORT_SIZE;
        return;
    }

    haptic_report[0] = HAPTIC_REPORT_ID;
    haptic_report[1] = 0;
    if (req_len > (int)sizeof(haptic_report)) {
        req_len = sizeof(haptic_report);
    }
    e->opaque = haptic_report;
    e->max_len = req_len;
}

void usb_handle_hid_set_report_start(struct usb_endpoint *e,
                                     int req_len,
                                     uint32_t value_index)
{
    uint8_t report_id = (uint8_t)value_index;

    if (report_id != HAPTIC_REPORT_ID) {
        e->max_len = 0;
        return;
    }
    if (req_len > (int)sizeof(haptic_report)) {
        req_len = sizeof(haptic_report);
    }
    haptic_report[0] = 0;
    haptic_report[1] = 0;
    e->max_len = req_len;
}

int main(void)
{
    SystemInit();
    funGpioInitAll();
    funPinMode(ENCODER_S1_PIN, GPIO_CFGLR_IN_PUPD);
    funPinMode(ENCODER_S2_PIN, GPIO_CFGLR_IN_PUPD);
    funPinMode(HAPTIC_PIN, GPIO_CFGLR_OUT_10Mhz_PP);
    funDigitalWrite(ENCODER_S1_PIN, FUN_HIGH);
    funDigitalWrite(ENCODER_S2_PIN, FUN_HIGH);
    funDigitalWrite(HAPTIC_PIN, FUN_LOW);

    uint8_t previous = (uint8_t)((funDigitalRead(ENCODER_S1_PIN) << 1) |
                                 funDigitalRead(ENCODER_S2_PIN));
    int8_t quarter_steps = 0;
    uint8_t haptic_ms_remaining = 0;

    Delay_Ms(1);
    usb_setup();

    for (;;) {
        if (haptic_report_ready) {
            haptic_report_ready = 0;
            if (haptic_report[1] == HAPTIC_COMMAND_PULSE) {
                funDigitalWrite(HAPTIC_PIN, FUN_HIGH);
                haptic_ms_remaining = HAPTIC_PULSE_MS;
            }
        }

        uint8_t current = (uint8_t)((funDigitalRead(ENCODER_S1_PIN) << 1) |
                                    funDigitalRead(ENCODER_S2_PIN));
        if (current != previous) {
            int8_t movement = transition_table[(previous << 2) | current];
            previous = current;
            quarter_steps = (int8_t)(quarter_steps + movement);

            if (quarter_steps >= 4) {
                if (pending_delta < 120) {
                    pending_delta = (int8_t)(pending_delta + ENCODER_DIRECTION);
                }
                quarter_steps = 0;
            } else if (quarter_steps <= -4) {
                if (pending_delta > -120) {
                    pending_delta = (int8_t)(pending_delta - ENCODER_DIRECTION);
                }
                quarter_steps = 0;
            }
        }

        Delay_Ms(1);
        if (haptic_ms_remaining > 0u) {
            haptic_ms_remaining--;
            if (haptic_ms_remaining == 0u) {
                funDigitalWrite(HAPTIC_PIN, FUN_LOW);
            }
        }
    }
}
