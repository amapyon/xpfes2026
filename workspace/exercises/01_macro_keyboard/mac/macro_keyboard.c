#include "ch32fun.h"
#include "rv003usb.h"

#define ENCODER_KEY_PIN PC3
#define DEBOUNCE_MS 20u
#define KEY_LEFT_SHIFT 0x02u
#define KEYBOARD_REPORT_SIZE 8u

/* bmRequestType is stored in the low byte and bRequest in the high byte. */
#define HID_REQ_GET_REPORT   0x01A1u
#define HID_REQ_GET_IDLE     0x02A1u
#define HID_REQ_GET_PROTOCOL 0x03A1u
#define HID_REQ_SET_IDLE     0x0A21u
#define HID_REQ_SET_PROTOCOL 0x0B21u

static volatile uint8_t sequence_active;
static volatile uint8_t sequence_index;
static uint8_t current_report[KEYBOARD_REPORT_SIZE];
static uint8_t idle_rate;
static uint8_t keyboard_protocol = 1u; /* Report protocol is the HID default. */

static const uint8_t key_sequence[][KEYBOARD_REPORT_SIZE] = {
    {KEY_LEFT_SHIFT, 0, 0x04, 0, 0, 0, 0, 0}, {0},
    {0, 0, 0x05, 0, 0, 0, 0, 0}, {0},
    {KEY_LEFT_SHIFT, 0, 0x06, 0, 0, 0, 0, 0}, {0},
    {0, 0, 0x07, 0, 0, 0, 0, 0}, {0},
    {KEY_LEFT_SHIFT, 0, 0x08, 0, 0, 0, 0, 0}, {0}
};

static void copy_report(const uint8_t *source)
{
    uint8_t i;
    for (i = 0; i < KEYBOARD_REPORT_SIZE; i++) {
        current_report[i] = source[i];
    }
}

void usb_handle_user_in_request(struct usb_endpoint *e, uint8_t *scratchpad,
                                int endp, uint32_t sendtok,
                                struct rv003usb_internal *ist)
{
    (void)e;
    (void)scratchpad;
    (void)ist;

    if (endp == 1) {
        if (sequence_active) {
            uint8_t index = sequence_index;
            copy_report(key_sequence[index]);
            usb_send_data(current_report, KEYBOARD_REPORT_SIZE, 0, sendtok);
            index++;
            if (index >= (uint8_t)(sizeof(key_sequence) / sizeof(key_sequence[0]))) {
                sequence_index = 0;
                sequence_active = 0;
            } else {
                sequence_index = index;
            }
        } else {
            usb_send_data(current_report, KEYBOARD_REPORT_SIZE, 0, sendtok);
        }
    } else {
        usb_send_empty(sendtok);
    }
}

/*
 * rv003usb forwards unhandled endpoint-zero requests here when
 * RV003USB_OTHER_CONTROL is enabled.  macOS requests these HID boot-keyboard
 * states while attaching IOHIDFamily.
 */
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
        e->max_len = (length < KEYBOARD_REPORT_SIZE) ? length : KEYBOARD_REPORT_SIZE;
        break;
    case HID_REQ_GET_IDLE:
        e->opaque = &idle_rate;
        e->max_len = (length < 1u) ? length : 1u;
        break;
    case HID_REQ_SET_IDLE:
        idle_rate = (uint8_t)(value >> 8);
        break;
    case HID_REQ_GET_PROTOCOL:
        e->opaque = &keyboard_protocol;
        e->max_len = (length < 1u) ? length : 1u;
        break;
    case HID_REQ_SET_PROTOCOL:
        keyboard_protocol = (uint8_t)(value & 0x01u);
        break;
    default:
        break;
    }
}

int main(void)
{
    SystemInit();
    funGpioInitAll();
    funPinMode(ENCODER_KEY_PIN, GPIO_CFGLR_IN_PUPD);
    funDigitalWrite(ENCODER_KEY_PIN, FUN_HIGH);

    /* Static storage initializes current_report to the all-keys-released state. */
    Delay_Ms(1);
    usb_setup();

    uint8_t last_raw = (uint8_t)funDigitalRead(ENCODER_KEY_PIN);
    uint8_t stable = last_raw;
    uint8_t stable_count = 0;

    for (;;) {
        uint8_t raw = (uint8_t)funDigitalRead(ENCODER_KEY_PIN);
        if (raw == last_raw) {
            if (stable_count < DEBOUNCE_MS) {
                stable_count++;
            }
        } else {
            last_raw = raw;
            stable_count = 0;
        }

        if (stable_count >= DEBOUNCE_MS && raw != stable) {
            stable = raw;
            if (stable == 0 && !sequence_active) {
                sequence_index = 0;
                sequence_active = 1;
            }
        }
        Delay_Ms(1);
    }
}
