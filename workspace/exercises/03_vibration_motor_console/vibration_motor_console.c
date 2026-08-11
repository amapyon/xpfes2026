#include "ch32fun.h"
#include "rv003usb.h"
#include "usb_config.h"

#include <stdint.h>
#include <string.h>

/* UIAPduino D6/A2 = CH32V003 PC4。モジュールのIN端子だけを駆動する。 */
#define MOTOR_PIN PC4
#define HAPTIC_PIN MOTOR_PIN
#include "haptic_pattern.h"

/* macOSが接続時に送るHIDクラス要求。 */
#define HID_REQ_GET_IDLE 0x02A1u
#define HID_REQ_SET_IDLE 0x0A21u

static volatile uint8_t report_ready;
static uint8_t idle_rate;
static uint8_t feature_report[MOTOR_REPORT_TOTAL_SIZE] = {
    MOTOR_REPORT_ID,
    0
};

int main(void)
{
    SystemInit();
    funGpioInitAll();

    /* USB初期化より前に必ずLowへ固定し、起動時の誤振動を防ぐ。 */
    haptic_pattern_init();

    Delay_Ms(100);
    usb_setup();

    for (;;) {
        if (report_ready) {
            uint16_t on_ms;
            uint16_t off_ms;

            report_ready = 0;
            on_ms = (uint16_t)(feature_report[HAPTIC_ON_MS_LO_OFFSET] |
                               ((uint16_t)feature_report[HAPTIC_ON_MS_HI_OFFSET] << 8));
            off_ms = (uint16_t)(feature_report[HAPTIC_OFF_MS_LO_OFFSET] |
                                ((uint16_t)feature_report[HAPTIC_OFF_MS_HI_OFFSET] << 8));
            haptic_pattern_start(feature_report[HAPTIC_LEVEL_OFFSET], on_ms,
                                 off_ms, feature_report[HAPTIC_COUNT_OFFSET]);
        }
        Delay_Ms(1);
        haptic_pattern_tick_1ms();
    }
}

void usb_handle_user_in_request(struct usb_endpoint *e,
                                uint8_t *scratchpad,
                                int endp,
                                uint32_t sendtok,
                                struct rv003usb_internal *ist)
{
    (void)e;
    (void)scratchpad;
    (void)ist;
    if (endp) {
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
    if (to_copy > 0 && offset < (int)sizeof(feature_report)) {
        if (to_copy > (int)sizeof(feature_report) - offset) {
            to_copy = (int)sizeof(feature_report) - offset;
        }
        memcpy(feature_report + offset, data, (size_t)to_copy);
    }

    e->count++;
    if ((e->count << 3) >= e->max_len &&
        e->max_len == (int)sizeof(feature_report) &&
        feature_report[0] == MOTOR_REPORT_ID) {
        report_ready = 1;
    }
}

void usb_handle_hid_get_report_start(struct usb_endpoint *e,
                                     int req_len,
                                     uint32_t value)
{
    (void)value;
    feature_report[0] = MOTOR_REPORT_ID;
    feature_report[HAPTIC_LEVEL_OFFSET] = haptic_pattern_current_level();
    if (req_len > (int)sizeof(feature_report)) {
        req_len = sizeof(feature_report);
    }
    e->opaque = feature_report;
    e->max_len = req_len;
}

void usb_handle_hid_set_report_start(struct usb_endpoint *e,
                                     int req_len,
                                     uint32_t value)
{
    uint8_t report_id = (uint8_t)(value & 0xffu);

    if (report_id != MOTOR_REPORT_ID) {
        e->max_len = 0;
        return;
    }
    if (req_len > (int)sizeof(feature_report)) {
        req_len = sizeof(feature_report);
    }
    memset(feature_report, 0, sizeof(feature_report));
    e->max_len = req_len;
}
