#include "ch32fun.h"
#include "rv003usb.h"
#include "ch32v003_GPIO_branchless.h"

#define JOY_X_PIN PA2
#define JOY_Y_PIN PA1
#define JOY_SW_PIN PC3
#define JOY_X_ADC GPIO_Ain0_A2
#define JOY_Y_ADC GPIO_Ain1_A1

#define REPORT_SIZE 4u
#define CENTER_SAMPLES 64u
#define FILTER_SHIFT 2u
#define DEAD_ZONE 36
#define LEVEL_STEP 56
#define X_DIRECTION 1
#define Y_DIRECTION 1

#define HID_REQ_GET_REPORT 0x01A1u
#define HID_REQ_GET_IDLE   0x02A1u
#define HID_REQ_SET_IDLE   0x0A21u

static volatile uint8_t report_data[REPORT_SIZE];
static uint8_t usb_report[REPORT_SIZE];
static uint8_t control_report[REPORT_SIZE];
static uint8_t idle_rate;

static int8_t axis_level(int32_t filtered, int32_t center, int direction)
{
    int32_t delta = (filtered - center) * direction;
    int32_t magnitude;
    int32_t level;

    if (delta >= -DEAD_ZONE && delta <= DEAD_ZONE) return 0;
    magnitude = (delta < 0) ? -delta : delta;
    level = 1 + (magnitude - DEAD_ZONE - 1) / LEVEL_STEP;
    if (level > 5) level = 5;
    return (int8_t)((delta < 0) ? -level : level);
}

void usb_handle_user_in_request(struct usb_endpoint *e, uint8_t *scratchpad,
                                int endp, uint32_t sendtok,
                                struct rv003usb_internal *ist)
{
    uint8_t i;
    (void)e;
    (void)scratchpad;
    (void)ist;

    if (endp != 1) {
        usb_send_empty(sendtok);
        return;
    }
    for (i = 0; i < REPORT_SIZE; ++i) usb_report[i] = report_data[i];
    usb_send_data(usb_report, REPORT_SIZE, 0, sendtok);
}

void usb_handle_other_control_message(struct usb_endpoint *e,
                                      struct usb_urb *s,
                                      struct rv003usb_internal *ist)
{
    uint16_t request = s->wRequestTypeLSBRequestMSB;
    uint16_t value = (uint16_t)(s->lValueLSBIndexMSB & 0xffffu);
    uint16_t length = s->wLength;
    uint8_t i;
    (void)ist;

    switch (request) {
    case HID_REQ_GET_REPORT:
        for (i = 0; i < REPORT_SIZE; ++i) control_report[i] = report_data[i];
        e->opaque = control_report;
        e->max_len = (length < REPORT_SIZE) ? length : REPORT_SIZE;
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
    uint32_t x_sum = 0;
    uint32_t y_sum = 0;
    int32_t x_center;
    int32_t y_center;
    int32_t x_filtered;
    int32_t y_filtered;
    uint8_t i;
    uint8_t sequence = 0;

    SystemInit();
    funGpioInitAll();
    GPIO_pinMode(JOY_X_PIN, GPIO_pinMode_I_analog, GPIO_Speed_In);
    GPIO_pinMode(JOY_Y_PIN, GPIO_pinMode_I_analog, GPIO_Speed_In);
    funPinMode(JOY_SW_PIN, GPIO_CFGLR_IN_PUPD);
    funDigitalWrite(JOY_SW_PIN, FUN_HIGH);
    GPIO_ADCinit();

    /* Keep the stick untouched during this approximately 0.5 s calibration. */
    Delay_Ms(250);
    for (i = 0; i < CENTER_SAMPLES; ++i) {
        x_sum += GPIO_analogRead(JOY_X_ADC);
        y_sum += GPIO_analogRead(JOY_Y_ADC);
        Delay_Ms(4);
    }
    x_center = (int32_t)(x_sum / CENTER_SAMPLES);
    y_center = (int32_t)(y_sum / CENTER_SAMPLES);
    x_filtered = x_center;
    y_filtered = y_center;

    report_data[0] = 0;
    report_data[1] = 0;
    report_data[2] = 0;
    report_data[3] = 0;
    usb_setup();

    for (;;) {
        int32_t x_raw = GPIO_analogRead(JOY_X_ADC);
        int32_t y_raw = GPIO_analogRead(JOY_Y_ADC);
        x_filtered += (x_raw - x_filtered) >> FILTER_SHIFT;
        y_filtered += (y_raw - y_filtered) >> FILTER_SHIFT;

        report_data[0] = (uint8_t)axis_level(x_filtered, x_center, X_DIRECTION);
        report_data[1] = (uint8_t)axis_level(y_filtered, y_center, Y_DIRECTION);
        report_data[2] = (uint8_t)(funDigitalRead(JOY_SW_PIN) == FUN_LOW);
        report_data[3] = sequence++;
        Delay_Ms(5);
    }
}
